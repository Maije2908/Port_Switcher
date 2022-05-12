import Control
import numpy as np


def save_two_port():
    S11 = Control.get_trace_data("S11")
    S21 = Control.get_trace_data("S21")
    S12 = Control.get_trace_data("S12")
    S22 = Control.get_trace_data("S22")

    with open("MES/2port_measurement.s2p", "w") as file:
        file.write(get_header(2))
        for i in range(0, len(S11)):
            file.write(str(S11[i][0]) + " " + str(np.real(S11[i][1])) + " " + str(np.imag(S11[i][1])) + " " +
                       str(np.real(S21[i][1])) + " " + str(np.imag(S21[i][1])) + " " +
                       str(np.real(S12[i][1])) + " " + str(np.imag(S12[i][1])) + " " +
                       str(np.real(S22[i][1])) + " " + str(np.imag(S22[i][1])) + "\n")


def get_header(nr_ports):
    if nr_ports == 2:
        return "# Hz S RI R 50.000000000000\n"
