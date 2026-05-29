from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os
import copy

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import *
from aircraft import *
from aircraft import _parse_time
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

# Variables per fer la simulació física en directe
live_bcn = None
live_hour = 0
live_running = False


# ============================================================
# setup_style
# Dona un aspecte més professional a la interfície.
# Ho fem per fer la V4 més clara i presentable.
# ============================================================
def setup_style():

    style = ttk.Style()         #centralitzem disseny de la interface
    style.theme_use("clam")

    primary = "#1E88E5"         #colors principals
    primary_dark = "#1565C0"
    bg = "#ECEFF1"
    text = "#263238"

    window.configure(bg=bg)

    style.configure(            #disseny dels botons
        "Modern.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=9,
        foreground="white",
        background=primary,
        borderwidth=0
    )

    style.map(                          #canvi color quan ratolí de l'usuari pasa per sobre
        "Modern.TButton",
        background=[("active", primary_dark)]
    )
#canvis de separacio de titols, mida, i mida de titols
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
def create_button(parent, text, command):        #funcio comuna per a crear botons
    return ttk.Button(parent, text=text, command=command, style="Modern.TButton")


# ============================================================
# clear_visual_panel
# Esborra el panell dret abans de posar un nou gràfic, text o mapa.
# ============================================================
def clear_visual_panel():

    global current_plot_widget

    for widget in visual_area.winfo_children():     # Netegem aquesta zona abans de mostrar una nova gràfica o resultat
        widget.destroy()

    current_plot_widget = None          #Reiniciem per evitar treballar amb gràfiques antigues


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
    text += "-" * 90 + "\n"

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


# ============================================================
# AssignGatesButton
# Crea l'estat inicial de gates.
# IMPORTANT: no assignem tots els vols del dia aquí,
# perquè això ompliria gates sense alliberar-les.
# Només assignem avions nocturns, que ja estan a LEBL a les 00:00.
# La resta es fa amb Simulate Hour o Start Live Gate Map.
# ============================================================
def AssignGatesButton():

    global bcn

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    # Assignem només avions nocturns
    night_assigned, night_failed = AssignNightGates(bcn, merged)

    messagebox.showinfo(
        "Initial Gate Assignment",
        "Initial gate state created.\n\n" +
        "Night aircraft assigned: " + str(night_assigned) + "\n" +
        "Night aircraft not assigned: " + str(night_failed) + "\n\n" +
        "Use Simulate Hour or Start Live Gate Map for the full day."
    )

    DrawPhysicalGateMap(bcn, "00:00 initial state", night_failed)
def ShowGateOccupancyButton():

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    occupancy = GateOccupancy(bcn)

    text = "TERMINAL | AREA | GATE | STATUS\n"
    text += "-" * 70 + "\n"

    for terminal, area, gate, occupied, aircraft_id in occupancy:
        status = "Occupied by " + aircraft_id if occupied else "Free"
        text += f"{terminal} | {area} | {gate} | {status}\n"

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


