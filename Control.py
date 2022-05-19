from libreVNA import libreVNA
from libreVNA import NoConnectionException
import time

import subprocess

VNA_PORT = 19542
# enter your GUI path here
GUI_PATH = "/home/david/Desktop/work/libreVNA_gui/LibreVNA-GUI-Ubuntu-v1.3.0/LibreVNA-GUI"
NO_GUI = False

gui_process = None
vna = None


def init_vna():
    """
    starts the libreVNA-gui in a separate process, either with visible gui or without,
    in order to start the tcp server to send SCPI commands. Then creates a libreVNA instance
    and tries to connect every 5 until connection is established.
    """
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


def check_calibration_ongoing():
    """
    checks if a calibration measurement is currently ongoing
    :return: a bool, either true or false
    """
    ongoing = vna.query(":VNA:CAL:BUSY?")
    if ongoing == "TRUE":
        return True
    else:
        return False


def calibration_measure(cal_type: str):
    """
    starts a calibration measurement
    :param type: the type of calibration measurement
    """
    vna.cmd(":VNA:CAL:MEAS " + cal_type)


def load_calibration(calibration_file: str):
    """
    loads a calibration_file
    :param calibration_file: the path of the calibration file as a string,
    relative to where the application was started
    """
    success = vna.query(":VNA:CAL:LOAD? " + calibration_file)
    if success == "FALSE":
        raise ValueError("could not load calibration file" + calibration_file)


def close_gui():
    """
    terminates the libreVNA gui process used for the tcp server.
    """
    gui_process.terminate()


def get_min_freq():
    """
    getter for min frequency of the libreVNA
    :return: min frequency of the libreVNA
    """
    return vna.query(":DEV:INF:MINF?")


def get_max_freq():
    """
    getter for max frequency of the libreVNA
    :return: max frequency of the libreVNA
    """
    return vna.query(":DEV:INF:MAXF?")


def get_avg_done_fraction():
    """
    getter for how many measurements of the total number to be averaged over
    are done already
    :return: float from 0 to 1 representing the status of the averaging process
    """
    return float(get_avg_current()) / float(get_avg_total())


def get_avg_total():
    return vna.query(":VNA:ACQ:AVG?")


def get_avg_current():
    return vna.query(":VNA:ACQ:AVGLEV?")


def get_trace_data(trace):
    """
    getter for trace data
    :param trace: which trace (S11, S21 etc)
    :return: the trace data as a list
    """
    return vna.parse_trace_data(vna.query(":VNA:TRAC:DATA? " + trace))


def set_min_freq(min_freq):
    """
    setter for start frequency of the libreVNA
    :param min_freq: start frequency for measurements
    """
    vna.cmd(":VNA:FREQuency:START " + str(min_freq))
    result = vna.query(":VNA:FREQuency:START?")
    if min_freq != float(result):
        raise ValueError("min_freq was not saved")


def set_max_freq(max_freq):
    """
    setter for stop frequency of the libreVNA
    :param max_freq: stop frequency for measurements
    """
    vna.cmd(":VNA:FREQuency:STOP " + str(max_freq))
    result = vna.query(":VNA:FREQuency:STOP?")
    if max_freq != float(result):
        raise ValueError("max_freq was not saved")


def set_center_freq(center_freq):
    """
    setter for center frequency of the libreVNA
    :param center_freq: center frequency for measurements
    """
    vna.cmd(":VNA:FREQuency:CENTer " + str(center_freq))
    result = vna.query(":VNA:FREQuency:CENTer?")
    if center_freq != float(result):
        raise ValueError("min_freq was not saved")


def set_span_freq(span_freq):
    """
    setter for span frequency of the libreVNA
    :param span_freq: span frequency for measurements
    """
    vna.cmd(":VNA:FREQuency:SPAN " + str(span_freq))
    result = vna.query(":VNA:FREQuency:SPAN?")
    if span_freq != float(result):
        raise ValueError("max_freq was not saved")


def set_points(nr_points):
    """
    setter for the number of points per measurement
    :param nr_points: number of points for measurement
    """
    vna.cmd(":VNA:ACQuisition:POINTS " + str(nr_points))
    result = vna.query(":VNA:ACQuisition:POINTS?")
    if nr_points != int(result):
        raise ValueError("points were not saved")


def set_bandwidth(bandwidth):
    """
    setter for the bandwidth of the bandpass filter
    :param bandwidth: bandwidth of the bandpass filter
    """
    vna.cmd(":VNA:ACQuisition:IFBW " + str(bandwidth))
    result = vna.query(":VNA:ACQuisition:IFBW?")
    if bandwidth != int(result):
        raise ValueError("IF bandwidth not saved")


def set_power(power):
    """
    setter for the power level of the measurement signal
    :param power: power level in dBm
    """
    vna.cmd(":VNA:STIMulus:LVL " + str(power))
    result = vna.query(":VNA:STIMulus:LVL?")
    if power != float(result):
        raise ValueError("power not saved")


def set_average(average):
    """
    setter for over how many samples the average is calculated
    :param average: power level in dBm
    """
    vna.cmd(":VNA:ACQ:AVG " + str(average))
    result = vna.query(":VNA:ACQ:AVG?")
    if average != int(result):
        raise ValueError("power not saved")


def set_cal_type(cal_type: str):
    vna.cmd(":VNA:CAL:TYPE " + cal_type)
    result = vna.query(":VNA:CAL:TYPE?")
    if cal_type != result:
        raise ValueError("cal type not saved")
