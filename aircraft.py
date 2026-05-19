# aircraft.py
import matplotlib.pyplot as plt
import webbrowser
import math
from airport import IsSchengenAirport, LoadAirports


# CLASSE Aircraft
# Aquesta classe representa un vol que arribarà a LEBL
# Guarda la informació bàsica que necessitem:
# - Identificador de l'avió
# -Companyia aèria
# - Aeroport d'origen
# - Hora prevista d'arribada
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



# Aquesta funció llegeix un fitxer d'arribades i crea una llista d'objectes Aircraft.
def LoadArrivals(filename):

    aircrafts = []
    #Obrim el fitxer
    try:
        file = open(filename, "r")
    except:
        print("Error: file not found")
        return aircrafts

    # La primera línia és la capçalera
    header = file.readline()

    for line in file:

        parts = line.split()

        #Cada línia bona ha de tenir:
        if len(parts) != 4:
            continue

        aircraft_id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        #Comprovem que hi hagi ":" a l'hora
        if ":" not in arrival:
            continue

        time_parts = arrival.split(":")

        #L'hora s'ha de poder separar en hora i minut
        if len(time_parts) != 2:
            continue

        try:
            hour = int(time_parts[0])
            minute = int(time_parts[1])
        except:
            continue

        #Validem rang d'hores
        if hour < 0 or hour > 23:
            continue

        #Validem rang de minuts
        if minute < 0 or minute > 59:
            continue

        #Si la línia és correcta creem el vol
        aircraft = Aircraft(
            aircraft_id,
            airline,
            origin,
            arrival
        )

        aircrafts.append(aircraft)

    file.close()

    return aircrafts



# Mostra una gràfica amb el nombre d'arribades per hora
def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: empty list")
        return
    #Creem una llista de 24 posicions una per cada hora
    hours = [0] * 24

    i = 0
    while i < len(aircrafts):
        #Per cada vol llegim l'hora d'arribada
        arrival = aircrafts[i].arrival
        hour = int(arrival.split(":")[0])
        # Sumem 1 al comptador d'aquella hora
        hours[hour] += 1
        i += 1

    #Fem el gràfic de barres
    plt.bar(range(24), hours)
    plt.title("Landing frequency per hour")
    plt.xlabel("Hour")
    plt.ylabel("Number of arrivals")
    plt.show()



# Desa la informació dels vols en un fitxer de text.
def SaveFlights(aircrafts, filename):
    #Comprovem que la llista no sigui buida
    if len(aircrafts) == 0:
        print("Error: empty list")
        return -1

    #Obrim el fitxer de sortida
    file = open(filename, "w")

    file.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
    #recorrem tots els vols
    i = 0
    while i < len(aircrafts):

        aircraft = aircrafts[i]

        aircraft_id = aircraft.aircraft_id
        origin = aircraft.origin
        arrival = aircraft.arrival
        airline = aircraft.airline

        # Si algun camp està buit el substituïm
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


# Mostra una gràfica amb el nombre de vols per companyia
def PlotAirlines(aircrafts):

    if len(aircrafts) == 0:
        print("Error: empty list")
        return

    airlines = []
    counts = []

    #Anem guardant les companyies que apareixen
    i = 0
    while i < len(aircrafts):

        airline = aircrafts[i].airline

        #Si la companyia ja hi és incrementem el comptador
        if airline in airlines:
            j = airlines.index(airline)
            counts[j] += 1

        #Si no hi és l'afegim i comencem a comptar des de 1
        else:
            airlines.append(airline)
            counts.append(1)

        i += 1
    #Fem una barra per cada companyia
    plt.bar(airlines, counts)
    plt.xlabel("Airlines")
    plt.ylabel("Number of flights")
    plt.title("Flights per airline")
    plt.show()


# Compara quants vols venen de països Schengen i quants no.
def PlotFlightsType(aircrafts):
    #Per cada vol, mirem el codi ICAO d'origen
    if len(aircrafts) == 0:
        print("Error: empty aircraft list")
        return

    schengen_count = 0
    non_schengen_count = 0

    i = 0
    while i < len(aircrafts):

        origin = aircrafts[i].origin
        #Usem IsSchengenAirport per saber el tipus
        #Comptem Schengen i non-Schengen
        if IsSchengenAirport(origin):
            schengen_count += 1
        else:
            non_schengen_count += 1

        i += 1
    #Fm una barra
    plt.bar(["Flights"], [schengen_count], label="Schengen")
    plt.bar(["Flights"], [non_schengen_count],
            bottom=[schengen_count],
            label="Non-Schengen")

    plt.xlabel("Flights")
    plt.ylabel("Number of flights")
    plt.title("Schengen vs Non-Schengen arrivals")
    plt.legend()
    plt.show()

