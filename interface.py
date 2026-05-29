from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os
import copy

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import *
from aircraft import *
from LEBL import *


# ============================================================
# VARIABLES GLOBALS
# Guardem dades carregades perquè els botons puguin compartir informació.
# ============================================================
airports = []
arrivals = []
departures = []
merged = []
bcn = None
current_plot_widget = None


# ============================================================
# setup_style
# Dona un aspecte més professional a la interfície.
# Ho fem per fer la V4 més clara i presentable.
# ============================================================
def setup_style():

    style = ttk.Style()
    style.theme_use("clam")

    primary = "#1E88E5"
    primary_dark = "#1565C0"
    bg = "#ECEFF1"
    text = "#263238"

    window.configure(bg=bg)

    style.configure(
        "Modern.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=9,
        foreground="white",
        background=primary,
        borderwidth=0
    )

    style.map(
        "Modern.TButton",
        background=[("active", primary_dark)]
    )

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 20, "bold"),
        background=bg,
        foreground=text,
        padding=10
    )

    style.configure(
        "Section.TLabel",
        font=("Segoe UI", 13, "bold"),
        background=bg,
        foreground=primary,
        padding=5
    )

    style.configure(
        "Text.TLabel",
        font=("Segoe UI", 10),
        background=bg,
        foreground=text
    )


# ============================================================
# create_button
# Evita repetir codi cada vegada que fem un botó.
# ============================================================
def create_button(parent, text, command):
    return ttk.Button(parent, text=text, command=command, style="Modern.TButton")


# ============================================================
# clear_visual_panel
# Esborra el panell dret abans de posar un nou gràfic o text.
# ============================================================
def clear_visual_panel():

    global current_plot_widget

    for widget in visual_area.winfo_children():
        widget.destroy()

    current_plot_widget = None


# ============================================================
# show_text_in_panel
# Mostra resultats textuals al panell principal.
# Això evita obrir massa finestres separades.
# ============================================================
def show_text_in_panel(text):

    clear_visual_panel()

    txt = Text(visual_area, wrap="word", font=("Consolas", 10))
    txt.pack(fill=BOTH, expand=True)
    txt.insert("1.0", text)
    txt.config(state=DISABLED)


# ============================================================
# show_plot_in_panel
# Mostra una figura de matplotlib dins la GUI.
# Aquesta és una millora visual important de la V4.
# ============================================================
def show_plot_in_panel(fig):

    global current_plot_widget

    clear_visual_panel()

    canvas = FigureCanvasTkAgg(fig, master=visual_area)
    canvas.draw()

    current_plot_widget = canvas.get_tk_widget()
    current_plot_widget.pack(fill=BOTH, expand=True)


# ============================================================
# ensure_airports_loaded
# Carrega aeroports si encara no s'han carregat.
# Ho fem per no obligar l'usuari a seguir sempre un ordre perfecte.
# ============================================================
def ensure_airports_loaded():

    global airports

    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")

        for ap in airports:
            SetSchengen(ap)

    return len(airports) > 0


# ============================================================
# V1 — AIRPORT MANAGEMENT
# ============================================================
def load_airports():

    global airports

    airports = LoadAirports("Airports.txt")

    if len(airports) == 0:
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    for ap in airports:
        SetSchengen(ap)

    messagebox.showinfo("OK", f"Loaded {len(airports)} airports")
    show_text_in_panel(f"Airports loaded: {len(airports)}")


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

    err = AddAirport(airports, airport)

    if err == -1:
        messagebox.showerror("Error", "Airport already exists")
    else:
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


def save_schengen():

    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    err = SaveSchengenAirports(airports, "SchengenAirports.txt")

    if err == -1:
        messagebox.showerror("Error", "File could not be saved")
    else:
        messagebox.showinfo("OK", "SchengenAirports.txt saved")


def map_airports():

    if not ensure_airports_loaded():
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    kml_path = MapAirports(airports)

    if kml_path == -1:
        messagebox.showerror("Error", "KML could not be created")
        return

    try:
        os.startfile(kml_path)
    except:
        messagebox.showinfo("OK", f"KML created at:\n{kml_path}")

    show_text_in_panel("AirportsMap.kml created.\nOpen it in Google Earth if it did not open automatically.")


