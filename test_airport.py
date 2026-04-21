#STEP 2

from airport import *
airport = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport(airport)

# STEP 4

# LOAD AIRPORTS FROM FILE

airports = LoadAirports("Airports.txt")
print("Number of airports loaded:")
print(len(airports))


# SET SCHENGEN FOR ALL AIRPORTS

i = 0
while i < len(airports):

    SetSchengen(airports[i])
    i = i + 1


# PRINT FIRST 5 AIRPORTS

print("First airports:")
i = 0

while i < 5 and i < len(airports):

    PrintAirport(airports[i])
    i = i + 1


# ADD NEW AIRPORT TEST

print("Adding airport TEST")
new_airport = Airport("TEST", 10.0, 20.0)
SetSchengen(new_airport)
AddAirport(airports, new_airport)
print("Number of airports after adding:")
print(len(airports))


# REMOVE AIRPORT TEST

print("Removing airport TEST")
RemoveAirport(airports, "TEST")
print("Number of airports after removing:")
print(len(airports))


# SAVE SCHENGEN AIRPORTS TEST
print("Saving Schengen airports to file")
SaveSchengenAirports(airports, "SchengenAirports.txt")


# STEP 5

airports = LoadAirports("Airports.txt")
i = 0
while i < len(airports):
    SetSchengen(airports[i])
    i += 1

PlotAirports(airports)
MapAirports(airports)