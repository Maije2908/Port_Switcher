import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import Control
import dataToTouchstone


class calibrationFrame(tk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        self.measure_type = kwargs.pop("measure_type")
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.config(width=400)

        # text for type
        tk.Label(self, textvariable=self.measure_type).grid(row=0, column=0)
