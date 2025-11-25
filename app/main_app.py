import sys
import json
import socket
import numpy as np
import cv2
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSlider, QGridLayout,
                            QGroupBox, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor

# --- CẤU HÌNH ---
DEFAULT_ROBOT_IP = "192.168.1.15"  # <--- Thay IP ESP32 của bạn vào đây
ROBOT_PORT = 8888
LOCAL_PORT = 9999

# --- CSS STYLESHEET (Làm đẹp giao diện) ---
STYLESHEET = """
QMainWindow { background-color: #1e1e1e; color: #ffffff; }
QGroupBox { 
    border: 2px solid #333; 
    border-radius: 5px; 
    margin-top: 10px; 
    font-weight: bold; 
    color: #00ff00; 
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QLabel { color: #dddddd; font-family: 'Segoe UI', sans-serif; }
QPushButton {
    background-color: #333333; color: white; border: 1px solid #555;
    border-radius: 8px; padding: 10px; font-weight: bold; font-size: 14px;
}
QPushButton:hover { background-color: #444444; border-color: #00ff00; }
QPushButton:pressed { background-color: #00ff00; color: black; }
QPushButton#btn_stop { background-color: #c0392b; border: none; }
QPushButton#btn_stop:pressed { background-color: #e74c3c; }
QPushButton#btn_active { background-color: #00ff00; color: black; border: 2px solid white; }
QSlider::groove:horizontal { height: 8px; background: #333; border-radius: 4px; }
QSlider::handle:horizontal { background: #00ff00; width: 20px; margin: -6px 0; border-radius: 10px; }
QLineEdit { background-color: #2d2d2d; color: white; border: 1px solid #444; padding: 5px; border-radius: 4px; }
"""