# ============================================================
# DRAW PHYSICAL GATE MAP
# Dibuixa l'aeroport com si fos físic:
# terminal, boarding areas i gates lliures/ocupades.
# Verd = gate lliure.
# Vermell = gate ocupada.
# ============================================================
def DrawPhysicalGateMap(bcn_state, hour_label="", rejected=0):

    clear_visual_panel()

    container = Frame(visual_area, bg="white")
    container.pack(fill=BOTH, expand=True)

    v_scroll = Scrollbar(container, orient=VERTICAL)
    h_scroll = Scrollbar(container, orient=HORIZONTAL)

    canvas = Canvas(
        container,
        bg="white",
        yscrollcommand=v_scroll.set,
        xscrollcommand=h_scroll.set
    )

    v_scroll.config(command=canvas.yview)
    h_scroll.config(command=canvas.xview)

    v_scroll.pack(side=RIGHT, fill=Y)
    h_scroll.pack(side=BOTTOM, fill=X)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    title = "LIVE GATE MANAGEMENT"

    if hour_label != "":
        title += " — " + hour_label

    canvas.create_text(
        40, 25,
        text=title,
        anchor="w",
        font=("Segoe UI", 18, "bold"),
        fill="#263238"
    )

    # Llegenda
    canvas.create_rectangle(40, 55, 58, 73, fill="#43A047", outline="black")
    canvas.create_text(65, 64, text="Free gate", anchor="w", font=("Segoe UI", 10))

    canvas.create_rectangle(160, 55, 178, 73, fill="#E53935", outline="black")
    canvas.create_text(185, 64, text="Occupied gate", anchor="w", font=("Segoe UI", 10))

    canvas.create_rectangle(310, 55, 328, 73, fill="#0E5A70", outline="black")
    canvas.create_text(335, 64, text="Terminal / Boarding Area", anchor="w", font=("Segoe UI", 10))

    canvas.create_text(
        40, 90,
        text="Rejected aircraft this hour: " + str(rejected),
        anchor="w",
        font=("Segoe UI", 11, "bold"),
        fill="#B71C1C"
    )

    start_x = 60
    start_y = 140

    area_gap = 165
    gate_size = 11
    gate_spacing = 17

    page_width = 1400
    page_height = 900

    terminal_index = 0

    for terminal in bcn_state.terminals:

        terminal_y = start_y + terminal_index * 560

        max_rows = 0

        for area in terminal.boarding_areas:
            rows = (len(area.gates) + 1) // 2
            if rows > max_rows:
                max_rows = rows

        pier_height = max(260, max_rows * gate_spacing + 70)
        corridor_width = max(900, len(terminal.boarding_areas) * area_gap + 80)

        # Nom del terminal
        canvas.create_text(
            start_x,
            terminal_y - 35,
            text="Terminal " + terminal.name,
            anchor="w",
            font=("Segoe UI", 16, "bold"),
            fill="#263238"
        )

        # Passadís principal
        canvas.create_rectangle(
            start_x,
            terminal_y,
            start_x + corridor_width,
            terminal_y + 28,
            fill="#0E5A70",
            outline="#083A47"
        )

        area_index = 0

        for area in terminal.boarding_areas:

            pier_x = start_x + 50 + area_index * area_gap
            pier_y = terminal_y + 28

            # Boarding area vertical
            canvas.create_rectangle(
                pier_x,
                pier_y,
                pier_x + 28,
                pier_y + pier_height,
                fill="#0E5A70",
                outline="#083A47"
            )

            canvas.create_text(
                pier_x + 14,
                pier_y + pier_height + 25,
                text=terminal.name + "BA" + area.name,
                font=("Segoe UI", 11, "bold"),
                fill="#263238"
            )

            canvas.create_text(
                pier_x + 14,
                pier_y + pier_height + 43,
                text=area.area_type,
                font=("Segoe UI", 8),
                fill="#546E7A"
            )

            gate_index = 0

            for gate in area.gates:

                row = gate_index // 2
                left_side = gate_index % 2 == 0

                gate_y = pier_y + 40 + row * gate_spacing

                if left_side:
                    gate_x = pier_x - 48

                    canvas.create_line(
                        gate_x + gate_size,
                        gate_y + gate_size // 2,
                        pier_x,
                        gate_y + gate_size // 2,
                        fill="#263238",
                        width=2
                    )

                else:
                    gate_x = pier_x + 65

                    canvas.create_line(
                        pier_x + 28,
                        gate_y + gate_size // 2,
                        gate_x,
                        gate_y + gate_size // 2,
                        fill="#263238",
                        width=2
                    )

                if gate.occupied:
                    color = "#E53935"
                else:
                    color = "#43A047"

                canvas.create_rectangle(
                    gate_x,
                    gate_y,
                    gate_x + gate_size,
                    gate_y + gate_size,
                    fill=color,
                    outline="black"
                )

                # Mostrem aircraft_id si està ocupada
                if gate.occupied:
                    if left_side:
                        text_x = gate_x - 4
                        anchor = "e"
                    else:
                        text_x = gate_x + gate_size + 4
                        anchor = "w"

                    canvas.create_text(
                        text_x,
                        gate_y + gate_size // 2,
                        text=gate.aircraft_id,
                        anchor=anchor,
                        font=("Segoe UI", 6),
                        fill="#B71C1C"
                    )

                # Mostrem alguns números de gate per orientar-nos
                if gate_index % 8 == 0:
                    if left_side:
                        label_x = gate_x - 4
                        anchor = "e"
                    else:
                        label_x = gate_x + gate_size + 4
                        anchor = "w"

                    gate_number = gate.name.split("_G")[-1]

                    canvas.create_text(
                        label_x,
                        gate_y + gate_size + 7,
                        text=gate_number,
                        anchor=anchor,
                        font=("Segoe UI", 6),
                        fill="#455A64"
                    )

                gate_index += 1

            area_index += 1

        page_height = terminal_y + pier_height + 140
        terminal_index += 1

    canvas.config(scrollregion=(0, 0, page_width, page_height + 100))


