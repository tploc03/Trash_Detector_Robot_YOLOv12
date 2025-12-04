# video.py
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
from PyQt6.QtGui import QImage
from ai_engine import TrashDetector

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    ai_results_signal = pyqtSignal(dict)
    fps_signal = pyqtSignal(int)
    
    def __init__(self, cam_ip, model_path):
        super().__init__()
        self.cam_ip = cam_ip
        self.running = True
        self.enable_ai = False
        self.detector = TrashDetector(model_path=model_path)
        
        # Biến điều khiển việc đổi IP an toàn
        self.pending_ip = None 
        self.mutex = QMutex()

    def run(self):
        print(f"🎥 Starting Video Thread: {self.cam_ip}")
        cap = cv2.VideoCapture()
        
        # Mở kết nối ban đầu
        if self.cam_ip:
            cap.open(self.cam_ip)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        prev_time = 0
        
        while self.running:
            # 1. KIỂM TRA YÊU CẦU ĐỔI IP (Non-blocking)
            self.mutex.lock()
            if self.pending_ip is not None:
                new_ip = self.pending_ip
                self.pending_ip = None
                self.mutex.unlock()
                
                print(f"🔄 Switching Stream to: {new_ip}")
                if cap.isOpened(): cap.release()
                
                # Thử kết nối IP mới (Hành động này tốn thời gian nhưng nằm trong Thread nên ko đơ UI)
                cap.open(new_ip)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.cam_ip = new_ip
            else:
                self.mutex.unlock()

            # 2. Đọc Frame
            if not cap.isOpened():
                time.sleep(0.5) # Nghỉ chút nếu chưa kết nối được
                continue

            try:
                ret, frame = cap.read()
                if ret:
                    # Tính FPS
                    now = time.time()
                    fps = int(1 / (now - prev_time)) if (now - prev_time) > 0 else 0
                    prev_time = now
                    self.fps_signal.emit(fps)
                    
                    # AI Processing
                    final_frame = frame
                    detections = []
                    if self.enable_ai:
                        # Resize 640x480 để đồng bộ model
                        frame_resized = cv2.resize(frame, (640, 480))
                        annotated_frame, detections = self.detector.detect(frame_resized)
                        final_frame = annotated_frame
                        self.ai_results_signal.emit({'detections': detections})
                    
                    # Convert QImage
                    rgb_frame = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    self.change_pixmap_signal.emit(qt_img)
                else:
                    # Mất kết nối frame -> Thử lại nhẹ nhàng
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"⚠️ Stream Error: {e}")
                time.sleep(1)

        cap.release()
        print("🎥 Video Thread Stopped Cleanly")
    
    def update_source(self, new_ip):
        # Hàm này được gọi từ UI, chỉ gán biến flag rồi return ngay lập tức -> KHÔNG ĐƠ UI
        self.mutex.lock()
        self.pending_ip = new_ip
        self.mutex.unlock()
    
    def set_ai_mode(self, enabled):
        self.enable_ai = enabled

    def update_conf(self, val):
        self.detector.update_conf(val)
    
    def stop(self):
        self.running = False
        self.wait() # Chờ thread kết thúc tác vụ hiện tại rồi đóng