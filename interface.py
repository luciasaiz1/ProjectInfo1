from tkinter import *
from tkinter import messagebox, filedialog
import os
from airport import *

# GLOBAL LISTS
airports = []
aircrafts = []


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


# =========================
# VERSION 1 FUNCTIONS
# =========================

def load_airports():
    global airports

    airports = LoadAirports("Airports.txt")

    if len(airports) == 0:
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        i = i + 1

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


def exit_program():
    window.destroy()


# =========================
# VERSION 2 FUNCTIONS
# =========================

def LoadArrivalsButton():
    global aircrafts

    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
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
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
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
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotArrivals(aircrafts)


def PlotAirlinesButton():
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotAirlines(aircrafts)


def PlotFlightsTypeButton():
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotFlightsType(aircrafts)


def MapFlightsButton():
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    MapFlights(aircrafts)


def MapLongDistanceButton():
    if not _v2_backend_ready():
        messagebox.showerror("Error", "Version 2 flight functions are not implemented in the project yet")
        return

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    long_distance = LongDistanceArrivals(aircrafts)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance arrivals found")
        return

    MapFlights(long_distance)


# =========================
# WINDOW
# =========================
window = Tk()
window.title("Airport Manager")
window.geometry("520x560")

# LABELS AND ENTRIES
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
frame_v1 = Frame(window)
frame_v1.pack(pady=10)

button1 = Button(frame_v1, text="Load Airports", width=28, command=load_airports)
button1.grid(row=0, column=0, padx=5, pady=5)
button2 = Button(frame_v1, text="Add Airport", width=28, command=add_airport)
button2.grid(row=0, column=1, padx=5, pady=5)
button3 = Button(frame_v1, text="Remove Airport", width=28, command=remove_airport)
button3.grid(row=1, column=0, padx=5, pady=5)
button4 = Button(frame_v1, text="Plot Airports", width=28, command=plot_airports)
button4.grid(row=1, column=1, padx=5, pady=5)
button5 = Button(frame_v1, text="Map Airports", width=28, command=map_airports)
button5.grid(row=2, column=0, padx=5, pady=5)
button6 = Button(frame_v1, text="Save Schengen Airports", width=28, command=save_schengen)
button6.grid(row=2, column=1, padx=5, pady=5)

# VERSION 2 BUTTONS
frame_v2 = Frame(window)
frame_v2.pack(pady=10)

Button(frame_v2, text="Load Arrivals", width=28, command=LoadArrivalsButton).grid(row=0, column=0, padx=5, pady=5)
Button(frame_v2, text="Save Flights", width=28, command=SaveFlightsButton).grid(row=0, column=1, padx=5, pady=5)
Button(frame_v2, text="Plot Arrivals / Hour", width=28, command=PlotArrivalsButton).grid(row=1, column=0, padx=5, pady=5)
Button(frame_v2, text="Plot Flights / Airline", width=28, command=PlotAirlinesButton).grid(row=1, column=1, padx=5, pady=5)
Button(frame_v2, text="Plot Schengen / Non-Schengen", width=28, command=PlotFlightsTypeButton).grid(row=2, column=0, padx=5, pady=5)
Button(frame_v2, text="Map All Flights", width=28, command=MapFlightsButton).grid(row=2, column=1, padx=5, pady=5)
Button(frame_v2, text="Map Long-Distance Flights", width=28, command=MapLongDistanceButton).grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# EXIT
button_exit = Button(window, text="Exit", width=28, command=exit_program)
button_exit.pack(pady=10)

window.mainloop()