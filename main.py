import threading
import tkinter as tk
import Scenes
import time

root = tk.Tk()

scene_countdown = Scenes.SceneCountdown(root=root)
scene_running = Scenes.SceneRunning(root=root)
scene_scoreboard = Scenes.SceneScoreboard(root=root)


def main():
    init_game()
    root.minsize(width=Scenes.bg_width, height=Scenes.bg_height)
    root.mainloop()


def init_game():
    Scenes.switch_scene(None, scene_countdown)
    root.after(Scenes.ms_counter, Scenes.switch_scene, scene_countdown, scene_running)
    root.after(Scenes.ms_counter + Scenes.ms_running, Scenes.switch_scene_score, scene_running, scene_scoreboard)


if __name__ == '__main__':
    main()
