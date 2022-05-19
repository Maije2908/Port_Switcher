import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
import Control


def get_calkit_options_from_folder():
    calkit_files = list(filter(lambda x: x.endswith('.calkit'), os.listdir('CALKITS')))
    calkit_files[:] = [elem.replace(".calkit", "") for elem in calkit_files]
    calkit_files.append("NO CAL-KIT")
    return calkit_files


class calibrationFrame(tk.LabelFrame):

    def __init__(self, parent, main_app, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.main_app = main_app
        self.config(width=400)

        self.all_measurements_done = False

        # calkit selection
        self.calkit_selection = tk.StringVar()
        self.calkit_valid = False
        self.add_calkit_selection()
        self.calkit_selection.trace_add('write', self.callback_calkit_changed)

        # if 4 port specify which calibration is taken
        # if self.measure_type == "4-port measurement":
        #     self.port_combination = tk.StringVar()
        #     self.add_port_combination_selection_4_port()

    def callback_calkit_changed(self, var, index, mode):
        # reset current measurements
        if self.__class__.__name__ == "calibrationFrame2port":
            calibrationFrame2port.reset_cal_measurements(self)
        else:
            pass  # 4 port reset

        if self.calkit_selection.get() == "NO CAL-KIT":
            self.calkit_valid = True
            return
        try:
            Control.load_calibration("CALKITS/" + self.calkit_selection.get() + ".cal")
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


class calibrationFrame2port(calibrationFrame):
    options = [
        "PORT_1_OPEN", "PORT_1_SHORT", "PORT_1_LOAD", "PORT_2_OPEN", "PORT_2_SHORT", "PORT_2_LOAD", "THROUGH"
    ]

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # text for type
        tk.Label(self, text="measure type: 2_port measurement").grid(row=0, column=0)

        self.cal_options = None
        self.measure_button = None
        self.apply_button = None
        self.calibration_meas_option = tk.StringVar(value=self.options[0])
        self.add_calibration_measure_buttons()

    def add_calibration_measure_buttons(self):

        self.cal_options = tk.OptionMenu(self, self.calibration_meas_option, *self.options)
        self.cal_options.grid(row=2, column=0)
        self.measure_button = tk.Button(self, text="Measure", command=self.measure_calibration)
        self.measure_button.grid(row=2, column=1)
        tk.Button(self, text="Apply Calibration", command=self.apply_calibration).grid(row=3, column=1)
        tk.Button(self, text="Reset Calibration", command=self.reset_cal_measurements).grid(row=3, column=0)

    def apply_calibration(self):
        if self.calkit_valid and self.all_measurements_done:
            try:
                Control.set_cal_type("SOLT")
            except ValueError as e:
                messagebox.showinfo("Error", "could not set calibration type")
                return
            self.main_app.close_calibration_window()
        else:
            if self.calkit_valid is True:
                messagebox.showinfo("Error", "not all measurements were taken")
            elif self.all_measurements_done is True:
                messagebox.showinfo("Error", "calkit invalid")
            else:
                messagebox.showinfo("Error", "calkit invalid\n"
                                             "not all measurements were taken")

    def reset_cal_measurements(self):
        self.all_measurements_done = False
        menu = self.cal_options["menu"]
        menu.delete(0, "end")
        for string in self.options:
            menu.add_command(label=string)
        self.calibration_meas_option.set(self.options[0])

    def measure_calibration(self):
        if self.calkit_valid is False:
            messagebox.showinfo("Error", "select valid calkit first")
            return
        if self.calibration_meas_option.get() == "":
            return
        self.measure_button["state"] = "disabled"
        Control.calibration_measure(self.calibration_meas_option.get())
        self.after(500, self.update_after_measurement)

    def update_after_measurement(self):
        if Control.check_calibration_ongoing() is True:
            self.after(500, self.update_after_measurement)
        else:
            self.remove_cal_option()
            if self.calibration_meas_option.get() == "":
                self.all_measurements_done = True
            self.measure_button["state"] = "normal"

    def remove_cal_option(self):
        r_index = self.cal_options['menu'].index(self.calibration_meas_option.get())  # index of selected option.
        self.cal_options['menu'].delete(r_index)  # deleted the option
        self.calibration_meas_option.set(self.cal_options['menu'].entrycget(0, "label"))
