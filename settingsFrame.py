import tkinter as tk
from tkinter import messagebox
import Control

MAX_POWER = 0 #dBm
MIN_POWER = -40
MAX_FREQ = 6000000000 #Hz
MIN_FREQ = 100000


def determine_freq_factor(postfix):
    if postfix == "kHz":
        return int(1000)
    elif postfix == "MHz":
        return int(1000000)
    elif postfix == "GHz":
        return int(1000000000)
    raise ValueError("no postfix selected")


class settingsFrame(tk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.config(width=200)

        self.freq_clicked_max = tk.StringVar()
        self.freq_clicked_min = tk.StringVar()
        self.freq_ent_max = tk.Entry(self)
        self.freq_ent_min = tk.Entry(self)

        self.add_freq_controls()
        tk.Button(self, text="Save Settings", command=self.save_settings).grid(row=2)

    def add_freq_controls(self):
        options = [
            "kHz",
            "MHz",
            "GHz",
        ]
        drop_min = tk.OptionMenu(self, self.freq_clicked_min, *options)
        drop_min.config(width=3)
        tk.Label(self, text="min frequency").grid(row=0, column=0)
        self.freq_ent_min.grid(row=0, column=1)
        drop_min.grid(row=0, column=2, sticky="ew")

        drop_max = tk.OptionMenu(self, self.freq_clicked_max, *options)
        drop_max.config(width=3)
        tk.Label(self, text="max frequency").grid(row=1, column=0)
        self.freq_ent_max.grid(row=1, column=1)
        drop_max.grid(row=1, column=2, sticky="ew")

    def save_settings(self):
        save_succeeded = [True]
        self.save_freq_settings(save_succeeded)

        messagebox.showinfo("showinfo", "Information")

    def save_freq_settings(self, succeeded):

        try:
            max_fac = determine_freq_factor(self.freq_clicked_max.get())
            min_fac = determine_freq_factor(self.freq_clicked_min.get())
            Control.set_min_freq(int(self.freq_ent_min.get()) * min_fac)
            Control.set_max_freq(int(self.freq_ent_max.get()) * max_fac)
        except ValueError:
            succeeded.pop()
            succeeded.append(False)
            print("Valueerror")
