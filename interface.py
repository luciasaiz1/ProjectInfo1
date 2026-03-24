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


window.mainloop()