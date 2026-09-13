import time
from core.tracker import HandTracker
from gestures.defaults.static_poses import StaticPoseDetector
from gestures.defaults.swipe import SwipeDetector


class GestureEngine:
    def __init__(self, tracker: HandTracker, custom_gestures_path=None, settings=None):
        self.tracker  = tracker
        self.active   = False

        self.static_detector = StaticPoseDetector(tracker)
        self.swipe_detector  = SwipeDetector(
            window_size=20,
            min_distance=0.15,
            min_speed=0.010,
            cooldown_sec=0.5
        )

        settings = settings or {}
        self._hold_duration_sec = settings.get("hold_duration_sec", 1.5)
        self._gesture_gap_sec   = settings.get("gesture_gap_sec", 1.2)

        self._last_gesture      = None
        self._last_gesture_time = 0
        self._activation_cooldown = 1.5

        self._pose_was_active    = False
        self._pose_active_start  = 0
        self._hold_triggered     = False
        self._miss_frames        = 0
        self._hysteresis_frames  = 8
        self.pose_active         = False

        print("[GestureEngine] Ready")

    def process(self, hands):
        if not hands:
            self.swipe_detector.reset()
            self._reset_hold()
            return None

        now = time.time()

        # Activation check
        two_hand_gesture = self.static_detector.detect_two_hands(hands)
        
        if two_hand_gesture == "two_hands_camera":
            if now - self._last_gesture_time > self._activation_cooldown:
                self.active = not self.active
                self._last_gesture_time = now
                return "system_activate" if self.active else "system_deactivate"

        if not self.active:
            self.swipe_detector.reset()
            self._reset_hold()
            return None
        
        # Single-hand gestures: process the first detected hand.
        # Don't reject when a 2nd hand is falsely detected - it would
        # silently block the peace-sign gesture every frame.
        hand = hands[0]
        pose = self.static_detector.detect(hand)

        # Peace sign: hold both fingers up for a few seconds to trigger.
        # One gesture per hold, with a gap before it can fire again.
        if pose == "two_fingers_straight":
            self._miss_frames = 0
            if not self._pose_was_active:
                self._pose_was_active   = True
                self._pose_active_start = now
                self._hold_triggered    = False
                print("[Pose] two_fingers_straight")

            self.pose_active = True
            held_for = now - self._pose_active_start
            if (not self._hold_triggered
                    and held_for >= self._hold_duration_sec
                    and now - self._last_gesture_time >= self._gesture_gap_sec):
                self._hold_triggered = True
                return self._emit("hold_peace_sign")
        else:
            # Hysteresis: a few lost frames (flicker) must NOT reset the
            # hold timer, otherwise the gesture can never reach threshold.
            self._miss_frames += 1
            if self._miss_frames >= self._hysteresis_frames:
                self._reset_hold()
            self.pose_active = self._pose_was_active

        return None

    def _reset_hold(self):
        self._pose_was_active   = False
        self._hold_triggered    = False
        self._miss_frames       = 0
        self.pose_active        = False

    def _emit(self, name):
        now = time.time()
        
        if now - self._last_gesture_time < 0.5:
            return None
        
        self._last_gesture      = name
        self._last_gesture_time = now
        print(f"[Gesture] {name}")
        return name

    def get_hold_progress(self):
        if not self.pose_active or self._hold_triggered:
            return 0.0
        p = (time.time() - self._pose_active_start) / self._hold_duration_sec
        return max(0.0, min(1.0, p))