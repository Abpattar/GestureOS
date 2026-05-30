import numpy as np
from core.tracker import HandData, HandTracker, LM


class StaticPoseDetector:
    def __init__(self, tracker: HandTracker):
        self.tracker = tracker

    def detect(self, hand: HandData):
        fingers = self.tracker.get_finger_states(hand)
        pinch   = self.tracker.get_pinch_distance(hand)
        lm      = hand.landmarks

        if self._ok_sign(hand, pinch):               return "ok_sign"
        if self._thumbs_up(fingers, lm):             return "thumbs_up"
        if self._thumbs_down(fingers, lm):           return "thumbs_down"
        if self._fist(fingers):                      return "fist"
        if self._open_palm(fingers):                 return "open_palm"
        if self._peace(fingers):                     return "peace_sign"
        if self._pointing(fingers):                  return "pointing"
        if self._three_up(fingers):                  return "three_fingers_up"
        if self._three_down(fingers, lm):            return "three_fingers_down"
        if self._four_up(fingers):                   return "four_fingers_up"
        if self._l_shape(fingers, hand, lm):         return "l_shape"
        return None

    def _fist(self, f):
        return not any(f.values())

    def _open_palm(self, f):
        return all(f.values())

    def _thumbs_up(self, f, lm):
        others = not f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]
        return f["thumb"] and others and lm[LM.THUMB_TIP].y < lm[LM.WRIST].y

    def _thumbs_down(self, f, lm):
        others = not f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]
        return others and lm[LM.THUMB_TIP].y > lm[LM.WRIST].y

    def _peace(self, f):
        return f["index"] and f["middle"] and not f["ring"] and not f["pinky"]

    def _pointing(self, f):
        return f["index"] and not f["middle"] and not f["ring"] and not f["pinky"]

    def _three_up(self, f):
        return f["index"] and f["middle"] and f["ring"] and not f["pinky"] and not f["thumb"]

    def _three_down(self, f, lm):
        extended = f["index"] and f["middle"] and f["ring"]
        tips_down = (lm[LM.INDEX_TIP].y  > lm[LM.INDEX_MCP].y and
                     lm[LM.MIDDLE_TIP].y > lm[LM.MIDDLE_MCP].y and
                     lm[LM.RING_TIP].y   > lm[LM.RING_MCP].y)
        return extended and tips_down

    def _four_up(self, f):
        return f["index"] and f["middle"] and f["ring"] and f["pinky"] and not f["thumb"]

    def _ok_sign(self, hand, pinch_dist):
        f = self.tracker.get_finger_states(hand)
        return pinch_dist < 0.07 and f["middle"] and f["ring"] and f["pinky"]

    def _l_shape(self, f, hand, lm):
        if not (f["index"] and f["thumb"] and not f["middle"] and not f["ring"] and not f["pinky"]):
            return False
        t  = np.array([lm[LM.THUMB_TIP].x,   lm[LM.THUMB_TIP].y])
        i  = np.array([lm[LM.INDEX_TIP].x,   lm[LM.INDEX_TIP].y])
        w  = np.array([lm[LM.WRIST].x,        lm[LM.WRIST].y])
        v1 = t - w;  v2 = i - w
        cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.degrees(np.arccos(np.clip(cos_a, -1, 1)))
        return 60 < angle < 120