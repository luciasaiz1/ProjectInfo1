import matplotlib.pyplot as plt
import webbrowser
import math
from airport import IsSchengenAirport, LoadAirports

# CLASSE AIRCRAFT
# Representa un vol d’arribada a l’aeroport.
# Guarda informació bàsica com l’identificador de l’avió,
# la companyia, l’origen i l’hora d’arribada.

class Aircraft:

    def __init__(self,
                 aircraft_id="",
                 airline="",
                 origin="",
                 arrival="",
                 destination="",
                 departure=""):

        # identificador avió
        self.aircraft_id = aircraft_id

        # companyia aeria
        self.airline = airline

        # aeroport d'origen (ICAO)
        self.origin = origin

        # hora d'arribada (hh:mm)
        self.arrival = arrival

        # aeroport destí (ICAO)
        self.destination = destination

        # hora de sortida (hh:mm)
        self.departure = departure


# LOAD ARRIVALS
# Llegeix un fitxer de vols i crea una llista d’Aircraft.
# Valida el format de l’hora i descarta línies incorrectes.

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

        # Validació del format d’hora
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

# Mostra un gràfic amb el nombre de vols per hora del dia.

def PlotArrivals(aircrafts):

    if len(aircrafts) == 0:
        print("Error: empty list")
        return

    hours = [0] * 24

    i = 0
    while i < len(aircrafts):

        arrival = aircrafts[i].arrival
        hour = int(arrival.split(":")[0])

        hours[hour] += 1
        i += 1

    plt.bar(range(24), hours)
    plt.title("Landing frequency per hour")
    plt.xlabel("Hour")
    plt.ylabel("Number of arrivals")
    plt.show()


# SAVE FLIGHTS

# Desa la llista de vols en un fitxer de text.


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

        # Substitució de camps buits
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

        i += 1

    file.close()

    print("Flights saved")
    return 0


# PLOT AIRLINES
# Mostra quants vols té cada companyia.


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
            counts[j] += 1
        else:
            airlines.append(airline)
            counts.append(1)

        i += 1

    plt.bar(airlines, counts)
    plt.xlabel("Airlines")
    plt.ylabel("Number of flights")
    plt.title("Flights per airline")
    plt.show()


# PLOT FLIGHTS TYPE
# Compara vols Schengen vs no Schengen segons l’origen.

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
            schengen_count += 1
        else:
            non_schengen_count += 1

        i += 1

    plt.bar(["Flights"], [schengen_count], label="Schengen")
    plt.bar(["Flights"], [non_schengen_count],
            bottom=[schengen_count],
            label="Non-Schengen")

    plt.xlabel("Flights")
    plt.ylabel("Number of flights")
    plt.title("Schengen vs Non-Schengen arrivals")
    plt.legend()
    plt.show()


# MAP FLIGHTS
# Genera un fitxer KML amb les rutes dels vols cap a LEBL.

def MapFlights(aircrafts, airports):

    if len(aircrafts) == 0:
        print("Error: no aircrafts")
        return -1

    if len(airports) == 0:
        print("Error: no airports")
        return -1

    lebl_lat = 41.297445
    lebl_lon = 2.0832941

    file = open("FlightsMap.kml", "w", encoding="utf-8")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write("<Document>\n")

    file.write('<Style id="schengen">\n')
    file.write('<LineStyle><color>ff00ff00</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    file.write('<Style id="nonschengen">\n')
    file.write('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>\n')
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
                j += 1

        if found:

            if IsSchengenAirport(origin_code):
                style = "#schengen"
            else:
                style = "#nonschengen"

            file.write("<Placemark>\n")
            file.write("<name>" + aircrafts[i].aircraft_id +
                       ": " + origin_code + " - LEBL</name>\n")
            file.write("<styleUrl>" + style + "</styleUrl>\n")
            file.write("<LineString>\n")
            file.write("<tessellate>1</tessellate>\n")
            file.write("<coordinates>\n")

            file.write(str(origin_lon) + "," + str(origin_lat) + ",0 ")
            file.write(str(lebl_lon) + "," + str(lebl_lat) + ",0\n")

            file.write("</coordinates>\n")
            file.write("</LineString>\n")
            file.write("</Placemark>\n")

        i += 1

    file.write("</Document>\n")
    file.write("</kml>\n")
    file.close()

    print("FlightsMap.kml created")
    webbrowser.open("FlightsMap.kml")

    return 0


# SEARCH AIRPORT
# Busca un aeroport pel seu codi ICAO.

def SearchAirportByCode(airports, code):

    i = 0
    while i < len(airports):
        if airports[i].code == code:
            return airports[i]
        i += 1
    return None


# HAVERSINE
# Calcula la distància entre dues coordenades geogràfiques.


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



# LONG DISTANCE ARRIVALS
# Retorna vols que arriben a LEBL des de més de 2000 km.

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


# V4 - NOVES FUNCIONALITATS (DEPARTURES + MERGE + NIGHT)

# LOAD DEPARTURES

def LoadDepartures(filename):

    #Aquesta funció carrega els vols de sortida (departures)
    # des d'un fitxer i retorna una llista d'objectes Aircraft.

    aircrafts = []

    try:
        file = open(filename, "r")
    except:
        print("Error: no s'ha pogut obrir el fitxer de departures")
        return aircrafts

    # Saltem la capçalera
    header = file.readline()

    for line in file:

        parts = line.split()

        # Format esperat: ID DESTINATION DEPARTURE AIRLINE
        if len(parts) != 4:
            continue

        aircraft_id = parts[0]
        destination = parts[1]
        departure = parts[2]
        airline = parts[3]

        # Validació format hora hh:mm
        if ":" not in departure:
            continue

        try:
            hour = int(departure.split(":")[0])
            minute = int(departure.split(":")[1])
        except:
            continue

        if hour < 0 or hour > 23:
            continue

        if minute < 0 or minute > 59:
            continue

        # Creem objecte Aircraft només amb dades de sortida
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline=airline,
            origin="",
            arrival="",
            destination=destination,
            departure=departure
        )

        aircrafts.append(aircraft)

    file.close()
    return aircrafts


# MERGE MOVEMENTS (ARRIVALS + DEPARTURES)

def MergeMovements(arrivals, departures):

    #Aquesta funció combina arribades i sortides en una sola llista.
    #Si un avió té arrival i departure, es fusionen en el mateix objecte.


    if len(arrivals) == 0 and len(departures) == 0:
        return []

    merged = {}

    # Primer afegim les arribades
    for a in arrivals:
        merged[a.aircraft_id] = a

    # Després afegim o actualitzem amb departures
    for d in departures:

        # Si ja existeix, completem la informació
        if d.aircraft_id in merged:

            a = merged[d.aircraft_id]

            a.destination = d.destination
            a.departure = d.departure

        else:
            merged[d.aircraft_id] = d

    return list(merged.values())


# NIGHT AIRCRAFT

def NightAircraft(aircrafts):

    #Aquesta funció retorna els avions que només tenen sortida (no tenen arribada durant el dia).

    if len(aircrafts) == 0:
        return -1

    result = []

    for a in aircrafts:

        # Avió nocturn: només departure
        if a.arrival == "" and a.departure != "":
            result.append(a)

    return result