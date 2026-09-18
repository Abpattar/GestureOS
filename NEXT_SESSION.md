# Next Session TODO — GestureOS

Read `UBUNTU_PORT.md` for the Ubuntu context. This list is the agreed work order
for the next opencode session on **Windows**.

## 🎯 Main Feature: Universal Play / Pause Gesture

Goal: one gesture that toggles play/pause in any media app (YouTube, Spotify web,
VLC, etc.) globally — regardless of which window is focused.

### Implementation notes (as agreed)
- The action **already exists**: `os_platform/windows.py` maps `media_play_pause`
  → `pyautogui.press("playpause")` (global media key, works for YT/Spotify/VLC).
- Play/pause is a **toggle** → it must fire **once per hold** (like the peace
  sign), NOT repeat every 0.2s like the volume gestures.
- Handedness is already corrected for the mirrored camera (see engine comment).
  Left hand is taken by volume up/down, so the new gesture should go on the
  **right hand** (alongside the peace sign).

### Steps
1. **Pick gesture shape** (user decision needed): thumbs-up 👍, pointing
   index ☝️, OK/pinch 👌, or 3-fingers-up 🩹 (index+middle+ring). Right hand.
2. Add the pose detector in `gestures/defaults/static_poses.py` → return a
   name (e.g. `"pointing"`, `"thumbs_up"`).
3. Route it in `core/gesture_engine.py`:
   - right-hand only
   - one-shot per hold, 0.7s identify (reuse `_hold_duration_sec`), one fire
     per hold (pattern: `_pose_was_active` / `_hold_triggered`)
4. Map gesture → action in `profiles/default.json` (e.g.
   `"pointing": "media_play_pause"`).
5. Add it to apps' profiles only if a context-specific action is desired
   (not required — `default` is the fallback).
6. Add an on-screen indicator in `main.py` (like the peace-sign progress bar).
7. Run `python main.py` and test against YouTube + Spotify web + VLC.

## 🐧 Secondary: Ubuntu port
- Not now. On the laptop, follow `UBUNTU_PORT.md`:
  `os_platform/ubuntu.py` is empty → volume (`pactl`/`amixer`) +
  window cycling (`wmctrl`/`xdotool`, X11 session). Install `wmctrl xdotool`
  and use Python 3.11 (`.venv`).

## ✅ Current known-good state (do not regress)
- ✌️ Right-hand peace sign (0.7s) → cycle window forward
- ✋ Left-hand open palm (0.7s identify, 0.2s repeat) → volume up
- 👊 Left-hand fist (0.7s identify, 0.2s repeat) → volume down
- 🖐️ Both open palms → activate/deactivate
- Formatting: no comments unless asked, keep code style consistent.