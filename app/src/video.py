# video.py
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from ai_engine import TrashDetector

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    ai_results_signal = pyqtSignal(dict) # Gửi dict chứa list detections
    fps_signal = pyqtSignal(int)
    
    def __init__(self, cam_ip, model_path):
        super().__init__()
        self.cam_ip = cam_ip
        self.running = True
        self.enable_ai = False # Mặc định tắt AI (Manual Mode)
        
        # Khởi tạo AI Engine
        self.detector = TrashDetector(model_path=model_path)
        
    def run(self):
        print(f"🎥 Connecting to Camera: {self.cam_ip}")
        cap = cv2.VideoCapture(self.cam_ip)
        
        # Tối ưu buffer để giảm lag
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        prev_time = 0
        while self.running:
            if not self.cam_ip: 
                time.sleep(0.1)
                continue
            try:
                ret, frame = cap.read()
                if ret:
                    # 1. Tính FPS
                    now = time.time()
                    fps = 1 / (now - prev_time) if (now - prev_time) > 0 else 0
                    prev_time = now
                    self.fps_signal.emit(int(fps))
                    
                    # 2. Xử lý AI (Nếu bật)
                    final_frame = frame
                    detections = []
                    
                    if self.enable_ai:
                        # Resize về 640x480 để AI chạy nhanh hơn
                        frame_resized = cv2.resize(frame, (640, 480))
                        annotated_frame, detections = self.detector.detect(frame_resized)
                        final_frame = annotated_frame
                        
                        # Gửi kết quả về Main
                        self.ai_results_signal.emit({'detections': detections})
                    
                    # 3. Convert sang Qt Image để hiển thị
                    rgb_frame = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    
                    # Scale ảnh cho vừa khung nhìn nếu cần (nhưng giữ tỷ lệ)
                    self.change_pixmap_signal.emit(qt_img)
                    
                else:
                    # Mất kết nối, thử lại sau 1s
                    time.sleep(1)
                    if self.running: cap.open(self.cam_ip)
                    
            except Exception as e:
                print(f"⚠️ Video Error: {e}")
                time.sleep(1)
        
        cap.release()
        print("🎥 Video Thread Stopped")
    
    def update_source(self, cam_ip):
        print(f"🔄 Switching Camera to: {cam_ip}")
        self.running = False # Dừng vòng lặp tạm thời
        self.wait()          # Chờ thread dừng hẳn
        
        self.cam_ip = cam_ip
        self.running = True  # Bật lại cờ
        self.start()
    
    def set_ai_mode(self, enabled):
        self.enable_ai = enabled

    def update_conf(self, val):
        self.detector.update_conf(val)
    
    def stop(self):
        self.running = False
        self.wait()