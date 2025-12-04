# ai_engine.py
import os
import cv2
from ultralytics import YOLO

class TrashDetector:
    def __init__(self, model_path, conf_thres=0.5):
        # Kiểm tra file model có tồn tại không
        if not os.path.exists(model_path):
            print(f"❌ Error: Model file not found at {model_path}")
            self.model = None
        else:
            print(f"🤖 Loading AI Model: {model_path}...")
            try:
                self.model = YOLO(model_path)
                print("✓ Model loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                self.model = None
        
        self.conf_thres = conf_thres
        self.classes = self.model.names if self.model else {}

    def detect(self, frame):
        if self.model is None:
            return frame, []

        # Chạy inference
        results = self.model.predict(frame, conf=self.conf_thres, imgsz=640, verbose=False)
        detections = []
        
        # Vẽ bounding box lên ảnh
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
                "box": (int(x1), int(y1), int(x2), int(y2))
            })

        return annotated_frame, detections
    
    def update_conf(self, val):
        self.conf_thres = val