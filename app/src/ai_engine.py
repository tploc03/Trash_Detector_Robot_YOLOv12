# ai_engine.py
import cv2
from ultralytics import YOLO

class TrashDetector:
    def __init__(self, model_path="D:\\Program Files\\Files\\25-26_HK1\\LV\\TrashDetectionCar\\app\\models\\best.pt", conf_thres=0.5):
        print(f"Loading AI Model: {model_path}...")
        try:
            self.model = YOLO(model_path)
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
        
        self.conf_thres = conf_thres
        self.classes = self.model.names if self.model else {}

    def detect(self, frame):
        """
        Nhận diện rác trong khung hình
        Trả về: frame đã vẽ khung, list kết quả
        """
        if self.model is None:
            return frame, []

        results = self.model.predict(frame, conf=self.conf_thres, imgsz=640, verbose=False)
        
        detections = []
        
        annotated_frame = results[0].plot()

        for r in results[0].boxes:
            cls_id = int(r.cls[0])
            label = self.classes[cls_id]
            conf = float(r.conf[0])
            
            x1, y1, x2, y2 = r.xyxy[0]
            center_x = int((x1 + x2) / 2)
            
            detections.append({
                "label": label,
                "conf": conf,
                "center_x": center_x,
                "box": (x1, y1, x2, y2)
            })

        return annotated_frame, detections
    
    def update_conf(self, val):
        self.conf_thres = val