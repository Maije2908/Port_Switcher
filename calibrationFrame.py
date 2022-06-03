import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox
import Control
import calFileHandler


def get_calkit_options_from_folder() -> list[str]:
    """
    gets the name of the calkit files from folder CALKITS
    :returns a list of strings containing the names of the calkit files
    """

    calkit_files = list(filter(lambda x: x.endswith('.calkit'), os.listdir('CALKITS')))
    calkit_files[:] = [elem.replace(".calkit", "") for elem in calkit_files]
    calkit_files.append("NO CAL-KIT")
    return calkit_files


class calibrationFrame(tk.LabelFrame):
    """
    base class to provide the calibration functionality in one gui frame
    """


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


    def callback_calkit_changed(self, var, index, mode):
        """
        callback function that runs whenever a different calkit gets selected
        """

        # reset current measurements
        if self.__class__.__name__ == "calibrationFrame2port":
            calibrationFrame2port.reset_cal_measurements(self)
        else:
            calibrationFrame4port.reset_cal_measurements(self)


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
        """
        adds the OptionMenu for the cal-kit selection
        """
        options = get_calkit_options_from_folder()

        tk.Label(self, text="select cal-kit").grid(row=1, column=0)
        tk.OptionMenu(self, self.calkit_selection, *options).grid(row=1, column=1)


class calibrationFrame2port(calibrationFrame):
    """
    derived 2port calibration class
    """

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
        self.add_calibration_measure_options()

    def add_calibration_measure_options(self):
        """
        adds the OptionMenu for the different calibration measurements, the measure button,
        the reset button which restores the measurement options,
        aswell as the apply button, which checks if all measurements are done,
        if the calkit is valid and closes the window.
        """

        self.cal_options = tk.OptionMenu(self, self.calibration_meas_option, *self.options)
        self.cal_options.grid(row=2, column=0)
        self.measure_button = tk.Button(self, text="Measure", command=self.measure_calibration)
        self.measure_button.grid(row=2, column=1)
        tk.Button(self, text="Apply Calibration", command=self.apply_calibration).grid(row=3, column=1)
        tk.Button(self, text="Reset Calibration", command=self.reset_cal_measurements).grid(row=3, column=0)

    def apply_calibration(self):
        """
        routine invoked by the apply button. prints the corresponding error messages if calkit is invalid,
        or not all measurements were taken, else sets the calibration type to SOLT and closes the calibration
        window.
        """
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
        """
        set all measurements done to false and restore the cal-measurement options in the OptionMenu
        """
        self.all_measurements_done = False
        menu = self.cal_options["menu"]
        menu.delete(0, "end")
        for string in self.options:
            menu.add_command(label=string)
        self.calibration_meas_option.set(self.options[0])

    def measure_calibration(self):
        """
        first check if calkit is valid and return if invalid.
        Do nothing if all measurements have been taken already.
        measure the currently selected calibration measurement and set the measure button
        to disabled while measurement is ongoing. Invoke update_after_measurement while
        cal measurement is ongoing.
        """
        if self.calkit_valid is False:
            messagebox.showinfo("Error", "select valid calkit first")
            return
        if self.calibration_meas_option.get() == "":
            return
        self.measure_button["state"] = "disabled"
        Control.calibration_measure(self.calibration_meas_option.get())
        self.after(500, self.update_after_measurement)

    def update_after_measurement(self):
        """
        Checks wheter the cal-measurement has finished or not. If not the function will be invoked by event queue
        after 500ms again. If finished the currently selected measurement option gets removed from the OptionMenu.
        If the option menu is empty all measurements were taken.
        """
        if Control.check_calibration_ongoing() is True:
            self.after(500, self.update_after_measurement)
        else:
            self.remove_cal_option()
            if self.calibration_meas_option.get() == "":
                self.all_measurements_done = True
            self.measure_button["state"] = "normal"

    def remove_cal_option(self):
        """
        removes the currently selected cal-measurement option from the menu.
        """
        r_index = self.cal_options['menu'].index(self.calibration_meas_option.get())  # index of selected option.
        self.cal_options['menu'].delete(r_index)  # deleted the option
        self.calibration_meas_option.set(self.cal_options['menu'].entrycget(0, "label"))


def is_done(done: list):
    """
    mainly used in calibrationFrame4port. iterates through a "done" list and if all entries are 1 True is returned
    :param done: a list of zeroes or ones indicating if the corresponding measurement was done or not.
    :return: True if all entries are 1 -> indicating done, False else
    """
    for i in range(0, len(done)):
        if done[i] == 0:
            return False

    return True


