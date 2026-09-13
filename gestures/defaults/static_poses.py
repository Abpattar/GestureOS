import numpy as np
from core.tracker import HandData, HandTracker, LM


class StaticPoseDetector:
    def __init__(self, tracker: HandTracker):
        self.tracker = tracker

    def detect(self, hand: HandData):
        """Detect single-hand gestures"""
        fingers = self.tracker.get_finger_states(hand)
        lm      = hand.landmarks

        # Two fingers straight (for window switching)
        if self._two_fingers_straight(fingers, lm):
            return "two_fingers_straight"
        
        # ADD YOUR OTHER GESTURES HERE
        
        return None

    def detect_two_hands(self, hands):
        """
        Detect TWO-HAND gestures
        hands: list of HandData objects
        Returns: gesture name or None
        """
        if len(hands) != 2:
            return None
        
        # Check if both hands are open palms facing camera
        if self._both_hands_facing_camera(hands):
            return "two_hands_camera"
        
        return None

    # ========== TWO-HAND GESTURES ==========
    
    def _both_hands_facing_camera(self, hands):
        """
        CLEAN VERSION: Both hands open, palms facing camera
        """
        
        if len(hands) != 2:
            return False
        
        for hand in hands:
            fingers = self.tracker.get_finger_states(hand)
            
            # All 5 fingers must be extended
            if not all(fingers.values()):
                return False
            
            lm = hand.landmarks
            
            # Check z-depth (palm facing camera)
            tips_z = [
                lm[LM.THUMB_TIP].z,
                lm[LM.INDEX_TIP].z,
                lm[LM.MIDDLE_TIP].z,
                lm[LM.RING_TIP].z,
                lm[LM.PINKY_TIP].z
            ]
            
            z_variance = max(tips_z) - min(tips_z)
            if z_variance > 0.08:
                return False
            
            # Check wrist behind fingertips
            wrist_z = lm[LM.WRIST].z
            avg_tip_z = np.mean(tips_z)
            if wrist_z < avg_tip_z:
                return False
            
            # Check finger spread
            tip_xs = [
                lm[LM.THUMB_TIP].x,
                lm[LM.INDEX_TIP].x,
                lm[LM.MIDDLE_TIP].x,
                lm[LM.RING_TIP].x,
                lm[LM.PINKY_TIP].x
            ]
            horizontal_span = max(tip_xs) - min(tip_xs)
            if horizontal_span < 0.15:
                return False
        
        return True

    # ========== ADD YOUR SINGLE-HAND GESTURE FUNCTIONS BELOW ==========
    def _two_fingers_straight(self, f, lm):
        """
        Index and middle fingers straight and together (peace sign).

        Fully rotation-invariant: all measurements are relative to the
        hand's own size (palm length) and use 2D distances, so it works
        at any angle, distance, or hand orientation.
        """

        # Index and middle must be raised
        if not (f["index"] and f["middle"]):
            return False

        # Ring and pinky must be tucked down
        if f["ring"] or f["pinky"]:
            return False

        # Thumb state is ignored (people naturally leave it out/bent)

        # Reference scale = palm length (wrist -> middle MCP).
        # Stable at any angle; everything is compared against it.
        wrist       = lm[LM.WRIST]
        middle_mcp  = lm[LM.MIDDLE_MCP]
        index_tip   = lm[LM.INDEX_TIP]
        index_mcp   = lm[LM.INDEX_MCP]
        middle_tip  = lm[LM.MIDDLE_TIP]

        hand_scale = np.hypot(wrist.x - middle_mcp.x, wrist.y - middle_mcp.y)
        if hand_scale < 1e-4:
            return False

        def length(a, b):
            return np.hypot(a.x - b.x, a.y - b.y)

        # Both fingers must clearly extend (relative to the hand size)
        if length(index_tip, index_mcp) < 0.40 * hand_scale:
            return False
        if length(middle_tip, middle_mcp) < 0.40 * hand_scale:
            return False

        # Finger tips must be close together (2D, any angle)
        if length(index_tip, middle_tip) > 0.50 * hand_scale:
            return False

        # Fingers must be parallel
        index_vec = np.array([index_tip.x - index_mcp.x,
                              index_tip.y - index_mcp.y])
        middle_vec = np.array([middle_tip.x - middle_mcp.x,
                               middle_tip.y - middle_mcp.y])

        index_vec = index_vec / (np.linalg.norm(index_vec) + 1e-6)
        middle_vec = middle_vec / (np.linalg.norm(middle_vec) + 1e-6)

        dot_product = np.dot(index_vec, middle_vec)
        angle = np.degrees(np.arccos(np.clip(dot_product, -1.0, 1.0)))
        if angle > 25:
            return False

        return True