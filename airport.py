# STEP 1

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

        lat = degrees + minutes / 60 + seconds / 3600
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


        if found:
            return 0
        else:
            return -1
    F.close()

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

    if len(airports) == 0:
        print("Error: no airports")
        return -1

    file = open("AirportsMap.kml", "w")

    file.write("<kml>\n")
    file.write("<Document>\n")

    # GREEN → Schengen

    file.write("<Style id='green'>\n")
    file.write("<IconStyle>\n")
    file.write("<color>ff00ff00</color>\n")
    file.write("</IconStyle>\n")
    file.write("</Style>\n")

    # RED → Non-Schengen

    file.write("<Style id='red'>\n")
    file.write("<IconStyle>\n")
    file.write("<color>ff0000ff</color>\n")
    file.write("</IconStyle>\n")
    file.write("</Style>\n")

    i = 0

    while i < len(airports):

        airport = airports[i]

        if airport.schengen == True:
            style = "green"
        else:
            style = "red"

        lat = airport.coordinates[0]
        lon = airport.coordinates[1]

        file.write("<Placemark>\n")

        file.write("<name>")
        file.write(airport.code)
        file.write("</name>\n")

        file.write("<styleUrl>#")
        file.write(style)
        file.write("</styleUrl>\n")

        file.write("<Point>\n")

        file.write("<coordinates>")

        file.write(str(lon))
        file.write(",")

        file.write(str(lat))
        file.write(",0")

        file.write("</coordinates>\n")

        file.write("</Point>\n")

        file.write("</Placemark>\n")

        i = i + 1

    file.write("</Document>\n")
    file.write("</kml>\n")

    file.close()

    print("AirportsMap.kml created")

    return 0

