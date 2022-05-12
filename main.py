import tkinter as tk

import Control
import settingsFrame
import measureFrame
import sys


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.settings_frame = settingsFrame.settingsFrame(self, text="settings", pady=5, padx=5)
        self.settings_frame.grid(row=0, column=0)
        self.measure_window = None

    def open_measure_window(self, measure_type):
        self.measure_window = tk.Toplevel(self.parent)
        measureFrame.measureFrame(self.measure_window, measure_type, text="measure", pady=5, padx=5).pack()

    def close_measure_window(self):
        if self.measure_window is not None:
            self.measure_window.destroy()
            self.measure_window.update()
            self.measure_window = None


def main():
    """
    main function that parses argv to for --no-gui option
    inits the libreVNA, sets the window size of the tkinter-gui and instantiates
    the main application, which is basically a frame. Enters mainloop()
    and closes the libreVNA-gui again.
    """
    try:
        if sys.argv[1] == "--no-gui":
            Control.NO_GUI = True
    except IndexError:
        pass
    Control.init_vna()
    root = tk.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h))
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
    Control.close_gui()


if __name__ == "__main__":
    main()