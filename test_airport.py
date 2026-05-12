# TEST AIRPORT - V1 / V2 FUNCIONALITATS AEROPORTS

# Aquest fitxer serveix per provar manualment les funcions
# principals del mòdul airport.py:
# - Creació d’aeroports
# - Càrrega des de fitxer
# - Afegir / eliminar aeroports
# - Assignació Schengen
# - Guardat de dades
# - Gràfics i mapa KML

from airport import *

# STEP 2 - CREACIÓ I PROVA D'AEROPORT

airport = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport(airport)

# STEP 4 - CARREGA D'AEROPORTS DES DE FITXER

airports = LoadAirports("Airports.txt")

print("Number of airports loaded:")
print(len(airports))


# ASSIGNACIÓ SCHENGEN A TOTS ELS AEROPORTS

i = 0
while i < len(airports):
    SetSchengen(airports[i])
    i += 1

# MOSTRAR ELS PRIMERS AEROPORTS

print("First airports:")

i = 0
while i < 5 and i < len(airports):
    PrintAirport(airports[i])
    i += 1

# TEST - AFEGIR AEROPORT

print("Adding airport TEST")

new_airport = Airport("TEST", 10.0, 20.0)
SetSchengen(new_airport)

AddAirport(airports, new_airport)

print("Number of airports after adding:")
print(len(airports))

# TEST - ELIMINAR AEROPORT

print("Removing airport TEST")

RemoveAirport(airports, "TEST")

print("Number of airports after removing:")
print(len(airports))


# TEST - GUARDAR AEROPORTS SCHENGEN

print("Saving Schengen airports to file")

SaveSchengenAirports(airports, "SchengenAirports.txt")


# STEP 5 - GRÀFICS I MAPA

airports = LoadAirports("Airports.txt")

i = 0
while i < len(airports):
    SetSchengen(airports[i])
    i += 1

PlotAirports(airports)
MapAirports(airports)