import cv2
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

from core.camera import Camera
from core.tracker import HandTracker
from core.gesture_engine import GestureEngine
from core.context_detector import ContextDetector
from core.action_executor import ActionExecutor


def load_config(path: str = "config.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


def main():
    print("=" * 50)
    print("  GestureOS - Starting up")
    print("=" * 50)

    config = load_config()

    cam = Camera(
        camera_index=config["camera"]["index"],
        target_fps=config["camera"]["target_fps"]
    )

    tracker = HandTracker(
        max_hands=config["tracker"]["max_hands"],
        detection_confidence=config["tracker"]["detection_confidence"],
        tracking_confidence=config["tracker"]["tracking_confidence"],
        draw_landmarks=config["tracker"]["draw_landmarks"]
    )

    engine = GestureEngine(
        tracker=tracker,
        custom_gestures_path=config["paths"]["custom_gestures"],
        settings=config.get("gesture_engine", {})
    )

    context = ContextDetector()
    executor = ActionExecutor(context_detector=context)

    cam.start()

    print("\nGestureOS running.")
    print("  Show both open palms -> Activate / Deactivate")
    print("  Press Q to quit.\n")

    try:
        while True:
            frame = cam.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            # Process tracking
            try:
                hands, annotated_frame = tracker.process(frame)
            except Exception as e:
                print(f"[Error] Tracking: {e}")
                annotated_frame = frame
                hands = []

            # Process gestures
            gesture = None
            try:
                gesture = engine.process(hands)
            except Exception as e:
                print(f"[Error] Gesture engine: {e}")

            # Execute action
            if gesture:
                try:
                    executor.execute(gesture)
                except Exception as e:
                    print(f"[Error] Executor: {e}")

            # Draw UI
            status_color = (0, 255, 80) if engine.active else (0, 80, 255)
            status_text  = "ACTIVE" if engine.active else "INACTIVE"

            cv2.putText(annotated_frame, f"GestureOS: {status_text}",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
            cv2.putText(annotated_frame, f"FPS: {cam.fps_actual:.0f}",
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            # 2-finger hold progress bar
            progress = engine.get_hold_progress()
            if progress > 0.0 or engine.pose_active:
                cv2.putText(annotated_frame, "RIGHT: 2 FINGERS UP - SWITCH WINDOW",
                            (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 220, 255), 1)
                bar_w = int(280 * progress)
                cv2.rectangle(annotated_frame, (10, 108), (290, 122), (60, 60, 60), -1)
                cv2.rectangle(annotated_frame, (10, 108), (10 + bar_w, 122), (0, 220, 255), -1)

            # Left hand volume indicators
            if engine.volume_active:
                vol_text = "LEFT: OPEN PALM - VOLUME UP" if engine._vol_pose == "open_palm" else "LEFT: FIST - VOLUME DOWN"
                cv2.putText(annotated_frame, vol_text,
                            (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (80, 255, 80), 1)

            if gesture:
                cv2.putText(annotated_frame, f"Gesture: {gesture}",
                            (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2)

            # Show window
            cv2.imshow("GestureOS", annotated_frame)

            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        cam.stop()
        tracker.close()
        cv2.destroyAllWindows()
        print("GestureOS stopped.")


if __name__ == "__main__":
    main()