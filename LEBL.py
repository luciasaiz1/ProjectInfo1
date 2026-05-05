# LEBL.py
# Version 3 - Gate management

# Fem servir la funció de V1/V2 per saber si un vol és Schengen
from airport import IsSchengenAirport

# A la test section carregarem arribades de V2
from aircraft import LoadArrivals


# CLASS BarcelonaAP
# Aixo guarda el codi de l'aeroport i la llista de terminals

class BarcelonaAP:

    def __init__(self, code=""):
        self.code = code
        self.terminals = []   # cada element serà un Terminal


# CLASS Terminal
# Guarda el nom del terminal, les seves boarding areas i la llista d'airlines que operen en aquest terminal

class Terminal:

    def __init__(self, name=""):
        self.name = name
        self.boarding_areas = []   # cada element serà un BoardingArea
        self.airlines = []         # codis ICAO de companyies, ex: VLG, RYR


# CLASS BoardingArea
# Guarda el nom de l'àrea, el tipus (Schengen o non-Schengen) i les gates que conté
class BoardingArea:

    def __init__(self, name="", area_type=""):
        self.name = name
        self.area_type = area_type   # "Schengen" o "non-Schengen"
        self.gates = []              # cada element serà un Gate


# CLASS Gate
# Guarda el nom de la porta, si està ocupada o no i quin avió hi ha aparcat si està ocupada

class Gate:

    def __init__(self, name="", occupied=False, aircraft_id=""):
        self.name = name
        self.occupied = occupied
        self.aircraft_id = aircraft_id


# SetGates(area, init_gate, end_gate, prefix)
# Crea la llista de gates d'una boarding area
def SetGates(area, init_gate, end_gate, prefix):

    # Si el rang és incorrecte, retornem error
    if end_gate <= init_gate:
        return -1

    # Esborrem qualsevol llista anterior de gates
    area.gates = []

    # Recorrem tots els números de gate del rang
    gate_num = init_gate
    while gate_num <= end_gate:

        # Construïm el nom del gate amb prefix + número
        # Exemple: T1A_G1, T1A_G2, ...
        gate_name = prefix + str(gate_num)

        # Creem la gate lliure
        gate = Gate(gate_name, False, "")

        # L'afegim a la boarding area
        area.gates.append(gate)

        gate_num += 1

    return 0


# LoadAirlines(terminal, t_name)
# Carrega les companyies que operen en un terminal llegint T1_Airlines.txt o T2_Airlines.txt

def LoadAirlines(terminal, t_name):

    filename = t_name + "_Airlines.txt"

    # Obrim el fitxer; si no existeix, error i no toquem el terminal
    try:
        F = open(filename, "r")
    except:
        return -1

    lines = F.readlines()
    F.close()

    # Llista temporal: només si tot va bé la copiem al terminal
    airlines_temp = []

    i = 0
    while i < len(lines):

        line = lines[i].strip()

        # Si la línia no és buida, la processem
        if line != "":

            # Els fitxers tenen: NomCompanyia \t CodiICAO
            # Exemple: Vueling   VLG
            # Fem split() i ens quedem amb l'últim camp
            parts = line.split()

            if len(parts) >= 2:
                icao = parts[len(parts) - 1]
                airlines_temp.append(icao)

        i += 1

    # Si hem arribat aquí, la càrrega ha anat bé
    terminal.airlines = airlines_temp

    return 0


# LoadAirportStructure(filename)
# Llegeix l'estructura de LEBL des del fitxer V3 i crea l'objecte BarcelonaAP complet

def LoadAirportStructure(filename):

    try:
        F = open(filename, "r")
    except:
        return -1

    lines = F.readlines()
    F.close()

    if len(lines) == 0:
        return -1


    # Primera línia esperada, segons l'enunciat:
    # LEBL 2 terminals

    first = lines[0].split()

    if len(first) < 2:
        return -1

    airport_code = first[0]
    num_terminals = int(first[1])

    # Creem l'aeroport
    bcn = BarcelonaAP(airport_code)

    # Índex de línia actual
    i = 1

    terminals_loaded = 0

    # Anem carregant terminals
    while i < len(lines) and terminals_loaded < num_terminals:

        # -------------------------------------------------
        # Línia esperada:
        # Terminal T1 5 boarding areas
        # -------------------------------------------------
        parts = lines[i].split()

        if len(parts) < 3:
            return -1

        if parts[0] != "Terminal":
            return -1

        terminal_name = parts[1]
        num_areas = int(parts[2])

        terminal = Terminal(terminal_name)

        # Carreguem les companyies d'aquest terminal
        err = LoadAirlines(terminal, terminal_name)
        if err == -1:
            return -1

        i += 1
        areas_loaded = 0

        # Carreguem les boarding areas del terminal
        while i < len(lines) and areas_loaded < num_areas:


            # Línies esperades:
            # Area A Schengen Gates 1 - 11
            # Area D non-Schengen Gates 1 - 11

            parts = lines[i].split()

            if len(parts) < 7:
                return -1

            if parts[0] != "Area":
                return -1

            area_name = parts[1]
            area_type = parts[2]
            init_gate = int(parts[4])
            end_gate = int(parts[6])

            area = BoardingArea(area_name, area_type)

            # Prefix perquè el nom del gate sigui únic i fàcil de localitzar
            # Exemple: T1A_G1, T1B_G15, T2M_G7...
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


