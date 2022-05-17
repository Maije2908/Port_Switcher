import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
import Control
import dataToTouchstone


def get_calkit_options_from_folder():
    calkit_files = list(filter(lambda x: x.endswith('.calkit'), os.listdir('CALKITS')))
    calkit_files[:] = [elem.replace(".calkit", "") for elem in calkit_files]
    calkit_files.append("NO CAL-KIT")
    return calkit_files


class calibrationFrame(tk.LabelFrame):

    def __init__(self, parent, measure_type, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.measure_type = measure_type
        self.config(width=400)

        # text for type
        tk.Label(self, text="measure type: " + measure_type).grid(row=0, column=0)

        # calkit selection
        self.calkit_selection = tk.StringVar()
        self.calkit_valid = False
        self.add_calkit_selection()
        self.calkit_selection.trace_add('write', self.callback_calkit_changed)

        # if 4 port specify which calibration is taken
        if self.measure_type == "4-port measurement":
            self.port_combination = tk.StringVar()
            self.add_port_combination_selection_4_port()

        # normal 2 port calibration
        else:
            self.measure_button = None
            self.calibration_meas_type = tk.StringVar()
            self.add_calibration_measure_buttons_2_port()

    def callback_calkit_changed(self, var, index, mode):
        if self.calkit_selection.get() == "NO CAL-KIT":
            self.calkit_valid = True
            return
        try:
            Control.load_calibration("CAL/" + self.calkit_selection.get() + ".cal")
            self.calkit_valid = True
        except ValueError:
            self.calkit_valid = False
            messagebox.showinfo("Error", "Could not open calibration kit")



    def add_calkit_selection(self):
        options = get_calkit_options_from_folder()

        tk.Label(self, text="select cal-kit").grid(row=1, column=0)
        tk.OptionMenu(self, self.calkit_selection, *options).grid(row=1, column=1)

    def add_port_combination_selection_4_port(self):
        options = [
            "port 1 SOL", "port 2 SOL", "port 3 SOL", "port 4 SOL",
            "port 1 and 2 THROUGH", "port 1 and 3 THROUGH", "port 1 and 4 THROUGH",
            "port 2 and 3 THROUGH", "port 2 and 4 THROUGH", "port 3 and 4 THROUGH",
        ]

        tk.Label(self, text="select port/s").grid(row=2, column=0)
        tk.OptionMenu(self, self.port_combination, *options).grid(row=2, column=1)


    def add_calibration_measure_buttons_2_port(self):
        options = [
            "PORT_1_OPEN", "PORT_1_SHORT", "PORT_1_LOAD", "PORT_2_OPEN", "PORT_2_SHORT", "PORT_2_LOAD", "THROUGH"
        ]

        tk.OptionMenu(self, self.calibration_meas_type, *options).grid(row=2, column=0)
        self.measure_button = tk.Button(self, text="Measure", command=self.measure_calibration_2_port)
        self.measure_button.grid(row=2, column=1)

    def measure_calibration_2_port(self):
        if self.calkit_valid is False:
            messagebox.showinfo("Error", "select valid calkit first")
            return
        self.measure_button["state"] = "disabled"
        Control.calibration_measure(self.calibration_meas_type.get())
        self.after(500, self.reset_button_after_cal_meas)

    def reset_button_after_cal_meas(self):
        if Control.check_calibration_ongoing() is True:
            self.after(500, self.reset_button_after_cal_meas)
        else:
            self.measure_button["state"] = "normal"


