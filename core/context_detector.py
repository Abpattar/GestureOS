import platform
import json
import os

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "..", "profiles")

APP_PROFILE_MAP = {
    "chrome": "chrome", "firefox": "chrome", "msedge": "chrome",
    "brave":  "chrome", "opera":   "chrome",
    "code":   "vscode",
    "vlc":    "vlc",    "spotify": "vlc",    "wmplayer": "vlc",
}


class ContextDetector:
    def __init__(self):
        self._platform       = platform.system()
        self._cached_context = "default"
        self._cached_window  = ""
        self._profiles       = {}
        self._load_all_profiles()

    def _load_all_profiles(self):
        if not os.path.exists(PROFILE_DIR):
            return
        for fname in os.listdir(PROFILE_DIR):
            if fname.endswith(".json"):
                name = fname.replace(".json", "")
                with open(os.path.join(PROFILE_DIR, fname)) as f:
                    self._profiles[name] = json.load(f)
        print(f"[Context] Profiles loaded: {list(self._profiles.keys())}")

    def get_active_window_name(self):
        if self._platform == "Windows":
            try:
                import win32gui
                return win32gui.GetWindowText(win32gui.GetForegroundWindow())
            except Exception as e:
                print(f"[Context] Error: {e}")
                return ""
        else:
            try:
                import subprocess
                r = subprocess.run(["xdotool","getactivewindow","getwindowname"],
                                   capture_output=True, text=True)
                return r.stdout.strip()
            except:
                return ""

    def get_context(self):
        window = self.get_active_window_name().lower()
        if window == self._cached_window:
            return self._cached_context
        self._cached_window  = window
        self._cached_context = "default"
        for keyword, profile in APP_PROFILE_MAP.items():
            if keyword in window:
                self._cached_context = profile
                break
        return self._cached_context

    def get_gesture_action(self, gesture_name, context):
        action = self._profiles.get(context, {}).get("gestures", {}).get(gesture_name)
        if action is None:
            action = self._profiles.get("default", {}).get("gestures", {}).get(gesture_name)
        return action