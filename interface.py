from tkinter import *
from airport import *

# GLOBAL LIST

airports = []


# FUNCTIONS

def load_airports():
    global airports
    airports = LoadAirports("Airports.txt")
    i = 0

    while i < len(airports):
        SetSchengen(airports[i])
        i = i + 1

    print("Airports loaded")
    print(len(airports))


def add_airport():
    global airports
    code = entry_code.get()
    lat = float(entry_lat.get())
    lon = float(entry_lon.get())
    airport = Airport(code, lat, lon)
    SetSchengen(airport)
    AddAirport(airports, airport)
    print("Airport added")


def remove_airport():
    global airports
    code = entry_code.get()
    RemoveAirport(airports, code)
    print("Airport removed")


def plot_airports():
    PlotAirports(airports)


def map_airports():
    MapAirports(airports)


def save_schengen():
    SaveSchengenAirports(airports, "SchengenAirports.txt")
    print("File saved")


def exit_program():
    window.destroy()


# WINDOW
window = Tk()
window.title("Airport Manager")
window.geometry("400x300")


# LABELS
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


# BUTTONS

button1 = Button(window, text="Load Airports", command=load_airports)
button1.pack()
button2 = Button(window, text="Add Airport", command=add_airport)
button2.pack()
button3 = Button(window, text="Remove Airport", command=remove_airport)
button3.pack()
button4 = Button(window, text="Plot Airports", command=plot_airports)
button4.pack()
button5 = Button(window, text="Map Airports", command=map_airports)
button5.pack()
button6 = Button(window, text="Save Schengen Airports", command=save_schengen)
button6.pack()
button7 = Button(window, text="Exit", command=exit_program)
button7.pack()


from tkinter import *
from tkinter import filedialog, messagebox

from airports import *
aircrafts = []
def LoadArrivalsButton():
    global aircrafts

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
    global aircrafts

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotArrivals(aircrafts)


def PlotAirlinesButton():
    global aircrafts

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotAirlines(aircrafts)


def PlotFlightsTypeButton():
    global aircrafts

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    PlotFlightsType(aircrafts)


def MapFlightsButton():
    global aircrafts

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    MapFlights(aircrafts)


def MapLongDistanceButton():
    global aircrafts

    if len(aircrafts) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    long_distance = LongDistanceArrivals(aircrafts)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance arrivals found")
        return

    MapFlights(long_distance)

frame_v2 = Frame(root)
frame_v2.pack(pady=10)

Button(frame_v2, text="Load Arrivals", width=28, command=LoadArrivalsButton).grid(row=0, column=0, padx=5, pady=5)
Button(frame_v2, text="Save Flights", width=28, command=SaveFlightsButton).grid(row=0, column=1, padx=5, pady=5)

Button(frame_v2, text="Plot Arrivals / Hour", width=28, command=PlotArrivalsButton).grid(row=1, column=0, padx=5, pady=5)
Button(frame_v2, text="Plot Flights / Airline", width=28, command=PlotAirlinesButton).grid(row=1, column=1, padx=5, pady=5)

Button(frame_v2, text="Plot Schengen / Non-Schengen", width=28, command=PlotFlightsTypeButton).grid(row=2, column=0, padx=5, pady=5)
Button(frame_v2, text="Map All Flights", width=28, command=MapFlightsButton).grid(row=2, column=1, padx=5, pady=5)

Button(frame_v2, text="Map Long-Distance Flights", width=28, command=MapLongDistanceButton).grid(row=3, column=0, columnspan=2, padx=5, pady=5)