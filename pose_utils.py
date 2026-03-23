import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose

class PoseDetector:
    def __init__(self, static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.pose = mp_pose.Pose(static_image_mode=static_image_mode,
                                 min_detection_confidence=min_detection_confidence,
                                 min_tracking_confidence=min_tracking_confidence)

    def detect_pose(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)
        return result

    def detect_pose_in_roi(self, frame, roi):
        x1, y1, x2, y2 = roi
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return None
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb)
        if result.pose_landmarks:
            # Adjust landmarks to original frame coordinates
            for lm in result.pose_landmarks.landmark:
                lm.x = x1 + lm.x * (x2 - x1)
                lm.y = y1 + lm.y * (y2 - y1)
        return result

    def draw_landmarks(self, frame, result):
        if result.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_pose_landmarks_style())
        return frame
