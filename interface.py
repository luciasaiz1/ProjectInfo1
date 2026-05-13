from tkinter import *
from tkinter import messagebox, filedialog
from tkinter import *
from tkinter import messagebox, filedialog
import os
from airport import *
from aircraft import *
from LEBL import *
import math
# GLOBALS

# Aquí guardem la llista d'aeroports que fa servir la part de V1 i V2.
airports = []

# Aquí guardem la llista de vols d'arribada que carrega la V2.
aircrafts = []

# Aquí guardarem l'estructura de l'aeroport de Barcelona per la V3.
bcn = None


# HELPER FUNCTIONS

def _v2_backend_ready():
    # Aquesta funció comprova si les funcions principals de la V2 existeixen.
    required = [
        "LoadArrivals",
        "SaveFlights",
        "PlotArrivals",
        "PlotAirlines",
        "PlotFlightsType",
        "MapFlights",
        "LongDistanceArrivals",
        "TreuArrivalsMenys1000"
    ]

    i = 0
    while i < len(required):
        if required[i] not in globals():
            return False
        i += 1

    return True


def _v3_backend_ready():
    # Aquesta funció comprova si les funcions principals de la V3 existeixen.
    required = [
        "LoadAirportStructure",
        "AssignGate",
        "GateOccupancy",
        "SearchTerminal",
        "IsAirlineInTerminal"
    ]

    i = 0
    while i < len(required):
        if required[i] not in globals():
            return False
        i += 1

    return True


# VERSION 1 FUNCTIONS

def load_airports():
    # Aquesta funció carrega el fitxer Airports.txt i calcula si cada aeroport és Schengen o no.
    global airports

    airports = LoadAirports("Airports.txt")

    if len(airports) == 0:
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        i += 1

    messagebox.showinfo("OK", "Loaded " + str(len(airports)) + " airports")


def add_airport():
    # Aquesta funció afegeix un aeroport nou amb el codi i les coordenades escrites a la interfície.
    global airports

    code = entry_code.get().strip().upper()

    if len(code) != 4:
        messagebox.showerror("Error", "ICAO code must have 4 characters")
        return

    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except:
        messagebox.showerror("Error", "Latitude and longitude must be numbers")
        return

    airport = Airport(code, lat, lon)
    SetSchengen(airport)
    AddAirport(airports, airport)

    messagebox.showinfo("OK", "Airport added")


def remove_airport():
    # Aquesta funció elimina un aeroport de la llista a partir del codi ICAO escrit.
    global airports

    code = entry_code.get().strip().upper()

    if code == "":
        messagebox.showerror("Error", "Write an ICAO code first")
        return

    err = RemoveAirport(airports, code)

    if err == -1:
        messagebox.showerror("Error", "Airport not found")
    else:
        messagebox.showinfo("OK", "Airport removed")


def plot_airports():
    # Aquesta funció mostra el gràfic d'aeroports Schengen i no Schengen.
    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    PlotAirports(airports)


def map_airports():
    # Aquesta funció crea el KML dels aeroports i intenta obrir-lo automàticament.
    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    kml_path = MapAirports(airports)

    try:
        os.startfile(kml_path)
    except:
        messagebox.showinfo("OK", "KML created at:\n" + kml_path)


def save_schengen():
    # Aquesta funció desa en un fitxer només els aeroports que són Schengen.
    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    err = SaveSchengenAirports(airports, "SchengenAirports.txt")

    if err == -1:
        messagebox.showerror("Error", "File could not be saved")
    else:
        messagebox.showinfo("OK", "SchengenAirports.txt saved")


# VERSION 2 FUNCTIONS

