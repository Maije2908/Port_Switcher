import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Control


class measureFrame(tk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.config(width=400)

        tk.Button(self, text="Save Measurement", command=self.save_measurement).grid(row=1, column=0)
        self.add_avg_progress_bar()

    def save_measurement(self):
        pass

    def add_avg_progress_bar(self):
        pb = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='indeterminate',
            length=280
        )
        pb.grid(row=0, column=0)

        while True:
            self.after(1000, self.update_progress_bar)

    def update_progress_bar(self):
        pass