# GestureOS — Ubuntu / Linux Porting Guide

This file is the single source of truth for making GestureOS work on Ubuntu
(and desktop Linux in general). Read it fully before changing anything.

> IMPORTANT: This file is written to be used as **context for an opencode
> session on the Ubuntu machine**. When you clone the repo there and start a
> session, tell opencode to read this file first.

---

## 1. TL;DR — What currently works where

| Feature                     | Windows        | Ubuntu (current) |
|-----------------------------|----------------|------------------|
| Hand tracking (MediaPipe)   | ✅ works       | ✅ will work     |
| Gesture recognition         | ✅ works       | ✅ will work     |
| Volume up / down            | ✅ works       | ❌ NOT implemented |
| Window cycling (peace sign) | ✅ works       | ❌ NOT implemented |
| App-context detection       | ✅ Win32       | ⚠️ has xdotool code, untested |

The entire **gesture pipeline** (camera → tracking → pose → profile action map)
is 100% cross-platform. ONLY the final "executor" step is OS-specific, and it
is cleanly isolated in one file:

```
os_platform/windows.py   -> Windows implementation (Win32/ctypes + pyautogui)
os_platform/ubuntu.py    -> <--- EMPTY FILE. This is what must be written.
```

---

## 2. How the pipeline works (understand this before touching anything)

Every gesture flows through these exact steps:

```
camera.py ──frame──▶ tracker.py ──hands──▶ gesture_engine.py ──gesture name──▶ action_executor.py
                                          (poses, hold timing)     │        (maps name → platform action)
                                                                   ▼
                                                   context_detector.py (active app profile)
                                                        │
                                                        ▼
                                        os_platform/{windows,ubuntu}.execute(action_name)
                                                        │
                                                        ▼
                                                    real OS action
```

Key files and their role:

| File | Role |
|------|------|
| `main.py` | Main loop, camera window, on-screen status text |
| `core/camera.py` | Webcam capture (cross-platform, OpenCV). **Note: flips the frame** (selfie view) and MediaPipe handedness is assumed swapped accordingly |
| `core/tracker.py` | MediaPipe HandLandmarker; `get_finger_states()`; `HandData` has `.handedness` ("Left"/"Right") |
| `core/gesture_engine.py` | Hold/repeat timing, handedness routing, hysteresis |
| `gestures/defaults/static_poses.py` | Single-hand pose detectors (`two_fingers_straight`, `open_palm`, `fist`) |
| `gestures/defaults/swipe.py` | Swipe detector (unused in current build path, keep working) |
| `core/context_detector.py` | Active-window → app profile (`chrome`, `vscode`, `vlc`, `default`) |
| `core/action_executor.py` | Chooses platform module based on `platform.system()` |
| `os_platform/windows.py` | Windows actions + `ACTION_MAP` + `execute()` |
| `os_platform/ubuntu.py` | **EMPTY — must be implemented** |
| `profiles/*.json` | Maps gesture names → action names (context-specific) |
| `config.json` | Timing + camera + tracker settings |

### Critical: handedness is SWAPPED (do not "fix" it)

The camera frame is mirrored (`cv2.flip(frame, 1)` in `core/camera.py`).
For a mirrored/selfie feed, MediaPipe's handedness output is **reversed** vs.
the user's real hands. The engine already accounts for this:

- MediaPipe `"Left"`  = user's actual **right** hand → peace sign / window switch
- MediaPipe `"Right"` = user's actual **left** hand → volume gestures

This behavior is correct for BOTH Windows and Linux. Do NOT swap it in the
Ubuntu module — it lives in the engine, not the platform layer.

---

## 3. The platform contract (how to make ANY future gesture work on Ubuntu)

The gesture system is **action-name based and fully generic**. New gestures are
added by (a) writing a pose detector, (b) returning a gesture name, (c) mapping
that name to an action in `profiles/*.json`. The platform layer NEVER sees the
gesture — it only receives an **action name string**.

Therefore the Ubuntu module only needs ONE function contract:

```python
def execute(action_name: str) -> None:
    # dispatch via a universal ACTION_MAP, same keys as windows.py
```

**Rule:** every action key in `os_platform/windows.py`'s `ACTION_MAP` must have
a working Linux equivalent. Then ANY future gesture/action works everywhere
automatically — no per-gesture porting ever.

### The universal action list (mirror windows.py exactly)

The base actions (mostly `pyautogui`, already cross-platform — reuse them):

```
browser_back, browser_forward, new_tab, close_tab, next_tab, prev_tab, refresh_page,
scroll_up, scroll_down, zoom_in, zoom_out, zoom_reset,
undo, redo, copy, paste, select_all,
minimize_window, maximize_window, show_desktop, close_window, switch_window,
switch_virtual_desktop_left, switch_virtual_desktop_right,
media_play_pause, media_next, media_previous, volume_mute,
take_screenshot
```

These need a **custom Linux implementation** (they are Win32/Windows-hotkey
specific today):

```
volume_up, volume_down                    -> pactl / amixer
cycle_window_forward, cycle_window_backward -> wmctrl/xdotool focus cycle
switch_window_left, switch_window_right   -> xdotool key alt+shift+tab / alt+tab
```

---

## 4. What to build in `os_platform/ubuntu.py`

Create a file that mirrors the structure of `windows.py`:

### 4.1 Volume control (highest priority — the fist/open-palm gestures)

Primary: **PulseAudio/PipeWire** via `pactl` (no extra install on modern Ubuntu):

