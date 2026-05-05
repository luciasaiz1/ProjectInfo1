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
    current_terminal = None
    line = file.readline()

    while line != "":

        line = line.strip()

        if line != "":

            parts = line.split()

            # CASE 1: TERMINAL
            if len(parts) == 1:

                terminal_name = parts[0]
                terminal = Terminal(terminal_name)
                LoadAirlines(terminal, terminal_name)
                bcn.terminals.append(terminal)
                current_terminal = terminal

            # CASE 2: BOARDING AREA
            elif len(parts) == 4:

                name = parts[0]
                area_type = parts[1]
                init_gate = int(parts[2])
                end_gate = int(parts[3])

                area = BoardingArea(name, area_type)

                prefix = name + "G"

                SetGates(area, init_gate, end_gate, prefix)

                if current_terminal != None:
                    current_terminal.boarding_areas.append(area)

        line = file.readline()

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