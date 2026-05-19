import matplotlib.pyplot as plt
import webbrowser
import math
from airport import IsSchengenAirport, LoadAirports

# CLASS AIRCRAFT

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

        print("Error: file not found")

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

        if hour < 0 or hour > 23:
            continue

        if minute < 0 or minute > 59:
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

        print("Error: empty list")

        return

    hours = [0] * 24

    i = 0

    while i < len(aircrafts):

        arrival = aircrafts[i].arrival

        hour = int(arrival.split(":")[0])

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

        print("Error: empty list")

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


# PLOT AIRLINES

def PlotAirlines(aircrafts):

    if len(aircrafts) == 0:

        print("Error: empty list")

        return

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


# PLOT FLIGHTS TYPE (SCHENGEN / NON)


def PlotFlightsType(aircrafts):

    if len(aircrafts) == 0:

        print("Error: empty aircraft list")

        return

    schengen_count = 0
    non_schengen_count = 0

    i = 0

    while i < len(aircrafts):

        origin = aircrafts[i].origin

        if IsSchengenAirport(origin):

            schengen_count = schengen_count + 1

        else:

            non_schengen_count = non_schengen_count + 1

        i = i + 1

    plt.bar(
        ["Flights"],
        [schengen_count],
        label="Schengen"
    )

    plt.bar(
        ["Flights"],
        [non_schengen_count],
        bottom=[schengen_count],
        label="Non-Schengen"
    )

    plt.xlabel("Flights")

    plt.ylabel("Number of flights")

    plt.title("Schengen vs Non-Schengen arrivals")

    plt.legend()

    plt.show()


# MAP FLIGHTS

def MapFlights(aircrafts, airports):

    if len(aircrafts) == 0:

        print("Error: no aircrafts")

        return -1

    if len(airports) == 0:

        print("Error: no airports")

        return -1

    lebl_lat = 41.297445
    lebl_lon = 2.0832941

    file = open(
        "FlightsMap.kml",
        "w",
        encoding="utf-8"
    )

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    file.write(
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    )

    file.write("<Document>\n")

    file.write('<Style id="schengen">\n')
    file.write(
        '<LineStyle><color>ff00ff00</color>'
        '<width>3</width></LineStyle>\n'
    )
    file.write("</Style>\n")

    file.write('<Style id="nonschengen">\n')
    file.write(
        '<LineStyle><color>ff0000ff</color>'
        '<width>3</width></LineStyle>\n'
    )
    file.write("</Style>\n")

    i = 0

    while i < len(aircrafts):

        origin_code = aircrafts[i].origin

        found = False

        j = 0

        while j < len(airports) and not found:

            if airports[j].code == origin_code:

                found = True

                origin_lat = airports[j].coordinates[0]

                origin_lon = airports[j].coordinates[1]

            else:

                j = j + 1

        if found:

            if IsSchengenAirport(origin_code):

                style = "#schengen"

            else:

                style = "#nonschengen"

            file.write("<Placemark>\n")

            file.write(
                "<name>" +
                aircrafts[i].aircraft_id +
                ": " +
                origin_code +
                " - LEBL</name>\n"
            )

            file.write(
                "<styleUrl>" +
                style +
                "</styleUrl>\n"
            )

            file.write("<LineString>\n")

            file.write("<tessellate>1</tessellate>\n")

            file.write("<coordinates>\n")

            file.write(
                str(origin_lon) + "," +
                str(origin_lat) + ",0 "
            )

            file.write(
                str(lebl_lon) + "," +
                str(lebl_lat) + ",0\n"
            )

            file.write("</coordinates>\n")

            file.write("</LineString>\n")

            file.write("</Placemark>\n")

        i = i + 1

    file.write("</Document>\n")

    file.write("</kml>\n")

    file.close()

    print("FlightsMap.kml created")

    webbrowser.open("FlightsMap.kml")

    return 0

def SearchAirportByCode(airports, code):
    i = 0
    while i < len(airports):
        if airports[i].code == code:
            return airports[i]
        i += 1
    return None


def Haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def LongDistanceArrivals(aircrafts):
    result = []

    if len(aircrafts) == 0:
        return result

    airports = LoadAirports("Airports.txt")
    if len(airports) == 0:
        print("Error: Airports.txt could not be loaded")
        return result

    lebl = SearchAirportByCode(airports, "LEBL")

    if lebl is None:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
    else:
        lebl_lat = lebl.coordinates[0]
        lebl_lon = lebl.coordinates[1]

    i = 0
    while i < len(aircrafts):
        origin_airport = SearchAirportByCode(airports, aircrafts[i].origin)

        if origin_airport is not None:
            dist = Haversine(
                origin_airport.coordinates[0],
                origin_airport.coordinates[1],
                lebl_lat,
                lebl_lon
            )

            if dist > 2000:
                result.append(aircrafts[i])

        i += 1

    return result

# TEST SECTION

if __name__ == "__main__":

    aircrafts = LoadArrivals("Arrivals.txt")

    airports = LoadAirports("Airports.txt")

    print("Aircraft loaded:")

    print(len(aircrafts))

    PlotArrivals(aircrafts)

    PlotAirlines(aircrafts)

    PlotFlightsType(aircrafts)

    SaveFlights(
        aircrafts,
        "FlightsOutput.txt"
    )

    MapFlights(
        aircrafts,
        airports
    )