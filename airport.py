# airport.py

import os
import matplotlib.pyplot as pyplot


# CLASS AIRPORT
# Aquesta classe guarda la informació bàsica d'un aeroport:
# - Codi ICAO
# - Coordenades
# - Si és Schengen o no

class Airport:

    def __init__(self, code, lat, lon):

        # Comprovem que el codi ICAO tingui 4 caràcters
        if len(code) == 4:
            self.code = code.upper()
        else:
            raise ValueError("ICAO code must have 4 characters")

        # Coordenades en graus decimals
        self.coordinates = [lat, lon]

        # Inicialment l'aeroport no està marcat com Schengen
        self.schengen = False


# IS SCHENGEN AIRPORT
# Aquesta funció comprova si un aeroport pertany a un país Schengen
# Ho fa mirant els dos primers caràcters del codi ICAO

def IsSchengenAirport(code):

    # Si el codi és buit retornem False
    if code == "":
        return False

    # Prefixos ICAO de països Schengen
    schengen_codes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED',
        'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM',
        'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    # Guardem els dos primers caràcters
    prefix = code[0:2].upper()

    i = 0

    # Busquem si el prefix està dins la llista
    while i < len(schengen_codes):

        if prefix == schengen_codes[i]:
            return True

        i += 1

    return False


# SET SCHENGEN
# Aquesta funció calcula i guarda si un aeroport és Schengen

def SetSchengen(airport):

    airport.schengen = IsSchengenAirport(airport.code)


# PRINT AIRPORT
# Aquesta funció mostra tota la informació d'un aeroport

def PrintAirport(airport):

    print("Code:", airport.code)
    print("Latitude:", airport.coordinates[0])
    print("Longitude:", airport.coordinates[1])
    print("Schengen:", airport.schengen)


# LOAD AIRPORTS
# Aquesta funció carrega aeroports des d'un fitxer de text

def LoadAirports(filename):

    airports = []

    # Intentem obrir el fitxer
    try:
        F = open(filename, "r")
    except:
        print("Error: file could not be opened")
        return airports

    lines = F.readlines()

    F.close()

    # Comencem a la línia 1 perquè la primera és la capçalera
    i = 1

    while i < len(lines):

        line = lines[i].strip()

        # Ignorem línies buides
        if line == "":
            i += 1
            continue

        data = line.split()

        # Comprovem que hi hagi prou dades
        if len(data) < 3:
            i += 1
            continue

        code = data[0]
        lat_str = data[1]
        lon_str = data[2]

        # LATITUD

        sign = 1

        # Si comença per S és negativa
        if lat_str[0] == 'S':
            sign = -1

        degrees = int(lat_str[1:3])
        minutes = int(lat_str[3:5])
        seconds = int(lat_str[5:7])

        # Convertim DMS a graus decimals
        lat = degrees + minutes / 60 + seconds / 3600

        lat = lat * sign

        # LONGITUD

        sign = 1

        # Si comença per W també és negativa
        if lon_str[0] == 'W':
            sign = -1

        degrees = int(lon_str[1:4])
        minutes = int(lon_str[4:6])
        seconds = int(lon_str[6:8])

        # Convertim DMS a graus decimals
        lon = degrees + minutes / 60 + seconds / 3600

        lon = lon * sign

        # Creem l'aeroport i l'afegim a la llista
        airport = Airport(code, lat, lon)

        airports.append(airport)

        i += 1

    return airports


# SAVE SCHENGEN AIRPORTS
# Aquesta funció desa en un fitxer només els aeroports Schengen