class calibrationFrame4port(calibrationFrame):
    """
    derived 4port calibration class
    """
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
        self.add_calibration_measure_options()

    def callback_meas_option_0_changed(self, *args):
        """
        callback function that is invoked if meas_option_0 changes (Port Selection or Through)
        :param args: trace_add provides args for callback function but not used here
        """
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
        """
        if short open load is done the whole port will be set to done
        """
        if is_done(self.sol_done):
            # set sol of port to done
            index = self.options_0.index(self.calibration_meas_option_0_old_text)
            self.ports_sol_done[index] = 1
            self.reset_sol_done()

    def switch_cal_options_1_2(self):
        """
        Switches the OptionMenu containing Short, Open, Load to the OptionMenu
        containing the different Trough combinations to be displayed on the screen.
        """
        self.cal_options_1.grid_forget()
        self.cal_options_2.grid(row=3, column=1)
        self.calibration_meas_option_2.set(self.options_2_through[0])

    def switch_cal_options_2_1(self):
        """
        Switches the OptionMenu containing the different Trough combinations to the OptionMenu
        containing Short, Open, Load to be displayed on the screen.
        """
        self.cal_options_2.grid_forget()
        self.cal_options_1.grid(row=3, column=1)
        self.calibration_meas_option_1.set(self.options_1_sol[0])

    def reset_all_done(self):
        """
        resets all done flags
        """
        self.reset_sol_done()
        for i in range(0, len(self.ports_sol_done)):
            self.ports_sol_done[i] = 0
        for i in range(0, len(self.through_done)):
            self.through_done[i] = 0

    def reset_sol_done(self):
        """
        resets done flags for short open load
        """
        for i in range(0, len(self.sol_done)):
            self.sol_done[i] = 0

    def disable_menus(self):
        """
        disables OptionMenus that should not be changed during measurement
        """
        self.cal_options_0.configure(state="disabled")
        self.cal_options_1.configure(state="disabled")
        self.cal_options_2.configure(state="disabled")

    def enable_menus(self):
        """
        enables OptionMenus that can changed after measurement
        """
        self.cal_options_0.configure(state="normal")
        self.cal_options_1.configure(state="normal")
        self.cal_options_2.configure(state="normal")

    def save_sol_file(self):
        """
        saves the SOL measurements to .cal file for one port.
        """
        actual_port = int((self.options_0.index(self.calibration_meas_option_0_old_text) + 1))
        # find libre port
        calFileHandler.save_sol_file(actual_port, actual_port)

    def save_through_file(self):
        """
        saves the Through measurement between two ports to file.
        """
        calFileHandler.save_through_file(self.calibration_meas_option_2.get())

    def add_cal_options(self):
        """
        creates and adds all the OptionMenus to the frame.
        """
        self.cal_options_0 = tk.OptionMenu(self, self.calibration_meas_option_0, *self.options_0,
                                           command=self.callback_meas_option_0_changed)
        self.cal_options_1 = tk.OptionMenu(self, self.calibration_meas_option_1, *self.options_1_sol)
        self.cal_options_2 = tk.OptionMenu(self, self.calibration_meas_option_2, *self.options_2_through,
                                           command=self.callback_meas_option_2_changed)

        self.cal_options_0.grid(row=2, column=1)
        self.cal_options_1.grid(row=3, column=1)

    def add_calibration_measure_options(self):
        """
        creates and adds the Measure, Apply and Reset button
        """

        self.measure_button = tk.Button(self, text="Measure", command=self.measure_calibration)
        self.measure_button.grid(row=3, column=2)
        tk.Button(self, text="Apply Calibration", command=self.apply_calibration).grid(row=4, column=1)
        tk.Button(self, text="Reset Calibration", command=self.reset_cal_measurements).grid(row=4, column=0)

    def apply_calibration(self):
        """
        Apply function that is run on Apply button beeing clicked.
        If all measurements are taken the calFileHandler merges the .cal files into
        six SOLT files that get loaded during the 4 port measurement.
        """
        # merge individual sol files to 6 2port files
        self.try_set_port_to_done()
        if is_done(self.ports_sol_done) and is_done(self.through_done):
            self.all_measurements_done = True
            calFileHandler.merge_into_1_solt_file()
        else:
            messagebox.showinfo("error", "finish all measurements first")

    def reset_cal_measurements(self):
        """
        function invoked when calkit gets changed or Reset button pressed
        """
        self.all_measurements_done = False

        if self.calibration_meas_option_0.get() == "THROUGH":
            self.switch_cal_options_2_1()

        self.reset_all_done()
        self.calibration_meas_option_0.set(self.options_0[0])
        self.calibration_meas_option_0_old_text = self.options_0[0]
        self.calibration_meas_option_1.set(self.options_1_sol[0])
        self.calibration_meas_option_2.set(self.options_2_through[0])

    def measure_calibration(self):
        """
        starts a calibration measurement and disables the Measure button and the corresponding OptionMenus
        Sets the correct done flags and queues the update_after_measurement.
        """
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
        """
        finds the parameters that are passed to Control to do the correct measurement.
        """
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
        """
        function that periodically checks if measurement is finished after measure button was pressed and
        when finished it saves a .cal file if through was selected and updates the done status aswell as the menus
        """
        if Control.check_calibration_ongoing() is True:
            self.after(500, self.update_after_measurement)
        else:
            if self.calibration_meas_option_0.get() == "THROUGH":
                self.save_through_file()
            if is_done(self.ports_sol_done) and is_done(self.through_done):
                self.all_measurements_done = True
            self.measure_button["state"] = "normal"
            self.enable_menus()
