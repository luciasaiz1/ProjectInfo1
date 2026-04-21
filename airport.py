# STEP 1
import math
# We create the class
class Airport:

   def __init__(self, code, lat, lon):

       if len(code) == 4:
           self.code = code           # ICAO code, it must have 4 characters
       else:
           print("Error: ICAO code must have 4 characters")

       self.coordinates = [lat, lon]  # Coordinates
       self.schengen = False          # Schengen


# Check if the airport is in a Schengen country
def IsSchengenAirport(code):

   #  If the input parameter is empty then False is returned
   if code == "":
       return False

   schengen_codes = [
       'LO','EB','LK','LC','EK','EE','EF','LF','ED','LG',
       'EH','LH','BI','LI','EV','EY','EL','LM','EN','EP',
       'LP','LZ','LJ','LE','ES','LS']

   i = 0
   found = False


   # Search if the first two characters of the ICAO are in the list
   while (i < len(schengen_codes)) and not(found):


       # Check if code starts with that country code

       if code[0] == schengen_codes[i][0]:
           if code[1] == schengen_codes[i][1]:
               found = True

       if not(found):
           i=i+1

   if found:
       return True
   else:
       return False

# Writes the information of the airports that are Schengen into a file whose name is in filename.
def SetSchengen(airport):
   airport.schengen = IsSchengenAirport(airport.code)

def PrintAirport(airport):

   print("Code:", airport.code)
   print("Latitude:", airport.coordinates[0])
   print("Longitude:", airport.coordinates[1])
   print("Schengen:", airport.schengen)

# STEP 3

def LoadAirports(filename):

    airports = []
    try:
        F = open(filename, "r")
    except:
        return airports

    lineas = F.readlines()
    F.close()

    i = 1  # Skips the first line
    while i < len(lineas):

        linea = lineas[i]
        datos = linea.split(" ")
        code = datos[0]
        lat_str = datos[1]
        lon_str = datos[2]

        # CONVERT the format of LATITUDE

        sign = 1

        if lat_str[0] == 'S':
            sign = -1 # Negative for South

        degrees = int(lat_str[1:3])
        minutes = int(lat_str[3:5])
        seconds = int(lat_str[5:7])

        lat= degrees + minutes / 60 + seconds / 3600
        lat = lat * sign

        # CONVERT the format of LONGITUDE
        sign = 1

        if lon_str[0] == 'W':
            sign = -1 # Negative for West
        degrees = int(lon_str[1:4])
        minutes = int(lon_str[4:6])
        seconds = int(lon_str[6:8])

        lon = degrees + minutes / 60 + seconds / 3600
        lon = lon * sign
        airport = Airport(code, lat, lon)
        airports.append(airport)
        i = i + 1

        return airports


def SaveSchengenAirports(airports, filename):

    if len(airports) == 0:
        return -1

    F = open(filename, "w")
    F.write("CODE LAT LON\n")

    i = 0
    found = False

    while i < len(airports):

        if airports[i].schengen == True:
            found = True
            code = airports[i].code
            lat = airports[i].coordinates[0]
            lon = airports[i].coordinates[1]
            F.write(code + " ")
            F.write(str(lat) + " ")
            F.write(str(lon) + "\n")

        i = i + 1
        F.close()

        if found:
            return 0
        else:
            return -1

def AddAirport(airports, airport):

    i = 0
    found = False
    while (i < len(airports)) and not (found):

        if airports[i].code == airport.code:
            found = True
        else:
            i = i + 1

        if not (found):
           airports.append(airport)

def RemoveAirport(airports, code):

    i = 0
    found = False

    while (i < len(airports)) and not (found):

        if airports[i].code == code:
            found = True
        else:
            i = i + 1

        if found:
           del airports[i]
           return 0

        else:
           return -1

#STEP 5
#Stacked bar
import matplotlib.pyplot as pyplot

