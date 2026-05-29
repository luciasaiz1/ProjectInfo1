import matplotlib.pyplot as plt
import webbrowser
import math
from airport import IsSchengenAirport, LoadAirports

# CLASSE AIRCRAFT
# Representa un vol d’arribada/sortida a l’aeroport.
# Guarda informació bàsica com l’identificador de l’avió,
# la companyia, l’origen, el destí i les hores d’arribada i sortida.

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

        # companyia aeria (ICAO 3 lletres)
        self.airline = airline

        # aeroport d'origen (ICAO)
        self.origin = origin

        # hora d'arribada (hh:mm)
        self.arrival = arrival

        # aeroport destí (ICAO)
        self.destination = destination

        # hora de sortida (hh:mm)
        self.departure = departure


# --------- FUNCIONS AUXILIARS TEMPS ---------

def _parse_time(t):
    #Converteix una hora 'hh:mm' a minuts des de mitjanit. Retorna None si és invàlida.
    if t == "" or ":" not in t:
        return None
    parts = t.split(":")
    if len(parts) != 2:
        return None
    try:
        h = int(parts[0])
        m = int(parts[1])
    except:
        return None
    if h < 0 or h > 23 or m < 0 or m > 59:
        return None
    return h * 60 + m


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
        if _parse_time(arrival) is None:
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

# PLOT ARRIVALS
# fa un gràfic del nombre d'arribades per hora
# si rep una figura (fig), dibuixa dins d'aquella figura
# si no rep figura, crea una finestra nova

def PlotArrivals(aircrafts, fig=None):
    import matplotlib.pyplot as plt

    # si no ens passen una figura, en creem una
    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    # comptem quants vols arriben a cada hora
    hours = [0] * 24
    for a in aircrafts:
        if a.arrival != "":
            h = int(a.arrival.split(":")[0])
            hours[h] += 1

    ax.bar(range(24), hours)
    ax.set_title("Arrivals per hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Name of arrivals")

    # si no hi ha figura externa, mostrem el gràfic normalment
    if fig is None:
        plt.show()



# SAVE FLIGHTS
# Desa la llista de vols en un fitxer de text.
# Ara inclou també destí i hora de sortida (V4).

def SaveFlights(aircrafts, filename):

    if len(aircrafts) == 0:
        print("Error: empty list")
        return -1

    file = open(filename, "w")

    # Capçalera ampliada per incloure destí i sortida
    file.write("AIRCRAFT ORIGIN ARRIVAL DESTINATION DEPARTURE AIRLINE\n")

    i = 0
    while i < len(aircrafts):

        aircraft = aircrafts[i]

        aircraft_id = aircraft.aircraft_id or "-"
        origin = aircraft.origin or "-"
        arrival = aircraft.arrival or "-"
        destination = aircraft.destination or "-"
        departure = aircraft.departure or "-"
        airline = aircraft.airline or "-"

        file.write(
            aircraft_id + " " +
            origin + " " +
            arrival + " " +
            destination + " " +
            departure + " " +
            airline + "\n"
        )

        i += 1

    file.close()

    print("Flights saved")
    return 0


# PLOT AIRLINES
# Mostra el número de vols per aerolínia


def PlotAirlines(aircrafts, fig=None):
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    counts = {}
    for a in aircrafts:
        counts[a.airline] = counts.get(a.airline, 0) + 1

    airlines = list(counts.keys())
    flights = list(counts.values())

    ax.bar(airlines, flights, color="#1E88E5")

    ax.set_title("Flights per Airline")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Number of Flights")

    # Rotació i canvi de tamany perquè es pugi llegir bé
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=7)

    # Si hi ha massa airlines mostrar menys noms
    if len(airlines) > 20:
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for i, label in enumerate(ax.get_xticklabels()):
            if i % 3 == 0:  # Cada 3 noms
                label.set_visible(True)

    fig.tight_layout()

    if fig is None:
        plt.show()




# PLOT FLIGHTS TYPE
# Compara vols Schengen vs no Schengen segons l’origen.


def PlotFlightsType(aircrafts, fig=None):
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    schengen = 0
    non_schengen = 0

    for a in aircrafts:
        if IsSchengenAirport(a.origin):
            schengen += 1
        else:
            non_schengen += 1

    ax.bar(["Schengen", "Non-Schengen"], [schengen, non_schengen])
    ax.set_title("Types of Flights")
    ax.set_ylabel("Number of flights")

    if fig is None:
        plt.show()



