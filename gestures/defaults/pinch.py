from collections import deque
import time


class PinchDetector:
    def __init__(self, window_size=10, pinch_threshold=0.05,
                 open_threshold=0.12, min_delta=0.04, cooldown_sec=0.3):
        self.pinch_threshold = pinch_threshold
        self.open_threshold  = open_threshold
        self.min_delta       = min_delta
        self.cooldown_sec    = cooldown_sec
        self._history        = deque(maxlen=window_size)
        self._last_fire      = 0
        self._is_pinching    = False

    def update(self, pinch_distance: float, other_fingers_closed: bool):
        """
        pinch_distance: Distance between thumb and index
        other_fingers_closed: True if middle, ring, pinky are closed
        """
        now = time.time()
        
        # Only detect pinch if other fingers are closed
        if not other_fingers_closed:
            self._history.clear()
            self._is_pinching = False
            return None
        
        self._history.append(pinch_distance)

        if len(self._history) < self._history.maxlen:
            return None
        if now - self._last_fire < self.cooldown_sec:
            return None

        delta = self._history[-1] - self._history[0]

        # Pinch out (opening)
        if delta > self.min_delta and self._history[0] < self.open_threshold:
            self._last_fire = now
            self._history.clear()
            self._is_pinching = False
            return "pinch_out"

        # Pinch in (closing)
        if delta < -self.min_delta and self._history[-1] < self.pinch_threshold:
            self._last_fire = now
            self._history.clear()
            self._is_pinching = True
            return "pinch_in"

        return None

    def reset(self):
        self._history.clear()
        self._is_pinching = False