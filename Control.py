from libreVNA import libreVNA
from libreVNA import NoConnectionException
import time

import subprocess

# Create the control instance
VNA_PORT = 19542
GUI_PATH = "/home/david/Desktop/work/libreVNA_gui/LibreVNA-GUI-Ubuntu-v1.3.0/LibreVNA-GUI"
NO_GUI = False

gui_process = None
vna = None


def init_vna():
    global gui_process
    global vna
    # start gui/tcp server
    if NO_GUI:
        gui_process = subprocess.Popen([GUI_PATH, "--no-gui"], shell=False)
    else:
        gui_process = subprocess.Popen([GUI_PATH], shell=False)
    # Create the control instance
    not_connected_port = True
    not_connected_device = True
    while not_connected_port:
        try:
            vna = libreVNA('localhost', VNA_PORT)
        except NoConnectionException as e:
            time.sleep(1)
            continue
        not_connected_port = False

    # Quick connection check (should print "LibreVNA-GUI")
    print(vna.query("*IDN?"))

    # Make sure we are connecting to a device (just to be sure, with default settings the LibreVNA-GUI auto-connects)
    while not_connected_device:
        vna.cmd(":DEV:CONN")
        dev = vna.query(":DEV:CONN?")
        if dev == "Not connected":
            print("Not connected to any device")
            time.sleep(5)
        else:
            print("Connected to " + dev)
            not_connected_device = False


def load_calibration(calibration_file):
    vna.cmd(":VNA:CAL:LOAD " + calibration_file)
    result = vna.query(":VNA:CAL:LOAD?")
    print(result)


def close_gui():
    gui_process.terminate()


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


def set_bandwidth(bandwidth):
    vna.cmd(":VNA:ACQuisition:IFBW " + str(bandwidth))
    result = vna.query(":VNA:ACQuisition:IFBW?")
    if bandwidth != int(result):
        raise ValueError("IF bandwidth not saved")


def set_power(power):
    vna.cmd(":VNA:STIMulus:LVL " + str(power))
    result = vna.query(":VNA:STIMulus:LVL?")
    if power != float(result):
        raise ValueError("power not saved")
