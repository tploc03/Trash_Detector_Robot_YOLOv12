# main.py
import sys
import numpy as np
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QIcon

from network import NetworkThread
from styles import MAIN_THEME, BTN_STOP_STYLE, PRIMARY_COLOR, PRIMARY_DARK, TEXT_PRIMARY
from ui.widgets import SensorBox
from ui.panels import ManualPanel, AutoPanel, SettingsPanel

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLOV12-Based Trash Detection Robot")
        self.resize(1400, 800)
        self.setStyleSheet(MAIN_THEME)
        self.setWindowIcon(QIcon("app/resources/icons/rover.ico"))
        
        # Modern window styling
        self.setWindowOpacity(1.0)
        # Network Logic
        self.net_thread = NetworkThread()
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.start()

        # Variables
        self.speed = 200
        self.keys_pressed = set()
        self.is_auto = False

        # --- GIAO DIỆN CHÍNH ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # [CỘT TRÁI] VIDEO (65%)
        # Tạo một Frame chứa video để căn giữa dễ hơn
        video_container = QFrame()
        video_container.setStyleSheet("""
            background-color: #FFFFFF; 
            border-radius: 16px; 
            border: 2px solid #0078D4;
            padding: 2px;
        """)
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0,0,0,0) # Full khung
        
        # Header Info (FPS) - Overlay style
        self.lbl_fps = QLabel("⚡ AI: 0 FPS | 📡 PING: -- ms")
        self.lbl_fps.setStyleSheet("""
            color: #0078D4; 
            font-weight: bold; 
            padding: 12px; 
            background: rgba(255, 255, 255, 0.85);
            border-radius: 8px;
            font-size: 12px;
            letter-spacing: 0.5px;
        """)
        self.lbl_fps.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Camera Display
        self.lbl_cam = QLabel()
        self.lbl_cam.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cam.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.lbl_cam.setStyleSheet("background: transparent;") # Trong suốt để đè lên nền đen
        
        video_layout.addWidget(self.lbl_fps)
        video_layout.addWidget(self.lbl_cam)
        video_layout.setStretch(1, 1) # Ưu tiên không gian cho Camera
        
        main_layout.addWidget(video_container, stretch=65)

        # [CỘT PHẢI] CONTROL PANELS (35%)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        # 1. RADAR SENSORS
        grp_sensor = QGroupBox("RADAR SENSORS")
        sens_grid = QGridLayout()
        sens_grid.setVerticalSpacing(10)
        self.box_F = SensorBox("FRONT")
        self.box_L = SensorBox("LEFT")
        self.box_R = SensorBox("RIGHT")
        sens_grid.addWidget(self.box_F, 0, 1)
        sens_grid.addWidget(self.box_L, 1, 0)
        sens_grid.addWidget(self.box_R, 1, 2)
        grp_sensor.setLayout(sens_grid)
        right_layout.addWidget(grp_sensor)

        # 2. TAB CONTROL
        self.tabs = QTabWidget()
        
        # -- Tab Operation --
        tab_op = QWidget()
        op_layout = QVBoxLayout(tab_op)
        op_layout.setContentsMargins(10, 15, 10, 10)
        
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

        # -- Tab Settings --
        self.panel_settings = SettingsPanel(self)
        self.tabs.addTab(self.panel_settings, "SETTINGS")
        
        right_layout.addWidget(self.tabs)

        # 3. EMERGENCY STOP
        self.btn_stop = QPushButton("EMERGENCY STOP (SPACE)")
        self.btn_stop.setStyleSheet(BTN_STOP_STYLE)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self.emergency_stop)
        right_layout.addWidget(self.btn_stop)

        main_layout.addLayout(right_layout, stretch=35)

        # Timer Video
        self.timer = QTimer()
        self.timer.timeout.connect(self.mock_video)
        self.timer.start(30)

    # --- LOGIC GIỮ NGUYÊN ---
    def toggle_mode(self, checked):
        self.is_auto = checked
        if checked:
            self.btn_mode.setText("⚙ AUTO MODE RUNNING (CLICK TO MANUAL)")
            self.btn_mode.setStyleSheet(f"""
                QPushButton {{
                    background-color: #06D6A0; 
                    color: #000; 
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-weight: 700;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background-color: #2EE7B8; }}
                QPushButton:pressed {{ background-color: #04A87E; }}
            """)
            self.stack.setCurrentIndex(1)
            self.net_thread.send_command({"cmd": "AUTO_START"})
        else:
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("") # Reset về default trong style
            self.stack.setCurrentIndex(0)
            self.emergency_stop()

    def emergency_stop(self):
        self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})
        self.is_auto = False
        self.btn_mode.setChecked(False)
        self.stack.setCurrentIndex(0)

    def update_speed_var(self, val):
        self.speed = val

    def update_sensors(self, msg):
        if "F" in msg: self.box_F.update_val(msg["F"])
        if "L" in msg: self.box_L.update_val(msg["L"])
        if "R" in msg: self.box_R.update_val(msg["R"])

    # --- INPUT ---
    def keyPressEvent(self, event):
        if event.isAutoRepeat(): return
        self.handle_input(event.key(), True)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat(): return
        self.handle_input(event.key(), False)
    
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

    def mock_video(self):
        # Tạo ảnh giả lập với nền gradient đẹp
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create gradient background (from dark blue to slightly lighter)
        for y in range(480):
            # Gradient effect
            intensity = int(30 + (y / 480) * 20)
            img[y, :] = [intensity, intensity + 10, intensity + 15]
        
        # Add subtle grid pattern
        for x in range(0, 640, 80):
            cv2.line(img, (x, 0), (x, 480), (50, 50, 50), 1)
        for y in range(0, 480, 60):
            cv2.line(img, (0, y), (640, y), (50, 50, 50), 1)
        
        # Chữ đẹp hơn
        cv2.putText(img, "WAITING FOR STREAM", (140, 200), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (180, 180, 180), 1)
        cv2.putText(img, "Connect your camera...", (160, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Modern rectangle border (Mint Green)
        cv2.rectangle(img, (180, 120), (460, 340), (0, 214, 160), 3)
        
        # Add corner accents
        corner_size = 30
        cv2.line(img, (180, 120), (180 + corner_size, 120), (0, 214, 160), 3)
        cv2.line(img, (180, 120), (180, 120 + corner_size), (0, 214, 160), 3)
        cv2.line(img, (460, 120), (460 - corner_size, 120), (0, 214, 160), 3)
        cv2.line(img, (460, 120), (460, 120 + corner_size), (0, 214, 160), 3)
        cv2.line(img, (180, 340), (180 + corner_size, 340), (0, 214, 160), 3)
        cv2.line(img, (180, 340), (180, 340 - corner_size), (0, 214, 160), 3)
        cv2.line(img, (460, 340), (460 - corner_size, 340), (0, 214, 160), 3)
        cv2.line(img, (460, 340), (460, 340 - corner_size), (0, 214, 160), 3)
        
        h, w, ch = img.shape
        qt_img = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        # Scale với SmoothTransformation để ảnh mượt hơn
        target_size = self.lbl_cam.size()
        scaled_pixmap = QPixmap.fromImage(qt_img).scaled(
            target_size, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_cam.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        self.net_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotApp()
    window.show()
    sys.exit(app.exec())