def LoadArrivalsButton():
    # Aquesta funció deixa triar un fitxer d'arribades i el carrega a la llista de vols.
    global aircrafts

    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    filename = filedialog.askopenfilename(
        title="Select arrivals file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    aircrafts = LoadArrivals(filename)

    if len(aircrafts) == 0:
        messagebox.showerror("Error", "No arrivals loaded")
    else:
        messagebox.showinfo("OK", "Loaded " + str(len(aircrafts)) + " arrivals")


def SaveFlightsButton():
    # Aquesta funció desa la llista de vols carregada en un fitxer triat per l'usuari.
    global aircrafts

    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    filename = filedialog.asksaveasfilename(
        title="Save flights file",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    err = SaveFlights(aircrafts, filename)

    if err == -1:
        messagebox.showerror("Error", "Flights could not be saved")
    else:
        messagebox.showinfo("OK", "Flights saved correctly")


def PlotArrivalsButton():
    # Aquesta funció mostra el gràfic del nombre d'arribades per hora.
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotArrivals(aircrafts)


def PlotAirlinesButton():
    # Aquesta funció mostra el gràfic del nombre de vols per companyia.
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotAirlines(aircrafts)


def PlotFlightsTypeButton():
    # Aquesta funció mostra el gràfic de vols Schengen i no Schengen.
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotFlightsType(aircrafts)


def MapFlightsButton():
    # Aquesta funció crea el mapa KML de totes les trajectòries dels vols carregats.
    global airports

    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    # Si encara no hem carregat aeroports, els carreguem ara perquè el mapa els necessita.
    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")

        if len(airports) == 0:
            messagebox.showerror("Error", "Airports could not be loaded")
            return

        i = 0
        while i < len(airports):
            SetSchengen(airports[i])
            i += 1

    MapFlights(aircrafts, airports)


def MapLongDistanceButton():
    # Aquesta funció crea el mapa només dels vols que venen de més de 2000 km.
    global airports

    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    # Si encara no hem carregat aeroports, els carreguem ara perquè el mapa els necessita.
    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")

        if len(airports) == 0:
            messagebox.showerror("Error", "Airports could not be loaded")
            return

        i = 0
        while i < len(airports):
            SetSchengen(airports[i])
            i += 1

    long_distance = LongDistanceArrivals(aircrafts)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance arrivals found")
        return

    MapFlights(long_distance, airports)

def TreureShortDistanceButton():
    # Aquesta funció elimina de la llista d'arribades vols -1000km i després surt a google earth només les arribades que queden.

    global aircrafts
    global airports

    # Si encara no hem carregat arribades no es pot eliminar res
    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    # Si encara no hem carregat aeroports els carreguem i ara necessitem arrivals perque es calcuulen amb coordenades
    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")

        if len(airports) == 0:
            messagebox.showerror("Error", "Airports could not be loaded")
            return

        # Marquem cada aeroport com schengen o no chengen.
        i = 0
        while i < len(airports):
            SetSchengen(airports[i])
            i = i + 1

    # Guardem quants vols hi havia abans de filtrar
    numero_abans = len(aircrafts)

    # La linia de codi substitueix la llista per una nova llista filtrada
    aircrafts = TreuArrivalsMenys1000(aircrafts, airports)

    # Calculem quants vols s'han eliminat
    removed = numero_abans - len(aircrafts)


    # A google earth només les arribades que queden
    MapFlights(aircrafts, airports)

    #Missatge per saber que ha funcionat
    messagebox.showinfo(
        "OK",
        "Removed arrivals closer than 1000 km: " + str(removed) +
        "\nRemaining arrivals: " + str(len(aircrafts))
    )

# VERSION 3 FUNCTIONS

def BuildLEBLStructureButton():
    # Aquesta funció carrega des de LEBL.txt l'estructura de terminals, àrees i gates.
    global bcn

    if not _v3_backend_ready():
        messagebox.showerror("Error", "Version 3 backend is not ready")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    messagebox.showinfo(
        "OK",
        "LEBL structure loaded with " + str(len(bcn.terminals)) + " terminals"
    )


def AssignGatesButton():
    # Aquesta funció assigna una gate a cada vol carregat segons les regles de la V3.
    global bcn
    global aircrafts

    if not _v3_backend_ready():
        messagebox.showerror("Error", "Version 3 backend is not ready")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    # Reconstruïm LEBL abans d'assignar per evitar que es dupliquin ocupacions si premem dues vegades.
    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    assigned = 0
    failed = 0

    i = 0
    while i < len(aircrafts):
        gate_name = AssignGate(bcn, aircrafts[i])

        if gate_name == -1:
            failed += 1
        else:
            assigned += 1

        i += 1

    messagebox.showinfo(
        "Gate Assignment",
        "Assigned: " + str(assigned) + "\nNot assigned: " + str(failed)
    )


def ShowGateOccupancyButton():
    # Aquesta funció obre una finestra nova i mostra l'estat de totes les gates.
    global bcn

    if not _v3_backend_ready():
        messagebox.showerror("Error", "Version 3 backend is not ready")
        return

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    occupancy = GateOccupancy(bcn)

    if len(occupancy) == 0:
        messagebox.showinfo("Info", "No gate occupancy data available")
        return

    # Aquí construïm el text que veurem a la finestra d'ocupació.
    text = ""

    i = 0
    while i < len(occupancy):
        terminal = occupancy[i][0]
        area = occupancy[i][1]
        gate = occupancy[i][2]
        occupied = occupancy[i][3]
        aircraft_id = occupancy[i][4]

        if occupied:
            status = "Occupied by " + aircraft_id
        else:
            status = "Free"

        text = text + terminal + " | " + area + " | " + gate + " | " + status + "\n"
        i += 1

    occ_window = Toplevel(window)
    occ_window.title("Gate Occupancy")
    occ_window.geometry("800x500")

    scrollbar = Scrollbar(occ_window)
    scrollbar.pack(side=RIGHT, fill=Y)

    txt = Text(occ_window, wrap="none", yscrollcommand=scrollbar.set)
    txt.pack(fill=BOTH, expand=True)

    scrollbar.config(command=txt.yview)

    txt.insert("1.0", text)


# EXIT

def exit_program():
    # Aquesta funció tanca la finestra principal del programa.
    window.destroy()


# WINDOW

# Aquí creem la finestra principal del programa.
window = Tk()
window.title("Airport Manager")
window.geometry("520x620")


# INPUTS DE V1

# Aquests Entry serveixen per afegir aeroports manualment a la V1.
label1 = Label(window, text="ICAO Code")
label1.pack()
entry_code = Entry(window)
entry_code.pack()

label2 = Label(window, text="Latitude")
label2.pack()
entry_lat = Entry(window)
entry_lat.pack()

label3 = Label(window, text="Longitude")
label3.pack()
entry_lon = Entry(window)
entry_lon.pack()


# VERSION 1 BUTTONS

# Aquest frame agrupa els botons de la part d'aeroports de la V1.
frame_v1 = Frame(window)
frame_v1.pack(pady=10)

Button(frame_v1, text="Load Airports", width=28, command=load_airports).grid(row=0, column=0, padx=5, pady=5)
Button(frame_v1, text="Add Airport", width=28, command=add_airport).grid(row=0, column=1, padx=5, pady=5)
Button(frame_v1, text="Remove Airport", width=28, command=remove_airport).grid(row=1, column=0, padx=5, pady=5)
Button(frame_v1, text="Plot Airports", width=28, command=plot_airports).grid(row=1, column=1, padx=5, pady=5)
Button(frame_v1, text="Map Airports", width=28, command=map_airports).grid(row=2, column=0, padx=5, pady=5)
Button(frame_v1, text="Save Schengen Airports", width=28, command=save_schengen).grid(row=2, column=1, padx=5, pady=5)


# VERSION 2 BUTTONS

# Aquest frame agrupa els botons de la part de vols i arribades de la V2.
frame_v2 = Frame(window)
frame_v2.pack(pady=10)

Button(frame_v2, text="Load Arrivals", width=28, command=LoadArrivalsButton).grid(row=0, column=0, padx=5, pady=5)
Button(frame_v2, text="Save Flights", width=28, command=SaveFlightsButton).grid(row=0, column=1, padx=5, pady=5)
Button(frame_v2, text="Plot Arrivals / Hour", width=28, command=PlotArrivalsButton).grid(row=1, column=0, padx=5, pady=5)
Button(frame_v2, text="Plot Flights / Airline", width=28, command=PlotAirlinesButton).grid(row=1, column=1, padx=5, pady=5)
Button(frame_v2, text="Plot Schengen / Non-Schengen", width=28, command=PlotFlightsTypeButton).grid(row=2, column=0, padx=5, pady=5)
Button(frame_v2, text="Map All Flights", width=28, command=MapFlightsButton).grid(row=2, column=1, padx=5, pady=5)
Button(frame_v2, text="Map Long-Distance Flights", width=28, command=MapLongDistanceButton).grid(row=3, column=0, columnspan=2, padx=5, pady=5)
Button(frame_v2, text="Remove <1000 km and Map", width=28, command=TreureShortDistanceButton).grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# VERSION 3 BUTTONS

# Aquest frame agrupa els botons nous de la V3 per gestionar gates.
frame_v3 = Frame(window)
frame_v3.pack(pady=10)

Button(frame_v3, text="Build LEBL Structure", width=28, command=BuildLEBLStructureButton).grid(row=0, column=0, padx=5, pady=5)
Button(frame_v3, text="Assign Gates", width=28, command=AssignGatesButton).grid(row=0, column=1, padx=5, pady=5)
Button(frame_v3, text="Show Gate Occupancy", width=28, command=ShowGateOccupancyButton).grid(row=1, column=0, columnspan=2, padx=5, pady=5)


# EXIT BUTTON

# Aquest botó tanca el programa.
button_exit = Button(window, text="Exit", width=28, command=exit_program)
button_exit.pack(pady=10)

window.mainloop()