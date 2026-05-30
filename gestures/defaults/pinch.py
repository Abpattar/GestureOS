from collections import deque
import time


class PinchDetector:
    def __init__(self, window_size=15, pinch_threshold=0.07,
                 open_threshold=0.15, min_delta=0.06, cooldown_sec=0.5):
        self.pinch_threshold = pinch_threshold
        self.open_threshold  = open_threshold
        self.min_delta       = min_delta
        self.cooldown_sec    = cooldown_sec
        self._history        = deque(maxlen=window_size)
        self._last_fire      = 0

    def update(self, pinch_distance: float):
        now = time.time()
        self._history.append(pinch_distance)

        if len(self._history) < self._history.maxlen:
            return None
        if now - self._last_fire < self.cooldown_sec:
            return None

        delta = self._history[-1] - self._history[0]

        if delta > self.min_delta and self._history[0] < self.open_threshold:
            self._last_fire = now;  self._history.clear()
            return "pinch_out"

        if delta < -self.min_delta and self._history[-1] < self.pinch_threshold:
            self._last_fire = now;  self._history.clear()
            return "pinch_in"

        return None

    def reset(self):
        self._history.clear()