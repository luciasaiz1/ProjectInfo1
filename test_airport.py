# TESTS

from airport import *
from aircraft import *
from LEBL import *

print("V1")

# TEST 1: Crear aeroport manualment

a = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(a)
PrintAirport(a)


# TEST 2: Carregar Airports.txt

airports = LoadAirports("Airports.txt")
print("\nAirports carregats:", len(airports))

for ap in airports:
    SetSchengen(ap)

print("Primer aeroport carregat:")
PrintAirport(airports[0])


# TEST 3: Afegir i eliminar aeroport

print("\nAfegint aeroport TEST...")
test_ap = Airport("TEST", 10.0, 20.0)
SetSchengen(test_ap)
AddAirport(airports, test_ap)
print("Total aeroports:", len(airports))

print("Eliminant aeroport TEST...")
RemoveAirport(airports, "TEST")
print("Total aeroports:", len(airports))


# TEST 4: Guardar aeroports Schengen

print("\nGuardant aeroports Schengen...")
SaveSchengenAirports(airports, "SchengenAirports.txt")
print("Fitxer creat: SchengenAirports.txt")


# TEST 5: Gràfic i mapa

print("\nMostrant gràfic Schengen/No-Schengen...")
PlotAirports(airports)

print("Creant mapa KML...")
MapAirports(airports)


# V2 - TEST ARRIVALS I VOLS

print("V2")

# TEST 6: Carregar Arrivals.txt

arrivals = LoadArrivals("Arrivals.txt")
print("Arrivals carregats:", len(arrivals))


# TEST 7: Gràfics

print("\nMostrant gràfic d'arribades per hora...")
PlotArrivals(arrivals)

print("Mostrant gràfic per companyies...")
PlotAirlines(arrivals)

print("Mostrant gràfic Schengen/No-Schengen...")
PlotFlightsType(arrivals)


# TEST 8: Guardar vols

print("\nGuardant vols en format ampliat...")
SaveFlights(arrivals, "SavedFlights.txt")
print("Fitxer creat: SavedFlights.txt")


# TEST 9: Mapa de vols

print("\nCreant mapa de vols...")
MapFlights(arrivals, airports)


# V3 - TEST ESTRUCTURA LEBL I GATES

print("V3")

# TEST 10: Carregar estructura LEBL

bcn = LoadAirportStructure("LEBL.txt")

if bcn == -1:
    print("ERROR: No s'ha pogut carregar LEBL.txt")
else:
    print("Estructura carregada correctament")
    print("Terminals:", len(bcn.terminals))


# TEST 11: Assignar gates als primers 10 vols

print("\nAssignant gates als primers 10 vols...")

for i in range(min(10, len(arrivals))):
    g = AssignGate(bcn, arrivals[i])
    print(arrivals[i].aircraft_id, "→", g)


# TEST 12: Mostrar ocupació de gates

print("\nMostrant ocupació de gates (primeres 20):")
occ = GateOccupancy(bcn)

for i in range(min(20, len(occ))):
    print(occ[i])



# V4 - TEST ARRIVALS, DEPARTURES, SIMULACIÓ

print(" V4")



# TEST 13: Carregar Departures.txt

departures, err = LoadDepartures("Departures.txt")

print("Departures carregats:", len(departures))


# TEST 14: Fusionar moviments

merged = MergeMovements(arrivals, departures)

print("Total moviments fusionats:", len(merged))


# TEST 15: Assignar gates a vols nocturns

print("\nAssignant gates a vols nocturns...")
AssignNightGates(bcn, merged)


# TEST 16: Simulació d'un dia complet

print("\nSimulant un dia complet...")
PlotDayOccupancy(bcn, merged)

print("\nTEST FINALITZAT CORRECTAMENT")
