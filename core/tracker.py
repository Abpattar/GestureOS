import cv2
import numpy as np
from dataclasses import dataclass
from typing import List
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions


@dataclass
class Landmark:
    x: float
    y: float
    z: float


@dataclass
class HandData:
    landmarks: List[Landmark]
    handedness: str
    confidence: float


class LM:
    WRIST = 0
    THUMB_CMC=1;  THUMB_MCP=2;  THUMB_IP=3;   THUMB_TIP=4
    INDEX_MCP=5;  INDEX_PIP=6;  INDEX_DIP=7;  INDEX_TIP=8
    MIDDLE_MCP=9; MIDDLE_PIP=10; MIDDLE_DIP=11; MIDDLE_TIP=12
    RING_MCP=13;  RING_PIP=14;  RING_DIP=15;  RING_TIP=16
    PINKY_MCP=17; PINKY_PIP=18; PINKY_DIP=19; PINKY_TIP=20

# Drawing constants
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17)
]


class HandTracker:
    def __init__(self, max_hands=2, detection_confidence=0.7,
                 tracking_confidence=0.6, draw_landmarks=True):
        self.draw_landmarks = draw_landmarks
        self._results = None

        # Download model if not present
        import os, urllib.request
        model_path = "hand_landmarker.task"
        if not os.path.exists(model_path):
            print("[Tracker] Downloading hand landmarker model...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("[Tracker] Model downloaded.")

        options = HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        self._frame_timestamp = 0
        print("[Tracker] Ready.")

    def process(self, frame):
        self._frame_timestamp += 1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self._landmarker.detect_for_video(mp_image, self._frame_timestamp)

        hands_detected = []

        if result.hand_landmarks:
            for i, hand_lms in enumerate(result.hand_landmarks):
                landmarks = [Landmark(x=lm.x, y=lm.y, z=lm.z) for lm in hand_lms]

                handedness = "Right"
                confidence = 1.0
                if result.handedness and i < len(result.handedness):
                    handedness = result.handedness[i][0].display_name
                    confidence = result.handedness[i][0].score

                hands_detected.append(HandData(
                    landmarks=landmarks,
                    handedness=handedness,
                    confidence=confidence
                ))

                if self.draw_landmarks:
                    h, w = frame.shape[:2]
                    for connection in HAND_CONNECTIONS:
                        a, b = connection
                        x1 = int(hand_lms[a].x * w); y1 = int(hand_lms[a].y * h)
                        x2 = int(hand_lms[b].x * w); y2 = int(hand_lms[b].y * h)
                        cv2.line(frame, (x1,y1), (x2,y2), (0, 200, 100), 2)
                    for lm in hand_lms:
                        cx = int(lm.x * w); cy = int(lm.y * h)
                        cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)

        return hands_detected, frame

    def get_finger_states(self, hand: HandData) -> dict:
        """
        Detect which fingers are extended.

        Rotation-invariant: compares each finger's distance from the wrist,
        so it works no matter which way the hand is angled or flipped.
        Returns dict with True/False for each finger.
        """
        lm = hand.landmarks
        wrist = lm[LM.WRIST]

        def dist_to_wrist(idx):
            return np.hypot(lm[idx].x - wrist.x, lm[idx].y - wrist.y)

        # A finger is extended when its TIP is clearly farther from the
        # wrist than its PIP knuckle -- true for any hand orientation.
        return {
            "thumb":  dist_to_wrist(LM.THUMB_TIP) > dist_to_wrist(LM.THUMB_IP),
            "index":  dist_to_wrist(LM.INDEX_TIP) > dist_to_wrist(LM.INDEX_PIP),
            "middle": dist_to_wrist(LM.MIDDLE_TIP) > dist_to_wrist(LM.MIDDLE_PIP),
            "ring":   dist_to_wrist(LM.RING_TIP)   > dist_to_wrist(LM.RING_PIP),
            "pinky":  dist_to_wrist(LM.PINKY_TIP)  > dist_to_wrist(LM.PINKY_PIP),
        }

    def get_pinch_distance(self, hand: HandData) -> float:
        thumb = hand.landmarks[LM.THUMB_TIP]
        index = hand.landmarks[LM.INDEX_TIP]
        return np.sqrt((thumb.x - index.x)**2 + (thumb.y - index.y)**2)

    def get_hand_center(self, hand: HandData) -> tuple:
        xs = [lm.x for lm in hand.landmarks]
        ys = [lm.y for lm in hand.landmarks]
        return (sum(xs)/len(xs), sum(ys)/len(ys))

    def close(self):
        self._landmarker.close()
        print("[Tracker] Closed.")