# MAP FLIGHTS
# Genera un fitxer KML amb les rutes dels vols cap a LEBL.
# Versió V4: només rep aircrafts i carrega Airports.txt internament.

def MapFlights(aircrafts, airports):

    if len(aircrafts) == 0:
        print("Error: no aircrafts")
        return -1

    if len(airports) == 0:
        print("Error: no airports")
        return -1

    # Buscar LEBL en la llista d'aeroports
    lebl = None
    for ap in airports:
        if ap.code == "LEBL":
            lebl = ap
            break

    # Si no es troba, usar coordenades per defecte
    if lebl is None:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
    else:
        lebl_lat = lebl.coordinates[0]
        lebl_lon = lebl.coordinates[1]

    # Crear fitxer KML
    file = open("FlightsMap.kml", "w", encoding="utf-8")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write("<Document>\n")

    # Estils
    file.write('<Style id="schengen">\n')
    file.write('<LineStyle><color>ff00ff00</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    file.write('<Style id="nonschengen">\n')
    file.write('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    # Escriure cada trajectòria
    for a in aircrafts:

        # Buscar aeroport d'origen
        origin_airport = None
        for ap in airports:
            if ap.code == a.origin:
                origin_airport = ap
                break

        if origin_airport is None:
            continue

        origin_lat = origin_airport.coordinates[0]
        origin_lon = origin_airport.coordinates[1]

        # Color segons Schengen
        if IsSchengenAirport(a.origin):
            style = "#schengen"
        else:
            style = "#nonschengen"

        # Placemark
        file.write("<Placemark>\n")
        file.write("<name>" + a.aircraft_id + ": " +
                   a.origin + " - LEBL</name>\n")
        file.write("<styleUrl>" + style + "</styleUrl>\n")
        file.write("<LineString>\n")
        file.write("<tessellate>1</tessellate>\n")
        file.write("<coordinates>\n")

        file.write(f"{origin_lon},{origin_lat},0 ")
        file.write(f"{lebl_lon},{lebl_lat},0\n")

        file.write("</coordinates>\n")
        file.write("</LineString>\n")
        file.write("</Placemark>\n")

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


# --------- VERSIÓ 4 ---------

# LOAD DEPARTURES
# Carrega vols de sortida des d'un fitxer i actualitza només
# els camps relacionats amb la sortida.
# Si el fitxer no existeix, retorna llista buida i codi d'error.

def LoadDepartures(filename):

    aircrafts = []

    try:
        file = open(filename, "r")
    except:
        print("Error: file not found")
        return [], -1

    header = file.readline()

    for line in file:

        parts = line.split()

        if len(parts) != 4:
            continue

        aircraft_id = parts[0]
        destination = parts[1]
        departure = parts[2]
        airline = parts[3]

        # validació de format hora hh:mm
        if _parse_time(departure) is None:
            continue

        # creem objecte amb camps de sortida
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline=airline,
            destination=destination,
            departure=departure
        )

        aircrafts.append(aircraft)

    file.close()
    return aircrafts, 0


# MERGE MOVEMENTS (ARRIVALS + DEPARTURES)
# Combina arribades i sortides en una sola llista.
# Només es fusionen si els temps són compatibles (arrival < departure).

def MergeMovements(arrivals, departures):

    if len(arrivals) == 0 and len(departures) == 0:
        return []

    merged = {}

    # Primer afegim les arribades
    for a in arrivals:
        merged[a.aircraft_id] = a

    # Després afegim o actualitzem amb departures
    for d in departures:

        if d.aircraft_id in merged:

            a = merged[d.aircraft_id]

            t_arr = _parse_time(a.arrival)
            t_dep = _parse_time(d.departure)

            # Només fusionem si els temps són compatibles
            if t_arr is not None and t_dep is not None and t_arr < t_dep:
                a.destination = d.destination
                a.departure = d.departure
            # Si no són compatibles, ignorem la fusió (no modifiquem l'arribada)

        else:
            merged[d.aircraft_id] = d

    return list(merged.values())


# NIGHT AIRCRAFT
# Retorna els avions que només tenen sortida (no tenen arribada durant el dia).

def NightAircraft(aircrafts):

    result = []

    if len(aircrafts) == 0:
        return result

    for a in aircrafts:

        # Avió nocturn: només departure
        if a.arrival == "" and a.departure != "":
            result.append(a)

    return result


# TEST SECTION
if __name__ == "__main__":
    # Exemple bàsic de prova
    arr = LoadArrivals("Arrivals.txt")
    print("Arrivals loaded:", len(arr))