# ============================================================
# V2/V4 — FLIGHT MANAGEMENT
# ============================================================
def LoadArrivalsButton():

    global arrivals

    filename = filedialog.askopenfilename(
        title="Select arrivals file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    arrivals = LoadArrivals(filename)

    if len(arrivals) == 0:
        messagebox.showerror("Error", "No arrivals loaded")
    else:
        messagebox.showinfo("OK", f"Loaded {len(arrivals)} arrivals")
        show_text_in_panel(f"Arrivals loaded: {len(arrivals)}")


def LoadDeparturesButton():

    global departures

    filename = filedialog.askopenfilename(
        title="Select departures file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    departures, err = LoadDepartures(filename)

    if err == -1:
        messagebox.showerror("Error", "Departures file could not be loaded")
    else:
        messagebox.showinfo("OK", f"Loaded {len(departures)} departures")
        show_text_in_panel(f"Departures loaded: {len(departures)}")


def MergeMovementsButton():

    global merged

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    if len(departures) == 0:
        messagebox.showwarning("Warning", "Load departures first")
        return

    merged = MergeMovements(arrivals, departures)

    night = NightAircraft(merged)

    messagebox.showinfo("OK", f"Merged movements: {len(merged)}")
    show_text_in_panel(
        "MERGE COMPLETED\n\n" +
        f"Arrivals: {len(arrivals)}\n" +
        f"Departures: {len(departures)}\n" +
        f"Merged movements: {len(merged)}\n" +
        f"Night aircraft: {len(night)}\n"
    )


def ShowMovementsButton():

    if len(merged) == 0:
        messagebox.showwarning("Warning", "No merged movements")
        return

    text = "AIRCRAFT | ORIGIN | ARRIVAL | DESTINATION | DEPARTURE | AIRLINE\n"
    text += "-" * 75 + "\n"

    for a in merged:
        text += f"{a.aircraft_id} | {a.origin or '-'} | {a.arrival or '-'} | {a.destination or '-'} | {a.departure or '-'} | {a.airline}\n"

    show_text_in_panel(text)


def SaveFlightsButton():

    if len(merged) == 0:
        messagebox.showwarning("Warning", "No merged movements to save")
        return

    filename = filedialog.asksaveasfilename(
        title="Save flights file",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    err = SaveFlights(merged, filename)

    if err == -1:
        messagebox.showerror("Error", "Flights could not be saved")
    else:
        messagebox.showinfo("OK", "Flights saved correctly")


# ============================================================
# V3/V4 — GATE MANAGEMENT
# ============================================================
def BuildLEBLStructureButton():

    global bcn

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    total_gates = 0

    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            total_gates += len(area.gates)

    messagebox.showinfo("OK", f"LEBL structure loaded with {len(bcn.terminals)} terminals")
    show_text_in_panel(
        "LEBL STRUCTURE LOADED\n\n" +
        f"Airport: {bcn.code}\n" +
        f"Terminals: {len(bcn.terminals)}\n" +
        f"Total gates: {total_gates}\n"
    )


def AssignGatesButton():

    global bcn

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    night_assigned, night_failed = AssignNightGates(bcn, merged)

    assigned = night_assigned
    failed = night_failed

    # Assignació estàtica per obtenir una foto inicial de portes ocupades
    for a in merged:
        if a.arrival != "":
            gate_name = AssignGate(bcn, a)
            if gate_name == -1:
                failed += 1
            else:
                assigned += 1

    messagebox.showinfo(
        "Gate Assignment",
        f"Assigned: {assigned}\nNot assigned: {failed}"
    )

    ShowGateOccupancyButton()


def ShowGateOccupancyButton():

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    occupancy = GateOccupancy(bcn)

    text = "TERMINAL | AREA | GATE | STATUS\n"
    text += "-" * 60 + "\n"

    for terminal, area, gate, occupied, aircraft_id in occupancy:
        status = "Occupied by " + aircraft_id if occupied else "Free"
        text += f"{terminal} | {area} | {gate} | {status}\n"

    show_text_in_panel(text)


# ============================================================
# V4 — SIMULATION, DASHBOARD I EXPORTACIÓ
# ============================================================
def SimulateHourButton():

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    time = entry_hour.get().strip()

    if _parse_time(time) is None:
        messagebox.showerror("Error", "Write a valid hour as hh:mm")
        return

    # Fem una còpia per simular sense destruir l'estat real
    bcn_copy = copy.deepcopy(bcn)
    AssignNightGates(bcn_copy, merged)

    target_hour = int(time.split(":")[0])
    rejected_total = 0

    for h in range(target_hour + 1):
        rejected_total += AssignGatesAtTime(bcn_copy, merged, f"{h:02d}:00")

    counts = CountOccupiedByTerminal(bcn_copy)
    occ = GateOccupancy(bcn_copy)

    text = f"SIMULATION AT {time}\n"
    text += "-" * 50 + "\n"

    for terminal in counts:
        text += f"Occupied gates {terminal}: {counts[terminal]}\n"

    text += f"Rejected until this hour: {rejected_total}\n\n"
    text += "CURRENT OCCUPANCY\n"
    text += "-" * 50 + "\n"

    for terminal, area, gate, occupied, aircraft_id in occ:
        if occupied:
            text += f"{terminal} | {area} | {gate} | {aircraft_id}\n"

    show_text_in_panel(text)


def SimulateDayButton():

    if bcn is None or bcn == -1:
        messagebox.showerror("Error", "Load LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(7, 5))
    PlotDayOccupancy(bcn, merged, fig=fig)
    show_plot_in_panel(fig)


def DashboardButton():

    if bcn is None or bcn == -1:
        messagebox.showerror("Error", "Load LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    data = DashboardData(bcn, merged)

    text = "FINAL OPERATIONS DASHBOARD\n"
    text += "=" * 50 + "\n\n"
    text += f"Total arrivals: {data['arrivals']}\n"
    text += f"Total departures: {data['departures']}\n"
    text += f"Merged movements: {data['movements']}\n"
    text += f"Night aircraft assigned: {data['night_aircraft']}\n"
    text += f"Maximum gates occupied: {data['max_occupied']}\n"
    text += f"Peak congestion hour: {data['max_hour']}\n"
    text += f"Not assigned during simulation: {data['not_assigned']}\n\n"
    text += "This dashboard summarizes the full operational day."

    show_text_in_panel(text)


def ExportGateAssignmentsButton():

    if bcn is None or bcn == -1:
        messagebox.showerror("Error", "Load or assign gates first")
        return

    filename = filedialog.asksaveasfilename(
        title="Save gate assignments",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    err = SaveGateAssignments(bcn, filename)

    if err == -1:
        messagebox.showerror("Error", "Gate assignments could not be saved")
    else:
        messagebox.showinfo("OK", "Gate assignments saved")


def PlotArrivalsButton():

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7, 5))
    PlotArrivals(arrivals, fig=fig)
    show_plot_in_panel(fig)


def PlotAirlinesButton():

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7, 5))
    PlotAirlines(arrivals, fig=fig)
    show_plot_in_panel(fig)


def PlotFlightsTypeButton():

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7, 5))
    PlotFlightsType(arrivals, fig=fig)
    show_plot_in_panel(fig)


