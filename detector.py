import cv2
from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8s.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        # Lower confidence for better detection in CCTV
        results = self.model(frame, conf=0.25)[0]

        boxes = []
        for r in results.boxes.data.tolist():
            x1, y1, x2, y2, score, cls_id = r

            # class 0 = person
            if int(cls_id) == 0:
                boxes.append([int(x1), int(y1), int(x2), int(y2)])

        return boxes
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces