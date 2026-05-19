# fem servir la funció de V1/V2 per saber si un vol és schengen
from airport import IsSchengenAirport

# importem la funció per carregar vols (V2)
from aircraft import LoadArrivals

# CLASSE BARCELONA AP
# representa l’aeroport de barcelona i conté els terminals

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
# crea les gates d’una boarding àrea segons un rang numèric

def SetGates(area, init_gate, end_gate, prefix):

    # si el rang és incorrecte, retornem error
    if end_gate <= init_gate:
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
# carrega les companyies que operen en un terminal

def LoadAirlines(terminal, t_name):

    filename = t_name + "_Airlines.txt"

    try:
        F = open(filename, "r")
    except:
        return -1

    lines = F.readlines()
    F.close()

    airlines_temp = []

    i = 0
    while i < len(lines):

        line = lines[i].strip()

        if line != "":

            parts = line.split()

            if len(parts) >= 2:
                # agafem el codi ICAO de la companyia
                icao = parts[len(parts) - 1]
                airlines_temp.append(icao)

        i += 1

    # assignem la llista al terminal
    terminal.airlines = airlines_temp

    return 0


# LOAD AIRPORT STRUCTURE
# llegeix el fitxer LEBL.txt i crea tota l’estructura

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

    if len(first) < 2:
        return -1

    airport_code = first[0]
    num_terminals = int(first[1])

    # creem l’objecte principal de l’aeroport
    bcn = BarcelonaAP(airport_code)

    i = 1
    terminals_loaded = 0

    # carreguem cada terminal
    while i < len(lines) and terminals_loaded < num_terminals:

        parts = lines[i].split()

        if len(parts) < 3:
            return -1

        if parts[0] != "Terminal":
            return -1

        terminal_name = parts[1]
        num_areas = int(parts[2])

        terminal = Terminal(terminal_name)

        # carreguem companyies del terminal
        err = LoadAirlines(terminal, terminal_name)
        if err == -1:
            return -1

        i += 1
        areas_loaded = 0

        # carreguem boarding areas del terminal
        while i < len(lines) and areas_loaded < num_areas:

            parts = lines[i].split()

            if len(parts) < 7:
                return -1

            if parts[0] != "Area":
                return -1

            area_name = parts[1]
            area_type = parts[2]

            init_gate = int(parts[4])
            end_gate = int(parts[6])

            # creem boarding area
            area = BoardingArea(area_name, area_type)

            # prefix per identificar gates fàcilment
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
# retorna l’estat de totes les gates de l’aeroport

def GateOccupancy(bcn):

    occupancy = []

    i = 0
    while i < len(bcn.terminals):

        terminal = bcn.terminals[i]

        j = 0
        while j < len(terminal.boarding_areas):

            area = terminal.boarding_areas[j]

            k = 0
            while k < len(area.gates):

                gate = area.gates[k]

                occupancy.append([
                    terminal.name,
                    area.name,
                    gate.name,
                    gate.occupied,
                    gate.aircraft_id
                ])

                k += 1
            j += 1
        i += 1

    return occupancy


# IS AIRLINE IN TERMINAL
# comprova si una companyia opera en un terminal

def IsAirlineInTerminal(terminal, name):

    if name == "":
        print("Error: empty airline name")
        return False

    i = 0
    found = False

    while i < len(terminal.airlines) and not found:

        if terminal.airlines[i] == name:
            found = True
        else:
            i += 1

    return found

# SEARCH TERMINAL
# retorna en quin terminal opera una companyia

def SearchTerminal(bcn, name):

    i = 0
    found = False
    terminal_name = ""

    while i < len(bcn.terminals) and not found:

        if IsAirlineInTerminal(bcn.terminals[i], name):
            found = True
            terminal_name = bcn.terminals[i].name
        else:
            i += 1

    return terminal_name



# ASSIGN GATE
# assigna una gate lliure segons terminal i tipus de vol

def AssignGate(bcn, aircraft):

    # busquem terminal segons companyia
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    # determinem si el vol és schengen
    flight_is_schengen = IsSchengenAirport(aircraft.origin)

    i = 0
    while i < len(bcn.terminals):

        terminal = bcn.terminals[i]

        if terminal.name == terminal_name:

            j = 0
            while j < len(terminal.boarding_areas):

                area = terminal.boarding_areas[j]

                correct_area = False

                # seleccionem àrea correcta segons tipus de vol
                if flight_is_schengen and area.area_type.lower() == "schengen":
                    correct_area = True

                if (not flight_is_schengen) and area.area_type.lower() != "schengen":
                    correct_area = True

                if correct_area:

                    k = 0
                    while k < len(area.gates):

                        gate = area.gates[k]

                        # primera gate lliure que trobem
                        if not gate.occupied:

                            gate.occupied = True
                            gate.aircraft_id = aircraft.aircraft_id

                            return gate.name

                        k += 1
                j += 1
        i += 1

    return -1



# TEST SECTION
# proves manuals per comprovar que la V3 funciona

if __name__ == "__main__":

    print("TEST LOAD AIRPORT STRUCTURE")

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        print("Error: airport structure could not be loaded")
    else:
        print("Airport code:", bcn.code)
        print("Number of terminals:", len(bcn.terminals))

    print("TEST LOAD ARRIVALS + ASSIGN GATES")

    aircrafts = LoadArrivals("Arrivals.txt")
    print("Arrivals loaded:", len(aircrafts))

    if bcn != -1 and len(aircrafts) > 0:

        i = 0
        while i < len(aircrafts) and i < 10:

            gate_name = AssignGate(bcn, aircrafts[i])

            if gate_name == -1:
                print("Aircraft", aircrafts[i].aircraft_id, "not assigned")
            else:
                print("Aircraft", aircrafts[i].aircraft_id, "assigned to", gate_name)

            i += 1

    print("TEST GATE OCCUPANCY")

    if bcn != -1:

        occ = GateOccupancy(bcn)

        i = 0
        while i < len(occ) and i < 20:
            print(occ[i])
            i += 1