def PlotAirports(airports):
    if len(airports) == 0:
        print("Error: empty airport list")
        return -1

    schengen_count = 0
    no_schengen_count = 0

    i = 0
    while i < len(airports):
        if airports[i].schengen:
            schengen_count += 1
        else:
            no_schengen_count += 1
        i += 1

    pyplot.bar(["Airports"], [schengen_count], label="Schengen")
    pyplot.bar(["Airports"], [no_schengen_count], bottom=[schengen_count], label="No Schengen")
    pyplot.ylabel("Count")
    pyplot.xlabel("Airports")
    pyplot.title("Schengen and non-Schengen airports")
    pyplot.legend()
    pyplot.grid()
    pyplot.show()


#Mapa Aeroports KML

def MapAirports(airports):

    F = open("AirportsMap.kml", "w")

    F.write("<kml>\n")

    F.write("  <Document>\n")


    # STYLES

    F.write("    <Style id=\"green\">\n")

    F.write("      <IconStyle>\n")

    F.write("        <color>ff00ff00</color>\n")

    F.write("      </IconStyle>\n")

    F.write("    </Style>\n")


    F.write("    <Style id=\"red\">\n")

    F.write("      <IconStyle>\n")

    F.write("        <color>ff0000ff</color>\n")

    F.write("      </IconStyle>\n")

    F.write("    </Style>\n")


    i = 0

    while i < len(airports):

        code = airports[i].code
        lat = airports[i].coordinates[0]
        lon = airports[i].coordinates[1]

        if airports[i].schengen == True:
            color = "ff00ff00"   # verd
        else:
            color = "ff0000ff"   # vermell

        F.write("    <Placemark>\n")
        F.write("      <name>" + code + "</name>\n")
        F.write("      <Style>\n")
        F.write("        <IconStyle>\n")
        F.write("          <color>" + color + "</color>\n")
        F.write("        </IconStyle>\n")
        F.write("      </Style>\n")
        F.write("      <Point>\n")
        F.write("        <coordinates>")
        F.write(str(lon) + "," + str(lat) + ",0")
        F.write("</coordinates>\n")
        F.write("      </Point>\n")
        F.write("    </Placemark>\n")

        i = i + 1

    F.write("  </Document>\n")
    F.write("</kml>\n")

    F.close()

    print("KML file created")

# =========================================================
# Haversine + LongDistanceArrivals
# =========================================================

def SearchAirportByCode(airports, code):
    """
    Returns the airport with the given ICAO code.
    If not found, returns None.
    """
    i = 0
    while i < len(airports):
        if airports[i].code == code:
            return airports[i]
        i += 1
    return None


def Haversine(lat1, lon1, lat2, lon2):
    """
    Returns distance in km between two coordinates in decimal degrees.
    """
    R = 6371.0  # Earth radius in km

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
    """
    Returns a list with aircrafts arriving to LEBL from airports
    more than 2000 km away.
    """
    result = []

    if len(aircrafts) == 0:
        return result

    airports = LoadAirports("Airports.txt")
    if len(airports) == 0:
        print("Error: Airports.txt could not be loaded")
        return result

    lebl = SearchAirportByCode(airports, "LEBL")

    # Fallback per si LEBL no surt al fitxer
    if lebl is None:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
    else:
        lebl_lat = lebl.latitude
        lebl_lon = lebl.longitude

    i = 0
    while i < len(aircrafts):
        origin_airport = SearchAirportByCode(airports, aircrafts[i].origin)

        if origin_airport is not None:
            dist = Haversine(
                origin_airport.latitude,
                origin_airport.longitude,
                lebl_lat,
                lebl_lon
            )

            if dist > 2000:
                result.append(aircrafts[i])

        i += 1

    return result


def MapLongDistanceFlights(aircrafts):
    """
    Optional helper: shows only long-distance arrivals on the map.
    """
    long_distance = LongDistanceArrivals(aircrafts)

    if len(long_distance) == 0:
        print("No long-distance arrivals found")
        return

    MapFlights(long_distance)