from collections import deque
import time
import numpy as np
from core.tracker import HandData, LM


class WaveDetector:
    def __init__(self, reversal_threshold=0.08, max_wave_duration=1.2, cooldown_sec=0.8):
        self.reversal_threshold = reversal_threshold
        self.max_wave_duration  = max_wave_duration
        self.cooldown_sec       = cooldown_sec
        self._positions         = deque(maxlen=60)
        self._reversals         = []
        self._last_direction    = None
        self._last_fire         = 0

    def update(self, hand_center_x: float):
        now = time.time()
        self._positions.append((hand_center_x, now))
        self._reversals = [t for t in self._reversals if now - t < self.max_wave_duration]

        if len(self._positions) < 3:
            return None

        delta = self._positions[-1][0] - self._positions[-2][0]
        if abs(delta) < 0.01:
            return None

        direction = "right" if delta > 0 else "left"

        if self._last_direction and direction != self._last_direction:
            if abs(delta) > self.reversal_threshold:
                self._reversals.append(now)

        self._last_direction = direction

        if now - self._last_fire < self.cooldown_sec:
            return None

        wave_count = len(self._reversals) // 2

        if wave_count >= 1:
            self._last_fire = now
            self._reversals.clear()
            return True

        return None

    def reset(self):
        self._positions.clear()
        self._reversals.clear()
        self._last_direction = None


class WristRotationDetector:
    def __init__(self, min_rotation_deg=45.0, window_size=15, cooldown_sec=0.5):
        self.min_rotation_deg = min_rotation_deg
        self.cooldown_sec     = cooldown_sec
        self._angles          = deque(maxlen=window_size)
        self._last_fire       = 0

    def update(self, hand: HandData):
        lm     = hand.landmarks
        wrist  = np.array([lm[LM.WRIST].x,      lm[LM.WRIST].y])
        middle = np.array([lm[LM.MIDDLE_MCP].x,  lm[LM.MIDDLE_MCP].y])
        angle  = np.degrees(np.arctan2(*(middle - wrist)[::-1]))
        self._angles.append(angle)

        if len(self._angles) < self._angles.maxlen:
            return None

        now   = time.time()
        if now - self._last_fire < self.cooldown_sec:
            return None

        delta = self._angles[-1] - self._angles[0]
        if delta > 180:   delta -= 360
        elif delta < -180: delta += 360

        if abs(delta) > self.min_rotation_deg:
            self._last_fire = now
            self._angles.clear()
            return "wrist_rotate"

        return None

    def reset(self):
        self._angles.clear()