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