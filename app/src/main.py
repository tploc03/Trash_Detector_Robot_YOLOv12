# main.py
import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon

# Import modules (Đảm bảo bạn đã cập nhật network.py và video.py từ phần 1)
from network import NetworkThread
from styles import MAIN_THEME, BTN_STOP_STYLE
from ui.widgets import SensorBox, LoadingOverlay
from ui.panels import ManualPanel, AutoPanel, SettingsPanel
from video import VideoThread
from sound_manager import SoundManager

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOv12 Trash Collector - Command Center")
        self.resize(1280, 800)
        self.setStyleSheet(MAIN_THEME)
        
        # --- 1. BIẾN HỆ THỐNG ---
        # Config Manual
        self.man_speed = 200
        self.man_conf = 0.7
        
        # Config Auto
        self.auto_speed = 180
        self.auto_conf = 0.65
        self.auto_fwd_time = 3 # giây
        self.is_auto = False
        
        # Logic Loop
        self.patrol_state = 0 # 0: Forward, 1: Turn
        self.patrol_timer_start = 0
        self.keys_pressed = set()
        self.is_processing = False
        self.last_near_trash_alert = 0 # Tránh spam âm thanh "gần rác"

        # AI Logic
        self.trash_counter = 0      
        self.current_trash = None   
        self.is_trash_confirmed = False
        
        # Paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        self.MODEL_PATH = os.path.join(parent_dir, "models", "best.pt")

        # --- 2. KHỞI TẠO THREADS ---
        # Network
        self.net_thread = NetworkThread("192.168.1.19")
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.ping_signal.connect(self.update_ping)
        self.net_thread.start()
        
        # Sound
        self.sound = SoundManager(self.net_thread)
        
        # Video
        self.video_thread = VideoThread("http://192.168.1.19:81/stream", self.MODEL_PATH)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.ai_results_signal.connect(self.handle_ai_logic)
        self.video_thread.fps_signal.connect(self.update_fps)
        self.video_thread.start()

        # Timer chính cho Auto Mode (Chạy 50ms/lần để mượt)
        self.loop_timer = QTimer()
        self.loop_timer.timeout.connect(self.auto_loop_logic)

        # --- 3. UI SETUP ---
        self.setup_ui()
        self.loader = LoadingOverlay(self)
        
        # Âm thanh khởi động
        QTimer.singleShot(2000, self.sound.play_startup)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        
        # --- CỘT TRÁI: CAMERA ---
        left_lay = QVBoxLayout()
        
        # Header FPS & Ping (Đưa lên trên theo yêu cầu)
        info_lay = QHBoxLayout()
        self.lbl_fps = QLabel("FPS: 0")
        self.lbl_fps.setStyleSheet("color: #0F0; font-weight: bold; font-size: 14px;")
        self.lbl_ping = QLabel("Ping: --")
        self.lbl_ping.setStyleSheet("color: #FA0; font-weight: bold; font-size: 14px; margin-left: 15px;")
        info_lay.addWidget(self.lbl_fps)
        info_lay.addWidget(self.lbl_ping)
        info_lay.addStretch()
        left_lay.addLayout(info_lay)

        # Video Frame
        self.lbl_video = QLabel("NO SIGNAL")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setStyleSheet("background: #000; border: 2px solid #0078D4; color: #555;")
        self.lbl_video.setMinimumSize(640, 480)
        left_lay.addWidget(self.lbl_video, 1)
        
        main_lay.addLayout(left_lay, 65)

        # --- CỘT PHẢI: CONTROLS ---
        right_lay = QVBoxLayout()
        
        # Sensors
        grp_sens = QGroupBox("📡 RADAR")
        g_lay = QGridLayout()
        self.box_F = SensorBox("FRONT")
        self.box_L = SensorBox("LEFT")
        self.box_R = SensorBox("RIGHT")
        g_lay.addWidget(self.box_F, 0, 1)
        g_lay.addWidget(self.box_L, 1, 0)
        g_lay.addWidget(self.box_R, 1, 2)
        grp_sens.setLayout(g_lay)
        right_lay.addWidget(grp_sens)
        
        # Tab điều khiển
        self.main_tabs = QTabWidget()
        
        # Tab 1: Operation
        tab_op = QWidget()
        op_lay = QVBoxLayout(tab_op)
        
        self.btn_mode = QPushButton("SWITCH TO AUTO MODE")
        self.btn_mode.setCheckable(True)
        self.btn_mode.setMinimumHeight(50)
        self.btn_mode.clicked.connect(self.request_toggle_mode)
        op_lay.addWidget(self.btn_mode)

        self.stack = QStackedWidget()
        self.panel_man = ManualPanel(self)
        self.panel_auto = AutoPanel()
        self.stack.addWidget(self.panel_man)
        self.stack.addWidget(self.panel_auto)
        op_lay.addWidget(self.stack)
        
        self.main_tabs.addTab(tab_op, "OPERATION")

        # Tab 2: Settings (Giao diện mới)
        self.panel_set = SettingsPanel(self)
        self.main_tabs.addTab(self.panel_set, "SETTINGS")
        
        right_lay.addWidget(self.main_tabs)

        # Emergency Stop
        btn_stop = QPushButton("🛑 EMERGENCY STOP (SPACE)")
        btn_stop.setStyleSheet(BTN_STOP_STYLE)
        btn_stop.clicked.connect(self.emergency_stop)
        right_lay.addWidget(btn_stop)
        
        main_lay.addLayout(right_lay, 35)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # --- LOGIC: CẬP NHẬT SETTINGS ---
    def update_robot_ip(self, ip):
        self.show_loading(f"CONNECTING ROBOT: {ip}...", 1000)
        self.net_thread.update_target_ip(ip)
        self.sound.play_remote("setting.wav")

    def update_cam_ip(self, url):
        self.show_loading(f"CONNECTING CAM: {url}...", 2000)
        self.video_thread.update_source(url)
        self.sound.play_remote("setting.wav")

    def apply_manual_config(self, speed, conf):
        self.man_speed = speed
        self.man_conf = conf
        # Nếu đang ở manual thì update ngay
        if not self.is_auto:
            self.video_thread.update_conf(conf)
            self.net_thread.send_command({"cmd": "SET_CONFIG", "speed": speed})
        
        self.show_loading("APPLIED MANUAL CONFIG", 800)
        self.sound.play_remote("setting.wav")

    def apply_auto_config(self, speed, conf, time_val, turn_time=None):
        self.auto_speed = speed
        self.auto_conf = conf
        self.auto_fwd_time = time_val
        if turn_time is not None:
            self.auto_turn_time = turn_time
        # Nếu đang auto thì update ngay
        if self.is_auto:
            self.video_thread.update_conf(conf)
        
        self.show_loading("APPLIED AUTO CONFIG", 800)
        self.sound.play_remote("setting.wav")

    # --- LOGIC: CHUYỂN MODE ---
    def request_toggle_mode(self):
        checked = self.btn_mode.isChecked()
        if checked:
            self.show_loading("STARTING AUTO MODE...", 2000)
            QTimer.singleShot(500, lambda: self.set_mode(True))
        else:
            self.show_loading("SWITCHING TO MANUAL...", 1000)
            QTimer.singleShot(500, lambda: self.set_mode(False))

    def set_mode(self, auto):
        self.is_auto = auto
        self.video_thread.set_ai_mode(auto)
        
        if auto:
            self.btn_mode.setText("⚙ AUTO RUNNING (CLICK TO STOP)")
            self.btn_mode.setStyleSheet("background-color: #06D6A0; color: #000; font-weight: bold;")
            self.stack.setCurrentIndex(1)
            self.sound.play_remote("auto.wav")
            
            # Setup Auto Params
            self.video_thread.update_conf(self.auto_conf)
            self.patrol_state = 0 # Bắt đầu bằng đi thẳng
            self.patrol_timer_start = time.time()
            self.loop_timer.start(50) # Bắt đầu vòng lặp Logic
        else:
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("")
            self.stack.setCurrentIndex(0)
            self.sound.play_remote("manual.wav")
            
            self.loop_timer.stop()
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})

    # --- LOGIC: AUTO LOOP (QUAN TRỌNG) ---
    def auto_loop_logic(self):
        # Nếu đã tìm thấy rác -> Dừng logic tuần tra
        if self.is_trash_confirmed: return

        current_time = time.time()
        elapsed = current_time - self.patrol_timer_start
        
        # 1. Kiểm tra cảm biến va chạm trước
        dist_f = self.box_F.current_value
        if 0 < dist_f < 30:
            # Gặp vật cản gần -> Lùi lại ngay
            self.net_thread.send_command({"cmd": "MOVE", "L": -150, "R": -150})
            return

        # 2. State Machine: Tiến -> Quay -> Tiến
        if self.patrol_state == 0: # STATE: FORWARD
            if elapsed < self.auto_fwd_time:
                # Đi thẳng
                s = self.auto_speed
                self.net_thread.send_command({"cmd": "MOVE", "L": s, "R": s})
            else:
                # Hết giờ -> Chuyển sang Quay
                self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
                self.patrol_state = 1
                self.patrol_timer_start = current_time # Reset timer cho turn
        
        elif self.patrol_state == 1: # STATE: TURN 180
            # Giả sử quay 180 độ mất khoảng 1.5 giây (cần tinh chỉnh thực tế)
            turn_duration = 1.5 
            if elapsed < turn_duration:
                # Quay tại chỗ (Trái lùi, Phải tiến)
                s = self.auto_speed
                self.net_thread.send_command({"cmd": "MOVE", "L": -s, "R": s})
            else:
                # Quay xong -> Dừng -> Chuyển sang Tiến
                self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
                self.patrol_state = 0
                self.patrol_timer_start = current_time

    # --- LOGIC: AI XỬ LÝ ---
    def handle_ai_logic(self, result):
        if not self.is_auto: return
        
        dets = result.get('detections', [])
        if not dets:
            self.trash_counter = 0
            return

        # Lấy vật thể có độ tin cậy cao nhất
        best = max(dets, key=lambda x: x['conf'])
        label = best['label']
        
        if label == self.current_trash:
            self.trash_counter += 1
        else:
            self.current_trash = label
            self.trash_counter = 1
        
        # Xác nhận rác (liên tiếp 5 frame)
        if self.trash_counter >= 5 and not self.is_trash_confirmed:
            self.start_trash_pickup_sequence(label)
        
        # Âm thanh cảnh báo khi xe đến gần rác (Sonar < 15cm)
        if self.is_trash_confirmed:
            dist = self.box_F.current_value
            if 0 < dist < 15 and (time.time() - self.last_near_trash_alert > 5):
                # Phát âm thanh "Gần rác" (Bạn cần có file near.wav hoặc tương tự)
                # Tạm thời dùng beep ngắn
                self.sound.play_remote("beep.wav") 
                self.last_near_trash_alert = time.time()

    def start_trash_pickup_sequence(self, label):
        self.is_trash_confirmed = True
        self.loop_timer.stop() # Dừng tuần tra
        
        # 1. Dừng xe & Phát hiện
        self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        self.sound.play_remote("detect.wav") # Âm thanh "Phát hiện rác"
        self.show_loading(f"DETECTED: {label.upper()}", 1000)
        
        # 2. Nói tên rác (Sau 1.5s)
        QTimer.singleShot(1500, lambda: self.sound.play_trash_detect(label))
        
        # 3. Thông báo "Đang đi tới rác" (Sau 3s)
        QTimer.singleShot(3500, lambda: self.sound.play_remote("moving_to_trash.wav"))
        
        # 4. Logic lao vào rác (Đơn giản hóa: Tiến chậm trong 2s)
        QTimer.singleShot(4000, lambda: self.net_thread.send_command({"cmd": "MOVE", "L": 120, "R": 120}))
        
        # 5. Kết thúc (Dừng sau 2s tiến)
        QTimer.singleShot(6000, self.finish_trash_job)

    def finish_trash_job(self):
        self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        self.sound.play_remote("done.wav") # Âm thanh chạm rác/hoàn thành
        
        # Ghi log
        t_str = time.strftime("%H:%M:%S")
        self.panel_auto.add_trash_item(f"COLLECTED: {self.current_trash}", t_str)
        
        # Quay lại tuần tra sau 3s
        QTimer.singleShot(3000, self.resume_patrol)

    def resume_patrol(self):
        if self.is_auto:
            self.is_trash_confirmed = False
            self.trash_counter = 0
            self.patrol_state = 0 # Reset về đi thẳng
            self.patrol_timer_start = time.time()
            self.loop_timer.start(50)

    # --- UTILS ---
    def update_sensors(self, data):
        if "F" in data: self.box_F.update_val(data["F"])
        if "L" in data: self.box_L.update_val(data["L"])
        if "R" in data: self.box_R.update_val(data["R"])

    def update_ping(self, ping_str):
        self.lbl_ping.setText(f"Ping: {ping_str}")
        if "TIMEOUT" in ping_str: self.lbl_ping.setStyleSheet("color: #F00;")
        else: self.lbl_ping.setStyleSheet("color: #0F0;")

    def update_image(self, img):
        scaled = img.scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.lbl_video.setPixmap(QPixmap.fromImage(scaled))

    def update_fps(self, fps):
        self.lbl_fps.setText(f"FPS: {fps}")

    def show_loading(self, msg, duration):
        self.is_processing = True
        self.loader.show_msg(msg)
        self.setEnabled(False)
        QTimer.singleShot(duration, self.finish_loading)

    def finish_loading(self):
        self.loader.hide()
        self.setEnabled(True)
        self.is_processing = False
        self.setFocus()

    # Input Keyboard (Giữ nguyên logic cũ)
    def keyPressEvent(self, e):
        if not e.isAutoRepeat() and not self.is_processing: self.handle_key(e.key(), True)
    def keyReleaseEvent(self, e):
        if not e.isAutoRepeat() and not self.is_processing: self.handle_key(e.key(), False)
    
    def handle_key(self, key, pressed):
        if key == Qt.Key.Key_Space: 
            if pressed: self.emergency_stop()
            return
        if self.is_auto: return
        
        valid = [Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D]
        if key not in valid: return
        
        if pressed: self.keys_pressed.add(key)
        elif key in self.keys_pressed: self.keys_pressed.remove(key)
        
        # Update Visual
        self.panel_man.btn_w.set_active(Qt.Key.Key_W in self.keys_pressed)
        self.panel_man.btn_a.set_active(Qt.Key.Key_A in self.keys_pressed)
        self.panel_man.btn_s.set_active(Qt.Key.Key_S in self.keys_pressed)
        self.panel_man.btn_d.set_active(Qt.Key.Key_D in self.keys_pressed)

        L, R = 0, 0
        s = self.man_speed
        if Qt.Key.Key_W in self.keys_pressed: L=s; R=s
        elif Qt.Key.Key_S in self.keys_pressed: L=-s; R=-s
        elif Qt.Key.Key_A in self.keys_pressed: L=-s; R=s
        elif Qt.Key.Key_D in self.keys_pressed: L=s; R=-s
        
        self.net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})

    def on_gui_btn_press(self, k): self.handle_key(k, True)
    def on_gui_btn_release(self, k): self.handle_key(k, False)

    def emergency_stop(self):
        self.loop_timer.stop()
        self.is_auto = False
        self.btn_mode.setChecked(False)
        self.btn_mode.setText("SWITCH TO AUTO MODE")
        self.btn_mode.setStyleSheet("")
        self.stack.setCurrentIndex(0)
        
        for _ in range(3):
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        
        self.show_loading("🚨 EMERGENCY STOP!", 1000)

    def closeEvent(self, e):
        self.video_thread.stop()
        self.net_thread.stop()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RobotApp()
    win.show()
    sys.exit(app.exec())