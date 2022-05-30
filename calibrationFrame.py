import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
import Control
import calFileHandler


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


def is_done(done: list):
    for i in range(0, len(done)):
        if done[i] == 0:
            return False

    return True


class calibrationFrame4port(calibrationFrame):
    options_0 = [
        "PORT_1", "PORT_2", "THROUGH"
    ]

    options_1_sol = [
        "SHORT", "OPEN", "LOAD"
    ]

    options_2_through = [
        "PORT_1_2", "PORT_1_3", "PORT_1_4", "PORT_2_3", "PORT_2_4", "PORT_3_4"
    ]

    sol_done = [0, 0, 0]  # 1 if done, short, open, load through
    ports_sol_done = [0, 0]  # 1 if done, port1 sol, port2 sol ... port4 sol
    through_done = [0]

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        # text for type
        tk.Label(self, text="measure type: 4_port measurement").grid(row=0, column=0)

        self.cal_options_0 = None
        self.cal_options_1 = None
        self.cal_options_2 = None
        self.measure_button = None
        self.calibration_meas_option_0 = tk.StringVar(value=self.options_0[0])
        self.calibration_meas_option_0_old_text = self.calibration_meas_option_0.get()
        self.calibration_meas_option_1 = tk.StringVar(value=self.options_1_sol[0])
        self.calibration_meas_option_2 = tk.StringVar(value=self.options_2_through[0])

        # self.calibration_meas_option_0.trace_add('write', self.callback_meas_option_0_changed)

        self.add_cal_options()
        self.add_calibration_measure_buttons()

    def callback_meas_option_0_changed(self, *args):
        if self.calibration_meas_option_0_old_text != "THROUGH":
            if is_done(self.sol_done):
                # set to done
                self.try_set_port_to_done()
                # save one port cal file
                self.save_sol_file()
                # activate new selected port
                if self.calibration_meas_option_0.get() == "THROUGH":
                    self.switch_cal_options_1_2()
            else:
                self.calibration_meas_option_0.set(self.calibration_meas_option_0_old_text)
                self.update_idletasks()
                messagebox.showinfo("Error", "Finish all measurments for the selected port first.")

        else:
            if self.calibration_meas_option_0.get() != "THROUGH":
                self.cal_options_2.grid_forget()
                self.cal_options_1.grid(row=3, column=1)
                self.calibration_meas_option_1.set(self.options_1_sol[0])

        self.calibration_meas_option_0_old_text = self.calibration_meas_option_0.get()

    def callback_meas_option_2_changed(self, *args):
        pass

    def try_set_port_to_done(self):
        if is_done(self.sol_done):
            # set sol of port to done
            index = self.options_0.index(self.calibration_meas_option_0_old_text)
            self.ports_sol_done[index] = 1
            self.reset_sol_done()

    def switch_cal_options_1_2(self):
        self.cal_options_1.grid_forget()
        self.cal_options_2.grid(row=3, column=1)
        self.calibration_meas_option_2.set(self.options_2_through[0])

    def switch_cal_options_2_1(self):
        self.cal_options_2.grid_forget()
        self.cal_options_1.grid(row=3, column=1)
        self.calibration_meas_option_1.set(self.options_1_sol[0])

    def reset_all_done(self):
        self.reset_sol_done()
        for i in range(0, len(self.ports_sol_done)):
            self.ports_sol_done[i] = 0
        for i in range(0, len(self.through_done)):
            self.through_done[i] = 0

    def reset_sol_done(self):
        for i in range(0, len(self.sol_done)):
            self.sol_done[i] = 0

    def disable_menus(self):
        self.cal_options_0.configure(state="disabled")
        self.cal_options_1.configure(state="disabled")
        self.cal_options_2.configure(state="disabled")

    def enable_menus(self):
        self.cal_options_0.configure(state="normal")
        self.cal_options_1.configure(state="normal")
        self.cal_options_2.configure(state="normal")

    def save_sol_file(self):
        actual_port = int((self.options_0.index(self.calibration_meas_option_0_old_text) + 1))
        # find libre port
        calFileHandler.save_sol_file(actual_port, actual_port)

    def save_through_file(self):
        calFileHandler.save_through_file(self.calibration_meas_option_2.get())

    def add_cal_options(self):
        self.cal_options_0 = tk.OptionMenu(self, self.calibration_meas_option_0, *self.options_0,
                                           command=self.callback_meas_option_0_changed)
        self.cal_options_1 = tk.OptionMenu(self, self.calibration_meas_option_1, *self.options_1_sol)
        self.cal_options_2 = tk.OptionMenu(self, self.calibration_meas_option_2, *self.options_2_through,
                                           command=self.callback_meas_option_2_changed)

        self.cal_options_0.grid(row=2, column=1)
        self.cal_options_1.grid(row=3, column=1)

    def add_calibration_measure_buttons(self):

        self.measure_button = tk.Button(self, text="Measure", command=self.measure_calibration)
        self.measure_button.grid(row=3, column=2)
        tk.Button(self, text="Apply Calibration", command=self.apply_calibration).grid(row=4, column=1)
        tk.Button(self, text="Reset Calibration", command=self.reset_cal_measurements).grid(row=4, column=0)

    def apply_calibration(self):
        # merge individual sol files to 6 2port files
        self.try_set_port_to_done()
        if is_done(self.ports_sol_done) and is_done(self.through_done):
            self.all_measurements_done = True
            calFileHandler.merge_into_1_solt_file()
        else:
            messagebox.showinfo("error", "finish all measurements first")

    def reset_cal_measurements(self):
        if self.calibration_meas_option_0.get() == "THROUGH":
            self.switch_cal_options_2_1()

        self.reset_all_done()
        self.calibration_meas_option_0.set(self.options_0[0])
        self.calibration_meas_option_0_old_text = self.options_0[0]
        self.calibration_meas_option_1.set(self.options_1_sol[0])
        self.calibration_meas_option_2.set(self.options_2_through[0])

    def measure_calibration(self):
        if self.calkit_valid is False:
            messagebox.showinfo("Error", "select valid calkit first")
            return

        self.measure_button["state"] = "disabled"
        self.disable_menus()

        Control.calibration_measure(self.get_control_string())

        if self.calibration_meas_option_0.get() != "THROUGH":
            index = self.options_1_sol.index(self.calibration_meas_option_1.get())
            self.sol_done[index] = 1
        else:
            index = self.options_2_through.index(self.calibration_meas_option_2.get())
            self.through_done[index] = 1

        self.after(500, self.update_after_measurement)

    def get_control_string(self):
        # find the 2-port position for the selected 4-port
        return_string = ""
        sel_option_0 = self.calibration_meas_option_0.get()
        sel_option_1 = self.calibration_meas_option_1.get()
        if sel_option_0 == "PORT_1" or sel_option_0 == "PORT_2":
            return_string += (sel_option_0 + "_" + sel_option_1)
        elif sel_option_0 == "PORT_3" or sel_option_0 == "PORT_4":
            pass
        else:
            # through
            return_string += "THROUGH"

        return return_string

    def update_after_measurement(self):
        if Control.check_calibration_ongoing() is True:
            self.after(500, self.update_after_measurement)
        else:
            if self.calibration_meas_option_0.get() == "THROUGH":
                self.save_through_file()
            if is_done(self.ports_sol_done) and is_done(self.through_done):
                self.all_measurements_done = True
            self.measure_button["state"] = "normal"
            self.enable_menus()

    def remove_cal_option(self):
        r_index = self.cal_options['menu'].index(self.calibration_meas_option.get())  # index of selected option.
        self.cal_options['menu'].delete(r_index)  # deleted the option
        self.calibration_meas_option.set(self.cal_options['menu'].entrycget(0, "label"))
