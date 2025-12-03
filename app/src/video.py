import cv2
import time
import torch
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from ultralytics import YOLO

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    ai_results_signal = pyqtSignal(dict)
    fps_signal = pyqtSignal(int)
    
    def __init__(self, cam_ip, model_path):
        super().__init__()
        self.cam_ip = cam_ip
        self.model_path = model_path
        self.model = None
        self.confidence = 0.7
        self.running = True
        self.cap = None
        self.fps_counter = 0
        self.last_fps_time = 0
        
    def run(self):
        try:
            # Load model
            print("🤖 Loading YOLO model...")
            if torch.cuda.is_available():
                self.model = YOLO(self.model_path).to(0)  # GPU
                print("✓ Model loaded on GPU")
            else:
                self.model = YOLO(self.model_path)  # CPU
                print("✓ Model loaded on CPU")
            
            # Mở camera
            self.cap = cv2.VideoCapture(self.cam_ip)
            
            # SỬA: Cài đặt buffer nhỏ để tránh delay
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                print(f"❌ Không thể kết nối camera: {self.cam_ip}")
                return
            
            print(f"✓ Camera đã kết nối: {self.cam_ip}")
            
            last_frame_time = time.time()
            frame_count = 0
            
            while self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("⚠️ Không thể đọc frame từ camera")
                    # Thử kết nối lại
                    self.cap.release()
                    time.sleep(0.5)
                    self.cap = cv2.VideoCapture(self.cam_ip)
                    continue
                
                # SỬA: Giảm kích thước frame để xử lý nhanh hơn
                frame = cv2.resize(frame, (640, 480))
                
                # Inference
                annotated_frame = frame.copy()
                try:
                    results = self.model(frame, conf=self.confidence, verbose=False)
                    detections = []
                    
                    if results and len(results) > 0:
                        boxes = results[0].boxes
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            label = self.model.names[cls]
                            
                            detections.append({
                                'bbox': (x1, y1, x2, y2),
                                'conf': conf,
                                'class': cls,
                                'label': label
                            })
                            
                            # Vẽ bbox
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            text = f"{label} {conf:.2f}"
                            cv2.putText(annotated_frame, text, (x1, y1-10), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    if detections:
                        self.ai_results_signal.emit({
                            'detections': detections,
                            'frame_shape': frame.shape
                        })
                        
                except Exception as e:
                    print(f"⚠️ Lỗi inference: {e}")
                
                # Convert to QImage
                rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                p = convert_to_Qt_format.scaledToWidth(640)
                self.change_pixmap_signal.emit(p)
                
                # FPS counter
                frame_count += 1
                current_time = time.time()
                if current_time - last_frame_time >= 1:
                    fps = frame_count / (current_time - last_frame_time)
                    self.fps_signal.emit(int(fps))
                    frame_count = 0
                    last_frame_time = current_time
                
        except Exception as e:
            print(f"❌ Video Thread Error: {e}")
        finally:
            if self.cap:
                self.cap.release()
    
    def update_source(self, cam_ip):
        """Cập nhật nguồn camera"""
        self.cam_ip = cam_ip
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.cam_ip)
        print(f"🔄 Camera updated: {cam_ip}")
    
    def update_conf(self, conf):
        """Cập nhật confidence threshold"""
        self.confidence = conf
        print(f"🔧 Confidence updated: {conf}")
    
    def stop(self):
        self.running = False
        self.wait()
