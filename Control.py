from libreVNA import libreVNA

# Create the control instance
vna = libreVNA('localhost', 19542)

# Quick connection check (should print "LibreVNA-GUI")
print(vna.query("*IDN?"))

# Make sure we are connecting to a device (just to be sure, with default settings the LibreVNA-GUI auto-connects)
vna.cmd(":DEV:CONN")
dev = vna.query(":DEV:CONN?")
if dev == "Not connected":
    print("Not connected to any device, aborting")
    exit(-1)
else:
    print("Connected to " + dev)


def get_min_freq():
    return vna.query(":DEV:INF:MINF?")


def get_max_freq():
    return vna.query(":DEV:INF:MAXF?")


def set_min_freq(min_freq):
    vna.cmd(":VNA:FREQuency:START " + str(min_freq))
    result = vna.query(":VNA:FREQuency:START?")
    if min_freq != float(result):
        raise ValueError("min_freq was not saved")


def set_max_freq(max_freq):
    vna.cmd(":VNA:FREQuency:STOP " + str(max_freq))
    result = vna.query(":VNA:FREQuency:STOP?")
    if max_freq != float(result):
        raise ValueError("max_freq was not saved")


def set_points(nr_points):
    vna.cmd(":VNA:ACQuisition:POINTS " + str(nr_points))
    result = vna.query(":VNA:ACQuisition:POINTS?")
    if nr_points != int(result):
        raise ValueError("points were not saved")
