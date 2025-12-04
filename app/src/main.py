# main.py
import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

# Import modules
from network import NetworkThread
from styles import MAIN_THEME, BTN_STOP_STYLE
from ui.widgets import SensorBox, LoadingOverlay # Nhớ import LoadingOverlay
from ui.panels import ManualPanel, AutoPanel, SettingsPanel
from video import VideoThread
from sound_manager import SoundManager

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOV12 Trash Collector - Command Center")
        self.resize(1400, 850)
        self.setStyleSheet(MAIN_THEME)
        
        # --- 1. CONFIG & VARIABLES ---
        self.speed = 200
        self.keys_pressed = set()
        self.is_auto = False
        self.is_processing = False # Cờ chặn input khi đang loading
        
        # AI Logic Variables
        self.trash_counter = 0      
        self.current_trash = None   
        self.is_trash_confirmed = False
        
        # Cấu hình IP Mặc định
        self.DEFAULT_ROBOT_IP = "192.168.1.19" 
        self.DEFAULT_CAM_IP = "http://192.168.1.19:81/stream"
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.MODEL_PATH = os.path.join(base_dir, "models", "best.pt")

        # --- 2. START THREADS ---
        self.net_thread = NetworkThread(self.DEFAULT_ROBOT_IP)
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.start()
        
        self.sound_player = SoundManager(self.net_thread)
        
        self.video_thread = VideoThread(cam_ip=self.DEFAULT_CAM_IP, model_path=self.MODEL_PATH)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.ai_results_signal.connect(self.handle_ai_logic)
        self.video_thread.fps_signal.connect(self.update_fps)
        self.video_thread.start()

        # Timer cho Auto Mode
        self.patrol_timer = QTimer()
        self.patrol_timer.timeout.connect(self.patrol_loop)
        self.patrol_state = 0
        self.patrol_counter = 0

        # --- 3. UI SETUP ---
        self.setup_ui()
        
        # Loading Overlay (Luôn nằm trên cùng)
        self.loader = LoadingOverlay(self)
        
        QTimer.singleShot(2000, self.sound_player.play_startup)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        
        # --- LEFT: VIDEO ---
        left_layout = QVBoxLayout()
        self.lbl_video = QLabel("WAITING FOR STREAM...")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setMinimumSize(640, 480)
        self.lbl_video.setStyleSheet("background-color: #000; border: 2px solid #0078D4; color: white;")
        left_layout.addWidget(self.lbl_video, stretch=1)
        
        self.lbl_fps = QLabel("AI FPS: 0")
        self.lbl_fps.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 14px;")
        left_layout.addWidget(self.lbl_fps)
        main_layout.addLayout(left_layout, stretch=65)
        
        # --- RIGHT: CONTROLS ---
        right_layout = QVBoxLayout()
        
        grp_sensor = QGroupBox("📊 RADAR SENSORS")
        sens_grid = QGridLayout()
        self.box_F = SensorBox("FRONT")
        self.box_L = SensorBox("LEFT")
        self.box_R = SensorBox("RIGHT")
        sens_grid.addWidget(self.box_F, 0, 1)
        sens_grid.addWidget(self.box_L, 1, 0)
        sens_grid.addWidget(self.box_R, 1, 2)
        grp_sensor.setLayout(sens_grid)
        right_layout.addWidget(grp_sensor)
        
        self.tabs = QTabWidget()
        
        # Tab Operation
        tab_op = QWidget()
        op_layout = QVBoxLayout(tab_op)
        self.btn_mode = QPushButton("SWITCH TO AUTO MODE")
        self.btn_mode.setCheckable(True)
        self.btn_mode.toggled.connect(self.request_toggle_mode) # Gọi qua hàm trung gian
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

        # Emergency Stop
        self.btn_stop = QPushButton("🛑 EMERGENCY STOP (SPACE)")
        self.btn_stop.setStyleSheet(BTN_STOP_STYLE)
        self.btn_stop.clicked.connect(self.emergency_stop)
        right_layout.addWidget(self.btn_stop)
        
        main_layout.addLayout(right_layout, stretch=35)
        central_widget.setLayout(main_layout)
        
        # Focus Policy để bắt phím Space mọi lúc
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # --- LOADING & CONFIG LOGIC ---
    def show_loading(self, msg, duration=2000):
        """Hiển thị overlay chặn input trong duration (ms)"""
        self.is_processing = True
        self.loader.show_msg(msg)
        self.setEnabled(False) # Disable toàn bộ cửa sổ
        
        # Dùng SingleShot để tắt loading
        QTimer.singleShot(duration, self.finish_loading)

    def finish_loading(self):
        self.loader.hide()
        self.setEnabled(True) # Enable lại
        self.is_processing = False
        self.setFocus() # Lấy lại focus bàn phím

    def apply_system_config(self, robot_ip, cam_ip, conf, speed):
        # 1. Hiển thị loading 2s để phần cứng chuẩn bị
        self.show_loading("APPLYING SETTINGS...", 2000)
        
        # 2. Cập nhật biến
        self.net_thread.target_ip = robot_ip
        self.video_thread.update_conf(conf)
        self.speed = speed
        
        # 3. Restart Camera nếu IP thay đổi (sau khi hết loading)
        if cam_ip != self.video_thread.cam_ip:
            self.video_thread.update_source(cam_ip)

        # 4. Gửi lệnh xuống Robot
        cmd = {"cmd": "SET_CONFIG", "conf": conf, "speed": speed}
        self.net_thread.send_command(cmd)
        
        # 5. Âm thanh
        QTimer.singleShot(500, lambda: self.sound_player.play_remote("setting.wav"))
        print(f"✓ Config Updated: Robot={robot_ip}, Cam={cam_ip}")

    # --- MODE SWITCH LOGIC ---
    def request_toggle_mode(self, checked):
        # Hàm này được gọi khi bấm nút Toggle
        if checked:
            self.show_loading("STARTING AUTO MODE...", 3000)
            # Logic thực sự sẽ chạy sau 3s (dùng timer hoặc gọi hàm setup)
            QTimer.singleShot(500, lambda: self.execute_mode_switch(True))
        else:
            self.show_loading("SWITCHING TO MANUAL...", 1500)
            QTimer.singleShot(500, lambda: self.execute_mode_switch(False))

    def execute_mode_switch(self, is_auto):
        self.is_auto = is_auto
        self.video_thread.set_ai_mode(is_auto)
        
        if is_auto:
            self.btn_mode.setText("⚙ AUTO MODE RUNNING (CLICK TO STOP)")
            self.btn_mode.setStyleSheet("background-color: #06D6A0; color: black; font-weight: bold;")
            self.stack.setCurrentIndex(1)
            self.sound_player.play_remote("auto.wav")
            
            # Reset & Start Patrol
            self.patrol_counter = 0
            self.patrol_timer.start(100) 
        else:
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("")
            self.stack.setCurrentIndex(0)
            self.sound_player.play_remote("manual.wav")
            
            self.patrol_timer.stop()
            self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})

    # --- INPUT LOGIC (FIXED) ---
    def keyPressEvent(self, event):
        if event.isAutoRepeat() or self.is_processing: return
        self.handle_input(event.key(), True)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat() or self.is_processing: return
        self.handle_input(event.key(), False)
    
    def on_gui_btn_press(self, key_code):
        if not self.is_processing: self.handle_input(key_code, True)
    
    def on_gui_btn_release(self, key_code):
        if not self.is_processing: self.handle_input(key_code, False)

    def handle_input(self, key, pressed):
        # 1. EMERGENCY STOP (Space) - Luôn ưu tiên
        if key == Qt.Key.Key_Space:
            if pressed: self.emergency_stop()
            return

        # 2. Nếu đang Auto -> Không nhận phím di chuyển
        if self.is_auto: return 

        # 3. FILTER KEYS (Chỉ nhận W, A, S, D)
        valid_keys = [Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D]
        if key not in valid_keys: return

        if pressed: self.keys_pressed.add(key)
        elif key in self.keys_pressed: self.keys_pressed.remove(key)
        
        # Update Visual Keys
        self.panel_manual.btn_w.set_active(Qt.Key.Key_W in self.keys_pressed)
        self.panel_manual.btn_a.set_active(Qt.Key.Key_A in self.keys_pressed)
        self.panel_manual.btn_s.set_active(Qt.Key.Key_S in self.keys_pressed)
        self.panel_manual.btn_d.set_active(Qt.Key.Key_D in self.keys_pressed)

        # Logic điều khiển L298N
        L, R = 0, 0
        s = self.speed
        
        if Qt.Key.Key_W in self.keys_pressed: 
            L = s; R = s
        elif Qt.Key.Key_S in self.keys_pressed: 
            L = -s; R = -s
        elif Qt.Key.Key_A in self.keys_pressed: 
            L = -s; R = s   # Quay trái tại chỗ
        elif Qt.Key.Key_D in self.keys_pressed: 
            L = s; R = -s   # Quay phải tại chỗ
        
        # Gửi lệnh
        self.net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})

    def emergency_stop(self):
        """Hàm dừng khẩn cấp Hard Kill"""
        print("🚨 EMERGENCY STOP TRIGGERED!")
        # 1. Ngắt Timer AI
        self.patrol_timer.stop()
        
        # 2. Ngắt Video AI
        self.is_auto = False
        self.video_thread.set_ai_mode(False)
        
        # 3. Gửi lệnh dừng động cơ liên tục (để đảm bảo gói tin đến)
        for _ in range(3):
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        
        # 4. Reset UI
        self.btn_mode.blockSignals(True) # Chặn signal để không kích hoạt loading loop
        self.btn_mode.setChecked(False)
        self.btn_mode.setText("SWITCH TO AUTO MODE")
        self.btn_mode.setStyleSheet("")
        self.btn_mode.blockSignals(False)
        
        self.stack.setCurrentIndex(0) # Về Manual
        self.keys_pressed.clear()
        
        # 5. Visual Feedback
        self.loader.show_msg("🚨 EMERGENCY STOP!", "System Halted")
        QTimer.singleShot(1000, self.loader.hide)
        self.setFocus() # Lấy lại focus để nhận phím W A S D ngay

    # ... (Các hàm update_sensors, update_image, update_fps giữ nguyên) ...
    def update_sensors(self, msg):
        if "F" in msg: self.box_F.update_val(msg["F"])
        if "L" in msg: self.box_L.update_val(msg["L"])
        if "R" in msg: self.box_R.update_val(msg["R"])
        
    def update_image(self, qt_img):
        scaled_img = qt_img.scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(QPixmap.fromImage(scaled_img))

    def update_fps(self, fps):
        self.lbl_fps.setText(f"AI FPS: {fps}")

    def handle_ai_logic(self, detections_dict):
        # (Giữ nguyên logic cũ)
        if not self.is_auto: return
        detections = detections_dict.get('detections', [])
        if detections:
            best_det = max(detections, key=lambda x: x['conf'])
            label = best_det['label']
            if self.current_trash == label: self.trash_counter += 1
            else: self.current_trash = label; self.trash_counter = 1
            
            if self.trash_counter > 10 and not self.is_trash_confirmed:
                self.confirm_trash_found(label)
        else:
            self.trash_counter = 0; self.current_trash = None

    def confirm_trash_found(self, label_name):
        # (Giữ nguyên logic cũ)
        self.is_trash_confirmed = True
        self.patrol_timer.stop()
        self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})
        self.sound_player.play_remote("do.wav")
        QTimer.singleShot(1500, lambda: self.sound_player.play_trash_detect(label_name))
        timestamp = time.strftime("%H:%M:%S")
        self.panel_auto.add_trash_item(f"DETECTED: {label_name}", timestamp)
        QTimer.singleShot(4500, self.finish_trash_job)

    def finish_trash_job(self):
        self.sound_player.play_remote("done.wav")
        QTimer.singleShot(2000, self.resume_patrol)

    def resume_patrol(self):
        if self.is_auto:
            self.is_trash_confirmed = False
            self.trash_counter = 0
            self.patrol_timer.start(100)

    def patrol_loop(self):
        # (Giữ nguyên logic cũ)
        self.patrol_counter += 1
        if self.box_F.current_value > 0 and self.box_F.current_value < 30:
            self.net_thread.send_command({"cmd": "MOVE", "L": -150, "R": -150})
            return
        if self.patrol_counter <= 50:
            self.net_thread.send_command({"cmd": "MOVE", "L": 150, "R": 150})
        elif self.patrol_counter <= 80:
            self.net_thread.send_command({"cmd": "MOVE", "L": 150, "R": -150})
        else:
            self.patrol_counter = 0

    def closeEvent(self, event):
        self.video_thread.stop()
        self.net_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotApp()
    window.show()
    sys.exit(app.exec())