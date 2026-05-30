@"
# 🎮 GestureOS

Control your PC using hand gestures! No keyboard, no mouse – just your webcam.

## ✨ Features

- 🖐️ **20+ Gestures**: Swipes, pinches, static poses, holds, and rotations
- 🎯 **Context-Aware**: Different actions for Chrome, VS Code, VLC, etc.
- ⚡ **Real-time**: 30 FPS tracking with MediaPipe
- 🔧 **Customizable**: JSON-based profiles and gesture definitions
- 🪟 **Cross-Platform**: Windows & Linux support

## 🚀 Quick Start

### 1. Install Dependencies

\`\`\`powershell
pip install -r requirements.txt
\`\`\`

### 2. Run

\`\`\`powershell
python main.py
\`\`\`

### 3. Activate

- **Wave once** → Activate gesture control
- **Wave twice** → Deactivate
- **Press Q** → Quit

## 🎯 Supported Gestures

| Gesture | Default Action |
|---------|---------------|
| Swipe Left | Previous Tab |
| Swipe Right | Next Tab |
| Swipe Up | Scroll Up |
| Swipe Down | Scroll Down |
| Pinch In | Zoom Out |
| Pinch Out | Zoom In |
| Fist | Close Tab |
| Open Palm | Show Desktop |
| Thumbs Up | Volume Up |
| Thumbs Down | Volume Down |
| Peace Sign | Screenshot |
| OK Sign | Play/Pause |
| Pointing | Next Tab |
| L-Shape | Undo |

## 🛠️ Configuration

Edit \`config.json\` to adjust:
- Camera settings
- Detection thresholds
- Gesture timing

Edit \`profiles/*.json\` to customize actions per app.

## 📦 Requirements

- Python 3.8 - 3.11 (not 3.12)
- Webcam
- Windows 10/11 or Ubuntu 20.04+

## 📄 License

MIT License - Feel free to modify and distribute!

## 🙏 Credits

Built with [MediaPipe](https://mediapipe.dev/) by Google
"@ | Out-File -FilePath "README.md" -Encoding utf8
