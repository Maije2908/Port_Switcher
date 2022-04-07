import tkinter as tk
import asyncio
import threading
import Scenes

root = tk.Tk()


def main():
    t1 = threading.Thread(target=restart_game)
    t1.setDaemon(True)
    t1.start()
    start_game()


def restart_game():
    global root
    Scenes.restart_sem.acquire()
    Scenes.restart_flag = 1
    root.destroy()


def start_game():
    global root
    Scenes.restart_flag = 0

    scene_countdown = Scenes.SceneCountdown(root=root)
    scene_running = Scenes.SceneRunning(root=root)
    scene_scoreboard = Scenes.SceneScoreboard(root=root)

    Scenes.switch_scene(None, scene_countdown)
    root.after(Scenes.MS_COUNTER, Scenes.switch_scene, scene_countdown, scene_running)
    root.after(Scenes.MS_COUNTER + Scenes.MS_RUNNING, Scenes.switch_scene_score, scene_running, scene_scoreboard)

    root.minsize(width=Scenes.BG_WIDTH, height=Scenes.BG_HEIGHT)
    root.mainloop()
    root = tk.Tk()
    if Scenes.restart_flag:
        t1 = threading.Thread(target=restart_game)
        t1.setDaemon(True)
        t1.start()
        start_game()


if __name__ == '__main__':
    main()
