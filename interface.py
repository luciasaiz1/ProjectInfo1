from tkinter import *
from tkinter import ttk
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
    print("Number of airports:", len(airports))


def add_airport():

    global airports

    code = entry_code.get()

    lat_text = entry_lat.get()

    lon_text = entry_lon.get()

    if code == "" or lat_text == "" or lon_text == "":
        print("Error: missing data")
        return

    lat = float(lat_text)

    lon = float(lon_text)

    airport = Airport(code, lat, lon)

    SetSchengen(airport)

    AddAirport(airports, airport)

    print("Airport added")


def remove_airport():

    code = entry_code.get()

    result = RemoveAirport(airports, code)

    if result == 0:
        print("Airport removed")
    else:
        print("Airport not found")


def plot_airports():

    if len(airports) == 0:
        print("Error: no airports loaded")
        return

    PlotAirports(airports)


def map_airports():

    if len(airports) == 0:
        print("Error: no airports loaded")
        return

    MapAirports(airports)

    print("File AirportsMap.kml created")
    print("Open it with Google Earth")


def save_schengen():

    result = SaveSchengenAirports(
        airports,
        "SchengenAirports.txt"
    )

    if result == 0:
        print("File saved")
    else:
        print("Error: no Schengen airports")


def exit_program():

    window.destroy()


# MAIN WINDOW

window = Tk()

window.title("Airport Manager")

window.geometry("500x400")


# CREATE TABS

notebook = ttk.Notebook(window)

tab_controls = Frame(notebook)

tab_plot = Frame(notebook)

tab_map = Frame(notebook)


notebook.add(tab_controls, text="Controls")

notebook.add(tab_plot, text="Plot")

notebook.add(tab_map, text="Map")


notebook.pack(expand=1, fill="both")


# TAB 1 — CONTROLS

Label(tab_controls, text="ICAO Code").pack()

entry_code = Entry(tab_controls)

entry_code.pack()


Label(tab_controls, text="Latitude").pack()

entry_lat = Entry(tab_controls)

entry_lat.pack()


Label(tab_controls, text="Longitude").pack()

entry_lon = Entry(tab_controls)

entry_lon.pack()


Button(
    tab_controls,
    text="Load Airports",
    command=load_airports
).pack(pady=2)


Button(
    tab_controls,
    text="Add Airport",
    command=add_airport
).pack(pady=2)


Button(
    tab_controls,
    text="Remove Airport",
    command=remove_airport
).pack(pady=2)


Button(
    tab_controls,
    text="Plot Airports",
    command=plot_airports
).pack(pady=2)


Button(
    tab_controls,
    text="Map Airports",
    command=map_airports
).pack(pady=2)


Button(
    tab_controls,
    text="Save Schengen Airports",
    command=save_schengen
).pack(pady=2)


Button(
    tab_controls,
    text="Exit",
    command=exit_program
).pack(pady=2)


# TAB 2 — PLOT

Button(
    tab_plot,
    text="Show Plot",
    command=plot_airports
).pack(pady=40)


# TAB 3 — MAP

Button(
    tab_map,
    text="Create Map for Google Earth",
    command=map_airports
).pack(pady=40)


window.mainloop()

file.close()

print("AirportsMap.kml created")

import os
os.startfile("AirportsMap.kml")
