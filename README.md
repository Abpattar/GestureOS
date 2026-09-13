# 🎮 GestureOS

Control your PC using hand gestures! No keyboard, no mouse – just your webcam.

## ✨ Features

- ✌️ **Hold-to-Activate**: Hold two fingers up to switch the active window
- 🔄 **Smart Window Cycling**: Cycles through **all** open apps (Store, Paint, Chrome, games...) in a stable order — no Alt+Tab bounce
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

| Gesture | What it does |
|---------|-------------|
| ✌️ Hold 2 fingers (peace sign) up ~0.6s | Switch to the **next** open window |
| 👋 Swipe left / right | Previous / Next tab (Alt+Tab fallback) |

Notes:
- The peace sign works in **any rotation** (verified at all angles).
- The window list auto-syncs every gesture: new apps (e.g. Microsoft Store) appear, closed apps are dropped — nothing gets stuck.
- One switch per hold; wait ~0.8s before the next hold re-arms.

## 🛠️ Configuration

Edit `config.json`:

- `gesture_engine.hold_duration_sec` — how long to hold the peace sign (default `0.6`)
- `gesture_engine.gesture_gap_sec` — delay before a gesture can re-fire (default `0.8`)
- `camera.index` — webcam device ID
- `tracker.*` — MediaPipe detection/tracking confidence

Edit `profiles/*.json` to change which action each gesture fires (e.g.
`hold_peace_sign` → `cycle_window_forward` / `cycle_window_backward`).

## 📦 Requirements

- Python 3.8 – 3.11 (not 3.12 — MediaPipe)
- Webcam
- Windows 10/11

Windows-only: window switching uses Win32 via `ctypes` (no extra Windows deps).

## 📄 License

MIT License - Feel free to modify and distribute!

## 🙏 Credits

Built with [MediaPipe](https://mediapipe.dev/) by Google