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

# Finestra separada per veure el mapa físic molt més gran
physical_map_window = None
physical_map_canvas = None

# Mode vídeo: més lent i més gran perquè es vegi bé gravant pantalla
LIVE_DELAY_MS = 1500
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
# ============================================================
# load_airports
# Carrega aeroports i informa si alguna línia del fitxer era incorrecta.
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

    text = f"Airports loaded: {len(airports)}\n"

    if hasattr(LoadAirports, "last_errors") and len(LoadAirports.last_errors) > 0:

        text += "\nSome lines had errors and were skipped:\n\n"

        for error in LoadAirports.last_errors:
            text += "- " + error + "\n"

        messagebox.showwarning(
            "File warnings",
            "Some airport lines were incorrect and were skipped.\nCheck the panel for details."
        )

    show_text_in_panel(text)

def add_airport():

    global airports
    # Normalitzem el codi perquè tots els aeroports segueixin el mateix format ICAO
    code = entry_code.get().strip().upper()

    if len(code) != 4:
        messagebox.showerror("Error", "ICAO code must have 4 characters")
        return

    try:   # Convertim les coordenades a números
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except:
        messagebox.showerror("Error", "Latitude and longitude must be numbers")
        return

    airport = Airport(code, lat, lon)
    SetSchengen(airport)

    err = AddAirport(airports, airport)
    # Avisem si l'aeroport ja existia
    if err == -1:
        messagebox.showerror("Error", "Airport already exists")
    else:
        messagebox.showinfo("OK", "Airport added")


def remove_airport():

    global airports
    #búsqueda
    code = entry_code.get().strip().upper()
    #No eliminem un aeroport si l'usuari no ha escrit cap codi
    if code == "":
        messagebox.showerror("Error", "Write an ICAO code first")
        return

    err = RemoveAirport(airports, code)

    if err == -1:
        messagebox.showerror("Error", "Airport not found")
    else:
        messagebox.showinfo("OK", "Airport removed")


def save_schengen():

    if len(airports) == 0:    #    # Comprovem que hi hagi aeroports carregats abans de guardar el fitxer
        messagebox.showwarning("Warning", "Load airports first")
        return

    err = SaveSchengenAirports(airports, "SchengenAirports.txt")

    if err == -1:
        messagebox.showerror("Error", "File could not be saved")
    else:
        messagebox.showinfo("OK", "SchengenAirports.txt saved")

