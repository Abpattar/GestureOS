# 🎮 GestureOS

Control your PC using hand gestures! No keyboard, no mouse – just your webcam.

## ✨ Features

- ✌️ **Hold-to-Window-Switch**: Hold two fingers up (right hand) to switch the active window
- 🔊 **Gesture Volume Control**: Left hand open palm = volume up, left hand fist = volume down (continuous while held)
- 🔄 **Smart Window Cycling**: Cycles through **all** open apps (Store, Paint, Chrome, games...) in a stable order — no Alt+Tab bounce
- 🖐️ **Hand-Aware**: Peace sign needs the **right** hand; volume gestures need the **left** hand
- ⏱️ **Debounced Gestures**: Every hold gesture must be held for 0.7s to identify; then it repeats every 0.2s until you release
- 🧭 **Rotation-Invariant**: Gestures work at any hand angle
- 🎯 **Context-Aware**: Per-app action profiles (Chrome, VS Code, VLC, default)
- ⚡ **Real-time**: 30 FPS tracking with MediaPipe
- 🔧 **Customizable**: JSON-based profiles and settings

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run

```powershell
python main.py
```

### 3. Activate

- **Show both open palms** → Toggle gesture control ON/OFF
- **Press Q** → Quit

## 👋 Gestures

All hold gestures share the same timing: **hold the pose for 0.7s** to identify it, then it repeats **every 0.2s** until you let go.

| Gesture | Hand | What it does |
|---------|------|-------------|
| ✌️ Hold 2 fingers (peace sign) up ~0.7s | **Right** | Switch to the **next** open window |
| ✋ Open palm (all 5 fingers) hold | **Left** | Volume **up** (repeats every 0.2s while held) |
| 👊 Fist hold | **Left** | Volume **down** (repeats every 0.2s while held) |
| 👋 Swipe left / right | Any | Previous / Next tab (Alt+Tab fallback) |

Notes:
- Handedness is already corrected for the mirrored camera view — your real right hand is the "right hand" to the app.
- The peace sign works in **any rotation** (verified at all angles).
- The window list auto-syncs every gesture: new apps (e.g. Microsoft Store) appear, closed apps are dropped — nothing gets stuck.
- Volume controls are system-wide via the media volume keys — they work in any app.
- One window switch per hold; wait ~0.8s before the next hold re-arms.

## 🛠️ Configuration

Edit `config.json`:

- `gesture_engine.hold_duration_sec` — hold time to identify any hold gesture (default `0.7`)
- `gesture_engine.gesture_gap_sec` — delay before a gesture can re-fire (default `0.8`)
- `gesture_engine.volume_identify_sec` — hold time before volume control kicks in (default `0.7`)
- `gesture_engine.volume_repeat_sec` — volume step interval while held (default `0.2`)
- `camera.index` — webcam device ID
- `tracker.*` — MediaPipe detection/tracking confidence

Edit `profiles/*.json` to change which action each gesture fires (e.g.
`hold_peace_sign` → `cycle_window_forward`, `hold_open_palm` → `volume_up`,
`hold_fist` → `volume_down`).

## 📦 Requirements

- Python 3.8 – 3.11 (not 3.12 — MediaPipe)
- Webcam
- Windows 10/11

Windows-only: window switching uses Win32 via `ctypes` (no extra Windows deps).

## 📄 License

MIT License - Feel free to modify and distribute!

## 🙏 Credits

Built with [MediaPipe](https://mediapipe.dev/) by Google