def SaveSchengenAirports(airports, filename):

    # Si la llista és buida retornem error
    if len(airports) == 0:
        return -1

    # Funció auxiliar per convertir graus decimals a format DMS (N452805)
    def decimal_to_dms(value, is_latitude):
        # Determinem si és Nord/Sud o Est/Oest
        if is_latitude:
            direction = 'N' if value >= 0 else 'S'
            value = abs(value)
            degrees = int(value)
            minutes = int((value - degrees) * 60)
            seconds = int((((value - degrees) * 60) - minutes) * 60)
            return f"{direction}{degrees:02d}{minutes:02d}{seconds:02d}"
        else:
            direction = 'E' if value >= 0 else 'W'
            value = abs(value)
            degrees = int(value)
            minutes = int((value - degrees) * 60)
            seconds = int((((value - degrees) * 60) - minutes) * 60)
            return f"{direction}{degrees:03d}{minutes:02d}{seconds:02d}"

    # Intentem crear el fitxer
    try:
        F = open(filename, "w")
    except:
        return -1

    # Escrivim la capçalera
    F.write("CODE LAT LON\n")

    found = False

    for airport in airports:

        # Només guardem aeroports Schengen
        if airport.schengen:

            found = True

            lat = airport.coordinates[0]
            lon = airport.coordinates[1]

            # Convertim a format DMS
            lat_dms = decimal_to_dms(lat, True)
            lon_dms = decimal_to_dms(lon, False)

            F.write(f"{airport.code} {lat_dms} {lon_dms}\n")

    F.close()

    # Si hem trobat almenys un aeroport Schengen retornem OK
    if found:
        return 0
    else:
        return -1

# ADD AIRPORT
# Aquesta funció afegeix un aeroport a la llista només si el codi ICAO no existeix ja

def AddAirport(airports, airport):

    i = 0

    while i < len(airports):

        # Si el codi ja existeix retornem error
        if airports[i].code == airport.code:
            return -1

        i += 1

    airports.append(airport)

    return 0


# REMOVE AIRPORT
# Aquesta funció elimina un aeroport segons el codi ICAO

def RemoveAirport(airports, code):

    i = 0

    while i < len(airports):

        # Si trobem l'aeroport l'eliminem
        if airports[i].code == code:

            del airports[i]

            return 0

        i += 1

    # Si no existeix retornem error
    return -1


# PLOT AIRPORTS
# Aquesta funció mostra un gràfic d'aeroports
# Schengen i non-Schengen

def PlotAirports(airports):

    # Comprovem que la llista no sigui buida
    if len(airports) == 0:

        print("Error: empty airport list")

        return -1

    schengen_count = 0
    non_schengen_count = 0

    i = 0

    # Comptem aeroports Schengen i no Schengen
    while i < len(airports):

        if airports[i].schengen:
            schengen_count += 1
        else:
            non_schengen_count += 1

        i += 1

    pyplot.figure(figsize=(6, 6))

    pyplot.bar(
        ["Airports"],
        [schengen_count],
        label="Schengen"
    )

    pyplot.bar(
        ["Airports"],
        [non_schengen_count],
        bottom=[schengen_count],
        label="Non-Schengen"
    )

    pyplot.ylabel("Count")
    pyplot.xlabel("Airports")

    pyplot.title("Schengen vs Non-Schengen Airports")

    pyplot.legend()

    pyplot.grid(axis="y")

    pyplot.show()

    return 0


# MAP AIRPORTS
# Aquesta funció crea un fitxer KML amb tots els aeroports
# per poder-los veure a Google Earth

def MapAirports(airports, filename="AirportsMap.kml"):

    # Comprovem que la llista no sigui buida
    if len(airports) == 0:

        print("Error: empty airport list")

        return -1

    filepath = os.path.abspath(filename)

    # Intentem crear el fitxer
    try:
        F = open(filepath, "w", encoding="utf-8")
    except:
        print("Error: file could not be created")
        return -1

    # Capçalera KML

    F.write('<?xml version="1.0" encoding="UTF-8"?>\n')

    F.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')

    F.write("<Document>\n")

    i = 0

    # Recorrem tots els aeroports
    while i < len(airports):

        airport = airports[i]

        code = airport.code
        lat = airport.coordinates[0]
        lon = airport.coordinates[1]

        # Verd = Schengen
        # Vermell = non-Schengen

        if airport.schengen:
            color = "ff00ff00"
        else:
            color = "ff0000ff"

        F.write("<Placemark>\n")

        F.write("<name>" + code + "</name>\n")

        F.write("<Style>\n")

        F.write("<IconStyle>\n")

        F.write("<color>" + color + "</color>\n")

        F.write("</IconStyle>\n")

        F.write("</Style>\n")

        F.write("<Point>\n")

        F.write("<coordinates>")

        F.write(str(lon) + "," + str(lat) + ",0")

        F.write("</coordinates>\n")

        F.write("</Point>\n")

        F.write("</Placemark>\n")

        i += 1

    # Final del fitxer KML

    F.write("</Document>\n")

    F.write("</kml>\n")

    F.close()

    print("KML file created")

    return filepath