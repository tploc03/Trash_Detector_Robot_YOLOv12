# ui/panels.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QSlider, QGroupBox, QFormLayout, QLineEdit, 
                            QPushButton, QListWidget, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from ui.widgets import VisualKey
from styles import BTN_STYLE, INPUT_STYLE, BTN_SECONDARY, PRIMARY_COLOR, TEXT_SECONDARY

class ManualPanel(QWidget):
    """Modern Manual Control Panel - W A S D Navigation"""
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app 
        
        # Layout chính của tab này
        main_layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎮 KEYBOARD CONTROL")
        title_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {PRIMARY_COLOR}; letter-spacing: 0.5px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Instruction
        instr = QLabel("Only W, A, S, D are active")
        instr_font = QFont("Segoe UI", 10)
        instr.setFont(instr_font)
        instr.setStyleSheet(f"color: {TEXT_SECONDARY}; margin-bottom: 15px;")
        instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(instr)
        
        # Container
        container = QWidget()
        container_layout = QVBoxLayout(container)
        grid = QGridLayout()
        grid.setSpacing(12)
        
        self.btn_w = VisualKey("W", Qt.Key.Key_W)
        self.btn_a = VisualKey("A", Qt.Key.Key_A)
        self.btn_s = VisualKey("S", Qt.Key.Key_S)
        self.btn_d = VisualKey("D", Qt.Key.Key_D)

        for btn in [self.btn_w, self.btn_a, self.btn_s, self.btn_d]:
            btn.pressed.connect(lambda k=btn.key_code: self.app.on_gui_btn_press(k))
            btn.released.connect(lambda k=btn.key_code: self.app.on_gui_btn_release(k))

        grid.addWidget(self.btn_w, 0, 1)
        grid.addWidget(self.btn_a, 1, 0)
        grid.addWidget(self.btn_s, 1, 1)
        grid.addWidget(self.btn_d, 1, 2)
        
        container_layout.addLayout(grid)
        main_layout.addStretch(1)
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch(1)

class AutoPanel(QWidget):
    """Modern Auto Mode Panel - Real-time Detection Display"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        self.lbl_info = QLabel("AUTO MODE ACTIVE - SCANNING TRASH...")
        info_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.lbl_info.setFont(info_font)
        self.lbl_info.setStyleSheet(f"color: {PRIMARY_COLOR}; letter-spacing: 0.5px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_font = QFont("Segoe UI", 10)
        self.lbl_status = QLabel("Status: Ready | Items Detected: 0")
        self.lbl_status.setFont(status_font)
        self.lbl_status.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.lbl_status)
        
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("""
            QListWidget {
                background: #F5F5F5; 
                border: 2px solid #ECECEC; 
                border-radius: 12px;
                padding: 8px;
            }
        """)
        self.list_detect.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_detect.setIconSize(QSize(100, 100))
        self.list_detect.setSpacing(12)
        
        layout.addWidget(self.list_detect)

    def add_trash_item(self, trash_name, time_str):
        item = QListWidgetItem(f"{trash_name}\n{time_str}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_detect.addItem(item)
        self.list_detect.scrollToBottom()

class SettingsPanel(QWidget):
    """Modern Settings & Configuration Panel"""
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. NETWORK SETTINGS
        grp_param = QGroupBox("🌐 SYSTEM CONFIGURATION")
        form = QFormLayout()
        form.setSpacing(12)
        
        # Robot IP
        self.txt_robot_ip = QLineEdit()
        self.txt_robot_ip.setText("192.168.1.19") # Mặc định theo IP bạn hay test
        self.txt_robot_ip.setPlaceholderText("Ex: 192.168.1.19")
        self.txt_robot_ip.setStyleSheet(INPUT_STYLE)
        
        # Camera IP
        self.txt_cam_ip = QLineEdit()
        self.txt_cam_ip.setText("http://192.168.1.19:81/stream")
        self.txt_cam_ip.setPlaceholderText("Ex: http://192.168.1.19:81/stream")
        self.txt_cam_ip.setStyleSheet(INPUT_STYLE)
        
        form.addRow("🤖 Robot IP (ESP32):", self.txt_robot_ip)
        form.addRow("📷 Camera URL:", self.txt_cam_ip)
        
        # Motor Speed
        speed_container = QHBoxLayout()
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(0, 255)
        self.slider_speed.setValue(200)
        self.lbl_speed = QLabel("200")
        self.lbl_speed.setStyleSheet(f"color: {PRIMARY_COLOR}; font-weight: bold; min-width: 40px;")
        # Chỉ cập nhật số hiển thị, KHÔNG cập nhật biến hệ thống
        self.slider_speed.valueChanged.connect(lambda v: self.lbl_speed.setText(f"{v}"))
        speed_container.addWidget(self.slider_speed)
        speed_container.addWidget(self.lbl_speed)
        form.addRow("⚡ Motor Speed:", speed_container)
        
        # AI Confidence
        conf_container = QHBoxLayout()
        self.slider_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_conf.setRange(10, 100)
        self.slider_conf.setValue(70)
        self.lbl_conf = QLabel("70%")
        self.lbl_conf.setStyleSheet(f"color: {PRIMARY_COLOR}; font-weight: bold; min-width: 50px;")
        # Chỉ cập nhật số hiển thị
        self.slider_conf.valueChanged.connect(lambda v: self.lbl_conf.setText(f"{v}%"))
        conf_container.addWidget(self.slider_conf)
        conf_container.addWidget(self.lbl_conf)
        form.addRow("🧠 AI Confidence:", conf_container)
        
        grp_param.setLayout(form)
        layout.addWidget(grp_param)
        
        # 2. BUTTONS
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("APPLY ALL SETTINGS")
        btn_save.setStyleSheet(BTN_STYLE)
        btn_save.setMinimumHeight(45)
        btn_save.clicked.connect(self.apply_settings)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        # Msg
        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_msg)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def apply_settings(self):
        # Lấy dữ liệu
        robot_ip = self.txt_robot_ip.text().strip()
        cam_ip = self.txt_cam_ip.text().strip()
        conf = self.slider_conf.value() / 100.0
        speed = self.slider_speed.value()
        
        if not robot_ip or not cam_ip:
            self.lbl_msg.setText("❌ Missing IP Address!")
            self.lbl_msg.setStyleSheet("color: white; background: #DC3545; padding: 5px; border-radius: 4px;")
            return

        # Gọi hàm update của App Main -> Hàm này sẽ kích hoạt Loading Overlay
        self.app.apply_system_config(robot_ip, cam_ip, conf, speed)
        
        # Hiển thị log tạm
        self.lbl_msg.setText("✓ Settings Applied Successfully!")
        self.lbl_msg.setStyleSheet("color: white; background: #0078D4; padding: 5px; border-radius: 4px;")