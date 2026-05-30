import cv2
import threading
import time


class Camera:
    def __init__(self, camera_index=0, target_fps=30):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None
        self.frame = None
        self.running = False
        self._lock = threading.Lock()
        self._thread = None
        self.fps_actual = 0
        self._frame_count = 0
        self._fps_timer = time.time()

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera. Check it's connected and not used by another app.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)

        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[Camera] Started: {w}x{h}")

        self.running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)

            with self._lock:
                self.frame = frame

            self._frame_count += 1
            elapsed = time.time() - self._fps_timer
            if elapsed >= 1.0:
                self.fps_actual = self._frame_count / elapsed
                self._frame_count = 0
                self._fps_timer = time.time()

    def get_frame(self):
        with self._lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
        print("[Camera] Stopped.")