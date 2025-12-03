# main.py
import sys
import os
import time
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon

from network import NetworkThread
from styles import MAIN_THEME, BTN_STOP_STYLE
from ui.widgets import SensorBox
from ui.panels import ManualPanel, AutoPanel, SettingsPanel
from video import VideoThread
from sound_manager import SoundManager

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOV12 Trash Collector Control Center")
        self.resize(1400, 800)
        self.setStyleSheet(MAIN_THEME)
        
        self.speed = 200
        self.keys_pressed = set()
        self.is_auto = False
        self.is_running = True
        
        # Logic "Quy tắc 3 giây"
        self.trash_counter = 0      
        self.current_trash = None   
        self.is_trash_confirmed = False
        
        # Default IPs
        self.DEFAULT_ROBOT_IP = "192.168.1.100"
        self.DEFAULT_CAM_IP = "http://192.168.1.20:81/stream" 
        MODEL_PATH = r"D:\Program Files\Files\25-26_HK1\LV\TrashDetectionCar\app\models\best.pt"

        # --- NETWORK THREAD ---
        self.net_thread = NetworkThread(self.DEFAULT_ROBOT_IP)
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.start()
        
        # --- SOUND MANAGER ---
        self.sound_player = SoundManager()
        
        # --- VIDEO THREAD (Khởi động sau khi UI sẵn sàng) ---
        self.video_thread = VideoThread(cam_ip=self.DEFAULT_CAM_IP, model_path=MODEL_PATH)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.ai_results_signal.connect(self.handle_ai_logic)
        self.video_thread.fps_signal.connect(self.update_fps)

        # --- PATROL TIMER ---
        self.patrol_timer = QTimer()
        self.patrol_timer.timeout.connect(self.patrol_loop)
        self.patrol_state = 0
        self.patrol_counter = 0
        
        # --- UI SETUP ---
        self.setup_ui()
        
        # --- START VIDEO THREAD ---
        self.video_thread.start()

    def setup_ui(self):
        """Tách UI setup ra riêng"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # LEFT: VIDEO DISPLAY
        left_layout = QVBoxLayout()
        self.lbl_video = QLabel()
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setMinimumSize(640, 480)
        self.lbl_video.setStyleSheet("background-color: #000; border: 2px solid #0078D4;")
        left_layout.addWidget(self.lbl_video)
        
        # FPS Display
        fps_frame = QFrame()
        fps_layout = QHBoxLayout()
        self.lbl_fps = QLabel("FPS: 0")
        self.lbl_fps.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 14px;")
        fps_layout.addWidget(self.lbl_fps)
        fps_layout.addStretch()
        fps_frame.setLayout(fps_layout)
        left_layout.addWidget(fps_frame)
        
        main_layout.addLayout(left_layout, stretch=65)
        
        # RIGHT: CONTROLS & INFO
        right_layout = QVBoxLayout()
        
        # Group 1: Sensors
        grp_sensor = QGroupBox("📊 SENSORS")
        grp_sensor.setStyleSheet("QGroupBox { font-weight: bold; color: #0078D4; }")
        sens_grid = QGridLayout()
        
        self.box_F = SensorBox("FRONT")
        self.box_L = SensorBox("LEFT")
        self.box_R = SensorBox("RIGHT")
        
        sens_grid.addWidget(self.box_F, 0, 1)
        sens_grid.addWidget(self.box_L, 1, 0)
        sens_grid.addWidget(self.box_R, 1, 2)
        grp_sensor.setLayout(sens_grid)
        right_layout.addWidget(grp_sensor)
        
        # Group 2: Tab Control
        self.tabs = QTabWidget()
        
        # Tab Operation
        tab_op = QWidget()
        op_layout = QVBoxLayout(tab_op)
        self.btn_mode = QPushButton("SWITCH TO AUTO MODE")
        self.btn_mode.setCheckable(True)
        self.btn_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode.toggled.connect(self.toggle_mode)
        op_layout.addWidget(self.btn_mode)

        self.stack = QStackedWidget()
        self.panel_manual = ManualPanel(self)
        self.panel_auto = AutoPanel()
        self.stack.addWidget(self.panel_manual)
        self.stack.addWidget(self.panel_auto)
        op_layout.addWidget(self.stack)
        self.tabs.addTab(tab_op, "OPERATION")

        # Tab Settings
        self.panel_settings = SettingsPanel(self)
        self.tabs.addTab(self.panel_settings, "SETTINGS")
        
        right_layout.addWidget(self.tabs)

        # Group 3: Emergency Stop
        grp_stop = QGroupBox("⚠️ EMERGENCY")
        stop_layout = QVBoxLayout()
        self.btn_stop = QPushButton("EMERGENCY STOP (SPACE)")
        self.btn_stop.setStyleSheet(BTN_STOP_STYLE)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.emergency_stop)
        stop_layout.addWidget(self.btn_stop)
        grp_stop.setLayout(stop_layout)
        right_layout.addWidget(grp_stop)
        
        main_layout.addLayout(right_layout, stretch=35)
        central_widget.setLayout(main_layout)

    # --- HÀM LOGIC CẬP NHẬT TỪ SETTINGS ---
    def update_system_config(self, robot_ip, cam_ip, conf, speed):
        # 1. Cập nhật IP Robot (để điều khiển motor)
        self.net_thread.target_ip = robot_ip
        
        # 2. Cập nhật IP Camera (để xem video)
        if cam_ip != self.DEFAULT_CAM_IP:
            self.DEFAULT_CAM_IP = cam_ip
            print(f"🔄 Switching Camera to: {cam_ip}")
            self.video_thread.update_source(cam_ip)
        
        self.video_thread.update_conf(conf)
        self.speed = speed
        print(f"✓ Config updated - Robot: {robot_ip}, Speed: {speed}")
        self.net_thread.send_command({"cmd": "SPEAK", "file": "/setting.wav"})
        
        print(f"✓ Config updated - Robot: {robot_ip}, Speed: {speed}")

    # --- AI LOGIC ---
    def handle_ai_logic(self, detections_dict):
        if not self.is_auto: return
        
        detections = detections_dict.get('detections', [])
        
        if detections:
            for det in detections:
                label = det['label']
                conf = det['conf']
                print(f"🎯 Phát hiện: {label} ({conf:.2f})")
    
    def update_image(self, qt_img):
        """Cập nhật video"""
        self.lbl_video.setPixmap(QPixmap.fromImage(qt_img))
    
    def update_fps(self, fps):
        """Cập nhật FPS"""
        self.lbl_fps.setText(f"FPS: {fps}")
    
    def update_sensors(self, msg):
        """Cập nhật sensor data"""
        # Cần implement theo protocol robot của bạn
        pass
    
    def toggle_mode(self, checked):
        self.is_auto = checked
        self.video_thread.set_ai_mode(checked)
        
        if checked:
            # Chuyển sang AUTO
            self.btn_mode.setText("⚙ AUTO MODE RUNNING (CLICK TO STOP)")
            self.btn_mode.setStyleSheet("background-color: #06D6A0; color: black; font-weight: bold;")
            self.stack.setCurrentIndex(1)
            
            # Phát âm thanh AUTO
            self.net_thread.send_command({"cmd": "SPEAK", "file": "/auto.wav"})
            
            # Bắt đầu tuần tra
            self.patrol_counter = 0
            self.patrol_timer.start(100)
        else:
            # Chuyển về MANUAL
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("")
            self.stack.setCurrentIndex(0)
            
            # Phát âm thanh MANUAL
            self.net_thread.send_command({"cmd": "SPEAK", "file": "/manual.wav"})
            
            self.patrol_timer.stop()
            self.emergency_stop()
    
    def patrol_loop(self):
        """Logic patrol"""
        pass
    
    def emergency_stop(self):
        """Dừng khẩn cấp"""
        self.net_thread.send_command({"cmd": "STOP"})
        print("🛑 EMERGENCY STOP!")
    
    def closeEvent(self, event):
        """Cleanup khi đóng app"""
        self.is_running = False
        self.video_thread.stop()
        self.net_thread.stop()
        event.accept()
    def confirm_trash_found(self, label_name):
        self.is_trash_confirmed = True
        print(f"🚨 CONFIRMED TRASH: {label_name}")
        
        # 1. Dừng xe
        self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})
        
        # 2. Phát âm thanh theo trình tự
        # Bước A: Phát âm thanh hiệu lệnh "do.wav" (Chuẩn bị làm)
        self.net_thread.send_command({"cmd": "SPEAK", "file": "/do.wav"})
        
        # Bước B: Phát tên loại rác sau 1 khoảng thời gian ngắn (để không bị đè âm thanh)
        # Dùng QTimer để delay lệnh thứ 2 khoảng 1.5 giây (tùy độ dài file do.wav)
        QTimer.singleShot(1500, lambda: self.net_thread.send_command({"cmd": "SPEAK", "file": f"/{label_name}.wav"}))
        
        # 3. Hiện Log
        timestamp = time.strftime("%H:%M:%S")
        self.panel_auto.add_trash_item(f"DETECTED: {label_name}", timestamp)
        
        # --- LOGIC DI CHUYỂN ĐẾN RÁC (Sẽ làm ở phần sau) ---
        # Hiện tại giả lập: Sau khi nói xong tên rác (ví dụ 3s sau), coi như đã đến nơi -> Phát done.wav
        QTimer.singleShot(4500, self.simulate_arrival)

    def simulate_arrival(self):
        # Giả lập đã đến nơi (chạm rác)
        print("✅ Arrived at trash")
        self.net_thread.send_command({"cmd": "SPEAK", "file": "/done.wav"})
        
        # Sau khi xong việc, quay lại tuần tra sau 2s
        QTimer.singleShot(2000, self.resume_patrol)

    def resume_patrol(self):
        self.is_trash_confirmed = False
        self.trash_counter = 0
        if self.is_auto:
            print("🔄 Resuming Patrol...")
            # Gửi lệnh đi chậm hoặc quay vòng để tìm tiếp
            # self.net_thread.send_command({"cmd": "MOVE", "L": 150, "R": -150}) # Quay tròn tìm rác

    # --- UI UPDATES ---
    def update_image(self, qt_img):
        # Scale ảnh mượt mà
        scaled_img = qt_img.scaled(self.lbl_cam.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_cam.setPixmap(QPixmap.fromImage(scaled_img))

    def update_fps(self, fps):
        self.lbl_fps.setText(f"⚡ AI: {fps} FPS")

    def update_sensors(self, msg):
        if "F" in msg: self.box_F.update_val(msg["F"])
        if "L" in msg: self.box_L.update_val(msg["L"])
        if "R" in msg: self.box_R.update_val(msg["R"])

    # --- CONTROLS ---
    def toggle_mode(self, checked):
        self.is_auto = checked
        self.video_thread.set_ai_mode(checked)
        
        if checked:
            self.btn_mode.setText("⚙ AUTO MODE RUNNING (CLICK TO STOP)")
            self.btn_mode.setStyleSheet("background-color: #06D6A0; color: black; font-weight: bold;")
            self.stack.setCurrentIndex(1)
            
            # BẮT ĐẦU TUẦN TRA
            self.patrol_counter = 0
            self.patrol_timer.start(100) # Gọi hàm loop mỗi 100ms
        else:
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("")
            self.stack.setCurrentIndex(0)
            self.patrol_timer.stop() # Dừng timer
            self.emergency_stop()

    def patrol_loop(self):
        if not self.is_auto or self.is_trash_confirmed:
            return

        # Mỗi lần gọi hàm này tương ứng với 1 khoảng thời gian (ví dụ 100ms)
        self.patrol_counter += 1
        
        # 50 đơn vị * 100ms = 5 giây
        limit = 50 
        
        if self.patrol_counter <= limit:
            # Giai đoạn 1: TIẾN
            if self.patrol_state != 0:
                print("🚗 AUTO: Moving Forward")
                self.patrol_state = 0
            # Gửi lệnh tiến (tránh vật cản dựa vào cảm biến - logic né tránh đơn giản)
            # Nếu cảm biến trước < 30cm thì tự lùi hoặc rẽ
            if self.box_F.current_value > 0 and self.box_F.current_value < 30:
                self.net_thread.send_command({"cmd": "MOVE", "L": -150, "R": -150}) # Lùi khẩn cấp
            else:
                self.net_thread.send_command({"cmd": "MOVE", "L": 180, "R": 180})
                
        elif self.patrol_counter <= limit * 2:
            # Giai đoạn 2: QUAY ĐẦU (Quay tại chỗ)
            if self.patrol_state != 1:
                print("🔄 AUTO: Turning Around")
                self.patrol_state = 1
            self.net_thread.send_command({"cmd": "MOVE", "L": 180, "R": -180})
            
        else:
            # Reset chu kỳ
            self.patrol_counter = 0
    def emergency_stop(self):
        self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})
        self.is_auto = False
        self.btn_mode.setChecked(False)
        self.stack.setCurrentIndex(0)

    def update_speed_var(self, val):
        self.speed = val

    # --- INPUT HANDLING ---
    def keyPressEvent(self, event):
        if not event.isAutoRepeat(): self.handle_input(event.key(), True)

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat(): self.handle_input(event.key(), False)
    
    def on_gui_btn_press(self, key_code):
        self.handle_input(key_code, True)
    
    def on_gui_btn_release(self, key_code):
        self.handle_input(key_code, False)

    def handle_input(self, key, pressed):
        if key == Qt.Key.Key_Space and pressed:
            self.emergency_stop(); return
        if self.is_auto: return 

        if pressed: self.keys_pressed.add(key)
        elif key in self.keys_pressed: self.keys_pressed.remove(key)

        self.update_visual_keys()

        L, R = 0, 0
        s = self.speed
        if Qt.Key.Key_W in self.keys_pressed: L = s; R = s
        elif Qt.Key.Key_S in self.keys_pressed: L = -s; R = -s
        elif Qt.Key.Key_A in self.keys_pressed: L = -s; R = s
        elif Qt.Key.Key_D in self.keys_pressed: L = s; R = -s
        
        self.net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})

    def update_visual_keys(self):
        self.panel_manual.btn_w.set_active(Qt.Key.Key_W in self.keys_pressed)
        self.panel_manual.btn_a.set_active(Qt.Key.Key_A in self.keys_pressed)
        self.panel_manual.btn_s.set_active(Qt.Key.Key_S in self.keys_pressed)
        self.panel_manual.btn_d.set_active(Qt.Key.Key_D in self.keys_pressed)

    def closeEvent(self, event):
        self.net_thread.stop()
        self.video_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotApp()
    window.show()
    sys.exit(app.exec())