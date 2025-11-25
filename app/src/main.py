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
from styles import MAIN_THEME, BTN_STOP_STYLE
from ui.widgets import SensorBox
from ui.panels import ManualPanel, AutoPanel, SettingsPanel

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRASH COLLECTOR V3 - COMMAND CENTER")
        self.resize(1200, 700)
        self.setStyleSheet(MAIN_THEME)
        self.setWindowIcon(QIcon("app/resources/icons/rover.ico"))
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
        video_container.setStyleSheet("background-color: #000; border-radius: 10px; border: 2px solid #333;")
        video_layout = QVBoxLayout(video_container)
        video_layout.setContentsMargins(0,0,0,0) # Full khung
        
        # Header Info (FPS) - Overlay style
        self.lbl_fps = QLabel("AI: 0 FPS | PING: -- ms")
        self.lbl_fps.setStyleSheet("color: #00b894; font-weight: bold; padding: 10px; background: transparent;")
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
            self.btn_mode.setText("AUTO MODE RUNNING... (CLICK TO MANUAL)")
            self.btn_mode.setStyleSheet("background-color: #00b894; color: #1e1e1e; border: none;")
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
        # Tạo ảnh giả lập với nền xám nhẹ để không bị chìm hẳn vào nền đen
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:] = (30, 30, 30) # Dark gray background
        
        # Chữ đẹp hơn
        cv2.putText(img, "WAITING FOR STREAM...", (120, 240), cv2.FONT_HERSHEY_DUPLEX, 0.9, (200, 200, 200), 1)
        cv2.rectangle(img, (200, 150), (440, 330), (0, 184, 148), 2) # Xanh ngọc
        
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