# ============================================================
# PhysicalGateMapButton
# Mostra el mapa físic actual de gates.
# ============================================================
def PhysicalGateMapButton():

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    DrawPhysicalGateMap(bcn, "Current state", 0)


# ============================================================
# StartLiveGateMapButton
# Inicia una simulació visual en directe hora a hora.
# Cada 900 ms representa una hora del dia.
# ============================================================
def StartLiveGateMapButton():

    global live_bcn
    global live_hour
    global live_running

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    live_bcn = copy.deepcopy(bcn)

    # A les 00:00 ja hi ha avions nocturns ocupant gates
    AssignNightGates(live_bcn, merged)

    live_hour = 0
    live_running = True

    LiveGateStep()


# ============================================================
# StopLiveGateMapButton
# Atura l'animació del mapa de gates.
# ============================================================
def StopLiveGateMapButton():

    global live_running

    live_running = False
    show_text_in_panel("Live gate simulation stopped.")


# ============================================================
# LiveGateStep
# Fa avançar la simulació una hora.
# Allibera gates, assigna arribades i redibuixa el mapa físic.
# ============================================================
def LiveGateStep():

    global live_hour
    global live_running
    global live_bcn

    if not live_running:
        return

    if live_hour > 23:
        live_running = False
        DrawPhysicalGateMap(live_bcn, "End of day", 0)
        messagebox.showinfo("Simulation finished", "Full day live simulation completed")
        return

    time = f"{live_hour:02d}:00"

    rejected = AssignGatesAtTime(live_bcn, merged, time)

    DrawPhysicalGateMap(live_bcn, time, rejected)

    live_hour += 1

    window.after(900, LiveGateStep)


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

    bcn_copy = copy.deepcopy(bcn)

    # Assignem avions nocturns a les 00:00
    AssignNightGates(bcn_copy, merged)

    target_hour = int(time.split(":")[0])
    rejected_total = 0

    h = 0

    while h <= target_hour:
        rejected_total += AssignGatesAtTime(bcn_copy, merged, f"{h:02d}:00")
        h += 1

    DrawPhysicalGateMap(bcn_copy, time, rejected_total)


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


# ============================================================
# DashboardButton
# Mostra un resum final de tota la simulació.
# ============================================================
# ============================================================
# DashboardButton
# Mostra un resum final de tota la simulació.
# ============================================================
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
window.geometry("1500x900")
window.configure(bg="#ECEFF1")

setup_style()

ttk.Label(window, text="Airport Operations Manager", style="Title.TLabel").pack(pady=15)

main_frame = Frame(window, bg="#ECEFF1")
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=1)
main_frame.columnconfigure(3, weight=3)


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
create_button(col2, "Gate Occupancy Text", ShowGateOccupancyButton).pack(pady=5, fill=X)
create_button(col2, "Physical Gate Map", PhysicalGateMapButton).pack(pady=5, fill=X)
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
create_button(col3, "Start Live Gate Map", StartLiveGateMapButton).pack(pady=5, fill=X)
create_button(col3, "Stop Live Gate Map", StopLiveGateMapButton).pack(pady=5, fill=X)
create_button(col3, "Simulate Full Day Chart", SimulateDayButton).pack(pady=5, fill=X)
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
    "5) Physical Gate Map or Start Live Gate Map\n\n"
    "Green gates = free\n"
    "Red gates = occupied"
)

create_button(window, "Exit", window.destroy).pack(pady=15)

window.mainloop()