```bash
# +5%                  # −5%
pactl set-sink-volume @DEFAULT_SINK@ +5%
pactl set-sink-volume @DEFAULT_SINK@ -5%
pactl set-sink-mute @DEFAULT_SINK@ toggle     # volume_mute
```

Fallback: **ALSA** via `amixer`:

```bash
amixer -q set Master 5%+
amixer -q set Master 5%-
amixer -q set Master toggle
```

Wrap in a helper that tries `pactl`, then `amixer`, and logs which worked.

### 4.2 Window cycling (peace sign) + focus switching

Use `wmctrl` (list windows, stable order) + `xdotool` (activate/focus).

Install on Ubuntu:

```bash
sudo apt install wmctrl xdotool
```

Required session: **X11 (Xorg)**. On Wayland these won't work — the laptop must
log in with the "Ubuntu on Xorg / X11" session.

Notes for the implementation:
- Mirror the logic in `windows.py` `cycle_window_forward/backward` **conceptually**,
  but re-implement for Linux: snapshot window order via `wmctrl -l`, cycle an
  index, focus via `xdotool windowactivate <id>`.
- Exclude the GestureOS terminal/window itself (compare window titles).
- `xdotool` key combos for `switch_window_left/right`:
  `xdotool key alt+shift+Tab` / `xdotool key alt+Tab`.

### 4.3 App context detection

`core/context_detector.py` already branches to `xdotool getactivewindow
getwindowname` on non-Windows (line ~55). No change needed there, **but**
`xdotool` must be installed for profiles (chrome/vscode/vlc) to resolve.
Absent that, everything falls back to the `default` profile — still fine.

### 4.4 Structure to keep it maintainable

```python
# os_platform/ubuntu.py
import shutil, subprocess, time
import pyautogui          # for the base hotkey actions (unchanged)
pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.0

# ... base action functions identical to windows.py ...
# ... linux-specific functions (volume, window cycle) ...
# ACTION_MAP = { same keys as windows.py }
# def execute(action_name: str): dispatch from ACTION_MAP
```

---

## 5. Ubuntu machine requirements (what to install)

```bash
# System packages
sudo apt install python3.11 wmctrl xdotool

# Python deps (same as requirements.txt)
pip install -r requirements.txt
# NOTE: matches requirements.txt; mediapipe pins Python <= 3.11

# Webcam
# Built-in laptop cam is usually /dev/video0 -> camera.index = 0 (default)
```

NOTE: PulseAudio/PipeWire (`pactl`) is bundled with Ubuntu Desktop — no install.
If audio fails, confirm the output sink name: `pactl list sinks short`.

---

## 6. Environment gotchas on Ubuntu

1. **Python version** — must be 3.8–3.11 (MediaPipe). Ubuntu 24.04 ships 3.12;
   install 3.11 explicitly or use a venv/conda env. Don't rely on system python.
2. **Wayland vs X11** — window switching/`wmctrl` only works on X11. Tell the
   user to log in via the Xorg session. Volume still works under Wayland.
3. **Virtual environment** — strongly recommend: `python3.11 -m venv .venv`.
4. **Running in background** — the app opens an OpenCV window (`cv2.imshow`),
   needs a display; run from the desktop session, not over a bare SSH.
5. **`hand_landmarker.task`** — auto-downloaded on first run by `core/tracker.py`;
   it is git-ignored. If offline, copy it from the Windows machine manually.

---

## 7. How future gestures stay cross-platform (rules to follow)

When anyone adds a new gesture later:

1. Add the pose detector in `gestures/defaults/static_poses.py` → returns a
   name. (Cross-platform — free.)
2. In `core/gesture_engine.py`, route it by handedness + emit its gesture name.
   (Cross-platform — free.)
3. Map gesture name → **existing** action name in `profiles/default.json`
   (and/or app profiles). (Cross-platform — free.)
4. **Only if** the new gesture needs an action that doesn't exist yet:
   add ONE function + ONE `ACTION_MAP` entry in `windows.py` AND the same
   entry in `ubuntu.py`. Then it works on both.

This is why `ubuntu.py` must keep an **identical `ACTION_MAP` key set** to
`windows.py`. That is the entire secret to "future-proof".

---

## 8. Verification checklist after implementing `ubuntu.py`

Run `python main.py` and confirm:

1. App starts, camera opens, "GestureOS running." shows.
2. Both open palms → toggles ACTIVE (green "ACTIVE" text).
3. ✌️ Right-hand peace sign (0.7s hold) → cycles to next window.
4. ✋ Left-hand open palm (0.7s hold) → volume rises (repeats ~every 0.2s).
5. 👊 Left-hand fist (0.7s hold) → volume falls (repeats ~every 0.2s).
6. Volume changes via pactl are audible/visible (`pactl get-sink-volume @DEFAULT_SINK@`).
7. Context detection resolves profiles when inside Chrome/VS Code/VLC.

If 1–3 pass but the volume is silent, focus on `pactl` sink selection.

---

## 9. Current gesture + action map (reference for porting)

`profiles/default.json`:

```json
{
  "gestures": {
    "swipe_left": "switch_window_left",
    "swipe_right": "switch_window_right",
    "hold_peace_sign": "cycle_window_forward",
    "hold_open_palm": "volume_up",
    "hold_fist": "volume_down"
  }
}
```

Current engine settings (`config.json`):

```json
"hold_duration_sec": 0.7,     // seconds to identify ANY hold gesture
"gesture_gap_sec": 0.8,       // min gap before a hold gesture re-arms
"volume_identify_sec": 0.7,   // left-hand volume identify time
"volume_repeat_sec": 0.2      // volume step interval while held
```

Keep these the same for parity between Windows and Ubuntu.