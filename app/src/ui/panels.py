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
        instr = QLabel("Use W, A, S, D or click buttons to move")
        instr_font = QFont("Segoe UI", 10)
        instr.setFont(instr_font)
        instr.setStyleSheet(f"color: {TEXT_SECONDARY}; margin-bottom: 15px;")
        instr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(instr)
        
        # Tạo một container ở giữa để chứa các nút
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Grid phím
        grid = QGridLayout()
        grid.setSpacing(12) # Khoảng cách giữa các nút
        
        self.btn_w = VisualKey("W", Qt.Key.Key_W)
        self.btn_a = VisualKey("A", Qt.Key.Key_A)
        self.btn_s = VisualKey("S", Qt.Key.Key_S)
        self.btn_d = VisualKey("D", Qt.Key.Key_D)

        for btn in [self.btn_w, self.btn_a, self.btn_s, self.btn_d]:
            btn.pressed.connect(lambda k=btn.key_code: self.app.on_gui_btn_press(k))
            btn.released.connect(lambda k=btn.key_code: self.app.on_gui_btn_release(k))

        # Sắp xếp vị trí (Row, Col)
        grid.addWidget(self.btn_w, 0, 1)
        grid.addWidget(self.btn_a, 1, 0)
        grid.addWidget(self.btn_s, 1, 1)
        grid.addWidget(self.btn_d, 1, 2)
        
        container_layout.addLayout(grid)
        
        # --- CĂN GIỮA ---
        main_layout.addStretch(1) # Đẩy từ trên xuống
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter) # Widget ở giữa
        main_layout.addStretch(1) # Đẩy từ dưới lên

class AutoPanel(QWidget):
    """Modern Auto Mode Panel - Real-time Detection Display"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        self.lbl_info = QLabel("AUTO MODE ACTIVE - SCANNING TRASH...")
        info_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.lbl_info.setFont(info_font)
        self.lbl_info.setStyleSheet(f"color: {PRIMARY_COLOR}; letter-spacing: 0.5px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Status bar
        status_font = QFont("Segoe UI", 10)
        self.lbl_status = QLabel("Status: Ready | Items Detected: 0")
        self.lbl_status.setFont(status_font)
        self.lbl_status.setStyleSheet(f"color: {TEXT_SECONDARY};")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.lbl_status)
        
        # Detection list
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("""
            QListWidget {
                background: #F5F5F5; 
                border: 2px solid #ECECEC; 
                border-radius: 12px;
                padding: 8px;
            }
            QListWidget::item:hover {
                background: #ECECEC;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #0078D4;
                color: #FFF;
                border-radius: 8px;
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
        layout.setSpacing(20)

        # 1. SYSTEM CONFIGURATION
        grp_param = QGroupBox("⚙ SYSTEM CONFIGURATION")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setVerticalSpacing(15) # Khoảng cách giữa các dòng
        form.setHorizontalSpacing(15)
        
        # IP Address
        self.txt_ip = QLineEdit("192.168.1.15")
        
        # Speed Slider with live value
        speed_container = QHBoxLayout()
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(0, 255)
        self.slider_speed.setValue(200)
        self.lbl_speed = QLabel("200")
        self.lbl_speed.setFixedWidth(50)
        self.lbl_speed.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_speed.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.slider_speed.valueChanged.connect(lambda v: self.lbl_speed.setText(f"{v}"))
        self.slider_speed.valueChanged.connect(self.app.update_speed_var)
        speed_container.addWidget(self.slider_speed)
        speed_container.addWidget(self.lbl_speed)

        # Confidence Slider with live value
        conf_container = QHBoxLayout()
        self.slider_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_conf.setRange(10, 100)
        self.slider_conf.setValue(70)
        self.lbl_conf = QLabel("70%")
        self.lbl_conf.setFixedWidth(50)
        self.lbl_conf.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.lbl_conf.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.slider_conf.valueChanged.connect(lambda v: self.lbl_conf.setText(f"{v}%"))
        conf_container.addWidget(self.slider_conf)
        conf_container.addWidget(self.lbl_conf)

        # Add rows with nice labels
        lbl_ip = QLabel("Robot IP Address:")
        lbl_ip.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600;")
        
        lbl_sp = QLabel("Motor Speed:")
        lbl_sp.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600;")
        
        lbl_ai = QLabel("AI Confidence:")
        lbl_ai.setStyleSheet(f"color: {TEXT_SECONDARY}; font-weight: 600;")

        form.addRow(lbl_ip, self.txt_ip)
        form.addRow(lbl_sp, speed_container)
        form.addRow(lbl_ai, conf_container)
        
        grp_param.setLayout(form)
        layout.addWidget(grp_param)

        # 2. ACTION BUTTONS
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("APPLY SETTINGS")
        btn_save.setStyleSheet(BTN_STYLE)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.apply_settings)
        btn_layout.addWidget(btn_save)
        
        btn_reset = QPushButton("↻ RESET")
        btn_reset.setStyleSheet(BTN_SECONDARY)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.clicked.connect(self.reset_settings)
        btn_layout.addWidget(btn_reset)
        
        layout.addLayout(btn_layout)
        
        # Status message
        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setFont(QFont("Segoe UI", 11))
        self.lbl_msg.setStyleSheet("margin-top: 10px; padding: 8px; border-radius: 6px;")
        layout.addWidget(self.lbl_msg)
        
        layout.addStretch()

    def apply_settings(self):
        new_ip = self.txt_ip.text()
        self.app.net_thread.target_ip = new_ip
        
        conf = self.slider_conf.value() / 100.0
        cmd = {
            "cmd": "SET_CONFIG", 
            "conf": conf,
            "speed": self.slider_speed.value()
        }
        self.app.net_thread.send_command(cmd)
        
        # Show success message
        self.lbl_msg.setText(f"✓ Settings Applied Successfully\nIP: {new_ip} | Speed: {self.slider_speed.value()} | Confidence: {conf*100:.0f}%")
        self.lbl_msg.setStyleSheet(f"color: #FFF; background: #0078D4; padding: 10px; border-radius: 6px; font-weight: 600;")

    def reset_settings(self):
        self.txt_ip.setText("192.168.1.15")
        self.slider_speed.setValue(200)
        self.slider_conf.setValue(70)
        self.lbl_msg.setText("Settings reset to defaults")
        self.lbl_msg.setStyleSheet(f"color: {TEXT_SECONDARY}; background: transparent; padding: 5px;")