import tkinter as tk
import random
import Scoreboard
import threading

BG_WIDTH = 1200
BG_HEIGHT = 800

MS_COUNTER = 5000
MS_RUNNING = 20000

restart_sem = threading.Semaphore(0)
restart_flag = 0


def switch_scene(old_scene, new_scene):
    if old_scene is not None:
        old_scene.destroy()

    new_scene.start()


def switch_scene_score(old_scene, new_scene):
    old_scene.destroy()
    new_scene.score = old_scene.nr_clicked
    new_scene.start()


class Scene:

    def __init__(self, **kwargs):
        self.root = kwargs.pop('root')
        self.frame = tk.Frame(self.root)
        self.bg = tk.PhotoImage(master=self.root, file="5507878.png")
        self.my_label = tk.Label(self.frame, image=self.bg)
        self.my_label.place(x=0, y=0, relwidth=1, relheight=1)

    def start(self):
        raise NotImplementedError

    def destroy(self):
        self.frame.pack_forget()
        self.frame.destroy()


class SceneCountdown(Scene):
    def __init__(self, **kwargs):
        Scene.__init__(self, **kwargs)

    def start(self):
        self.init_countdown()

    def init_countdown(self):
        self.frame.pack(fill='both', expand=1)
        seconds = (MS_COUNTER / 1000) - 1
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
        self.seconds_left = MS_RUNNING / 1000
        self.init_button_timer()

    def start(self):
        self.frame.pack(fill='both', expand=1)
        self.update_seconds()

    def init_button_timer(self):
        self.click_btn = tk.PhotoImage(master=self.root, file='choke.png')
        self.common_mode_choke = tk.Button(self.frame, image=self.click_btn, bd='3',
                                           command=self.clicked_button)
        self.common_mode_choke.place(x=random.randint(0, BG_WIDTH), y=random.randint(0, BG_HEIGHT))
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
        self.common_mode_choke.place(x=random.randint(0, BG_WIDTH), y=random.randint(0, BG_HEIGHT))


class SceneScoreboard(Scene):
    def __init__(self, **kwargs):
        Scene.__init__(self, **kwargs)
        self.label_score = tk.Label(self.frame, text="score: ")
        self.score = None

    def start(self):
        self.frame.pack(fill='both', expand=1)
        self.label_score.config(text="score: " + str(self.score))
        self.label_score.pack()
        self.add_exit_try_again()
        if Scoreboard.is_highscore(self.score):
            self.show_new_highscore()
            self.handle_new_highscore()
        else:
            self.show_highscore_list()

    def show_new_highscore(self):
        tk.Label(self.frame,
                 text="NEW HIGHSCORE!!",
                 fg="blue",
                 bg="yellow",
                 font="Verdana 20 bold").pack(pady=30)

    def handle_new_highscore(self):
        enter_name = tk.Label(self.frame,
                              text="Enter Your Name",
                              font="Verdana 10 bold")
        enter_name.pack(pady=5)
        entry = tk.Entry(self.frame, borderwidth=5)
        entry.pack(pady=5)
        save_button = tk.Button(self.frame, text="Add to highscore list",
                                command=lambda: self.save_and_switch_to_highscore_list(entry.get(), save_button, entry,
                                                                                       enter_name))
        save_button.pack(pady=5)

    def save_and_switch_to_highscore_list(self, user_name, save_button, entry, enter_name):
        save_button.pack_forget()
        entry.pack_forget()
        enter_name.pack_forget()
        Scoreboard.save_highscore(user_name, self.score)
        self.show_highscore_list()

    def show_highscore_list(self):
        highscores = Scoreboard.get_all_highscores()
        tk.Label(self.frame,
                 text="HIGHSCORE LIST",
                 fg="white",
                 bg="red",
                 font="Verdana 20 bold").pack(pady=50)
        for highscore in highscores:
            text = "Name: " + highscore[0] + " Score: " + str(highscore[1])
            tk.Label(self.frame,
                     text=text,
                     fg="white",
                     bg="red",
                     font="Verdana 12 bold").pack(pady=5)

    def add_exit_try_again(self):
        exit_button = tk.Button(self.frame, text="exit", command=self.root.destroy)
        exit_button.pack(pady=5, side='bottom')

        again_button = tk.Button(self.frame, text="Try Again", command=signal_restart)
        again_button.pack(pady=5, side='bottom')


def signal_restart():
    restart_sem.release()
