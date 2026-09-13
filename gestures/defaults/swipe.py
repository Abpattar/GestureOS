from collections import deque
import time


class SwipeDetector:
    def __init__(self, window_size=20, min_distance=0.15,
                 min_speed=0.010, cooldown_sec=0.5):
        self.window_size  = window_size
        self.min_distance = min_distance
        self.min_speed    = min_speed
        self.cooldown_sec = cooldown_sec
        self._history     = deque(maxlen=window_size)
        self._last_swipe  = {}

    def update(self, hand_center: tuple):
        x, y = hand_center
        now  = time.time()
        self._history.append((x, y, now))

        if len(self._history) < self.window_size:
            return None

        oldest = self._history[0]
        newest = self._history[-1]
        
        dx = newest[0] - oldest[0]
        dy = newest[1] - oldest[1]
        dt = newest[2] - oldest[2]

        if dt <= 0:
            return None

        dist  = (dx**2 + dy**2) ** 0.5
        speed = dist / dt

        if dist < self.min_distance or speed < self.min_speed:
            return None

        # Determine direction (horizontal priority)
        if abs(dx) > abs(dy):
            direction = "swipe_right" if dx > 0 else "swipe_left"
        else:
            direction = "swipe_down" if dy > 0 else "swipe_up"

        if now - self._last_swipe.get(direction, 0) < self.cooldown_sec:
            return None

        self._last_swipe[direction] = now
        self._history.clear()
        
        return direction

    def reset(self):
        self._history.clear()