def MapFlightsButton():

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    if not ensure_airports_loaded():
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    MapFlights(arrivals, airports)
    show_text_in_panel("FlightsMap.kml generated.\nOpen it in Google Earth.")


def MapLongDistanceButton():

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    if not ensure_airports_loaded():
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    long_distance = LongDistanceArrivals(arrivals)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance arrivals found")
        return

    MapFlights(long_distance, airports)
    show_text_in_panel(f"Long-distance flights mapped: {len(long_distance)}")


# ============================================================
# INTERFÍCIE — 3 COLUMNES + PANELL VISUAL
# ============================================================
window = Tk()
window.title("Airport Manager — Professional Edition")
window.geometry("1400x900")
window.configure(bg="#ECEFF1")

setup_style()

ttk.Label(window, text="Airport Operations Manager", style="Title.TLabel").pack(pady=15)

main_frame = Frame(window, bg="#ECEFF1")
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=1)
main_frame.columnconfigure(3, weight=2)


# ============================================================
# COLUMN 1 — AIRPORT MANAGEMENT
# ============================================================
col1 = Frame(main_frame, bg="#ECEFF1")
col1.grid(row=0, column=0, sticky="nsew", padx=15)

ttk.Label(col1, text="Airport Management", style="Section.TLabel").pack(pady=10)

input_frame = Frame(col1, bg="#ECEFF1")
input_frame.pack(pady=5)

ttk.Label(input_frame, text="ICAO Code:", style="Text.TLabel").grid(row=0, column=0, sticky="e")
entry_code = ttk.Entry(input_frame, width=18)
entry_code.grid(row=0, column=1, pady=3)

ttk.Label(input_frame, text="Latitude:", style="Text.TLabel").grid(row=1, column=0, sticky="e")
entry_lat = ttk.Entry(input_frame, width=18)
entry_lat.grid(row=1, column=1, pady=3)

