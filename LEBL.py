# fem servir la funció de V1/V2 per saber si un vol és schengen
from airport import IsSchengenAirport

# importem la funció per carregar vols (V2)
from aircraft import LoadArrivals


# CLASSES PRINCIPALS

# CLASSE BARCELONA AP
# representa l’aeroport de Barcelona i conté els terminals

class BarcelonaAP:

    def __init__(self, code=""):
        self.code = code              # codi de l’aeroport (ex: LEBL)
        self.terminals = []           # llista de terminals


# CLASSE TERMINAL
# cada terminal té boarding areas i companyies associades

class Terminal:

    def __init__(self, name=""):
        self.name = name
        self.boarding_areas = []      # àrees d’embarcament
        self.airlines = []            # companyies que operen aquí


# CLASSE BOARDING AREA
# representa una zona schengen o no schengen dins del terminal

class BoardingArea:

    def __init__(self, name="", area_type=""):
        self.name = name
        self.area_type = area_type    # "Schengen" o "non-Schengen"
        self.gates = []               # gates dins d’aquesta àrea


# CLASSE GATE
# representa una porta d’embarcament

class Gate:

    def __init__(self, name="", occupied=False, aircraft_id=""):
        self.name = name
        self.occupied = occupied      # indica si està ocupada
        self.aircraft_id = aircraft_id  # avió assignat


# SET GATES

def SetGates(area, init_gate, end_gate, prefix):

    # si el rang és incorrecte, retornem error
    if end_gate < init_gate:
        return -1

    # reiniciem la llista de gates
    area.gates = []

    gate_num = init_gate

    # creem totes les gates dins del rang
    while gate_num <= end_gate:

        gate_name = prefix + str(gate_num)

        # cada gate comença lliure
        gate = Gate(gate_name, False, "")

        area.gates.append(gate)

        gate_num += 1

    return 0


# LOAD AIRLINES

def LoadAirlines(terminal, t_name):

    filename = t_name + "_Airlines.txt"

    try:
        F = open(filename, "r")
    except:
        return -1

    lines = F.readlines()
    F.close()

    airlines_temp = []

    for line in lines:

        line = line.strip()

        if line != "":
            parts = line.split()

            # últim element = codi ICAO
            icao = parts[-1]
            airlines_temp.append(icao)

    terminal.airlines = airlines_temp

    return 0


# LOAD AIRPORT STRUCTURE

def LoadAirportStructure(filename):

    try:
        F = open(filename, "r")
    except:
        return -1

    lines = F.readlines()
    F.close()

    if len(lines) == 0:
        return -1

    # primera línia: codi aeroport i nombre de terminals
    first = lines[0].split()

    if len(first) < 3:
        return -1

    airport_code = first[0]
    num_terminals = int(first[1])  # "LEBL 2 terminals"

    bcn = BarcelonaAP(airport_code)

    i = 1
    terminals_loaded = 0

    while i < len(lines) and terminals_loaded < num_terminals:

        parts = lines[i].split()

        if len(parts) < 4:
            return -1

        if parts[0] != "Terminal":
            return -1

        terminal_name = parts[1]
        num_areas = int(parts[2])  # "5 boarding areas"

        terminal = Terminal(terminal_name)

        # carreguem companyies del terminal
        err = LoadAirlines(terminal, terminal_name)
        if err == -1:
            return -1

        i += 1
        areas_loaded = 0

        # carreguem boarding areas
        while i < len(lines) and areas_loaded < num_areas:

            parts = lines[i].split()

            if len(parts) < 7:
                return -1

            if parts[0] != "Area":
                return -1

            area_name = parts[1]
            area_type = parts[2]  # Schengen / non-Schengen

            # format: Gates 1 - 11
            init_gate = int(parts[4])
            end_gate = int(parts[6])

            area = BoardingArea(area_name, area_type)

            prefix = terminal_name + area_name + "_G"

            err = SetGates(area, init_gate, end_gate, prefix)
            if err == -1:
                return -1

            terminal.boarding_areas.append(area)

            i += 1
            areas_loaded += 1

        bcn.terminals.append(terminal)
        terminals_loaded += 1

    return bcn


# GATE OCCUPANCY

def GateOccupancy(bcn):

    occupancy = []

    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:

                occupancy.append([
                    terminal.name,
                    area.name,
                    gate.name,
                    gate.occupied,
                    gate.aircraft_id
                ])

    return occupancy



# IS AIRLINE IN TERMINAL

def IsAirlineInTerminal(terminal, name):

    if name == "":
        return False

    return name in terminal.airlines



# SEARCH TERMINAL


def SearchTerminal(bcn, name):

    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.name

    return ""



# ASSIGN GATE


# ============================================================
# _movement_airport_code
# Decideix quin aeroport usem per saber si el moviment és Schengen.
# Si és una arribada usem origin.
# Si és un avió nocturn o una sortida usem destination.
# ============================================================
def _movement_airport_code(aircraft):

    if aircraft.origin != "":
        return aircraft.origin

    return aircraft.destination


