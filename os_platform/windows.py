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

def switch_window_left():
    """Switch to previous window (Alt+Shift+Tab)"""
    pyautogui.hotkey("alt", "shift", "tab")

def switch_window_right():
    """Switch to next window (Alt+Tab)"""
    pyautogui.hotkey("alt", "tab")


# =====================================================================
# Cyclic window switcher (Win32 via ctypes - no pywin32 required)
#
# Cycles through ALL open windows in a stable order, one step per call,
# wrapping back to the first after the last. Unlike Alt+Tab this does
# NOT bounce between the two most recent windows.
# =====================================================================

import ctypes as _ctypes
from ctypes import wintypes as _wt
import ctypes.wintypes as _wtw

_user32 = _ctypes.windll.user32

_ENUMPROC = _ctypes.WINFUNCTYPE(_wt.BOOL, _wt.HWND, _wt.LPARAM)

_user32.IsWindowVisible.argtypes      = [_wt.HWND]
_user32.IsWindowVisible.restype       = _wt.BOOL
_user32.IsIconic.argtypes             = [_wt.HWND]
_user32.IsIconic.restype              = _wt.BOOL
_user32.IsWindow.argtypes             = [_wt.HWND]
_user32.IsWindow.restype              = _wt.BOOL
_user32.GetWindowTextLengthW.argtypes = [_wt.HWND]
_user32.GetWindowTextLengthW.restype  = _ctypes.c_int
_user32.GetWindowTextW.argtypes       = [_wt.HWND, _wt.LPWSTR, _ctypes.c_int]
_user32.GetWindowTextW.restype        = _ctypes.c_int
_user32.GetClassNameW.argtypes        = [_wt.HWND, _wt.LPWSTR, _ctypes.c_int]
_user32.GetClassNameW.restype         = _ctypes.c_int
_user32.ShowWindow.argtypes           = [_wt.HWND, _ctypes.c_int]
_user32.ShowWindow.restype            = _wt.BOOL
_user32.SwitchToThisWindow.argtypes   = [_wt.HWND, _wt.BOOL]
_user32.SwitchToThisWindow.restype    = _ctypes.c_void_p
_user32.SetForegroundWindow.argtypes  = [_wt.HWND]
_user32.SetForegroundWindow.restype   = _wt.BOOL
_user32.GetForegroundWindow.argtypes  = []
_user32.GetForegroundWindow.restype   = _wt.HWND
_user32.EnumWindows.argtypes          = [_ENUMPROC, _wt.LPARAM]
_user32.EnumWindows.restype           = _wt.BOOL

_SKIP_CLASSES = {
    "Shell_TrayWnd", "Shell_SecondaryTrayWnd", "Progman", "WorkerW",
    "TaskListThumbnailWnd",
}

_DWMWA_CLOAKED = 14
_GWL_EXSTYLE   = -20
_WS_EX_TOOLWINDOW = 0x00000080

_dwmapi        = _ctypes.windll.dwmapi
_dwmapi.DwmGetWindowAttribute.argtypes = [_wt.HWND, _wt.DWORD,
                                          _ctypes.c_void_p, _wt.DWORD]
_dwmapi.DwmGetWindowAttribute.restype = _ctypes.c_long

try:
    _user32.GetWindowLongPtrW.argtypes = [_wt.HWND, _ctypes.c_int]
    _user32.GetWindowLongPtrW.restype = _ctypes.c_ssize_t
    _get_window_long = _user32.GetWindowLongPtrW
except AttributeError:
    _user32.GetWindowLongW.argtypes = [_wt.HWND, _ctypes.c_int]
    _user32.GetWindowLongW.restype = _ctypes.c_int
    _get_window_long = _user32.GetWindowLongW


def _is_cloaked(hwnd):
    value = _ctypes.c_int(0)
    _dwmapi.DwmGetWindowAttribute(hwnd, _DWMWA_CLOAKED,
                                  _ctypes.byref(value),
                                  _ctypes.sizeof(value))
    return bool(value.value)


def _is_switchable(hwnd):
    if not _user32.IsWindowVisible(hwnd):
        return False
    # Hidden/cloaked windows (shell-cached apps, virtual desktops)
    if _is_cloaked(hwnd):
        return False
    # Tool windows are small helper windows, never meant to be switched to
    if _get_window_long(hwnd, _GWL_EXSTYLE) & _WS_EX_TOOLWINDOW:
        return False
    # Never switch to the GestureOS app's own windows (camera preview, console)
    pid = _wt.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, _ctypes.byref(pid))
    if pid.value == os.getpid():
        return False
    title = _window_title(hwnd)
    if title.startswith("GestureOS"):
        return False
    cls = _ctypes.create_unicode_buffer(256)
    _user32.GetClassNameW(hwnd, cls, 256)
    if cls.value in _SKIP_CLASSES:
        return False
    return bool(title.strip())


def _window_title(hwnd):
    n = _user32.GetWindowTextLengthW(hwnd)
    buf = _ctypes.create_unicode_buffer(n + 1)
    _user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


_cycle_windows   = []
_cycle_index     = 0
_cycle_signature = None


def _enum_cb(hwnd, lparam):
    if _is_switchable(hwnd):
        _cycle_windows.append(hwnd)
    return True


def _refresh_cycle_windows():
    _cycle_windows.clear()
    _user32.EnumWindows(_ENUMPROC(_enum_cb), 0)