# Genera un fitxer KML amb les trajectòries dels vols des de l'aeroport d'origen fins a LEBL.
def MapFlights(aircrafts, airports):
    #Comprovem que hi hagi vols i aeroports
    if len(aircrafts) == 0:
        print("Error: no aircrafts")
        return -1

    if len(airports) == 0:
        print("Error: no airports")
        return -1

    #Coordenades fixes de LEBL
    lebl_lat = 41.297445
    lebl_lon = 2.0832941
    #Creem el fitxer KML
    file = open("FlightsMap.kml", "w", encoding="utf-8")

    file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    file.write("<Document>\n")

    # 3. Definim estils de color per Schengen / no Schengen
    #Estil per a vols Schengen
    file.write('<Style id="schengen">\n')
    file.write('<LineStyle><color>ff00ff00</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    #Estil per a vols no Schengen
    file.write('<Style id="nonschengen">\n')
    file.write('<LineStyle><color>ff0000ff</color><width>3</width></LineStyle>\n')
    file.write("</Style>\n")

    #Per cada vol, busquem les coordenades de l'origen
    i = 0
    while i < len(aircrafts):

        origin_code = aircrafts[i].origin
        found = False
        j = 0

        #Busquem l'aeroport d'origen dins la llista d'aeroports
        while j < len(airports) and not found:

            if airports[j].code == origin_code:
                found = True
                origin_lat = airports[j].coordinates[0]
                origin_lon = airports[j].coordinates[1]
            else:
                j += 1

        #Si hem trobat l'aeroport dibuixem la ruta
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
            file.write("<styleUrl>" + style + "</styleUrl>\n")
            file.write("<LineString>\n")
            file.write("<tessellate>1</tessellate>\n")
            file.write("<coordinates>\n")

            #Primer punt origen
            file.write(str(origin_lon) + "," + str(origin_lat) + ",0 ")

            #Segon punt Barcelona El Prat
            file.write(str(lebl_lon) + "," + str(lebl_lat) + ",0\n")

            file.write("</coordinates>\n")
            file.write("</LineString>\n")
            file.write("</Placemark>\n")

        i += 1

    file.write("</Document>\n")
    file.write("</kml>\n")
    file.close()
    #Obrim el KML
    print("FlightsMap.kml created")
    webbrowser.open("FlightsMap.kml")

    return 0

# Busca un aeroport dins una llista a partir del seu codi ICAO.
# Si el troba retorna l'objecte Airport si no retorna None.
def SearchAirportByCode(airports, code):

    i = 0
    while i < len(airports):
        if airports[i].code == code:
            return airports[i]
        i += 1

    return None


# Calcula la distància entre dues coordenades geogràfiques sobre la superfície de la Terra.
def Haversine(lat1, lon1, lat2, lon2):

    R = 6371.0  # radi de la Terra en km
    #Convertim graus a radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    #Calculem diferències de latitud i longitud
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    #Apliquem la fórmula de Haversine
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    #Retornem la distància en km
    return R * c


# Retorna només els vols que venen de més de 2000 km.
def LongDistanceArrivals(aircrafts):
    result = []
    #Carreguem la llista d'aeroports
    if len(aircrafts) == 0:
        return result

    airports = LoadAirports("Airports.txt")
    if len(airports) == 0:
        print("Error: Airports.txt could not be loaded")
        return result
    #Busquem LEBL
    lebl = SearchAirportByCode(airports, "LEBL")

    #Si no trobem LEBL al fitxer, fem servir coordenades fixes
    if lebl is None:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
    else:
        lebl_lat = lebl.coordinates[0]
        lebl_lon = lebl.coordinates[1]

    i = 0
    while i < len(aircrafts):
        #Per cada vol busquem l'aeroport d'origen
        origin_airport = SearchAirportByCode(airports, aircrafts[i].origin)

        if origin_airport is not None:
            #Calculem la distància amb Haversine
            dist = Haversine(
                origin_airport.coordinates[0],
                origin_airport.coordinates[1],
                lebl_lat,
                lebl_lon
            )
            #Si és > 2000 km afegim el vol al resultat
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