# ============================================================
# AssignGate
# Assigna una gate lliure a un avió.
# Procés:
# 1) companyia -> terminal
# 2) origin/destination -> Schengen o non-Schengen
# 3) primera gate lliure dins l'àrea correcta
# ============================================================
def AssignGate(bcn, aircraft):

    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    airport_code = _movement_airport_code(aircraft)

    if airport_code == "":
        return -1

    flight_is_schengen = IsSchengenAirport(airport_code)

    for terminal in bcn.terminals:

        if terminal.name == terminal_name:

            for area in terminal.boarding_areas:

                if flight_is_schengen and area.area_type.lower() == "schengen":
                    correct_area = True
                elif (not flight_is_schengen) and area.area_type.lower() != "schengen":
                    correct_area = True
                else:
                    correct_area = False

                if correct_area:

                    for gate in area.gates:

                        if not gate.occupied:
                            gate.occupied = True
                            gate.aircraft_id = aircraft.aircraft_id
                            return gate.name

    return -1

# FREE GATE

def FreeGate(bcn, aircraft_id):

    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:

                if gate.aircraft_id == aircraft_id:
                    gate.occupied = False
                    gate.aircraft_id = ""
                    return 0

    return -1



# ASSIGN NIGHT GATES

# ============================================================
# AssignNightGates
# Assigna gates als avions que ja estaven a LEBL a les 00:00.
# Són avions que tenen departure però no tenen arrival.
# Retorna quants s'han assignat i quants han fallat.
# ============================================================
def AssignNightGates(bcn, aircrafts):

    assigned = 0
    failed = 0

    for a in aircrafts:

        # Avió nocturn: no arriba durant el dia, però sí que surt
        if a.arrival == "" and a.departure != "":

            gate_name = AssignGate(bcn, a)

            if gate_name == -1:
                failed += 1
            else:
                assigned += 1

    return assigned, failed


# ASSIGN GATES AT TIME

def AssignGatesAtTime(bcn, aircrafts, time):

    current_hour = int(time.split(":")[0])

    # 1) alliberar gates dels avions que ja han marxat
    for a in aircrafts:

        if a.departure != "":
            dep_hour = int(a.departure.split(":")[0])

            if dep_hour <= current_hour:
                FreeGate(bcn, a.aircraft_id)

    # 2) assignar gates als avions que arriben ara
    not_assigned = 0

    for a in aircrafts:

        if a.arrival != "":
            arr_hour = int(a.arrival.split(":")[0])

            if arr_hour == current_hour:

                gate_name = AssignGate(bcn, a)

                if gate_name == -1:
                    not_assigned += 1

    return not_assigned



# PLOT DAY OCCUPANCY


# ============================================================
# PLOT DAY OCCUPANCY
# mostra l'ocupació de gates durant tot el dia
# si rep una figura, dibuixa dins del panell
# ============================================================

def PlotDayOccupancy(bcn, aircrafts, fig=None):
    import matplotlib.pyplot as plt
    import copy

    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    # fem una còpia per no modificar l'aeroport real
    bcn_copy = copy.deepcopy(bcn)

    hours = []
    occupied = []
    rejected = []

    for h in range(24):
        time = f"{h:02d}:00"
        na = AssignGatesAtTime(bcn_copy, aircrafts, time)

        # comptem gates ocupades
        count = 0
        for t in bcn_copy.terminals:
            for a in t.boarding_areas:
                for g in a.gates:
                    if g.occupied:
                        count += 1

        hours.append(h)
        occupied.append(count)
        rejected.append(na)

    ax.plot(hours, occupied, label="Gates ocupades")
    ax.plot(hours, rejected, label="No assignats")
    ax.set_title("Ocupació de gates durant el dia")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Nombre")
    ax.legend()
    ax.grid()

    if fig is None:
        plt.show()

# ============================================================
# SaveGateAssignments
# Desa l'estat actual de les gates en un fitxer de text.
# ============================================================
def SaveGateAssignments(bcn, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("TERMINAL | AREA | GATE | OCCUPIED | AIRCRAFT_ID\n")
            f.write("-" * 70 + "\n")

            for terminal in bcn.terminals:
                for area in terminal.boarding_areas:
                    for gate in area.gates:
                        occupied = "YES" if gate.occupied else "NO"
                        aircraft_id = gate.aircraft_id if gate.occupied else "-"
                        f.write(f"{terminal.name} | {area.name} | {gate.name} | {occupied} | {aircraft_id}\n")

        return 0  # tot correcte
    except Exception as e:
        print("Error saving gate assignments:", e)
        return -1  # error

# ============================================================
# DashboardData
# Calcula dades resum de l'operació diària per mostrar al dashboard.
# ============================================================
def DashboardData(bcn, aircrafts):
    data = {
        "arrivals": len([a for a in aircrafts if a.arrival]),
        "departures": len([a for a in aircrafts if a.departure]),
        "movements": len(aircrafts),
        "night_aircraft": len([a for a in aircrafts if a.arrival and int(a.arrival.split(":")[0]) < 6]),
        "max_occupied": 0,
        "max_hour": "-",
        "not_assigned": 0
    }

    # simulació simple per trobar hora de màxima ocupació
    import copy
    bcn_copy = copy.deepcopy(bcn)
    max_occ = 0
    max_hour = 0
    not_assigned_total = 0

    for h in range(24):
        rejected = AssignGatesAtTime(bcn_copy, aircrafts, f"{h:02d}:00")
        occupied = sum(1 for t in bcn_copy.terminals for a in t.boarding_areas for g in a.gates if g.occupied)
        if occupied > max_occ:
            max_occ = occupied
            max_hour = h
        not_assigned_total += rejected

    data["max_occupied"] = max_occ
    data["max_hour"] = f"{max_hour:02d}:00"
    data["not_assigned"] = not_assigned_total

    return data
