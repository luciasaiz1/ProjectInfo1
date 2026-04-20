import matplotlib.pyplot as plt


# CLASS

class Aircraft:

    def __init__(self,
                 aircraft_id="",
                 airline="",
                 origin="",
                 arrival=""):

        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival


# LOAD ARRIVALS

def LoadArrivals(filename):

    aircrafts = []

    try:

        file = open(filename, "r")

    except:

        print("Error")

        return aircrafts

    header = file.readline()

    for line in file:

        parts = line.split()

        if len(parts) != 4:
            continue

        aircraft_id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        # Validate time format

        if ":" not in arrival:
            continue

        time_parts = arrival.split(":")

        if len(time_parts) != 2:
            continue

        try:

            hour = int(time_parts[0])
            minute = int(time_parts[1])

        except:

            continue

        aircraft = Aircraft(
            aircraft_id,
            airline,
            origin,
            arrival
        )

        aircrafts.append(aircraft)

    file.close()

    return aircrafts


# PLOT ARRIVALS

def PlotArrivals(aircrafts):

    if len(aircrafts) == 0:

        print("Error")

        return

    hours = [0] * 24

    i = 0

    while i < len(aircrafts):

        arrival = aircrafts[i].arrival

        hour = int(arrival.split(":")[0])

        if hour >= 0 and hour < 24:

            hours[hour] = hours[hour] + 1

        i = i + 1

    plt.bar(range(24), hours)

    plt.title("Landing frequency per hour")

    plt.xlabel("Hour")

    plt.ylabel("Number of arrivals")

    plt.show()


# SAVE FLIGHTS

def SaveFlights(aircrafts, filename):

    if len(aircrafts) == 0:

        print("Error")

        return -1

    file = open(filename, "w")

    file.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    i = 0

    while i < len(aircrafts):

        aircraft = aircrafts[i]

        aircraft_id = aircraft.aircraft_id
        origin = aircraft.origin
        arrival = aircraft.arrival
        airline = aircraft.airline

        if aircraft_id == "":
            aircraft_id = "-"

        if origin == "":
            origin = "-"

        if arrival == "":
            arrival = "-"

        if airline == "":
            airline = "-"

        file.write(
            aircraft_id + " " +
            origin + " " +
            arrival + " " +
            airline + "\n"
        )

        i = i + 1

    file.close()

    print("Flights saved")

    return 0


# TEST SECTION

if __name__ == "__main__":

    aircrafts = LoadArrivals("Arrivals.txt")

    print("Aircraft loaded:")

    print(len(aircrafts))

    PlotArrivals(aircrafts)

    SaveFlights(aircrafts, "FlightsOutput.txt")


def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: empty list")
        return -1

    airlines = []
    counts = []

    i = 0
    while i < len(aircrafts):
        airline = aircrafts[i].airline

        if airline in airlines:
            j = airlines.index(airline)
            counts[j] = counts[j] + 1
        else:
            airlines.append(airline)
            counts.append(1)

        i = i + 1

    plt.bar(airlines, counts)
    plt.xlabel("Airlines")
    plt.ylabel("Number of flights")
    plt.title("Flights per airline")
    plt.show()

    return 0

#TEST SECTION PLOT AIRLINES
if __name__ == "__main__":

    aircrafts = LoadArrivals("Arrivals.txt")

    if len(aircrafts) > 0:
        PlotAirLines(aircrafts)
    else:
        print("Error: arrivals could not be loaded")


def PlotFlightsType(aircrafts):

    if len(aircrafts) == 0:
        print("Error: empty aircraft list")
        return -1

    schengen_count = 0
    non_schengen_count = 0

    i = 0
    while i < len(aircrafts):
        origin = aircrafts[i].origin

        if airport.IsSchengenAirport(origin) == True:
            schengen_count = schengen_count + 1
        else:
            non_schengen_count = non_schengen_count + 1

        i = i + 1

    plt.bar(["Flights"], [schengen_count], label="Schengen")
    plt.bar(["Flights"], [non_schengen_count], bottom=[schengen_count], label="No Schengen")

    plt.xlabel("Flights")
    plt.ylabel("Number of flights")
    plt.title("Schengen vs non-Schengen arrivals")
    plt.legend()
    plt.show()

    return 0

#TEST SECTION PLOT FLIGHT TYPES
if __name__ == "__main__":

    aircrafts = LoadArrivals("Arrivals.txt")

    if len(aircrafts) > 0:
        PlotFlightsType(aircrafts)
    else:
        print("Error: arrivals could not be loaded")

#MAP FLIGHTS
import webbrowser
from airport import LoadAirports, IsSchengenAirport

def MapFlights(aircrafts):
    if len(aircrafts) == 0:
        print("Error: no aircrafts to map")
        return -1

    airports = LoadAirports("Airports.txt")
    if len(airports) == 0:
        print("Error: airports could not be loaded")
        return -1

    lebl_lat = 41.297445
    lebl_lon = 2.0832941

    kml_file = open("FlightsMap.kml", "w", encoding="utf-8")

    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml_file.write('<Document>\n')

    kml_file.write('<Style id="schengenStyle">\n')
    kml_file.write('<LineStyle><color>ff00ff00</color><width>3</width></LineStyle>\n')
    kml_file.write('</Style>\n')

    kml_file.write('<Style id="nonSchengenStyle">\n')
    kml_file.write('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>\n')
    kml_file.write('</Style>\n')

    i = 0
    while i < len(aircrafts):
        origin_code = aircrafts[i].origin
        found = False
        j = 0

        while j < len(airports) and not found:
            if airports[j].code == origin_code:
                found = True
                origin_lat = airports[j].lat
                origin_lon = airports[j].lon
            else:
                j = j + 1

        if found:
            if IsSchengenAirport(origin_code):
                style = "#schengenStyle"
            else:
                style = "#nonSchengenStyle"

            kml_file.write('<Placemark>\n')
            kml_file.write('<name>' + aircrafts[i].id + ': ' + origin_code + ' - LEBL</name>\n')
            kml_file.write('<styleUrl>' + style + '</styleUrl>\n')
            kml_file.write('<LineString>\n')
            kml_file.write('<tessellate>1</tessellate>\n')
            kml_file.write('<coordinates>\n')
            kml_file.write(str(origin_lon) + ',' + str(origin_lat) + ',0 ')
            kml_file.write(str(lebl_lon) + ',' + str(lebl_lat) + ',0\n')
            kml_file.write('</coordinates>\n')
            kml_file.write('</LineString>\n')
            kml_file.write('</Placemark>\n')

        i = i + 1

    kml_file.write('</Document>\n')
    kml_file.write('</kml>\n')
    kml_file.close()

    webbrowser.open("FlightsMap.kml")
    return 0

#TEST SECTION MAP FLIGHT
if __name__ == "__main__":
    aircrafts = LoadArrivals("Arrivals.txt")

    if len(aircrafts) > 0:
        MapFlights(aircrafts)
    else:
        print("Error: arrivals could not be loaded")