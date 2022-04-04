import tkinter as tk
import random

bg_width = 1200
bg_height = 800

ms_counter = 6000
ms_running = 20000


def switch_scene(old_scene, new_scene):
    if old_scene is not None:
        old_scene.frame.pack_forget()

    new_scene.start()


def switch_scene_score(old_scene, new_scene):
    old_scene.frame.pack_forget()
    new_scene.score = old_scene.nr_clicked
    new_scene.start()


class Scene:

    def __init__(self, **kwargs):
        self.root = kwargs.pop('root')
        self.frame = tk.Frame(self.root)
        self.bg = tk.PhotoImage(file="5507878.png")
        self.my_label = tk.Label(self.frame, image=self.bg)
        self.my_label.place(x=0, y=0, relwidth=1, relheight=1)

    def start(self):
        raise NotImplementedError


class SceneCountdown(Scene):
    def __init__(self, **kwargs):
        Scene.__init__(self, **kwargs)

    def start(self):
        self.init_countdown()

    def init_countdown(self):
        self.frame.pack(fill='both', expand=1)
        seconds = 5
        countdown = tk.Label(self.frame, text="Game Starts In: " + str(seconds))
        countdown.pack()
        self.root.after(0, self.decrement_countdown, seconds, countdown)

    def decrement_countdown(self, seconds, countdown):
        if seconds < 1:
            countdown.config(text="Let's Go")
            return
        countdown.config(text="Game Starts In: " + str(seconds))
        self.root.after(1000, self.decrement_countdown, seconds - 1, countdown)


class SceneRunning(Scene):
    common_mode_choke = None
    nr_clicked = 0
    label_clicked = None
    label_timer = None
    click_btn = None

    def __init__(self, **kwargs):
        Scene.__init__(self, **kwargs)
        self.seconds_left = ms_running / 1000
        self.init_button_timer()

    def start(self):
        self.frame.pack(fill='both', expand=1)
        self.update_seconds()

    def init_button_timer(self):
        self.click_btn = tk.PhotoImage(file='choke.png')
        self.common_mode_choke = tk.Button(self.frame, image=self.click_btn, bd='10',
                                           command=self.clicked_button)
        self.common_mode_choke.place(x=random.randint(0, bg_width), y=random.randint(0, bg_height))
        self.label_clicked = tk.Label(self.frame, text="clicked " + str(self.nr_clicked) + " times")
        self.label_clicked.pack()
        self.label_timer = tk.Label(self.frame, text="seconds left: " + str(self.seconds_left))
        self.label_timer.pack()

    def update_seconds(self):
        if self.seconds_left < 1:
            return
        self.label_timer.config(text="seconds left: " + str(self.seconds_left))
        self.seconds_left = self.seconds_left - 1
        self.root.after(1000, self.update_seconds)

    def clicked_button(self):
        self.nr_clicked = self.nr_clicked + 1
        self.label_clicked.config(text="clicked " + str(self.nr_clicked) + " times")
        self.label_clicked.pack()
        self.common_mode_choke.place(x=random.randint(0, bg_width), y=random.randint(0, bg_height))


class SceneScoreboard(Scene):
    def __init__(self, **kwargs):
        Scene.__init__(self, **kwargs)
        self.label_score = tk.Label(self.frame, text="score: ")
        self.score = None

    def start(self):
        self.frame.pack(fill='both', expand=1)
        self.label_score.config(text="score: " + str(self.score))
        self.label_score.pack()
