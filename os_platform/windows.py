import pyautogui
import subprocess
import os
import time

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.0


def next_tab():        pyautogui.hotkey("ctrl", "tab")
def prev_tab():        pyautogui.hotkey("ctrl", "shift", "tab")
def new_tab():         pyautogui.hotkey("ctrl", "t")
def close_tab():       pyautogui.hotkey("ctrl", "w")
def browser_back():    pyautogui.hotkey("alt", "left")
def browser_forward(): pyautogui.hotkey("alt", "right")
def refresh_page():    pyautogui.hotkey("ctrl", "r")

def scroll_up(amount=3):   pyautogui.scroll(amount)
def scroll_down(amount=3): pyautogui.scroll(-amount)

def zoom_in():    pyautogui.hotkey("ctrl", "+")
def zoom_out():   pyautogui.hotkey("ctrl", "-")
def zoom_reset(): pyautogui.hotkey("ctrl", "0")

def media_play_pause(): pyautogui.press("playpause")
def media_next():       pyautogui.press("nexttrack")
def media_previous():   pyautogui.press("prevtrack")
def volume_up():        pyautogui.press("volumeup")
def volume_down():      pyautogui.press("volumedown")
def volume_mute():      pyautogui.press("volumemute")

def switch_window():              pyautogui.hotkey("alt", "tab")
def minimize_window():            pyautogui.hotkey("win", "down")
def maximize_window():            pyautogui.hotkey("win", "up")
def show_desktop():               pyautogui.hotkey("win", "d")
def switch_virtual_desktop_left():  pyautogui.hotkey("ctrl", "win", "left")
def switch_virtual_desktop_right(): pyautogui.hotkey("ctrl", "win", "right")
def close_window():               pyautogui.hotkey("alt", "f4")

def undo():       pyautogui.hotkey("ctrl", "z")
def redo():       pyautogui.hotkey("ctrl", "y")
def copy():       pyautogui.hotkey("ctrl", "c")
def paste():      pyautogui.hotkey("ctrl", "v")
def select_all(): pyautogui.hotkey("ctrl", "a")

def take_screenshot():
    ts   = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(os.path.expanduser("~"), "Desktop", f"gesture_{ts}.png")
    pyautogui.screenshot(path)
    print(f"[Windows] Screenshot → {path}")

def open_application(path): subprocess.Popen(path, shell=True)


ACTION_MAP = {
    "next_tab": next_tab, "prev_tab": prev_tab, "new_tab": new_tab,
    "close_tab": close_tab, "browser_back": browser_back,
    "browser_forward": browser_forward, "refresh_page": refresh_page,
    "scroll_up": scroll_up, "scroll_down": scroll_down,
    "zoom_in": zoom_in, "zoom_out": zoom_out, "zoom_reset": zoom_reset,
    "media_play_pause": media_play_pause, "media_next": media_next,
    "media_previous": media_previous, "volume_up": volume_up,
    "volume_down": volume_down, "volume_mute": volume_mute,
    "switch_window": switch_window, "minimize_window": minimize_window,
    "maximize_window": maximize_window, "show_desktop": show_desktop,
    "switch_virtual_desktop_left": switch_virtual_desktop_left,
    "switch_virtual_desktop_right": switch_virtual_desktop_right,
    "close_window": close_window, "take_screenshot": take_screenshot,
    "undo": undo, "redo": redo, "copy": copy, "paste": paste,
    "select_all": select_all,
}


def execute(action_name: str):
    fn = ACTION_MAP.get(action_name)
    if fn:
        fn()
    else:
        print(f"[Windows] Unknown action: {action_name}")