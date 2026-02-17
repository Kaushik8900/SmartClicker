import pyautogui
import time
import tkinter as tk
import keyboard
import threading
import random
import json
import os
import sys
from tkinter import ttk


# ================== SETTINGS ==================

SETTINGS_FILE = "settings.json"
STATIC_TIME = 1.5
HOTKEY = "F6"


# Speed in ms
speed_options = {
    "Very Slow": 500,
    "Slow": 300,
    "Normal": 150,
    "Fast": 80,
    "Ultra Fast": 20,
    "30 CPS": 33
}


pattern_options = [
    "Normal",
    "Burst",
    "Random"
]


# ================== STATE ==================

clicking = False
running = True

click_count = 0
cps_value = 0

stealth_mode = False


# ================== SETTINGS SYSTEM ==================

def load_settings():

    if os.path.exists(SETTINGS_FILE):

        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    return {}


def save_settings():

    data = {
        "speed": selected_speed.get(),
        "pattern": selected_pattern.get(),
        "stealth": stealth_var.get()
    }

    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)


settings = load_settings()


# ================== TOGGLE ==================

def toggle():

    global clicking

    clicking = not clicking

    if clicking:
        status.config(text="Status: ON", fg="green")
    else:
        status.config(text="Status: OFF", fg="red")


# ================== CLICK ENGINE ==================

def get_delay():

    base = speed_options[selected_speed.get()] / 1000

    if stealth_var.get():
        base *= random.uniform(0.8, 1.3)

    return base


def auto_click():

    global running, click_count

    last_x, last_y = pyautogui.position()
    static_start = None

    burst_counter = 0

    while running:

        x, y = pyautogui.position()

        if x == last_x and y == last_y:

            if static_start is None:
                static_start = time.time()

            elapsed = time.time() - static_start

            if elapsed >= STATIC_TIME and clicking:

                pattern = selected_pattern.get()

                # ---------- NORMAL ----------
                if pattern == "Normal":

                    pyautogui.click()
                    click_count += 1
                    time.sleep(get_delay())


                # ---------- BURST ----------
                elif pattern == "Burst":

                    if burst_counter < 5:

                        pyautogui.click()
                        click_count += 1
                        burst_counter += 1
                        time.sleep(0.03)

                    else:
                        time.sleep(0.5)
                        burst_counter = 0


                # ---------- RANDOM ----------
                elif pattern == "Random":

                    pyautogui.click()
                    click_count += 1

                    rand_delay = random.uniform(0.05, 0.3)
                    time.sleep(rand_delay)

        else:
            static_start = None

        last_x, last_y = x, y

        time.sleep(0.003)


# ================== CPS COUNTER ==================

def cps_counter():

    global click_count, cps_value

    while running:

        time.sleep(1)

        cps_value = click_count
        click_count = 0

        cps_label.config(text=f"CPS: {cps_value}")


# ================== GUI ==================

def resource_path(relative_path):
    """ Get absolute path to resource (works for .exe too) """
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.title("GOAT Smart Clicker")
root.iconbitmap(resource_path("smartclicker.ico"))
root.geometry("380x420")
root.resizable(False, False)


# ---------- STATUS ----------
status = tk.Label(
    root,
    text="Status: OFF",
    fg="red",
    font=("Arial", 15, "bold")
)
status.pack(pady=10)


# ---------- CPS ----------
cps_label = tk.Label(
    root,
    text="CPS: 0",
    font=("Arial", 12)
)
cps_label.pack(pady=3)


# ---------- BUTTON ----------
btn = tk.Button(
    root,
    text="Start / Stop (F6)",
    command=toggle,
    width=25,
    height=2
)
btn.pack(pady=10)


# ---------- SPEED ----------
tk.Label(root, text="Click Speed").pack(pady=5)

selected_speed = tk.StringVar()
selected_speed.set(settings.get("speed", "Normal"))

speed_box = ttk.Combobox(
    root,
    textvariable=selected_speed,
    values=list(speed_options.keys()),
    state="readonly",
    width=18
)
speed_box.pack()


# ---------- PATTERN ----------
tk.Label(root, text="Click Pattern").pack(pady=5)

selected_pattern = tk.StringVar()
selected_pattern.set(settings.get("pattern", "Normal"))

pattern_box = ttk.Combobox(
    root,
    textvariable=selected_pattern,
    values=pattern_options,
    state="readonly",
    width=18
)
pattern_box.pack()


# ---------- STEALTH ----------
stealth_var = tk.BooleanVar()
stealth_var.set(settings.get("stealth", False))

stealth_check = tk.Checkbutton(
    root,
    text="Stealth Mode (Human-like)",
    variable=stealth_var,
    command=save_settings
)

stealth_check.pack(pady=10)


# ---------- INFO ----------
info = tk.Label(
    root,
    text="Keep mouse still to activate\nF6 = Toggle",
    fg="gray"
)
info.pack(pady=10)


# ---------- SAVE BUTTON ----------
save_btn = tk.Button(
    root,
    text="Save Settings",
    command=save_settings,
    width=18
)
save_btn.pack(pady=5)


# ================== HOTKEY ==================

keyboard.add_hotkey(HOTKEY, toggle)


# ================== THREADS ==================

threading.Thread(target=auto_click, daemon=True).start()
threading.Thread(target=cps_counter, daemon=True).start()


# ================== CLOSE ==================

def on_close():

    global running

    running = False
    save_settings()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)


# ================== START ==================

root.mainloop()