_kernel32 = _ctypes.windll.kernel32
_kernel32.GetCurrentThreadId.restype = _wt.DWORD
_user32.GetWindowThreadProcessId.argtypes = [_wt.HWND, _wt.LPDWORD]
_user32.GetWindowThreadProcessId.restype = _wt.DWORD
_user32.AttachThreadInput.argtypes = [_wt.DWORD, _wt.DWORD, _wt.BOOL]
_user32.AttachThreadInput.restype = _wt.BOOL
_user32.keybd_event.argtypes = [_wt.BYTE, _wt.BYTE, _wt.DWORD, _ctypes.c_void_p]


def _activate_window(hwnd):
    if _user32.IsIconic(hwnd):
        _user32.ShowWindow(hwnd, 9)  # SW_RESTORE

    # AttachThreadInput + SetForegroundWindow bypasses Windows'
    # foreground lock so a background process can switch focus.
    target_thread = _user32.GetWindowThreadProcessId(hwnd, None)
    fg_thread     = _user32.GetWindowThreadProcessId(_user32.GetForegroundWindow(), None)
    mine          = _kernel32.GetCurrentThreadId()

    _user32.AttachThreadInput(mine, fg_thread, True)
    _user32.AttachThreadInput(mine, target_thread, True)
    _user32.SetForegroundWindow(hwnd)
    _user32.AttachThreadInput(mine, target_thread, False)
    _user32.AttachThreadInput(mine, fg_thread, False)

    # Fallback: a brief fake Alt press also lifts the foreground lock.
    if not _user32.GetForegroundWindow() == hwnd:
        _user32.keybd_event(0x12, 0, 0, 0)
        _user32.keybd_event(0x12, 0, 2, 0)
        _user32.SetForegroundWindow(hwnd)

    time.sleep(0.001)


def _snapshot_windows():
    """Fresh z-order list of switchable windows (topmost first)."""
    result = []

    def _cb(hwnd, lparam):
        if _is_switchable(hwnd):
            result.append(hwnd)
        return True

    _user32.EnumWindows(_ENUMPROC(_cb), 0)
    return result


def _sync_cycle_list():
    """Re-sync the cached list with what is currently open.

    Keeps the cached *relative order* stable (so cycling never bounces),
    drops windows that were closed, and appends newly opened windows.
    Returns True if the list changed in any way.
    """
    global _cycle_windows
    snapshot = _snapshot_windows()
    if set(snapshot) == set(_cycle_windows):
        return False
    keep = set(snapshot)
    ordered = [hwnd for hwnd in _cycle_windows if hwnd in keep]
    have = set(ordered)
    ordered += [hwnd for hwnd in snapshot if hwnd not in have]
    _cycle_windows = ordered
    return True


def _get_target(delta):
    """Return the hwnd to switch to next; advances _cycle_index by delta."""
    global _cycle_index
    n = len(_cycle_windows)
    if not n:
        return None
    _cycle_index = (_cycle_index + delta) % n
    return _cycle_windows[_cycle_index]


def cycle_window_forward():
    """Advance to the next open window; wraps to the first after the last.

    Picks up newly opened applications automatically and never gets
    stuck when one is closed.
    """
    global _cycle_index

    changed = _sync_cycle_list()
    if not _cycle_windows:
        print("[Windows] No switchable windows found.")
        return

    # Re-anchor to the currently focused window whenever the list was
    # rebuilt (new app opened / one closed) or our position is stale.
    current = _user32.GetForegroundWindow()
    if changed or _cycle_index >= len(_cycle_windows) or _cycle_windows[_cycle_index] == current:
        try:
            _cycle_index = _cycle_windows.index(current)
        except ValueError:
            _cycle_index = 0

    target = _get_target(+1)
    if target is None:
        return
    if not _user32.IsWindow(target):
        _cycle_windows.clear()
        return cycle_window_forward()

    _activate_window(target)
    print(f"[Windows] Cycle -> {_window_title(target)!r}")


def cycle_window_backward():
    """Go to the previous open window; wraps to the last after the first."""
    global _cycle_index

    changed = _sync_cycle_list()
    if not _cycle_windows:
        print("[Windows] No switchable windows found.")
        return

    current = _user32.GetForegroundWindow()
    if changed or _cycle_index >= len(_cycle_windows) or _cycle_windows[_cycle_index] == current:
        try:
            _cycle_index = _cycle_windows.index(current)
        except ValueError:
            _cycle_index = 0

    target = _get_target(-1)
    if target is None:
        return
    if not _user32.IsWindow(target):
        _cycle_windows.clear()
        return cycle_window_backward()

    _activate_window(target)
    print(f"[Windows] Cycle <- {_window_title(target)!r}")


def take_screenshot():
    import threading
    
    def _capture():
        ts   = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"gesture_{ts}.png")
        try:
            import PIL.ImageGrab
            img = PIL.ImageGrab.grab()
            img.save(path)
            print(f"[Windows] Screenshot saved -> {path}")
        except Exception as e:
            print(f"[Windows] Screenshot failed: {e}")
    
    threading.Thread(target=_capture, daemon=True).start()
    print("[Windows] Taking screenshot...")

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
    
    # ADD THESE TWO LINES:
    "switch_window_left": switch_window_left,
    "switch_window_right": switch_window_right,
    "cycle_window_forward": cycle_window_forward,
    "cycle_window_backward": cycle_window_backward,
}


def execute(action_name: str):
    fn = ACTION_MAP.get(action_name)
    if fn:
        fn()
    else:
        print(f"[Windows] Unknown action: {action_name}")