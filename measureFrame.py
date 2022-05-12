import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Control
import dataToTouchstone


class measureFrame(tk.LabelFrame):

    def __init__(self, parent, measure_type, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.measure_type = measure_type
        self.config(width=400)

        # text for progress
        self.averaging_string = tk.StringVar()
        tk.Label(self, textvariable=self.averaging_string).grid(row=0, column=0)

        # add progressbar
        self.pb = None
        self.add_avg_progress_bar()

        self.save_button = tk.Button(self, text="Save Measurement", command=self.save_measurement)
        self.save_button["state"] = "disabled"
        self.save_button.grid(row=2, column=0)

    def save_measurement(self):
        if self.measure_type == "2-port measurement":
            dataToTouchstone.save_two_port()

    def add_avg_progress_bar(self):
        self.pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=280
        )
        self.pb.grid(row=1, column=0)

        self.after(1000, self.update_progress_bar)

    def update_progress_bar(self):
        try:
            self.pb['value'] = Control.get_avg_done_fraction() * 100
            self.averaging_string.set("averaging:" + Control.get_avg_current() + "/" + Control.get_avg_total())
        except ValueError as e:
            print(e)
        if tk.Toplevel.winfo_exists(self.parent) == False or Control.get_avg_done_fraction() == 1:
            self.save_button["state"] = "normal"
            return
        else:
            self.after(1000, self.update_progress_bar)
