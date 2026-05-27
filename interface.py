from tkinter import *
from tkinter import ttk, messagebox, filedialog
import os

from airport import *
from aircraft import *
from LEBL import *
from LEBL import AssignGatesAtTime, PlotDayOccupancy

from matplotlib.backends.backend_agg import FigureCanvasAgg
from PIL import Image, ImageTk
import io


# ============================================================
# VARIABLES GLOBALS
# ============================================================

airports = []
arrivals = []
departures = []
merged = []
bcn = None

# ============================================================
# FUNCIÓ PER CREAR BOTONS MODERNS
# ============================================================

def create_button(parent, text, command):
    return ttk.Button(
        parent,
        text=text,
        command=command,
        style="Modern.TButton"
    )

# ============================================================
# CONFIGURACIÓ DE L'ESTIL MODERN
# ============================================================

def setup_style():

    style = ttk.Style()
    style.theme_use("clam")

    # Colors principals
    primary = "#1E88E5"
    primary_dark = "#1565C0"
    bg = "#F5F7FA"
    text = "#263238"

    # Fons general
    window.configure(bg=bg)

    # Estil de botons
    style.configure(
        "Modern.TButton",
        font=("Segoe UI", 11, "bold"),
        padding=10,
        foreground="white",
        background=primary,
        borderwidth=0
    )

    style.map(
        "Modern.TButton",
        background=[("active", primary_dark)]
    )

    # Estil de labels
    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 16, "bold"),
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

def show_plot_in_panel(fig):
    global visual_canvas, visual_panel

    # Convertir figura a imagen
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120)
    buf.seek(0)

    img = Image.open(buf)
    img_tk = ImageTk.PhotoImage(img)

    # Limpiar panel
    visual_canvas.delete("all")

    # Guardar referencia para evitar que Python borre la imagen
    visual_canvas.image = img_tk

    # Mostrar imagen centrada
    visual_canvas.create_image(
        visual_canvas.winfo_width() // 2,
        visual_canvas.winfo_height() // 2,
        image=img_tk,
        anchor="center"
    )

# ============================================================
# FUNCIONS BACKEND CHECK
# ============================================================

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
    return all(r in globals() for r in required)


def _v3_backend_ready():
    required = [
        "LoadAirportStructure",
        "AssignGate",
        "GateOccupancy",
        "SearchTerminal",
        "IsAirlineInTerminal"
    ]
    return all(r in globals() for r in required)


# ============================================================
# V1 - AEROPORTS
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
        messagebox.showinfo("OK", f"KML created at:\n{kml_path}")


def save_schengen():
    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    err = SaveSchengenAirports(airports, "SchengenAirports.txt")

    if err == -1:
        messagebox.showerror("Error", "File could not be saved")
    else:
        messagebox.showinfo("OK", "SchengenAirports.txt saved")


# ============================================================
# V2 - ARRIVALS I VOLS
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


def MergeMovementsButton():
    global merged

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    if len(departures) == 0:
        messagebox.showwarning("Warning", "Load departures first")
        return

    merged = MergeMovements(arrivals, departures)

    messagebox.showinfo("OK", f"Merged movements: {len(merged)}")


def ShowMovementsButton():
    global merged

    if len(merged) == 0:
        messagebox.showwarning("Warning", "No merged movements")
        return

    win = Toplevel(window)
    win.title("Merged Movements")
    win.geometry("700x500")

    scrollbar = Scrollbar(win)
    scrollbar.pack(side=RIGHT, fill=Y)

    text = Text(win, wrap="none", yscrollcommand=scrollbar.set)
    text.pack(fill=BOTH, expand=True)

    scrollbar.config(command=text.yview)

    for a in merged:
        line = f"{a.aircraft_id} | ORIG: {a.origin} | ARR: {a.arrival} | DEST: {a.destination} | DEP: {a.departure} | {a.airline}\n"
        text.insert(END, line)


def SaveFlightsButton():
    global merged

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


def PlotArrivalsButton():
    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return
    PlotArrivals(arrivals)


def PlotAirlinesButton():
    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return
    PlotAirlines(arrivals)


def PlotFlightsTypeButton():
    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return
    PlotFlightsType(arrivals)


def MapFlightsButton():
    global airports

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")
        for ap in airports:
            SetSchengen(ap)

    MapFlights(arrivals, airports)


def MapLongDistanceButton():
    global airports

    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "No arrivals loaded")
        return

    if len(airports) == 0:
        airports = LoadAirports("Airports.txt")
        for ap in airports:
            SetSchengen(ap)

    long_distance = LongDistanceArrivals(arrivals)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance arrivals found")
        return

    MapFlights(long_distance, airports)


# ============================================================
# V3 - GESTIÓ DE GATES
# ============================================================

def BuildLEBLStructureButton():
    global bcn

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    messagebox.showinfo("OK", f"LEBL structure loaded with {len(bcn.terminals)} terminals")


def AssignGatesButton():
    global bcn
    global merged

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    assigned = 0
    failed = 0

    for a in merged:
        gate_name = AssignGate(bcn, a)
        if gate_name == -1:
            failed += 1
        else:
            assigned += 1

    messagebox.showinfo(
        "Gate Assignment",
        f"Assigned: {assigned}\nNot assigned: {failed}"
    )


