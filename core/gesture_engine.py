import json
import os
import time
from core.tracker import HandTracker, HandData
from gestures.defaults.static_poses import StaticPoseDetector
from gestures.defaults.swipe import SwipeDetector
from gestures.defaults.pinch import PinchDetector
from gestures.defaults.compound import WaveDetector, HoldDetector, WristRotationDetector


class GestureEngine:
    def __init__(self, tracker: HandTracker, custom_gestures_path=None):
        self.tracker  = tracker
        self.active   = False

        self.static_detector = StaticPoseDetector(tracker)
        self.swipe_detector  = SwipeDetector()
        self.pinch_detector  = PinchDetector()
        self.wave_detector   = WaveDetector()
        self.hold_detector   = HoldDetector(hold_duration=1.5)
        self.wrist_detector  = WristRotationDetector()

        self._last_gesture      = None
        self._last_gesture_time = 0
        print("[GestureEngine] Ready.")

    def process(self, hands):
        if not hands:
            self.swipe_detector.reset()
            return None

        hand   = hands[0]
        center = self.tracker.get_hand_center(hand)
        pinch  = self.tracker.get_pinch_distance(hand)

        # Activation — always live
        wave = self.wave_detector.update(center[0])
        if wave == 1 and not self.active:
            self.active = True
            return "system_activate"
        if wave == 2 and self.active:
            self.active = False
            return "system_deactivate"

        if not self.active:
            return None

        swipe = self.swipe_detector.update(center)
        if swipe:
            return self._emit(swipe)

        pinch_g = self.pinch_detector.update(pinch)
        if pinch_g:
            return self._emit(pinch_g)

        wrist = self.wrist_detector.update(hand)
        if wrist:
            return self._emit(wrist)

        pose = self.static_detector.detect(hand)
        held = self.hold_detector.update(pose)
        if held:
            return self._emit(f"hold_{held}")

        instant = {"thumbs_up","thumbs_down","ok_sign",
                   "three_fingers_up","three_fingers_down",
                   "four_fingers_up","l_shape"}
        if pose in instant:
            return self._emit(pose)

        return None

    def _emit(self, name):
        now = time.time()
        if name == self._last_gesture and now - self._last_gesture_time < 0.4:
            return None
        self._last_gesture      = name
        self._last_gesture_time = now
        print(f"[Gesture] {name}")
        return name

    def get_hold_progress(self):
        return self.hold_detector.get_progress()