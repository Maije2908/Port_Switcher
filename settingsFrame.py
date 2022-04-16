import tkinter as tk
from tkinter import messagebox
import Control


# MAX_POWER = 0 #dBm
# MIN_POWER = -40
# MAX_FREQ = 6000000000 #Hz
# MIN_FREQ = 100000


def determine_freq_factor(postfix):
    if postfix == "kHz":
        return float(1000)
    elif postfix == "MHz":
        return float(1000000)
    elif postfix == "GHz":
        return float(1000000000)
    raise ValueError("no postfix selected")


class settingsFrame(tk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.config(width=200)

        #freq_controls
        self.freq_clicked_max = tk.StringVar()
        self.freq_clicked_min = tk.StringVar()
        self.freq_ent_max = tk.Entry(self)
        self.freq_ent_min = tk.Entry(self)
        self.add_freq_controls()

        #nr_points
        self.points_ent = tk.Entry(self)
        self.add_nr_points()

        tk.Button(self, text="Save Settings", command=self.save_settings).grid(row=3)

    def add_nr_points(self):
        tk.Label(self, text="number of points").grid(row=2, column=0)
        self.points_ent.grid(row=2, column=1)

    def add_freq_controls(self):
        options = [
            "kHz",
            "MHz",
            "GHz",
        ]
        drop_min = tk.OptionMenu(self, self.freq_clicked_min, *options)
        drop_min.config(width=3)
        tk.Label(self, text="start frequency").grid(row=0, column=0)
        self.freq_ent_min.grid(row=0, column=1)
        drop_min.grid(row=0, column=2, sticky="ew")

        drop_max = tk.OptionMenu(self, self.freq_clicked_max, *options)
        drop_max.config(width=3)
        tk.Label(self, text="stop frequency").grid(row=1, column=0)
        self.freq_ent_max.grid(row=1, column=1)
        drop_max.grid(row=1, column=2, sticky="ew")

    def save_settings(self):
        save_succeeded = [True]
        self.save_freq_settings(save_succeeded)
        self.save_nr_points(save_succeeded)

        if save_succeeded[0] is True:
            messagebox.showinfo("Success", "settings saved")
        else:
            error_msg = str()
            for error_entry in save_succeeded[1:]:
                error_msg += error_entry
            messagebox.showinfo("Error", error_msg)

    def save_freq_settings(self, succeeded):

        try:
            max_fac = determine_freq_factor(self.freq_clicked_max.get())
            min_fac = determine_freq_factor(self.freq_clicked_min.get())
            Control.set_min_freq(int(float(self.freq_ent_min.get()) * min_fac))
            Control.set_max_freq(int(float(self.freq_ent_max.get()) * max_fac))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save frequency settings\n")

    def save_nr_points(self, succeeded):
        try:
            Control.set_points(int(self.points_ent.get()))
        except ValueError as e:
            print(e)
            succeeded[0] = False
            succeeded.append("Could not save number of points\n")
