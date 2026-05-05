# Barcelona Airport

class BarcelonaAP:

    def __init__(self, code):

        self.code = code
        self.terminals = []


# Terminal

class Terminal:

    def __init__(self, name):

        self.name = name
        self.boarding_areas = []
        self.companies = []   # airlines (ICAO codes)


# Boarding Area

class BoardingArea:

    def __init__(self, name, area_type):

        self.name = name
        self.type = area_type   # "Schengen" or "Non-Schengen"
        self.gates = []


# Gate

class Gate:

    def __init__(self, name):

        self.name = name
        self.occupied = False
        self.aircraft_id = ""

# TEST
if __name__ == "__main__":

    airport = BarcelonaAP("LEBL")

    t1 = Terminal("T1")

    ba1 = BoardingArea("T1BAa", "Schengen")

    g1 = Gate("T1BAaG1")

    ba1.gates.append(g1)

    t1.boarding_areas.append(ba1)

    airport.terminals.append(t1)

    print("Airport:", airport.code)
    print("Terminal:", airport.terminals[0].name)
    print("Boarding Area:", airport.terminals[0].boarding_areas[0].name)
    print("Gate:", airport.terminals[0].boarding_areas[0].gates[0].name)

# SET GATES

    def SetGates(area, init_gate, end_gate, prefix):

        if end_gate <= init_gate:
            return -1

        area.gates = []

        i = init_gate

        while i <= end_gate:
            name = prefix + str(i)

            gate = Gate(name)

            area.gates.append(gate)

            i = i + 1

        return 0


# LOAD AIRLINES

def LoadAirlines(terminal, t_name):

    filename = t_name + "_Airlines.txt"

    try:
        file = open(filename, "r")
    except:
        return -1

    terminal.companies = []

    for line in file:

        airline = line.strip()

        if airline != "":
            terminal.companies.append(airline)

    file.close()

    return 0

# LOAD AIRPORT STRUCTURE

def LoadAirportStructure(filename):

    try:
        file = open(filename, "r")
    except:
        return -1

    bcn = BarcelonaAP("LEBL")

    # EJEMPLO SIMPLE (puedes adaptarlo a tu fichero real)

    t1 = Terminal("T1")

    ba1 = BoardingArea("T1BAa", "Schengen")
    ba2 = BoardingArea("T1BAb", "Non-Schengen")

    SetGates(ba1, 1, 5, "T1BAaG")
    SetGates(ba2, 1, 5, "T1BAbG")

    t1.boarding_areas.append(ba1)
    t1.boarding_areas.append(ba2)

    LoadAirlines(t1, "T1")

    bcn.terminals.append(t1)

    file.close()

    return bcn

# GATE OCCUPANCY

def GateOccupancy(bcn):

    result = []

    t = 0

    while t < len(bcn.terminals):

        terminal = bcn.terminals[t]

        b = 0

        while b < len(terminal.boarding_areas):

            area = terminal.boarding_areas[b]

            g = 0

            while g < len(area.gates):

                gate = area.gates[g]

                if gate.occupied:
                    status = "OCCUPIED"
                    aircraft = gate.aircraft_id
                else:
                    status = "FREE"
                    aircraft = "-"

                result.append([gate.name, status, aircraft])

                g = g + 1

            b = b + 1

        t = t + 1

    return result

# IS AIRLINE IN TERMINAL

def IsAirlineInTerminal(terminal, name):

    if name == "":
        return False

    if len(terminal.companies) == 0:
        return False

    i = 0

    while i < len(terminal.companies):

        if terminal.companies[i] == name:
            return True

        i = i + 1

    return False

# SEARCH TERMINAL

def SearchTerminal(bcn, name):

    t = 0

    while t < len(bcn.terminals):

        terminal = bcn.terminals[t]

        if IsAirlineInTerminal(terminal, name):
            return terminal.name

        t = t + 1

    return ""

# ASSIGN GATE

from airport import IsSchengenAirport

def AssignGate(bcn, aircraft):

    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    t = 0

    while t < len(bcn.terminals):

        terminal = bcn.terminals[t]

        if terminal.name == terminal_name:

            schengen = IsSchengenAirport(aircraft.origin)

            b = 0

            while b < len(terminal.boarding_areas):

                area = terminal.boarding_areas[b]

                if (schengen and area.type == "Schengen") or \
                   (not schengen and area.type == "Non-Schengen"):

                    g = 0

                    while g < len(area.gates):

                        gate = area.gates[g]

                        if gate.occupied == False:

                            gate.occupied = True
                            gate.aircraft_id = aircraft.aircraft_id

                            return 0

                        g = g + 1

                b = b + 1

        t = t + 1

    return -1

# TEST 2

if __name__ == "__main__":

    from aircraft import LoadArrivals

    bcn = LoadAirportStructure("LEBL.txt")

    aircrafts = LoadArrivals("Arrivals.txt")

    i = 0

    while i < len(aircrafts):

        AssignGate(bcn, aircrafts[i])

        i = i + 1

    gates = GateOccupancy(bcn)

    i = 0

    while i < len(gates):

        print(gates[i])

        i = i + 1