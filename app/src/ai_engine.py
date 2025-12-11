# ai_engine.py
import os
import cv2
import torch   
import types
from ultralytics import YOLO

def fix_aattn_compat(m):
    """Sửa lỗi tương thích cho module AAttn của YOLOv12"""
    try:
        model_to_scan = m.model if hasattr(m, 'model') else m
        for mod in model_to_scan.modules():
            # Tìm module có tên là AAttn (Attention)
            if mod.__class__.__name__ == 'AAttn':
                # Nếu thiếu hàm qkv nhưng có qk và v -> Vá lỗi
                if not hasattr(mod, 'qkv') and hasattr(mod, 'qk') and hasattr(mod, 'v'):
                    def _qkv(self, x):
                        qk_out = self.qk(x)
                        v_out = self.v(x)
                        return torch.cat([qk_out, v_out], dim=1)
                    # Gán hàm mới vào module (Monkey patching)
                    mod.qkv = types.MethodType(_qkv, mod)
        print("✅ Applied AAttn compatibility fix.")
    except Exception as e:
        print(f"⚠️ Could not apply AAttn fix: {e}")

class TrashDetector:
    def __init__(self, model_path, conf_thres=0.25):
        if not os.path.exists(model_path):
            print(f"❌ Error: Model file not found at {model_path}")
            self.model = None
        else:
            print(f"🔄 Loading AI Model: {model_path}...")
            try:
                self.model = YOLO(model_path)
                
                # --- QUAN TRỌNG: DÒNG NÀY PHẢI ĐƯỢC CHẠY ---
                fix_aattn_compat(self.model) 
                # --------------------------------------------
                
                print("✅ Model loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                self.model = None
        
        self.conf_thres = conf_thres
        # Lấy danh sách tên class an toàn
        if self.model and hasattr(self.model, 'names'):
            self.classes = self.model.names
        else:
            self.classes = {}

    def detect(self, frame):
        if self.model is None:
            return frame, []

        # YOLOv12 tự xử lý convert màu/resize, ta chỉ cần truyền frame vào
        # Tuy nhiên để vẽ box đúng màu trên PyQt, ta cần convert BGR -> RGB trước khi vẽ
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            # Predict
            results = self.model.predict(frame, conf=self.conf_thres, imgsz=640, verbose=False, stream=False)
            
            # Vẽ bounding box lên frame
            annotated_frame = results[0].plot() 
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            detections = []
            for r in results[0].boxes:
                cls_id = int(r.cls[0])
                label = self.classes[cls_id] if cls_id in self.classes else str(cls_id)
                conf = float(r.conf[0])
                x1, y1, x2, y2 = r.xyxy[0]
                center_x = int((x1 + x2) / 2)
                
                print(f"--> Detect: {label} ({conf:.2f})")

                detections.append({
                    "label": label,
                    "conf": conf,
                    "center_x": center_x,
                    "box": (int(x1), int(y1), int(x2), int(y2))
                })

            return annotated_frame_rgb, detections
            
        except AttributeError as e:
            print(f"❌ Prediction Error: {e}")
            # Nếu lỗi, trả về ảnh gốc để app không bị tắt
            return frame_rgb, []
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return frame_rgb, []
    
    def update_conf(self, val):
        self.conf_thres = val
        print(f"🔧 AI Config Updated: Conf={self.conf_thres}")