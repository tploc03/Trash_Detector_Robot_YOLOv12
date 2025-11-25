# ui/panels.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QSlider, QGroupBox, QFormLayout, QLineEdit, 
                            QPushButton, QListWidget, QListWidgetItem, QHBoxLayout)
from PyQt6.QtCore import Qt, QSize
from ui.widgets import VisualKey
from styles import BTN_STYLE, INPUT_STYLE

class ManualPanel(QWidget):
    """Panel điều khiển bằng tay W A S D (Đã căn giữa)"""
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app 
        
        # Layout chính của tab này
        main_layout = QVBoxLayout(self)
        
        # Tạo một container ở giữa để chứa các nút
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Grid phím
        grid = QGridLayout()
        grid.setSpacing(15) # Khoảng cách giữa các nút
        
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
    """Panel hiển thị hình ảnh rác khi chạy Auto"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.lbl_info = QLabel("⚙ AUTO MODE ACTIVE - SCANNING...")
        self.lbl_info.setStyleSheet("color: #00b894; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("background: #1e1e1e; border: 1px solid #444; border-radius: 6px;")
        self.list_detect.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_detect.setIconSize(QSize(90, 90))
        self.list_detect.setSpacing(10)
        
        layout.addWidget(self.lbl_info)
        layout.addWidget(self.list_detect)

    def add_trash_item(self, trash_name, time_str):
        item = QListWidgetItem(f"{trash_name}\n{time_str}")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.list_detect.addItem(item)
        self.list_detect.scrollToBottom()

class SettingsPanel(QWidget):
    """Panel cài đặt cấu hình (Đã bỏ Audio, làm gọn lại)"""
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 1. PARAMETERS
        grp_param = QGroupBox("SYSTEM CONFIGURATION")
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setVerticalSpacing(15) # Khoảng cách giữa các dòng
        
        # IP Address
        self.txt_ip = QLineEdit("192.168.1.15")
        
        # Speed Slider
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(0, 255); self.slider_speed.setValue(200)
        self.lbl_speed = QLabel("200")
        self.lbl_speed.setFixedWidth(40)
        self.slider_speed.valueChanged.connect(lambda v: self.lbl_speed.setText(f"{v}"))
        self.slider_speed.valueChanged.connect(self.app.update_speed_var)

        # Confidence Slider
        self.slider_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_conf.setRange(10, 100); self.slider_conf.setValue(70)
        self.lbl_conf = QLabel("70%")
        self.lbl_conf.setFixedWidth(40)
        self.slider_conf.valueChanged.connect(lambda v: self.lbl_conf.setText(f"{v}%"))


        row_conf = QHBoxLayout(); row_conf.addWidget(self.slider_conf); row_conf.addWidget(self.lbl_conf)
        row_speed = QHBoxLayout(); row_speed.addWidget(self.slider_speed); row_speed.addWidget(self.lbl_speed)

        # Add rows
        lbl_ip = QLabel("Robot IP Address:"); lbl_ip.setStyleSheet("color: #b2bec3;")
        lbl_sp = QLabel("Motor Speed:"); lbl_sp.setStyleSheet("color: #b2bec3;")
        lbl_ai = QLabel("AI Confidence:"); lbl_ai.setStyleSheet("color: #b2bec3;")

        form.addRow(lbl_ip, self.txt_ip)
        form.addRow(lbl_sp, row_speed)
        form.addRow(lbl_ai, row_conf)
        
        grp_param.setLayout(form)
        layout.addWidget(grp_param)

        # 2. SAVE BUTTON
        btn_save = QPushButton("APPLY SETTINGS")
        btn_save.setStyleSheet(BTN_STYLE)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.apply_settings)
        layout.addWidget(btn_save)
        
        self.lbl_msg = QLabel("")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setStyleSheet("font-size: 12px; margin-top: 5px;")
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
        
        self.lbl_msg.setText(f"Setting Saved\nIP: {new_ip}\nSpeed: {self.slider_speed.value()}\nConfidence: {conf*100:.0f}%")
        self.lbl_msg.setStyleSheet("color: #00b894;")