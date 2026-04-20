import matplotlib.pyplot as plt


# CLASS

class Aircraft:

    def __init__(self,
                 aircraft_id="",
                 airline="",
                 origin="",
                 arrival=""):

        self.aircraft_id = aircraft_id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival


# LOAD ARRIVALS

def LoadArrivals(filename):

    aircrafts = []

    try:

        file = open(filename, "r")

    except:

        print("Error")

        return aircrafts

    header = file.readline()

    for line in file:

        parts = line.split()

        if len(parts) != 4:
            continue

        aircraft_id = parts[0]
        origin = parts[1]
        arrival = parts[2]
        airline = parts[3]

        # Validate time format

        if ":" not in arrival:
            continue

        time_parts = arrival.split(":")

        if len(time_parts) != 2:
            continue

        try:

            hour = int(time_parts[0])
            minute = int(time_parts[1])

        except:

            continue

        aircraft = Aircraft(
            aircraft_id,
            airline,
            origin,
            arrival
        )

        aircrafts.append(aircraft)

    file.close()

    return aircrafts


# PLOT ARRIVALS

def PlotArrivals(aircrafts):

    if len(aircrafts) == 0:

        print("Error")

        return

    hours = [0] * 24

    i = 0

    while i < len(aircrafts):

        arrival = aircrafts[i].arrival

        hour = int(arrival.split(":")[0])

        if hour >= 0 and hour < 24:

            hours[hour] = hours[hour] + 1

        i = i + 1

    plt.bar(range(24), hours)

    plt.title("Landing frequency per hour")

    plt.xlabel("Hour")

    plt.ylabel("Number of arrivals")

    plt.show()


# SAVE FLIGHTS

def SaveFlights(aircrafts, filename):

    if len(aircrafts) == 0:

        print("Error")

        return -1

    file = open(filename, "w")

    file.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

    i = 0

    while i < len(aircrafts):

        aircraft = aircrafts[i]

        aircraft_id = aircraft.aircraft_id
        origin = aircraft.origin
        arrival = aircraft.arrival
        airline = aircraft.airline

        if aircraft_id == "":
            aircraft_id = "-"

        if origin == "":
            origin = "-"

        if arrival == "":
            arrival = "-"

        if airline == "":
            airline = "-"

        file.write(
            aircraft_id + " " +
            origin + " " +
            arrival + " " +
            airline + "\n"
        )

        i = i + 1

    file.close()

    print("Flights saved")

    return 0


# TEST SECTION

if __name__ == "__main__":

    aircrafts = LoadArrivals("Arrivals.txt")

    print("Aircraft loaded:")

    print(len(aircrafts))

    PlotArrivals(aircrafts)

    SaveFlights(aircrafts, "FlightsOutput.txt")