# --- Network Thread for UDP Communication ---
class NetworkThread(QThread):
    data_received = pyqtSignal(dict) 

    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", LOCAL_PORT))
        self.sock.settimeout(0.05)
        self.target_ip = DEFAULT_ROBOT_IP
        self.running = True

    def run(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = json.loads(data.decode())
                self.data_received.emit(msg)
            except:
                pass
    
    def send_command(self, cmd_dict):
        try:
            msg = json.dumps(cmd_dict).encode()
            self.sock.sendto(msg, (self.target_ip, ROBOT_PORT))
        except Exception as e:
            print(f"Send Error: {e}")

    def stop(self):
        self.running = False
        self.sock.close()

# MAIN INTERFACE
class ModernRobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRASH COLLECTOR BOT - COMMAND CENTER")
        self.resize(1280, 720)
        self.setStyleSheet(STYLESHEET)

        # Network
        self.net_thread = NetworkThread()
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.start()

        # Layout Main
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        #CAMERA STREAM
        left_panel = QVBoxLayout()
        
        # Header Info
        header_layout = QHBoxLayout()
        self.lbl_status = QLabel("● SYSTEM READY")
        self.lbl_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        self.lbl_fps = QLabel("AI: 0 FPS")
        header_layout.addWidget(self.lbl_status)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_fps)
        left_panel.addLayout(header_layout)

        # Camera View
        self.lbl_camera = QLabel()
        self.lbl_camera.setStyleSheet("background-color: #000; border: 2px solid #444; border-radius: 10px;")
        self.lbl_camera.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_camera.setText("NO SIGNAL\nWaiting for Stream...")
        self.lbl_camera.setMinimumSize(800, 600)
        left_panel.addWidget(self.lbl_camera, stretch=1)
        
        main_layout.addLayout(left_panel, stretch=7)

        #RIGHT PANEL
        right_panel = QVBoxLayout()

        # 1. GROUP: CONNECTION
        grp_conn = QGroupBox("CONNECTION")
        conn_layout = QVBoxLayout()
        self.txt_ip = QLineEdit(DEFAULT_ROBOT_IP)
        self.txt_ip.setPlaceholderText("Enter Robot IP")
        btn_connect = QPushButton("CONNECT / UPDATE IP")
        btn_connect.clicked.connect(self.update_ip)
        conn_layout.addWidget(self.txt_ip)
        conn_layout.addWidget(btn_connect)
        grp_conn.setLayout(conn_layout)
        right_panel.addWidget(grp_conn)

        # 2. GROUP: SENSORS (RADAR)
        grp_sensor = QGroupBox("SONAR RADAR")
        sensor_layout = QGridLayout()
        
        # Tạo 3 ô hiển thị cảm biến đẹp
        self.box_L = self.create_sensor_box("LEFT")
        self.box_F = self.create_sensor_box("FRONT")
        self.box_R = self.create_sensor_box("RIGHT")

        sensor_layout.addWidget(self.box_L, 1, 0)
        sensor_layout.addWidget(self.box_F, 0, 1)
        sensor_layout.addWidget(self.box_R, 1, 2)
        grp_sensor.setLayout(sensor_layout)
        right_panel.addWidget(grp_sensor)

        # 3. GROUP: MANUAL DRIVE (Visual Keys)
        grp_drive = QGroupBox("MANUAL DRIVE")
        drive_layout = QGridLayout()
        
        # Các nút điều khiển ảo
        self.btn_w = QPushButton("W")
        self.btn_a = QPushButton("A")
        self.btn_s = QPushButton("S")
        self.btn_d = QPushButton("D")
        
        # Gán ID để xử lý style
        for btn in [self.btn_w, self.btn_a, self.btn_s, self.btn_d]:
            btn.setFixedSize(60, 60)
            btn.setStyleSheet("font-size: 20px; font-weight: bold;")

        drive_layout.addWidget(self.btn_w, 0, 1)
        drive_layout.addWidget(self.btn_a, 1, 0)
        drive_layout.addWidget(self.btn_s, 1, 1)
        drive_layout.addWidget(self.btn_d, 1, 2)
        
        # Slider Speed
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(0, 255); self.slider_speed.setValue(200)
        self.lbl_speed = QLabel("Speed: 200")
        self.slider_speed.valueChanged.connect(lambda v: self.lbl_speed.setText(f"Speed: {v}"))

        drive_layout.addWidget(self.lbl_speed, 2, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        drive_layout.addWidget(self.slider_speed, 3, 0, 1, 3)

        grp_drive.setLayout(drive_layout)
        right_panel.addWidget(grp_drive)

        # 4. GROUP: MODE
        grp_mode = QGroupBox("OPERATION")
        mode_layout = QVBoxLayout()
        self.btn_auto = QPushButton("START AUTO MODE")
        self.btn_auto.setCheckable(True)
        self.btn_auto.toggled.connect(self.toggle_auto)
        
        self.btn_stop = QPushButton("EMERGENCY STOP (SPACE)")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.clicked.connect(self.emergency_stop)
        
        mode_layout.addWidget(self.btn_auto)
        mode_layout.addWidget(self.btn_stop)
        grp_mode.setLayout(mode_layout)
        right_panel.addWidget(grp_mode)

        right_panel.addStretch()
        main_layout.addLayout(right_panel, stretch=3)

        # Timer Mock Video
        self.timer_video = QTimer()
        self.timer_video.timeout.connect(self.mock_video)
        self.timer_video.start(30)

        # Keyboard Tracking
        self.keys_pressed = set()
        self.is_auto_mode = False

    def create_sensor_box(self, title):
        frame = QFrame()
        frame.setStyleSheet("background-color: #222; border: 1px solid #444; border-radius: 5px;")
        layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("color: #888; font-size: 10px;")
        
        lbl_val = QLabel("--")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_val.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold;")
        lbl_val.setObjectName("val") # Để tìm lại sau này
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_val)
        return frame

    def update_ip(self):
        self.net_thread.target_ip = self.txt_ip.text()
        self.lbl_status.setText(f"● TARGET: {self.net_thread.target_ip}")

    def update_sensors(self, msg):
        # Hàm cập nhật số liệu cảm biến và đổi màu nếu gần
        def update_box(frame, val):
            lbl = frame.findChild(QLabel, "val")
            lbl.setText(str(val))
            if val < 20: 
                lbl.setStyleSheet("color: #ff0000; font-size: 24px; font-weight: bold;") # Đỏ
            elif val < 50:
                lbl.setStyleSheet("color: #f1c40f; font-size: 24px; font-weight: bold;") # Vàng
            else:
                lbl.setStyleSheet("color: #00ff00; font-size: 24px; font-weight: bold;") # Xanh
        
        if "F" in msg: update_box(self.box_F, msg['F'])
        if "L" in msg: update_box(self.box_L, msg['L'])
        if "R" in msg: update_box(self.box_R, msg['R'])

    def toggle_auto(self, checked):
        self.is_auto_mode = checked
        if checked:
            self.btn_auto.setText("BACK TO MANUAL MODE")
            self.btn_auto.setStyleSheet("background-color: #00ff00; color: black;")
            # Gửi lệnh Auto xuống robot (nếu cần) hoặc xử lý logic tại đây
        else:
            self.btn_auto.setText("START AUTO MODE")
            self.btn_auto.setStyleSheet("")
            self.emergency_stop()

    def emergency_stop(self):
        self.net_thread.send_command({"cmd": "MOVE", "L": 0, "R": 0})
        self.keys_pressed.clear()
        self.update_visual_keys()

    # --- XỬ LÝ PHÍM & VISUAL FEEDBACK ---
    def keyPressEvent(self, event):
        if event.isAutoRepeat(): return
        key = event.key()
        self.keys_pressed.add(key)
        self.process_drive()
        self.update_visual_keys()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat(): return
        key = event.key()
        if key in self.keys_pressed: self.keys_pressed.remove(key)
        
        if key == Qt.Key.Key_Space:
            self.emergency_stop()
        else:
            self.process_drive()
        
        self.update_visual_keys()

    def update_visual_keys(self):
        style_normal = "font-size: 20px; font-weight: bold;"
        style_active = "font-size: 20px; font-weight: bold; background-color: #00ff00; color: black; border: 2px solid white;"
        
        self.btn_w.setStyleSheet(style_active if Qt.Key.Key_W in self.keys_pressed else style_normal)
        self.btn_s.setStyleSheet(style_active if Qt.Key.Key_S in self.keys_pressed else style_normal)
        self.btn_a.setStyleSheet(style_active if Qt.Key.Key_A in self.keys_pressed else style_normal)
        self.btn_d.setStyleSheet(style_active if Qt.Key.Key_D in self.keys_pressed else style_normal)

    def process_drive(self):
        if self.is_auto_mode: return

        speed = self.slider_speed.value()
        L, R = 0, 0
        
        if Qt.Key.Key_W in self.keys_pressed: L = speed; R = speed
        elif Qt.Key.Key_S in self.keys_pressed: L = -speed; R = -speed
        elif Qt.Key.Key_A in self.keys_pressed: L = -speed; R = speed # Quay trái
        elif Qt.Key.Key_D in self.keys_pressed: L = speed; R = -speed # Quay phải
        
        # Gửi lệnh
        self.net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})

    def mock_video(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Vẽ lưới
        cv2.line(img, (320, 0), (320, 480), (50, 50, 50), 1)
        cv2.line(img, (0, 240), (640, 240), (50, 50, 50), 1)
        cv2.putText(img, "WAITING FOR VIDEO STREAM...", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        h, w, ch = img.shape
        qt_img = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.lbl_camera.setPixmap(QPixmap.fromImage(qt_img).scaled(self.lbl_camera.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.net_thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernRobotApp()
    window.show()
    sys.exit(app.exec())