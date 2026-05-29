import matplotlib.pyplot as plt
import webbrowser
import math
from airport import IsSchengenAirport, LoadAirports

# CLASSE AIRCRAFT
# Representa un vol d’arribada/sortida a l’aeroport.
# Guarda informació bàsica com l’identificador de l’avió, la companyia, l’origen, el destí i les hores d’arribada i sortida.

class Aircraft:

    def __init__(self,
                 aircraft_id="",
                 airline="",
                 origin="",
                 arrival="",
                 destination="",
                 departure=""):

        # Identificador del avió
        self.aircraft_id = aircraft_id

        # Companyia aèria (ICAO 3 lletres)
        self.airline = airline

        # Aeroport d'origen (ICAO)
        self.origin = origin

        # Hora d'arribada (hh:mm)
        self.arrival = arrival

        # Aeroport destí (ICAO)
        self.destination = destination

        # Hora de sortida (hh:mm)
        self.departure = departure


# FUNCIONS AUXILIARS TEMPS

def _parse_time(t):
    # Converteix una hora hh:mm a minuts des de mitjanit. Retorna None si és invàlida.
    if t == "" or ":" not in t:
        return None
    parts = t.split(":")  # Separem hores i minuts
    if len(parts) != 2:
        return None
    try:
        h = int(parts[0])  # Convertim hores
        m = int(parts[1])  # Convertim minuts
    except:
        return None
    if h < 0 or h > 23 or m < 0 or m > 59:  # Validem rang
        return None
    return h * 60 + m  # Retornem minuts totals


# LOAD ARRIVALS
# Llegeix un fitxer de vols i crea una llista d’Aircraft.
# Valida el format de l’hora i descarta línies incorrectes.

def LoadArrivals(filename):

    aircrafts = []  # Llista on guardarem els avions carregats

    try:
        file = open(filename, "r")  # Obrim el fitxer
    except:
        print("Error: file not found")
        return aircrafts

    header = file.readline()  # Llegim la capçalera i l’ignorem

    for line in file:

        parts = line.split()  # Separem camps per espais

        if len(parts) != 4:  # Si el format incorrecte, saltem una línia
            continue

        aircraft_id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        # Validació del format d’hora
        if _parse_time(arrival) is None:
            continue

        # Creem l’objecte Aircraft amb les dades carregades
        aircraft = Aircraft(
            aircraft_id,
            airline,
            origin,
            arrival
        )

        aircrafts.append(aircraft)  # Afegim a la llista

    file.close()  # Tanquem fitxer

    return aircrafts


# PLOT ARRIVALS
# Fa un gràfic del nombre d'arribades per hora.
# Si rep una figura (fig), dibuixa dins d'aquella figura (que és el lloc de visualització)

def PlotArrivals(aircrafts, fig=None):
    import matplotlib.pyplot as plt

    # Si no ens passen una figura, en creem una nova
    if fig is None:
        fig = plt.figure()

    ax = fig.add_subplot(111)  # Creem un subplot

    # Comptem quants vols arriben a cada hora
    hours = [0] * 24  # Llista de 24 hores inicialitzada a 0
    for a in aircrafts:
        if a.arrival != "":
            h = int(a.arrival.split(":")[0])  # Extreiem l’hora
            hours[h] += 1  # Incrementem el comptador

    ax.bar(range(24), hours)  # Dibuixem el gràfic
    ax.set_title("Arrivals per Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Number of Arrivals")

    # Si no hi ha figura externa, mostrem el gràfic normalment
    if fig is None:
        plt.show()


# SAVE FLIGHTS
# Desa la llista de vols en un fitxer de text.

def SaveFlights(aircrafts, filename):

    if len(aircrafts) == 0:  # Si la llista és buida: error
        print("Error: empty list")
        return -1

    file = open(filename, "w")  # Obrim fitxer per escriure

    # Capçalera ampliada
    file.write("AIRCRAFT ORIGIN ARRIVAL DESTINATION DEPARTURE AIRLINE\n")

    i = 0
    while i < len(aircrafts):

        aircraft = aircrafts[i]  # Agafem l’avió actual

        # Substituïm camps buits per "-"
        aircraft_id = aircraft.aircraft_id or "-"
        origin = aircraft.origin or "-"
        arrival = aircraft.arrival or "-"
        destination = aircraft.destination or "-"
        departure = aircraft.departure or "-"
        airline = aircraft.airline or "-"

        # Escriure línia al fitxer
        file.write(
            aircraft_id + " " +
            origin + " " +
            arrival + " " +
            destination + " " +
            departure + " " +
            airline + "\n"
        )

        i += 1  # Avancem al següent avió

    file.close()  # Tanquem fitxer

    print("Flights saved")
    return 0


# PLOT AIRLINES
# Mostra el nombre de vols per aerolínia.

