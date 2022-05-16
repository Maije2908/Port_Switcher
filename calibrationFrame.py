import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Control
import dataToTouchstone


class calibrationFrame(tk.LabelFrame):

    def __init__(self, parent, measure_type, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.measure_type = measure_type
        self.config(width=400)

        # text for type
        tk.Label(self, text="measure type: ").grid(row=0, column=0)
        tk.Label(self, text="type", textvariable=self.measure_type).grid(row=0, column=1)