# ============================================================
# save_all_airports
# Guarda tots els aeroports carregats en un fitxer.
# Això cobreix millor el requisit de guardar dades d'aeroports.
# ============================================================
def save_all_airports():

    if len(airports) == 0:
        messagebox.showwarning("Warning", "Load airports first")
        return

    filename = filedialog.asksaveasfilename(
        title="Save airports file",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    err = SaveAirports(airports, filename)

    if err == -1:
        messagebox.showerror("Error", "Airports could not be saved")
    else:
        messagebox.showinfo("OK", "Airports saved correctly")
def map_airports():

    if not ensure_airports_loaded():    #si NO es pot load
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    kml_path = MapAirports(airports)

    if kml_path == -1:
        messagebox.showerror("Error", "KML could not be created")
        return

    try:        #obrim el mapa automàticament
        os.startfile(kml_path)
    except:
        messagebox.showinfo("OK", f"KML created at:\n{kml_path}")

    show_text_in_panel("AirportsMap.kml created.\nOpen it in Google Earth if it did not open automatically.")


# ============================================================
# V2/V4 — FLIGHT MANAGEMENT
# ============================================================
def LoadArrivalsButton():

    global arrivals

    filename = filedialog.askopenfilename(      #usuari tria el fitxer
        title="Select arrivals file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    arrivals = LoadArrivals(filename)   #carreguem les arribades

    if len(arrivals) == 0:
        messagebox.showerror("Error", "No arrivals loaded")
        # Confirmem la càrrega i mostrem el resultat també al panell visual
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
    #arribades i sortides
    if len(arrivals) == 0:
        messagebox.showwarning("Warning", "Load arrivals first")
        return

    if len(departures) == 0:
        messagebox.showwarning("Warning", "Load departures first")
        return

    merged = MergeMovements(arrivals, departures)       #unim arribades i sortides en una sola llista

    night = NightAircraft(merged)       #calculem els avions que passen la nit

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

    text = "AIRCRAFT | ORIGIN | ARRIVAL | DESTINATION | DEPARTURE | AIRLINE\n"      #capçalera
    text += "-" * 90 + "\n"

    for a in merged:        #afegim cada moviment en format
        text += f"{a.aircraft_id} | {a.origin or '-'} | {a.arrival or '-'} | {a.destination or '-'} | {a.departure or '-'} | {a.airline}\n"

    show_text_in_panel(text)


#Vuelos Estacionamiento Corto Button
#Mostra quants vols estan menys de 2 hores a l'aeroport.
def VuelosEstacionamientoCortoButton():

    # Si no hi ha moviments fusionats no podem calcular el temps a l'aeroport
    if len(merged) == 0:
        messagebox.showwarning(
            "Warning",
            "Dale al boton Merge Movements primero"
        )
        return

    #Busquem els vols que estan menys de 2 hores a l'aeroport
    estac_corto = VuelosEstacionamientoCorto(merged)

    text = "VUELOS ESTACIONAMIENTO CORTO\n"
    text += "Vuelos que pasan menos de 2 horas al aeropuerto: "
    text += str(len(estac_corto)) + "\n\n"

    text += "AIRCRAFT ID | LLEGADA | IDA | TIEMPO EN EL AEROPUERTO | AEROLINEA\n"

    #Busquem aircraft id per estac_corto
    for a in estac_corto:

        arrival_time = _parse_time(a.arrival)
        departure_time = _parse_time(a.departure)

        #Comprobar que les hores existeixen
        if arrival_time is not None and departure_time is not None:

            time_in_airport = (departure_time) - (arrival_time)

            # Si surt després de mitjanit
            if time_in_airport < 0:
                time_in_airport += 24 * 60

            hours = time_in_airport // 60
            minutes = time_in_airport % 60

            text += (
                a.aircraft_id + " | " +
                a.arrival + " | " +
                a.departure + " | " +
                str(hours) + "h " + str(minutes) + "min | " +
                a.airline + "\n"
            )

    show_text_in_panel(text)

    messagebox.showinfo(
        "Vuelos estacionamiento corto",
        str(len(estac_corto)) + " vuelos que se quedan menos de 2 horas en el aeropuerto"
    )


# SaveFlightsButton
# Guarda moviments fusionats si existeixen.
# Si encara no hi ha merge, guarda les arribades.
# Això evita que l'avaluador carregui només arrivals i no pugui guardar.

def SaveFlightsButton():

    if len(merged) > 0:
        data_to_save = merged
        label = "merged movements"

    elif len(arrivals) > 0:
        data_to_save = arrivals
        label = "arrivals"

    else:
        messagebox.showwarning("Warning", "No flights to save")
        return

    filename = filedialog.asksaveasfilename(
        title="Save flights file",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if filename == "":
        return

    err = SaveFlights(data_to_save, filename)

    if err == -1:
        messagebox.showerror("Error", "Flights could not be saved")
    else:
        messagebox.showinfo("OK", "Saved " + label + " correctly")
# ============================================================
# V3/V4 — GATE MANAGEMENT
# ============================================================
def BuildLEBLStructureButton():

    global bcn

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "LEBL structure could not be loaded")
        return

    total_gates = 0     #comptem totes les gates per donar un resum útil de l'estructura carregada


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

    global bcn      #permet modificar la variable global de l’aeroport

    if len(merged) == 0:
        messagebox.showwarning("Warning", "Load and merge movements first")
        return

    bcn = LoadAirportStructure("LEBL.txt")      #carrega l’estructura de l’aeroport LEBL

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

    occupancy = GateOccupancy(bcn)      #calcula l’estat de totes les portes

    text = "TERMINAL | AREA | GATE | STATUS\n"
    text += "-" * 70 + "\n"
    #recorre cada porta i mostra si està lliure o ocupada
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

    err = SaveGateAssignments(bcn, filename)  #guarda les assignacions de portes al fitxer triat

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
# ============================================================
# _draw_label_box
# Dibuixa un text amb fons blanc perquè sempre sigui llegible.
# Ho fem servir per noms de terminals, boarding areas i avions.
# ============================================================
def _draw_label_box(canvas, x, y, text, font=("Segoe UI", 10, "bold"),
                    fill="#263238", bg="white", anchor="center"):

    # Primer creem el text invisible per saber la mida real
    text_id = canvas.create_text(
        x,
        y,
        text=text,
        font=font,
        fill=fill,
        anchor=anchor,
        tags=("labels",)
    )

    box = canvas.bbox(text_id)

    if box is not None:
        x1, y1, x2, y2 = box

        # Fons blanc darrere del text
        rect_id = canvas.create_rectangle(
            x1 - 5,
            y1 - 3,
            x2 + 5,
            y2 + 3,
            fill=bg,
            outline="#B0BEC5",
            tags=("label_bg",)
        )

        # Pugem el rectangle just darrere el text
        canvas.tag_raise(text_id, rect_id)

    return text_id


# ============================================================
# PreparePhysicalMapWindow
# Crea una finestra separada amb scroll vertical i horitzontal.
# Ho fem perquè el mapa pugui ser gran i no se superposin gates.
# ============================================================
def PreparePhysicalMapWindow():

    global physical_map_window
    global physical_map_canvas

    if physical_map_window is None or not physical_map_window.winfo_exists():

        physical_map_window = Toplevel(window)
        physical_map_window.title("Live Physical Gate Map — Scroll Mode")
        physical_map_window.geometry("1550x900")
        physical_map_window.configure(bg="#ECEFF1")

        title = Label(
            physical_map_window,
            text="Live Physical Gate Management",
            font=("Segoe UI", 22, "bold"),
            bg="#ECEFF1",
            fg="#263238"
        )
        title.pack(pady=6)

        container = Frame(physical_map_window, bg="#ECEFF1")
        container.pack(fill=BOTH, expand=True, padx=8, pady=8)

        v_scroll = Scrollbar(container, orient=VERTICAL)
        h_scroll = Scrollbar(container, orient=HORIZONTAL)

        physical_map_canvas = Canvas(
            container,
            bg="#ECEFF1",
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            highlightthickness=0
        )

        v_scroll.config(command=physical_map_canvas.yview)
        h_scroll.config(command=physical_map_canvas.xview)

        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        physical_map_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    return physical_map_canvas


# ============================================================
# _draw_label_box
# Dibuixa un text amb fons blanc perquè sigui llegible.
# Ho fem perquè les etiquetes no quedin tapades per línies o rectangles.
# ============================================================
def _draw_label_box(canvas, x, y, text,
                    font=("Segoe UI", 10, "bold"),
                    fill="#263238",
                    bg="white",
                    anchor="center"):

    text_id = canvas.create_text(
        x,
        y,
        text=text,
        font=font,
        fill=fill,
        anchor=anchor,
        tags=("labels",)
    )

    box = canvas.bbox(text_id)

    if box is not None:

        x1, y1, x2, y2 = box

        rect_id = canvas.create_rectangle(
            x1 - 6,
            y1 - 3,
            x2 + 6,
            y2 + 3,
            fill=bg,
            outline="#B0BEC5",
            tags=("label_bg",)
        )

        canvas.tag_raise(text_id, rect_id)

    return text_id


# ============================================================
# DrawPhysicalGateMap
# Versió amb scroll i sense superposició:
# - cada boarding area té prou espai horitzontal
# - cada gate té prou espai vertical
# - les gates esquerra/dreta no es trepitgen
# - els aircraft_id tenen fons blanc
# - els textos passen sempre davant de tot
# ============================================================
def DrawPhysicalGateMap(bcn_state, hour_label="", rejected=0):

    canvas = PreparePhysicalMapWindow()
    canvas.delete("all")

    # -------------------------
    # COLORS
    # -------------------------
    bg_card = "#FFFFFF"
    terminal_color = "#0E5A70"
    terminal_dark = "#083A47"
    area_color = "#1565C0"
    area_dark = "#0D47A1"
    free_color = "#43A047"
    occupied_color = "#E53935"
    text_dark = "#263238"
    line_color = "#37474F"

    # -------------------------
    # HEADER
    # -------------------------
    header_x1 = 30
    header_y1 = 20
    header_x2 = 2100
    header_y2 = 125

    canvas.create_rectangle(
        header_x1,
        header_y1,
        header_x2,
        header_y2,
        fill="white",
        outline="#CFD8DC",
        width=2
    )

    title = "LIVE PHYSICAL GATE MANAGEMENT"

    if hour_label != "":
        title += "  |  " + hour_label

    canvas.create_text(
        55,
        52,
        text=title,
        anchor="w",
        font=("Segoe UI", 24, "bold"),
        fill=text_dark,
        tags=("labels",)
    )

    # Llegenda
    canvas.create_rectangle(60, 84, 90, 108, fill=free_color, outline="#1B5E20", width=2)
    canvas.create_text(
        102,
        96,
        text="Free gate",
        anchor="w",
        font=("Segoe UI", 12, "bold"),
        fill=text_dark,
        tags=("labels",)
    )

    canvas.create_rectangle(230, 84, 260, 108, fill=occupied_color, outline="#B71C1C", width=2)
    canvas.create_text(
        272,
        96,
        text="Occupied gate",
        anchor="w",
        font=("Segoe UI", 12, "bold"),
        fill=text_dark,
        tags=("labels",)
    )

    canvas.create_rectangle(460, 84, 490, 108, fill=terminal_color, outline=terminal_dark, width=2)
    canvas.create_text(
        502,
        96,
        text="Terminal / Boarding Area",
        anchor="w",
        font=("Segoe UI", 12, "bold"),
        fill=text_dark,
        tags=("labels",)
    )

    canvas.create_text(
        850,
        96,
        text="Rejected aircraft this hour: " + str(rejected),
        anchor="w",
        font=("Segoe UI", 13, "bold"),
        fill="#B71C1C",
        tags=("labels",)
    )

    # -------------------------
    # LAYOUT GRAN, AMB SCROLL
    # -------------------------
    start_x = 90
    current_y = 180

    # Aquestes mides són deliberadament grans per evitar superposicions
    terminal_card_width = 2300

    area_gap_x = 360        # separació entre boarding areas
    area_width = 70         # amplada del pier blau

    gate_width = 84
    gate_height = 30
    gate_gap_y = 46         # separació vertical entre gates

    gate_to_area_gap = 58   # separació horitzontal entre gate i pier

    page_width = 2450
    page_height = 1000

    # =========================================================
    # TERMINALS
    # =========================================================
    for terminal in bcn_state.terminals:

        # Calculem quantes files necessita el terminal segons l'àrea més carregada
        max_gate_rows = 0

        for area in terminal.boarding_areas:

            rows = (len(area.gates) + 1) // 2

            if rows > max_gate_rows:
                max_gate_rows = rows

        pier_height = max(470, max_gate_rows * gate_gap_y + 150)
        card_height = pier_height + 200

        terminal_y = current_y

        # Targeta blanca del terminal
        canvas.create_rectangle(
            start_x - 35,
            terminal_y - 70,
            start_x - 35 + terminal_card_width,
            terminal_y - 70 + card_height,
            fill=bg_card,
            outline="#B0BEC5",
            width=3
        )

        # Banda superior del terminal
        canvas.create_rectangle(
            start_x - 35,
            terminal_y - 70,
            start_x - 35 + terminal_card_width,
            terminal_y + 15,
            fill=terminal_color,
            outline=terminal_color
        )

        # Comptadors
        occupied_terminal = 0
        total_terminal = 0

        for area in terminal.boarding_areas:
            for gate in area.gates:

                total_terminal += 1

                if gate.occupied:
                    occupied_terminal += 1

        canvas.create_text(
            start_x + 20,
            terminal_y - 28,
            text="TERMINAL " + terminal.name,
            anchor="w",
            font=("Segoe UI", 28, "bold"),
            fill="white",
            tags=("labels",)
        )

        canvas.create_text(
            start_x + 450,
            terminal_y - 28,
            text="Occupied: " + str(occupied_terminal) + " / " + str(total_terminal),
            anchor="w",
            font=("Segoe UI", 18, "bold"),
            fill="white",
            tags=("labels",)
        )

        # Passadís principal
        corridor_x1 = start_x + 45
        corridor_y1 = terminal_y + 70
        corridor_x2 = corridor_x1 + max(1450, len(terminal.boarding_areas) * area_gap_x)
        corridor_y2 = corridor_y1 + 58

        canvas.create_rectangle(
            corridor_x1,
            corridor_y1,
            corridor_x2,
            corridor_y2,
            fill=terminal_color,
            outline=terminal_dark,
            width=4
        )

        canvas.create_text(
            corridor_x1 + 20,
            corridor_y1 + 29,
            text="Main terminal corridor",
            anchor="w",
            font=("Segoe UI", 16, "bold"),
            fill="white",
            tags=("labels",)
        )

        # =====================================================
        # BOARDING AREAS
        # =====================================================
        area_index = 0

        for area in terminal.boarding_areas:

            pier_x = corridor_x1 + 120 + area_index * area_gap_x
            pier_y = corridor_y2

            # Ombra
            canvas.create_rectangle(
                pier_x + 8,
                pier_y + 8,
                pier_x + area_width + 8,
                pier_y + pier_height + 8,
                fill="#B0BEC5",
                outline="#B0BEC5"
            )

            # Pier blau de la boarding area
            canvas.create_rectangle(
                pier_x,
                pier_y,
                pier_x + area_width,
                pier_y + pier_height,
                fill=area_color,
                outline=area_dark,
                width=4
            )

            # Etiquetes de l'àrea
            _draw_label_box(
                canvas,
                pier_x + area_width / 2,
                pier_y + 32,
                terminal.name + " AREA " + area.name,
                font=("Segoe UI", 12, "bold"),
                fill=text_dark,
                bg="white"
            )

            _draw_label_box(
                canvas,
                pier_x + area_width / 2,
                pier_y + 66,
                area.area_type,
                font=("Segoe UI", 10, "bold"),
                fill="#455A64",
                bg="#ECEFF1"
            )

            # Comptador d'àrea
            occupied_area = 0

            for gate in area.gates:
                if gate.occupied:
                    occupied_area += 1

            _draw_label_box(
                canvas,
                pier_x + area_width / 2,
                pier_y + pier_height + 36,
                "Gates " + str(occupied_area) + "/" + str(len(area.gates)),
                font=("Segoe UI", 11, "bold"),
                fill=text_dark,
                bg="white"
            )

            # =================================================
            # GATES
            # =================================================
            gate_index = 0

            for gate in area.gates:

                row = gate_index // 2
                left_side = gate_index % 2 == 0

                gate_y = pier_y + 115 + row * gate_gap_y

                if left_side:

                    gate_x = pier_x - gate_to_area_gap - gate_width

                    line_x1 = gate_x + gate_width
                    line_x2 = pier_x

                    aircraft_text_x = gate_x - 10
                    aircraft_anchor = "e"

                else:

                    gate_x = pier_x + area_width + gate_to_area_gap

                    line_x1 = pier_x + area_width
                    line_x2 = gate_x

                    aircraft_text_x = gate_x + gate_width + 10
                    aircraft_anchor = "w"

                # Línia de connexió
                canvas.create_line(
                    line_x1,
                    gate_y + gate_height / 2,
                    line_x2,
                    gate_y + gate_height / 2,
                    fill=line_color,
                    width=3
                )

                if gate.occupied:
                    gate_color = occupied_color
                    border_color = "#B71C1C"
                else:
                    gate_color = free_color
                    border_color = "#1B5E20"

                # Rectangle de gate
                canvas.create_rectangle(
                    gate_x,
                    gate_y,
                    gate_x + gate_width,
                    gate_y + gate_height,
                    fill=gate_color,
                    outline=border_color,
                    width=3
                )

                # Nom curt de gate dins del rectangle
                gate_number = gate.name.split("_G")[-1]
                gate_label = terminal.name + area.name + "-G" + gate_number

                canvas.create_text(
                    gate_x + gate_width / 2,
                    gate_y + gate_height / 2,
                    text=gate_label,
                    anchor="center",
                    font=("Segoe UI", 8, "bold"),
                    fill="white",
                    tags=("labels",)
                )

                # Aircraft ID amb fons blanc, fora de la gate
                if gate.occupied:

                    aircraft_label = gate.aircraft_id

                    _draw_label_box(
                        canvas,
                        aircraft_text_x,
                        gate_y + gate_height / 2,
                        aircraft_label,
                        font=("Segoe UI", 8, "bold"),
                        fill="#B71C1C",
                        bg="white",
                        anchor=aircraft_anchor
                    )

                gate_index += 1

            area_index += 1

        # Actualitzem l'altura per al següent terminal.
        # Així T1 i T2 mai es trepitgen verticalment.
        current_y = terminal_y + card_height + 130
        page_height = current_y + 100

    # Textos al davant de tot
    canvas.tag_raise("label_bg")
    canvas.tag_raise("labels")

    # Scroll gran perquè tot es pugui veure sense comprimir
    canvas.config(scrollregion=(0, 0, page_width, page_height))

    physical_map_window.lift()# ============================================================
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
# ============================================================
# LiveGateStep
# Avança la simulació una hora.
# Ara va més lent perquè en vídeo es pugui veure bé.
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

    # Més lent que abans perquè es vegi bé al vídeo
    window.after(LIVE_DELAY_MS, LiveGateStep)
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
# Ara també mostra el màxim d'ocupació per terminal.
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

    text += "MAXIMUM OCCUPANCY BY TERMINAL\n"
    text += "-" * 50 + "\n"

    if "terminal_max" in data:
        for terminal_name in data["terminal_max"]:
            text += terminal_name + ": " + str(data["terminal_max"][terminal_name]) + " gates\n"

    text += "\nThis dashboard summarizes the full operational day."

    show_text_in_panel(text)
    #aquestes funcions comproven que hi hagi dades carregades i després generen les gràfiques o el mapa dels vols

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


# ============================================================
# MapFlightsButton
# Mapa les trajectòries.
# Si hi ha merged, mapa arribades i sortides.
# Si no, mapa només arribades.
# ============================================================
def MapFlightsButton():

    if len(merged) > 0:
        data_to_map = merged
        label = "arrivals and departures"

    elif len(arrivals) > 0:
        data_to_map = arrivals
        label = "arrivals"

    else:
        messagebox.showwarning("Warning", "No flights loaded")
        return

    if not ensure_airports_loaded():
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    err = MapFlights(data_to_map, airports)

    if err == -1:
        messagebox.showerror("Error", "FlightsMap.kml could not be created")
    else:
        show_text_in_panel("FlightsMap.kml generated for " + label + ".\nOpen it in Google Earth.")

# ============================================================
# MapLongDistanceButton
# Mapa només els vols de llarga distància.
# Si hi ha merged, inclou arribades i sortides.
# ============================================================
def MapLongDistanceButton():

    if len(merged) > 0:
        data_to_check = merged
        label = "arrivals and departures"

    elif len(arrivals) > 0:
        data_to_check = arrivals
        label = "arrivals"

    else:
        messagebox.showwarning("Warning", "No flights loaded")
        return

    if not ensure_airports_loaded():
        messagebox.showerror("Error", "Airports could not be loaded")
        return

    long_distance = LongDistanceArrivals(data_to_check)

    if len(long_distance) == 0:
        messagebox.showinfo("Info", "No long-distance flights found")
        return

    err = MapFlights(long_distance, airports)

    if err == -1:
        messagebox.showerror("Error", "Long-distance KML could not be created")
    else:
        show_text_in_panel(
            "Long-distance flights mapped: " + str(len(long_distance)) +
            "\nSource: " + label
        )

# ============================================================
# INTERFÍCIE — 3 COLUMNES + PANELL VISUAL
# ============================================================
window = Tk()
window.title("Airport Manager — Professional Edition")
window.geometry("1600x950")
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
create_button(col1, "Save All Airports", save_all_airports).pack(pady=5, fill=X)
create_button(col1, "Map Airports", map_airports).pack(pady=5, fill=X)

# ============================================================
# COLUMN 2 — FLIGHT AND GATE MANAGEMENT
# mapes, gràfiques i simulacions
# ============================================================
col2 = Frame(main_frame, bg="#ECEFF1")
col2.grid(row=0, column=1, sticky="nsew", padx=15)

ttk.Label(col2, text="Flight Management", style="Section.TLabel").pack(pady=10)

create_button(col2, "Load Arrivals", LoadArrivalsButton).pack(pady=5, fill=X)
create_button(col2, "Load Departures", LoadDeparturesButton).pack(pady=5, fill=X)
create_button(col2, "Merge Movements", MergeMovementsButton).pack(pady=5, fill=X)
create_button(col2, "Show Movements", ShowMovementsButton).pack(pady=5, fill=X)
create_button(col2, "Vuelos Estac. Corto", VuelosEstacionamientoCortoButton).pack(pady=5, fill=X)
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