def PlotAirlines(aircrafts, fig=None):
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.figure()  # Creem figura si no ens la passen

    ax = fig.add_subplot(111)

    counts = {}
    for a in aircrafts:
        counts[a.airline] = counts.get(a.airline, 0) + 1  # Comptem vols

    airlines = list(counts.keys())  # Llista d’aerolínies
    flights = list(counts.values())  # Llista de quantitats

    ax.bar(airlines, flights, color="#1E88E5")  # Dibuixem barres

    ax.set_title("Flights per Airline")
    ax.set_xlabel("Airline")
    ax.set_ylabel("Number of Flights")

    # Rotació i canvi de tamany perquè es pugui llegir bé
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=7)

    # Si hi ha massa aerolínies, amaguem algunes etiquetes
    if len(airlines) > 20:
        for label in ax.get_xticklabels():
            label.set_visible(False)
        for i, label in enumerate(ax.get_xticklabels()):
            if i % 3 == 0:  # Mostrem només cada 3
                label.set_visible(True)

    fig.tight_layout()  # Ajustem marges

    if fig is None:
        plt.show()


# PLOT FLIGHTS TYPE
# Compara vols Schengen vs No Schengen amb una barra apilada (un a sobre de l'altre)
# Blau = Schengen i Vermell = Non-Schengen

def PlotFlightsType(aircrafts, fig=None):

    external_fig = fig is not None  # Comprovem si ens han passat figura externa

    if fig is None:
        fig = plt.figure()  # Creem figura si no existeix

    ax = fig.add_subplot(111)  # Afegim subplot

    schengen = 0
    non_schengen = 0

    for a in aircrafts:

        # Si és arribada usem origin; si és sortida/nocturn usem destination
        airport_code = a.origin

        if airport_code == "":
            airport_code = a.destination  # Si no hi ha origen, usem destí

        # Comptem segons si és Schengen o no
        if IsSchengenAirport(airport_code):
            schengen += 1
        else:
            non_schengen += 1

    # Barra apilada: primer Schengen i després Non-Schengen a sobre
    ax.bar(
        ["Flights"],
        [schengen],
        label="Schengen",
        color="#1E88E5"
    )

    ax.bar(
        ["Flights"],
        [non_schengen],
        bottom=[schengen],
        label="Non-Schengen",
        color="#E53935"
    )

    ax.set_title("Schengen vs Non-Schengen Flights")
    ax.set_ylabel("Number of Flights")
    ax.legend()
    ax.grid(axis="y")  # Línies horitzontals per llegir millor

    if not external_fig:
        plt.show()  # Només mostrem si no és figura externa


# MAP FLIGHTS
# Genera un fitxer KML amb les rutes dels vols cap a LEBL
# Només rep aircrafts i carrega Airports.txt internament

