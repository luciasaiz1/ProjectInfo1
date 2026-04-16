from airport import *

# STEP 2

print("STEP 2 TEST")

airport = Airport("LEBL", 41.297445, 2.0832941)

SetSchengen(airport)

PrintAirport(airport)


# STEP 4

print("\nSTEP 4 TEST")

# LOAD AIRPORTS FROM FILE

airports = LoadAirports("Airports.txt")

print("Number of airports loaded:")

print(len(airports))
MapAirports(airports)


# SET SCHENGEN FOR ALL AIRPORTS

i = 0

while i < len(airports):

    SetSchengen(airports[i])

    i = i + 1


# PRINT FIRST 5 AIRPORTS

print("\nFirst airports:")

i = 0

while i < 5 and i < len(airports):

    PrintAirport(airports[i])

    i = i + 1


# ADD NEW AIRPORT TEST

print("\nAdding airport TEST")

new_airport = Airport("TEST", 10.0, 20.0)

SetSchengen(new_airport)

AddAirport(airports, new_airport)

print("Number of airports after adding:")

print(len(airports))


# REMOVE AIRPORT TEST

print("\nRemoving airport TEST")

result = RemoveAirport(airports, "TEST")

if result == 0:

    print("Airport removed")

else:

    print("Airport not found")

print("Number of airports after removing:")

print(len(airports))


# SAVE SCHENGEN AIRPORTS TEST

print("\nSaving Schengen airports to file")

result = SaveSchengenAirports(
    airports,
    "SchengenAirports.txt"
)

if result == 0:

    print("File saved")

else:

    print("Error saving file")


# STEP 5

print("\nSTEP 5 TEST")

PlotAirports(airports)

MapAirports(airports)