ttk.Label(input_frame, text="Longitude:", style="Text.TLabel").grid(row=2, column=0, sticky="e")
entry_lon = ttk.Entry(input_frame, width=18)
entry_lon.grid(row=2, column=1, pady=3)

create_button(col1, "Load Airports", load_airports).pack(pady=5, fill=X)
create_button(col1, "Add Airport", add_airport).pack(pady=5, fill=X)
create_button(col1, "Remove Airport", remove_airport).pack(pady=5, fill=X)
create_button(col1, "Save Schengen", save_schengen).pack(pady=5, fill=X)
create_button(col1, "Map Airports", map_airports).pack(pady=5, fill=X)


# ============================================================
# COLUMN 2 — FLIGHT AND GATE MANAGEMENT
# ============================================================
col2 = Frame(main_frame, bg="#ECEFF1")
col2.grid(row=0, column=1, sticky="nsew", padx=15)

ttk.Label(col2, text="Flight Management", style="Section.TLabel").pack(pady=10)

create_button(col2, "Load Arrivals", LoadArrivalsButton).pack(pady=5, fill=X)
create_button(col2, "Load Departures", LoadDeparturesButton).pack(pady=5, fill=X)
create_button(col2, "Merge Movements", MergeMovementsButton).pack(pady=5, fill=X)
create_button(col2, "Show Movements", ShowMovementsButton).pack(pady=5, fill=X)
create_button(col2, "Save Flights", SaveFlightsButton).pack(pady=5, fill=X)

ttk.Label(col2, text="Gate Assignment", style="Section.TLabel").pack(pady=10)

create_button(col2, "Build LEBL Structure", BuildLEBLStructureButton).pack(pady=5, fill=X)
create_button(col2, "Assign Gates", AssignGatesButton).pack(pady=5, fill=X)
create_button(col2, "Gate Occupancy", ShowGateOccupancyButton).pack(pady=5, fill=X)
create_button(col2, "Export Gate Assignments", ExportGateAssignmentsButton).pack(pady=5, fill=X)


# ============================================================
# COLUMN 3 — VISUALIZATION AND SIMULATION
# ============================================================
col3 = Frame(main_frame, bg="#ECEFF1")
col3.grid(row=0, column=2, sticky="nsew", padx=15)

ttk.Label(col3, text="Maps & Charts", style="Section.TLabel").pack(pady=10)

create_button(col3, "Map Flights", MapFlightsButton).pack(pady=5, fill=X)
create_button(col3, "Long Distance Flights", MapLongDistanceButton).pack(pady=5, fill=X)
create_button(col3, "Plot Arrivals", PlotArrivalsButton).pack(pady=5, fill=X)
create_button(col3, "Plot Airlines", PlotAirlinesButton).pack(pady=5, fill=X)
create_button(col3, "Plot Schengen", PlotFlightsTypeButton).pack(pady=5, fill=X)

ttk.Label(col3, text="Simulation", style="Section.TLabel").pack(pady=10)

hour_frame = Frame(col3, bg="#ECEFF1")
hour_frame.pack(pady=5, fill=X)

ttk.Label(hour_frame, text="Hour hh:mm:", style="Text.TLabel").pack(side=LEFT)
entry_hour = ttk.Entry(hour_frame, width=8)
entry_hour.insert(0, "08:00")
entry_hour.pack(side=LEFT, padx=5)

create_button(col3, "Simulate Hour", SimulateHourButton).pack(pady=5, fill=X)
create_button(col3, "Simulate Full Day", SimulateDayButton).pack(pady=5, fill=X)
create_button(col3, "Final Dashboard", DashboardButton).pack(pady=5, fill=X)


# ============================================================
# COLUMN 4 — VISUAL PANEL
# ============================================================
visual_panel = Frame(main_frame, bg="white", relief="solid", bd=1)
visual_panel.grid(row=0, column=3, sticky="nsew", padx=15, pady=10)

ttk.Label(visual_panel, text="Visualization Panel", style="Section.TLabel").pack(pady=10)

visual_area = Frame(visual_panel, bg="white")
visual_area.pack(fill=BOTH, expand=True, padx=10, pady=10)

show_text_in_panel(
    "Ready.\n\nRecommended V4 workflow:\n"
    "1) Load Arrivals\n"
    "2) Load Departures\n"
    "3) Merge Movements\n"
    "4) Build LEBL Structure\n"
    "5) Simulate Full Day or Final Dashboard"
)

create_button(window, "Exit", window.destroy).pack(pady=20)

window.mainloop()