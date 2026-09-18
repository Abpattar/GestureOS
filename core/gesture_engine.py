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

        # Left-palm volume gesture
        self._volume_identify_sec = settings.get("volume_identify_sec", 0.6)
        self._volume_repeat_sec   = settings.get("volume_repeat_sec", 0.2)

        self._last_gesture      = None
        self._last_gesture_time = 0
        self._activation_cooldown = 1.5

        self._pose_was_active    = False
        self._pose_active_start  = 0
        self._hold_triggered     = False
        self._miss_frames        = 0
        self._hysteresis_frames  = 8
        self.pose_active         = False

        self._vol_pose_was_active = False
        self._vol_pose            = None
        self._vol_pose_start      = 0
        self._vol_last_fire       = 0
        self._vol_miss_frames     = 0
        self.volume_active        = False

        print("[GestureEngine] Ready")

    def process(self, hands):
        if not hands:
            self.swipe_detector.reset()
            self._reset_hold()
            self._reset_volume()
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
            self._reset_volume()
            return None

        # Split hands by handedness.
        # NOTE: the camera feed is mirrored, so MediaPipe's labels come back
        # reversed vs. reality: "Left" is actually the user's right hand and
        # "Right" is actually the user's left hand. Swap accordingly:
        #   right hand -> two-finger peace sign (window switching)
        #   left hand  -> open palm (continuous volume up)
        right_hand = next((h for h in hands if h.handedness == "Left"), None)
        left_hand  = next((h for h in hands if h.handedness == "Right"), None)

        # Peace sign on the RIGHT hand only.
        if right_hand is not None:
            pose = self.static_detector.detect(right_hand)

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
                # Hysteresis: a few lost frames (flicker) can't reset the timer.
                self._miss_frames += 1
                if self._miss_frames >= self._hysteresis_frames:
                    self._reset_hold()
                self.pose_active = self._pose_was_active
        else:
            self._reset_hold()

        # LEFT hand -> continuous volume gestures (identify 0.7s, repeat 0.2s):
        #   open palm -> volume up, fist -> volume down.
        if left_hand is not None:
            pose = self.static_detector.detect(left_hand)

            if pose in ("open_palm", "fist"):
                gesture_name = "hold_open_palm" if pose == "open_palm" else "hold_fist"

                # A pose change (open<->fist) restarts the identify timer.
                if not self._vol_pose_was_active or self._vol_pose != pose:
                    self._vol_pose_was_active = True
                    self._vol_pose           = pose
                    self._vol_pose_start     = now
                    self._vol_last_fire      = 0
                    print(f"[Pose] {pose}")

                self.volume_active = True
                held_for = now - self._vol_pose_start
                if (held_for >= self._volume_identify_sec
                        and now - self._vol_last_fire >= self._volume_repeat_sec):
                    self._vol_last_fire = now
                    return self._emit(gesture_name, force=True)
            else:
                self._vol_miss_frames += 1
                if self._vol_miss_frames >= self._hysteresis_frames:
                    self._reset_volume()
                self.volume_active = self._vol_pose_was_active
        else:
            self._reset_volume()

        return None

    def _reset_hold(self):
        self._pose_was_active   = False
        self._hold_triggered    = False
        self._miss_frames       = 0
        self.pose_active        = False

    def _reset_volume(self):
        self._vol_pose_was_active = False
        self._vol_pose            = None
        self._vol_last_fire       = 0
        self._vol_miss_frames     = 0
        self.volume_active        = False

    def _emit(self, name, force=False):
        now = time.time()
        
        if not force and now - self._last_gesture_time < 0.5:
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