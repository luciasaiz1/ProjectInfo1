from tkinter import *
from tkinter import messagebox, filedialog
import os

from airport import *
from aircraft import *
from LEBL import *


# VARIABLES GLOBALS
# airports: llista d’aeroports carregats (V1 i V2)
# aircrafts: llista de vols carregats (V2)
# bcn: estructura de l’aeroport de Barcelona (V3)

airports = []
aircrafts = []
bcn = None



# FUNCIONS D’AJUDA (BACKEND CHECK)
# Comproven si les funcions necessàries de cada versió
# estan disponibles abans d’executar funcionalitats.


def _v2_backend_ready():

    required = [
        "LoadArrivals",
        "SaveFlights",
        "PlotArrivals",
        "PlotAirlines",
        "PlotFlightsType",
        "MapFlights",
        "LongDistanceArrivals"
    ]

    i = 0
    while i < len(required):
        if required[i] not in globals():
            return False
        i += 1

    return True


def _v3_backend_ready():

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


# V1 - AEROPORTS

def load_airports():
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

    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    PlotAirports(airports)


def map_airports():

    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    kml_path = MapAirports(airports)

    try:
        os.startfile(kml_path)
    except:
        messagebox.showinfo("OK", "KML created at:\n" + kml_path)


def save_schengen():

    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    err = SaveSchengenAirports(airports, "SchengenAirports.txt")

    if err == -1:
        messagebox.showerror("Error", "File could not be saved")
    else:
        messagebox.showinfo("OK", "SchengenAirports.txt saved")


# V2 - ARRIBADES I VOLS

def LoadArrivalsButton():

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

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotArrivals(aircrafts)


def PlotAirlinesButton():

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotAirlines(aircrafts)


def PlotFlightsTypeButton():

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotFlightsType(aircrafts)


def MapFlightsButton():

    global airports

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

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

    global airports

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

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


# V3 - GESTIÓ DE GATES

def BuildLEBLStructureButton():

    global bcn         # fem servir bcn, que està fora de la funció

    if not _v3_backend_ready():       # si no esta preparada la versio 3, avisa de l'error
        messagebox.showerror("Error", "Version 3 backend is not ready")
        return

    bcn = LoadAirportStructure("LEBL.txt")   #llegim el fitxer i guardem la informació

    if bcn == -1:               # si NO s'ha pogut carregar bé, mostra error
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    messagebox.showinfo(        # si SI s'ha pogut, mostra OK i quantes termianls te l'aeroport
        "OK",
        "LEBL structure loaded with " + str(len(bcn.terminals)) + " terminals"
    )


def AssignGatesButton():

    global bcn
    global aircrafts

    if len(aircrafts) == 0:             # si NO hi ha cap avió carregat, avisa
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    bcn = LoadAirportStructure("LEBL.txt")          # guardem informació carregada

    if bcn == -1:                                   # si NO tenim res carregat, avisa error
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    assigned = 0            # comptador d'aviosna assignats
    failed = 0              # comptador avons que no s'han pogut assignar

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
        "Assigned: " + str(assigned) +
        "\nNot assigned: " + str(failed)
    )


def ShowGateOccupancyButton():

    global bcn

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    occupancy = GateOccupancy(bcn)

    if len(occupancy) == 0:
        messagebox.showinfo("Info", "No gate occupancy data available")
        return

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

        text += terminal + " | " + area + " | " + gate + " | " + status + "\n"

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


# SORTIDA DEL PROGRAMA

def exit_program():
    window.destroy()


# INTERFÍCIE GRÀFICA

window = Tk()
window.title("Airport Manager")
window.geometry("620x760")


# INPUTS V1

Label(window, text="ICAO Code").pack()
entry_code = Entry(window)
entry_code.pack()

Label(window, text="Latitude").pack()
entry_lat = Entry(window)
entry_lat.pack()

Label(window, text="Longitude").pack()
entry_lon = Entry(window)
entry_lon.pack()


# FRAME V1
frame_v1 = Frame(window)
frame_v1.pack(pady=10)

Button(frame_v1, text="Load Airports", width=28, command=load_airports).grid(row=0, column=0)
Button(frame_v1, text="Add Airport", width=28, command=add_airport).grid(row=0, column=1)
Button(frame_v1, text="Remove Airport", width=28, command=remove_airport).grid(row=1, column=0)
Button(frame_v1, text="Plot Airports", width=28, command=plot_airports).grid(row=1, column=1)
Button(frame_v1, text="Map Airports", width=28, command=map_airports).grid(row=2, column=0)
Button(frame_v1, text="Save Schengen", width=28, command=save_schengen).grid(row=2, column=1)


# FRAME V2
frame_v2 = Frame(window)
frame_v2.pack(pady=10)

Button(frame_v2, text="Load Arrivals", width=28, command=LoadArrivalsButton).grid(row=0, column=0)
Button(frame_v2, text="Save Flights", width=28, command=SaveFlightsButton).grid(row=0, column=1)
Button(frame_v2, text="Plot Arrivals", width=28, command=PlotArrivalsButton).grid(row=1, column=0)
Button(frame_v2, text="Plot Airlines", width=28, command=PlotAirlinesButton).grid(row=1, column=1)
Button(frame_v2, text="Plot Type", width=28, command=PlotFlightsTypeButton).grid(row=2, column=0)
Button(frame_v2, text="Map Flights", width=28, command=MapFlightsButton).grid(row=2, column=1)
Button(frame_v2, text="Long Distance", width=28, command=MapLongDistanceButton).grid(row=3, column=0, columnspan=2)


# FRAME V3
frame_v3 = Frame(window)
frame_v3.pack(pady=10)

Button(frame_v3, text="Build LEBL", width=28, command=BuildLEBLStructureButton).grid(row=0, column=0)
Button(frame_v3, text="Assign Gates", width=28, command=AssignGatesButton).grid(row=0, column=1)
Button(frame_v3, text="Gate Occupancy", width=28, command=ShowGateOccupancyButton).grid(row=1, column=0, columnspan=2)


# EXIT
Button(window, text="Exit", width=28, command=exit_program).pack(pady=10)

window.mainloop()