def ShowGateOccupancyButton():
    global bcn

    if bcn is None or bcn == -1:
        messagebox.showwarning("Warning", "Build LEBL structure first")
        return

    occupancy = GateOccupancy(bcn)

    win = Toplevel(window)
    win.title("Gate Occupancy")
    win.geometry("800x500")

    scrollbar = Scrollbar(win)
    scrollbar.pack(side=RIGHT, fill=Y)

    txt = Text(win, wrap="none", yscrollcommand=scrollbar.set)
    txt.pack(fill=BOTH, expand=True)

    scrollbar.config(command=txt.yview)

    for t, a, g, occ, ac_id in occupancy:
        status = f"Occupied by {ac_id}" if occ else "Free"
        txt.insert(END, f"{t} | {a} | {g} | {status}\n")


# ============================================================
# V4 - SIMULACIÓ DEL DIA
# ============================================================

def SimulateDayButton():
    global bcn
    global merged

    if bcn is None:
        messagebox.showerror("Error", "Load LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    hours = []
    occupancy = []
    rejected = []

    for h in range(24):
        time = f"{h:02d}:00"
        not_assigned = AssignGatesAtTime(bcn, merged, time)

        count = sum(
            1 for t in bcn.terminals
            for a in t.boarding_areas
            for g in a.gates
            if g.occupied
        )

        hours.append(h)
        occupancy.append(count)
        rejected.append(not_assigned)

    import matplotlib.pyplot as plt

    plt.plot(hours, occupancy, label="Gates ocupades")
    plt.plot(hours, rejected, label="No assignats")

    plt.title("Simulació diària")
    plt.xlabel("Hora")
    plt.ylabel("Nombre")
    plt.legend()
    plt.grid()
    plt.show()


def SimulateFullDayButton():
    global bcn
    global merged

    if bcn is None:
        messagebox.showerror("Error", "Load LEBL structure first")
        return

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")

    total_not_assigned = 0

    for h in range(24):
        time = f"{h:02d}:00"
        total_not_assigned += AssignGatesAtTime(bcn, merged, time)

    messagebox.showinfo(
        "Day Simulation",
        f"Simulation completed\nNot assigned flights: {total_not_assigned}"
    )

    PlotDayOccupancy(bcn, merged)



# ============================================================
# INTERFÍCIE GRÀFICA — DISEÑO PROFESIONAL EQUILIBRADO
# ============================================================

window = Tk()
window.title("Airport Manager — Professional Edition")
window.geometry("1400x900")
window.configure(bg="#ECEFF1")

setup_style()

# TÍTULO PRINCIPAL
ttk.Label(
    window,
    text="Airport Operations Manager",
    style="Title.TLabel"
).pack(pady=15)

# CONTENEDOR PRINCIPAL (3 COLUMNAS + PANEL DE VISUALIZACIÓN)
main_frame = Frame(window, bg="#ECEFF1")
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

# Configurar columnas para que ocupen el mismo espacio
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=1)
main_frame.columnconfigure(3, weight=2)   # panel de visualización más grande

# ============================================================
# COLUMNA 1 — AIRPORT MANAGEMENT
# ============================================================

col1 = Frame(main_frame, bg="#ECEFF1")
col1.grid(row=0, column=0, sticky="nsew", padx=20)

ttk.Label(col1, text="Airport Management", style="Section.TLabel").pack(pady=10)

# Inputs
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

# Botones columna 1
create_button(col1, "Load Airports", load_airports).pack(pady=5, fill=X)
create_button(col1, "Add Airport", add_airport).pack(pady=5, fill=X)
create_button(col1, "Remove Airport", remove_airport).pack(pady=5, fill=X)
create_button(col1, "Save Schengen", save_schengen).pack(pady=5, fill=X)

# ============================================================
# COLUMNA 2 — FLIGHT MANAGEMENT
# ============================================================

col2 = Frame(main_frame, bg="#ECEFF1")
col2.grid(row=0, column=1, sticky="nsew", padx=20)

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

# ============================================================
# COLUMNA 3 — MAPS & VISUALIZATION
# ============================================================

col3 = Frame(main_frame, bg="#ECEFF1")
col3.grid(row=0, column=2, sticky="nsew", padx=20)

ttk.Label(col3, text="Maps & Visualization", style="Section.TLabel").pack(pady=10)

create_button(col3, "Map Airports", map_airports).pack(pady=5, fill=X)
create_button(col3, "Map Flights", MapFlightsButton).pack(pady=5, fill=X)
create_button(col3, "Long Distance Flights", MapLongDistanceButton).pack(pady=5, fill=X)

ttk.Label(col3, text="Charts", style="Section.TLabel").pack(pady=10)

create_button(col3, "Plot Arrivals", PlotArrivalsButton).pack(pady=5, fill=X)
create_button(col3, "Plot Airlines", PlotAirlinesButton).pack(pady=5, fill=X)
create_button(col3, "Plot Schengen", PlotFlightsTypeButton).pack(pady=5, fill=X)

ttk.Label(col3, text="Simulation", style="Section.TLabel").pack(pady=10)

create_button(col3, "Simulate Day", SimulateDayButton).pack(pady=5, fill=X)
create_button(col3, "Full Day Simulation", SimulateFullDayButton).pack(pady=5, fill=X)

# ============================================================
# COLUMNA 4 — PANEL DE VISUALIZACIÓN
# ============================================================

visual_panel = Frame(main_frame, bg="white", relief="solid", bd=1)
visual_panel.grid(row=0, column=3, sticky="nsew", padx=20, pady=10)

ttk.Label(
    visual_panel,
    text="Visualization Panel",
    style="Section.TLabel"
).pack(pady=10)

# Aquí se mostrarán gráficos, mapas o imágenes
visual_canvas = Canvas(visual_panel, bg="white")
visual_canvas.pack(fill=BOTH, expand=True)

# BOTÓN SALIR
create_button(window, "Exit", window.destroy).pack(pady=20)

window.mainloop()