# GateOccupancy(bcn)
# Retorna una llista amb informació de totes les gates
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

                # Guardem:
                # terminal, area, gate name, occupied, aircraft_id
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


# IsAirlineInTerminal(terminal, name)
# Busca si una companyia pertany a aquest terminal
def IsAirlineInTerminal(terminal, name):

    if name == "":
        print("Error: empty airline name")
        return False

    i = 0
    found = False

    # Fem una cerca clàssica amb found
    while i < len(terminal.airlines) and not found:

        if terminal.airlines[i] == name:
            found = True
        else:
            i += 1

    return found


# SearchTerminal(bcn, name)
# Retorna el nom del terminal on opera una companyia
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


# AssignGate(bcn, aircraft)
# Assigna la primera gate lliure del tipus correcte

def AssignGate(bcn, aircraft):

    # 1) Busquem el terminal correcte segons la companyia
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    # 2) Determinem si el vol és Schengen segons l'origen
    flight_is_schengen = IsSchengenAirport(aircraft.origin)

    i = 0
    while i < len(bcn.terminals):

        terminal = bcn.terminals[i]

        # Només ens interessa el terminal correcte
        if terminal.name == terminal_name:

            j = 0
            while j < len(terminal.boarding_areas):

                area = terminal.boarding_areas[j]

                # 3) Comprovem si aquesta boarding area és del tipus correcte
                correct_area = False

                if flight_is_schengen and area.area_type.lower() == "schengen":
                    correct_area = True

                if (not flight_is_schengen) and area.area_type.lower() != "schengen":
                    correct_area = True

                # 4) Si l'àrea és correcta, busquem la primera gate lliure
                if correct_area:

                    k = 0
                    while k < len(area.gates):

                        gate = area.gates[k]

                        if not gate.occupied:
                            # Assignem la gate a aquest avió
                            gate.occupied = True
                            gate.aircraft_id = aircraft.aircraft_id

                            # Retornem el nom del gate assignat
                            return gate.name

                        k += 1

                j += 1

        i += 1

    # Si arribem aquí, no hi havia gate lliure correcta
    return -1


# TEST SECTION
# Aquí comprovem que la V3 funciona de veritat

if __name__ == "__main__":

    print("TEST LOAD AIRPORT STRUCTURE")

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        print("Error: airport structure could not be loaded")
    else:
        print("Airport code:", bcn.code)
        print("Number of terminals:", len(bcn.terminals))

        i = 0
        while i < len(bcn.terminals):
            print("Terminal:", bcn.terminals[i].name)
            print("  Boarding areas:", len(bcn.terminals[i].boarding_areas))
            print("  Airlines:", len(bcn.terminals[i].airlines))
            i += 1

    print("TEST LOAD ARRIVALS + ASSIGN GATES")

    aircrafts = LoadArrivals("Arrivals.txt")
    print("Arrivals loaded:", len(aircrafts))

    if bcn != -1 and len(aircrafts) > 0:

        # Assignem gates als primers 10 vols per provar
        i = 0
        while i < len(aircrafts) and i < 10:

            gate_name = AssignGate(bcn, aircrafts[i])

            if gate_name == -1:
                print(
                    "Aircraft",
                    aircrafts[i].aircraft_id,
                    "could not be assigned"
                )
            else:
                print(
                    "Aircraft",
                    aircrafts[i].aircraft_id,
                    "assigned to",
                    gate_name
                )

            i += 1

    print("TEST GATE OCCUPANCY")

    if bcn != -1:
        occ = GateOccupancy(bcn)

        # Ensenya'm només les primeres 20 files per no saturar
        i = 0
        while i < len(occ) and i < 20:
            print(occ[i])
            i += 1