# ============================================================
# MapFlights
# Genera un KML amb trajectòries de vols.
# Si el vol té origin, dibuixa origin -> LEBL.
# Si el vol té destination, dibuixa LEBL -> destination.
# Així cobrim arribades i sortides.
# ============================================================
def MapFlights(aircrafts, airports):

    if len(aircrafts) == 0:
        print("Error: no aircrafts")
        return -1

    if len(airports) == 0:
        print("Error: no airports")
        return -1

    lebl = SearchAirportByCode(airports, "LEBL")

    if lebl is None:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
    else:
        lebl_lat = lebl.coordinates[0]
        lebl_lon = lebl.coordinates[1]

    try:
        file = open("FlightsMap.kml", "w", encoding="utf-8")
    except:
        print("Error: KML file could not be created")
        return -1

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write("<Document>\n")

    # Estil arribades Schengen
    file.write('<Style id="arrival_schengen">\n')
    file.write('<LineStyle><color>ff00ff00</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    # Estil arribades non-Schengen
    file.write('<Style id="arrival_nonschengen">\n')
    file.write('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    # Estil sortides
    file.write('<Style id="departure">\n')
    file.write('<LineStyle><color>ffff9900</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    for a in aircrafts:

        # ----------------------------
        # ARRIVAL: origin -> LEBL
        # ----------------------------
        if a.origin != "":

            origin_airport = SearchAirportByCode(airports, a.origin)

            if origin_airport is not None:

                origin_lat = origin_airport.coordinates[0]
                origin_lon = origin_airport.coordinates[1]

                if IsSchengenAirport(a.origin):
                    style = "#arrival_schengen"
                else:
                    style = "#arrival_nonschengen"

                file.write("<Placemark>\n")
                file.write("<name>" + a.aircraft_id + " ARRIVAL: " + a.origin + " - LEBL</name>\n")
                file.write("<styleUrl>" + style + "</styleUrl>\n")
                file.write("<LineString>\n")
                file.write("<tessellate>1</tessellate>\n")
                file.write("<coordinates>\n")
                file.write(f"{origin_lon},{origin_lat},0 ")
                file.write(f"{lebl_lon},{lebl_lat},0\n")
                file.write("</coordinates>\n")
                file.write("</LineString>\n")
                file.write("</Placemark>\n")

        # ----------------------------
        # DEPARTURE: LEBL -> destination
        # ----------------------------
        if a.destination != "":

            destination_airport = SearchAirportByCode(airports, a.destination)

            if destination_airport is not None:

                dest_lat = destination_airport.coordinates[0]
                dest_lon = destination_airport.coordinates[1]

                file.write("<Placemark>\n")
                file.write("<name>" + a.aircraft_id + " DEPARTURE: LEBL - " + a.destination + "</name>\n")
                file.write("<styleUrl>#departure</styleUrl>\n")
                file.write("<LineString>\n")
                file.write("<tessellate>1</tessellate>\n")
                file.write("<coordinates>\n")
                file.write(f"{lebl_lon},{lebl_lat},0 ")
                file.write(f"{dest_lon},{dest_lat},0\n")
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
    while i < len(airports):  # Recorrem la llista
        if airports[i].code == code:  # Coincidència trobada
            return airports[i]
        i += 1
    return None  # No trobat


# HAVERSINE
# Calcula la distància entre dues coordenades geogràfiques.

def Haversine(lat1, lon1, lat2, lon2):

    R = 6371.0  # Radi de la Terra en km

    # Convertim graus a radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1  # Diferència de latitud
    dlon = lon2 - lon1  # Diferència de longitud

    # Fórmula Haversine
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distància final en km


# LONG DISTANCE ARRIVALS
# Retorna vols que arriben a LEBL des de més de 2000 km.

# ============================================================
# LongDistanceArrivals
# Retorna vols de més de 2000 km.
# Manté el nom per compatibilitat, però ara serveix per arribades i sortides.
# ============================================================
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

    for a in aircrafts:

        is_long = False

        # Arribada: origin -> LEBL
        if a.origin != "":

            origin_airport = SearchAirportByCode(airports, a.origin)

            if origin_airport is not None:

                dist = Haversine(
                    origin_airport.coordinates[0],
                    origin_airport.coordinates[1],
                    lebl_lat,
                    lebl_lon
                )

                if dist > 2000:
                    is_long = True

        # Sortida: LEBL -> destination
        if a.destination != "":

            destination_airport = SearchAirportByCode(airports, a.destination)

            if destination_airport is not None:

                dist = Haversine(
                    lebl_lat,
                    lebl_lon,
                    destination_airport.coordinates[0],
                    destination_airport.coordinates[1]
                )

                if dist > 2000:
                    is_long = True

        if is_long:
            result.append(a)

    return result


# --------- VERSIÓ 4 ---------

# LOAD DEPARTURES
# Carrega vols de sortida des d'un fitxer i actualitza només els camps relacionats amb la sortida.
# Si el fitxer no existeix, retorna llista buida i codi d'error.

def LoadDepartures(filename):

    aircrafts = []  # Llista de vols de sortida

    try:
        file = open(filename, "r")  # Obrim fitxer
    except:
        print("Error: file not found")
        return [], -1  # Retornem error

    header = file.readline()  # Llegim i ignorem capçalera

    for line in file:

        parts = line.split()  # Separem camps

        if len(parts) != 4:  # Format incorrecte
            continue

        aircraft_id = parts[0]
        destination = parts[1]
        departure = parts[2]
        airline = parts[3]

        # Validació de format hora hh:mm
        if _parse_time(departure) is None:
            continue

        # Creem objecte amb camps de sortida
        aircraft = Aircraft(
            aircraft_id=aircraft_id,
            airline=airline,
            destination=destination,
            departure=departure
        )

        aircrafts.append(aircraft)  # Afegim a la llista

    file.close()
    return aircrafts, 0  # Retornem llista i codi OK


# MERGE MOVEMENTS
# Combina arribades i sortides en una sola llista.
# Només es fusionen si els temps són compatibles (arrival < departure)

def MergeMovements(arrivals, departures):

    if len(arrivals) == 0 and len(departures) == 0:
        return []  # Si no hi ha dades, retornem buit

    merged = {}  # Diccionari aircraft_id → Aircraft

    # Primer afegim les arribades
    for a in arrivals:
        merged[a.aircraft_id] = a  # Guardem per ID

    # Després afegim o actualitzem amb departures
    for d in departures:

        if d.aircraft_id in merged:

            a = merged[d.aircraft_id]  # Recuperem arribada

            t_arr = _parse_time(a.arrival)
            t_dep = _parse_time(d.departure)

            # Només fusionem si els temps són compatibles
            if t_arr is not None and t_dep is not None and t_arr < t_dep:
                a.destination = d.destination
                a.departure = d.departure
            # Si no són compatibles, ignorem la fusió

        else:
            merged[d.aircraft_id] = d  # Afegim sortida sense arribada

    return list(merged.values())  # Convertim a llista


# NIGHT AIRCRAFT
# Retorna els avions que només tenen sortida (és a dir, que no tenen arribada durant el dia).

def NightAircraft(aircrafts):

    result = []  # Llista d’avions nocturns

    if len(aircrafts) == 0:
        return result

    for a in aircrafts:

        # Avió nocturn: només departure
        if a.arrival == "" and a.departure != "":
            result.append(a)

    return result


# TEST SECTION
# S'executa només si aquest fitxer es crida directament.

if __name__ == "__main__":
    # Exemple bàsic de prova
    arr = LoadArrivals("Arrivals.txt")  # Carreguem arribades
    print("Arrivals loaded:", len(arr))  # Mostrem quantes s’han carregat
