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
    print(min_freq)
    vna.cmd(":VNA:FREQuency:START " + str(min_freq))
    print(vna.query(":VNA:FREQuency:START?"))

def set_max_freq(max_freq):
    print(max_freq)
    vna.cmd(":VNA:FREQuency:STOP " + str(max_freq))
    print(vna.query(":VNA:FREQuency:STOP?"))
