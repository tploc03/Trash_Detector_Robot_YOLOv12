# video.py - FINAL FIXED AATTN ERROR
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from ultralytics import YOLO
import time
import torch
import types

# --- HÀM VÁ LỖI YOLOv12 ---
def fix_aattn_compat(m):
    """Sửa lỗi thiếu thuộc tính 'qkv' trong module AAttn của YOLOv12"""
    try:
        # Lấy model pytorch gốc từ wrapper của Ultralytics
        model_to_scan = m.model if hasattr(m, 'model') else m
        
        for mod in model_to_scan.modules():
            # Tìm các module tên là AAttn
            if mod.__class__.__name__ == 'AAttn':
                # Nếu thiếu hàm qkv nhưng có qk và v -> Tạo hàm qkv giả lập
                if not hasattr(mod, 'qkv') and hasattr(mod, 'qk') and hasattr(mod, 'v'):
                    def _qkv(self, x):
                        qk_out = self.qk(x)
                        v_out = self.v(x)
                        return torch.cat([qk_out, v_out], dim=1)
                    
                    # Gán hàm mới vào module (Monkey patching)
                    mod.qkv = types.MethodType(_qkv, mod)
                    
        print("✅ Applied YOLOv12 AAttn compatibility fix.")
    except Exception as e:
        print(f"⚠️ Warning: Could not apply AAttn fix: {e}")

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    ai_results_signal = pyqtSignal(dict)
    fps_signal = pyqtSignal(int)

    def __init__(self, stream_url, model_path):
        super().__init__()
        self.stream_url = stream_url
        self.model_path = model_path
        self._run_flag = True
        self.ai_enabled = False
        self.confidence = 0.25
        self.reconnect_requested = False
        
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        self.process_every_n_frames = 2  # 🆕 Giảm từ 4 -> 2 để detection nhanh hơn (chạy mỗi 2 frame)
        self.ai_frame_counter = 0
        self.detection_count = 0  # 🆕 Debug: Đếm số detection đã chạy

    def update_source(self, url):
        if url != self.stream_url:
            print(f"🔄 Setting new URL: {url}")
            self.stream_url = url
            self.reconnect_requested = True

    def update_conf(self, conf):
        self.confidence = conf
        
    def set_ai_mode(self, enabled):
        self.ai_enabled = enabled
        # Chỉ load model khi cần thiết (khi bật Auto Mode)
        if enabled and not hasattr(self, 'model'):
            print(f"🔄 Loading YOLO model from {self.model_path}...")
            try:
                self.model = YOLO(self.model_path)
                
                # --- GỌI HÀM SỬA LỖI NGAY SAU KHI LOAD ---
                fix_aattn_compat(self.model) 
                # -----------------------------------------
                
                print("✅ Model loaded successfully")
                print(f"🎯 AI Detection ENABLED - Running on every {self.process_every_n_frames} frames")
            except Exception as e:
                print(f"❌ Model Error: {e}")
                self.ai_enabled = False # Tắt AI nếu load lỗi
        elif not enabled:
            print("⏸️  AI Detection DISABLED")

    def run(self):
        print(f"🚀 Video Thread Starting with: {self.stream_url}")
        cap = cv2.VideoCapture(self.stream_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        while self._run_flag:
            if self.reconnect_requested:
                print(f"🔄 Reconnecting to NEW IP: {self.stream_url} ...")
                if cap.isOpened():
                    cap.release()
                time.sleep(0.5)
                cap = cv2.VideoCapture(self.stream_url)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.reconnect_requested = False

            ret, frame = cap.read()
            
            if not ret:
                if int(time.time()) % 2 == 0:
                    print("⚠️ No Frame. Check IP or Wifi.")
                self.msleep(500)
                continue
            
            # Resize để tăng tốc độ xử lý
            h, w = frame.shape[:2]
            if w > 640:
                scale = 640 / w
                frame = cv2.resize(frame, (640, int(h * scale)))
            
            # --- AI Logic ---
            if self.ai_enabled and hasattr(self, 'model'):
                self.ai_frame_counter += 1
                if self.ai_frame_counter % self.process_every_n_frames == 0:
                    try:
                        # Dự đoán
                        results = self.model.predict(
                            frame, 
                            conf=self.confidence, 
                            verbose=False, 
                            device='cpu', 
                            max_det=5
                        )
                        
                        detections = []
                        if results:
                            # Vẽ box và lấy thông tin
                            for box in results[0].boxes:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                                conf = float(box.conf[0])
                                cls = int(box.cls[0])
                                label = results[0].names[cls]
                                center_x = int((x1 + x2) / 2)
                                
                                detections.append({
                                    'label': label, 
                                    'conf': conf, 
                                    'center_x': center_x, 
                                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                                })
                                
                                # Vẽ trực tiếp lên frame
                                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                                cv2.putText(frame, f"{label} {conf:.2f}", (int(x1), int(y1)-10), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                          
                        if detections:
                            self.detection_count += 1
                            # 🆕 Log detection một lần mỗi 30 frame
                            if self.detection_count % 30 == 0:
                                print(f"🔍 Detection #{self.detection_count}: Found {len(detections)} object(s)")
                            self.ai_results_signal.emit({'detections': detections})
                            
                    except Exception as e:
                        print(f"AI Error: {e}")

            # Convert to Qt Image
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.change_pixmap_signal.emit(qt_image)
            
            # FPS Calculation
            self.frame_count += 1
            if time.time() - self.last_fps_time >= 1.0:
                self.fps = self.frame_count
                self.fps_signal.emit(self.fps)
                self.frame_count = 0
                self.last_fps_time = time.time()

            self.msleep(1)

        cap.release()
        print("🛑 Video Thread Stopped")

    def stop(self):
        self._run_flag = False
        if not self.wait(2000):
            self.terminate()