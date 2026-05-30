import cv2
import sys
import os
import json

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
    print("  GestureOS — Starting up")
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
        custom_gestures_path=config["paths"]["custom_gestures"]
    )

    context = ContextDetector()
    executor = ActionExecutor(context_detector=context)

    cam.start()

    print("\nGestureOS running.")
    print("  Wave once  → Activate")
    print("  Wave twice → Deactivate")
    print("  Press Q to quit.\n")

    try:
        while True:
            frame = cam.get_frame()
            if frame is None:
                continue

            hands, annotated_frame = tracker.process(frame)
            gesture = engine.process(hands)

            if gesture:
                executor.execute(gesture)

            status_color = (0, 255, 80) if engine.active else (0, 80, 255)
            status_text  = "ACTIVE" if engine.active else "INACTIVE"

            cv2.putText(annotated_frame, f"GestureOS: {status_text}",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
            cv2.putText(annotated_frame, f"FPS: {cam.fps_actual:.0f}",
                        (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

            if gesture:
                cv2.putText(annotated_frame, f"Gesture: {gesture}",
                            (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2)

            cv2.putText(annotated_frame, f"Context: {context.get_context()}",
                        (10, annotated_frame.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)

            hold_progress = engine.get_hold_progress()
            if hold_progress > 0.05:
                bar_w = int(annotated_frame.shape[1] * hold_progress)
                cv2.rectangle(annotated_frame,
                              (0, annotated_frame.shape[0] - 6),
                              (bar_w, annotated_frame.shape[0]),
                              (0, 255, 150), -1)

            cv2.imshow("GestureOS", annotated_frame)

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