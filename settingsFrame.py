import tkinter as tk
from tkinter import messagebox
import Control
import main


def determine_freq_factor(postfix: str) -> float:
    """
    transform the string postfix of the frequency to a numerical factor
    :param postfix: str containing the unit of the frequency
    :return: float representing the factor for multiplication with
    the textfield value. float because the textfield value can contain
    a decimal point
    """
    if postfix == "kHz":
        return float(1000)
    elif postfix == "MHz":
        return float(1000000)
    elif postfix == "GHz":
        return float(1000000000)
    raise ValueError("no postfix selected")


def show_bounds():
    """
    opens a messagebox that informs the user about possible values
    """
    bounds = "frequency range: 100kHz - 6GHz\n" \
             "number of points: 2 - 4501\n" \
             "bandwidth: 10Hz - 50kHz\n" \
             "power level: -40dBm - 0dBm\n" \
             "average over: 1 - 99"
    messagebox.showinfo("Bounds Info", bounds)


class settingsFrame(tk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.config(width=200)

        # freq_controls
        self.CENTER_SPAN = False
        self.start_freq_label = tk.Label(self, text="start frequency")
        self.stop_freq_label = tk.Label(self, text="stop frequency")
        self.center_freq_label = tk.Label(self, text="center frequency")
        self.span_freq_label = tk.Label(self, text="span frequency")
        self.freq_clicked_0 = tk.StringVar()
        self.freq_clicked_1 = tk.StringVar()
        self.freq_ent_max = tk.Entry(self)
        self.freq_ent_min = tk.Entry(self)
        self.add_freq_controls()

        # nr_points
        self.points_ent = tk.Entry(self)
        self.add_nr_points()

        # bandwidth
        self.bandwidth_ent = tk.Entry(self)
        self.add_bandwidth()

        # power level
        self.power_ent = tk.Entry(self)
        self.add_power()

        # average over
        self.average_ent = tk.Entry(self)
        self.add_average()

        # measurement type
        self.measurement_type = tk.StringVar()
        self.add_measurement_type()

        tk.Button(self, text="Save Settings", command=self.save_settings).grid(row=7, column=0)
        tk.Button(self, text="Bounds Info", command=show_bounds).grid(row=7, column=2)
        tk.Button(self, text="Switch Frequency", command=self.switch_freq_input).grid(row=7, column=1)
        tk.Button(self, text="Load Calib. (testing only)"
                  , command=lambda: Control.load_calibration("CAL/PORT12.cal")).grid(row=8)

    def switch_freq_input(self):
        """
        switches frequency labels between center/span and start/stop and sets a class member flag,
        so that the corresponding Control function is invoked when pressing the "Save Settings" button
        """
        if not self.CENTER_SPAN:  # switch to center/span
            print("switch to center/span")
            self.CENTER_SPAN = True
            self.start_freq_label.grid_remove()
            self.stop_freq_label.grid_remove()
            self.center_freq_label.grid(row=0, column=0)
            self.span_freq_label.grid(row=1, column=0)
        else:  # switch to start stop
            print("switch to start stop")
            self.CENTER_SPAN = False
            self.center_freq_label.grid_remove()
            self.span_freq_label.grid_remove()
            self.start_freq_label.grid(row=0, column=0)
            self.stop_freq_label.grid(row=1, column=0)

    def add_measurement_type(self):
        options = [
            "2-port measurement",
            "4-port measurement", ]
        tk.Label(self, text="measurement type").grid(row=6, column=0)
        self.measurement_type.set("2-port measurement")
        drop_type = tk.OptionMenu(self, self.measurement_type, *options)
        drop_type.grid(row=6, column=1)

    def add_average(self):
        """
        places average label and entry
        """
        tk.Label(self, text="average over").grid(row=5, column=0, padx=5, pady=5)
        self.average_ent.grid(row=5, column=1)

    def add_power(self):
        """
        places power label and entry
        """
        tk.Label(self, text="power level dBm").grid(row=4, column=0, padx=5, pady=5)
        self.power_ent.grid(row=4, column=1)

    def add_bandwidth(self):
        """
        places bandwidth label and entry
        """
        tk.Label(self, text="bandwidth Hz").grid(row=3, column=0, padx=5, pady=5)
        self.bandwidth_ent.grid(row=3, column=1)

    def add_nr_points(self):
        """
        places nr_points label and entry
        """
        tk.Label(self, text="number of points").grid(row=2, column=0, padx=5, pady=5)
        self.points_ent.grid(row=2, column=1)

    def add_freq_controls(self):
        """
        places default frequency labels (start/stop) as well as entries and drop down menus for the postfix
        """
        options = [
            "kHz",
            "MHz",
            "GHz",
        ]
        drop_min = tk.OptionMenu(self, self.freq_clicked_0, *options)
        drop_min.config(width=3)
        self.start_freq_label.grid(row=0, column=0)
        self.freq_ent_min.grid(row=0, column=1)
        drop_min.grid(row=0, column=2, sticky="ew")

        drop_max = tk.OptionMenu(self, self.freq_clicked_1, *options)
        drop_max.config(width=3)
        self.stop_freq_label.grid(row=1, column=0)
        self.freq_ent_max.grid(row=1, column=1)
        drop_max.grid(row=1, column=2, sticky="ew")

    def save_settings(self):
        """
        Invokes save method of each parameter, passes a list called save_succeeded to each
        save function. First entry of the list is set to false if a parameter save function fails and
        an error message is appended to the list. At the end the result, including the error messages,
        is displayed in a message box.
        """
        self.parent.close_measure_window()
        save_succeeded = [True]
        self.save_freq_settings(save_succeeded)
        self.save_nr_points(save_succeeded)
        self.save_bandwidth(save_succeeded)
        self.save_power(save_succeeded)
        self.save_average(save_succeeded)

        if save_succeeded[0] is True:
            messagebox.showinfo("Success", "settings saved")
            self.parent.open_measure_window()


        else:
            error_msg = str()
            for error_entry in save_succeeded[1:]:
                error_msg += error_entry
            messagebox.showinfo("Error", error_msg)

    def save_freq_settings(self, succeeded: list):
        """
        tries to save frequency settings distinguishing between center/span and start/stop.
        If Control's setter functions fail a ValueError is thrown and this is noted in the
        succeeded list.
        """
        try:
            first_fac = determine_freq_factor(self.freq_clicked_0.get())
            second_fac = determine_freq_factor(self.freq_clicked_1.get())
            if self.CENTER_SPAN:
                Control.set_center_freq(int(float(self.freq_ent_min.get()) * first_fac))
                Control.set_span_freq(int(float(self.freq_ent_max.get()) * second_fac))
            else:
                Control.set_min_freq(int(float(self.freq_ent_min.get()) * first_fac))
                Control.set_max_freq(int(float(self.freq_ent_max.get()) * second_fac))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save frequency settings\n")

    def save_nr_points(self, succeeded: list):
        """
        tries to save nr_points setting. If Control's setter functions fail a ValueError is thrown
        and this is noted in the succeeded list.
        """
        try:
            Control.set_points(int(self.points_ent.get()))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save number of points\n")

    def save_bandwidth(self, succeeded: list):
        """
        tries to save the bandwidth setting. If Control's setter functions fail a ValueError is thrown
        and this is noted in the succeeded list.
        """
        try:
            Control.set_bandwidth(int(self.bandwidth_ent.get()))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save number of points\n")

    def save_power(self, succeeded: list):
        """
        tries to save the power setting. If Control's setter functions fail a ValueError is thrown
        and this is noted in the succeeded list.
        """
        try:
            Control.set_power(float(self.power_ent.get()))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save power level\n")

    def save_average(self, succeeded: list):
        """
        tries to save average over setting. If Control's setter functions fail a ValueError is thrown
        and this is noted in the succeeded list.
        """
        try:
            Control.set_average(int(self.average_ent.get()))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save average\n")
