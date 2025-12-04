# ui/panels.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QSlider, QGroupBox, QLineEdit, QPushButton, 
                            QListWidget, QListWidgetItem, QHBoxLayout, 
                            QTabWidget, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.widgets import VisualKey
from styles import BTN_STYLE, INPUT_STYLE, PRIMARY_COLOR, TEXT_SECONDARY

# --- 1. MANUAL PANEL (Giữ nguyên) ---
class ManualPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app 
        main_layout = QVBoxLayout(self)
        
        title = QLabel("🎮 KEYBOARD CONTROL")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        container = QWidget()
        layout = QGridLayout()
        layout.setSpacing(10)
        
        self.btn_w = VisualKey("W", Qt.Key.Key_W)
        self.btn_a = VisualKey("A", Qt.Key.Key_A)
        self.btn_s = VisualKey("S", Qt.Key.Key_S)
        self.btn_d = VisualKey("D", Qt.Key.Key_D)

        for btn in [self.btn_w, self.btn_a, self.btn_s, self.btn_d]:
            btn.pressed.connect(lambda k=btn.key_code: self.app.on_gui_btn_press(k))
            btn.released.connect(lambda k=btn.key_code: self.app.on_gui_btn_release(k))

        layout.addWidget(self.btn_w, 0, 1)
        layout.addWidget(self.btn_a, 1, 0)
        layout.addWidget(self.btn_s, 1, 1)
        layout.addWidget(self.btn_d, 1, 2)
        
        container.setLayout(layout)
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

# --- 2. AUTO PANEL (Giữ nguyên) ---
class AutoPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.lbl_info = QLabel("AUTO MODE - LINE PATROL")
        self.lbl_info.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_info.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info)
        
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("border-radius: 10px; background: #EEE; font-size: 11px;")
        layout.addWidget(self.list_detect)

    def add_trash_item(self, trash_name, time_str):
        item = QListWidgetItem(f"{trash_name}\n{time_str}")
        self.list_detect.addItem(item)
        self.list_detect.scrollToBottom()

# --- 3. SETTINGS PANEL (Cấu trúc Tab mới) ---
class SettingsPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)

        # Tạo Tab Widget chính
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #DDD; border-radius: 6px; }
            QTabBar::tab { 
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
            }
        """)

        # Add 3 tabs con
        self.tabs.addTab(self.create_connection_tab(), "CONNECT")
        self.tabs.addTab(self.create_manual_tab(), "MANUAL")
        self.tabs.addTab(self.create_auto_tab(), "AUTO")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Robot IP Section
        robot_label = QLabel("Robot IP Address")
        robot_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        robot_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        layout.addWidget(robot_label)
        
        self.txt_robot_ip = QLineEdit("192.168.1.19")
        self.txt_robot_ip.setStyleSheet(INPUT_STYLE)
        self.txt_robot_ip.setMinimumHeight(40)
        layout.addWidget(self.txt_robot_ip)
        
        btn_robot = QPushButton("APPLY ROBOT IP")
        btn_robot.setStyleSheet(BTN_STYLE)
        btn_robot.setMinimumHeight(40)
        btn_robot.clicked.connect(lambda: self.app.update_robot_ip(self.txt_robot_ip.text()))
        layout.addWidget(btn_robot)
        
        layout.addSpacing(10)
        
        # Camera URL Section
        cam_label = QLabel("Camera URL")
        cam_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cam_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        layout.addWidget(cam_label)
        
        self.txt_cam_ip = QLineEdit("http://192.168.1.19:81/stream")
        self.txt_cam_ip.setStyleSheet(INPUT_STYLE)
        self.txt_cam_ip.setMinimumHeight(40)
        layout.addWidget(self.txt_cam_ip)
        
        btn_cam = QPushButton("APPLY CAM IP")
        btn_cam.setStyleSheet(BTN_STYLE)
        btn_cam.setMinimumHeight(40)
        btn_cam.clicked.connect(lambda: self.app.update_cam_ip(self.txt_cam_ip.text()))
        layout.addWidget(btn_cam)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_manual_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Speed
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(80)
        self.slider_man_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_man_speed.setRange(0, 255)
        self.slider_man_speed.setValue(200)
        lbl_speed = QLabel("200")
        lbl_speed.setMinimumWidth(40)
        lbl_speed.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_man_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title)
        l1.addWidget(self.slider_man_speed)
        l1.addWidget(lbl_speed)
        
        # Conf
        l2 = QHBoxLayout()
        lbl_conf_title = QLabel("AI Conf:")
        lbl_conf_title.setMinimumWidth(80)
        self.slider_man_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_man_conf.setRange(10, 100)
        self.slider_man_conf.setValue(70)
        lbl_conf = QLabel("70%")
        lbl_conf.setMinimumWidth(40)
        lbl_conf.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_man_conf.valueChanged.connect(lambda v: lbl_conf.setText(f"{v}%"))
        l2.addWidget(lbl_conf_title)
        l2.addWidget(self.slider_man_conf)
        l2.addWidget(lbl_conf)

        btn = QPushButton("APPLY MANUAL SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.apply_manual)

        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def create_auto_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Speed
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(80)
        self.slider_auto_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_speed.setRange(0, 255)
        self.slider_auto_speed.setValue(180)
        lbl_speed = QLabel("180")
        lbl_speed.setMinimumWidth(40)
        lbl_speed.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_auto_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title)
        l1.addWidget(self.slider_auto_speed)
        l1.addWidget(lbl_speed)
        
        # Conf
        l2 = QHBoxLayout()
        lbl_conf_title = QLabel("AI Conf:")
        lbl_conf_title.setMinimumWidth(80)
        self.slider_auto_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_conf.setRange(10, 100)
        self.slider_auto_conf.setValue(65)
        lbl_conf = QLabel("65%")
        lbl_conf.setMinimumWidth(40)
        lbl_conf.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_auto_conf.valueChanged.connect(lambda v: lbl_conf.setText(f"{v}%"))
        l2.addWidget(lbl_conf_title)
        l2.addWidget(self.slider_auto_conf)
        l2.addWidget(lbl_conf)

        # Time
        l3 = QHBoxLayout()
        lbl_time_title = QLabel("Forward Time:")
        lbl_time_title.setMinimumWidth(80)
        self.slider_auto_time = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_time.setRange(1, 20)
        self.slider_auto_time.setValue(3)
        lbl_time = QLabel("3")
        lbl_time.setMinimumWidth(40)
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_auto_time.valueChanged.connect(lambda v: lbl_time.setText(str(v)))
        l3.addWidget(lbl_time_title)
        l3.addWidget(self.slider_auto_time)
        l3.addWidget(lbl_time)
        
        # Turn Duration (Thời gian quay)
        l4 = QHBoxLayout()
        lbl_turn_title = QLabel("Turn Duration:")
        lbl_turn_title.setMinimumWidth(80)
        self.slider_auto_turn_time = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_turn_time.setRange(3, 30)  # 0.3 - 3.0 giây (x0.1)
        self.slider_auto_turn_time.setValue(8)  # Mặc định 0.8 giây
        lbl_turn_time = QLabel("0.8")
        lbl_turn_time.setMinimumWidth(40)
        lbl_turn_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_auto_turn_time.valueChanged.connect(lambda v: lbl_turn_time.setText(f"{v/10:.1f}"))
        l4.addWidget(lbl_turn_title)
        l4.addWidget(self.slider_auto_turn_time)
        l4.addWidget(lbl_turn_time)

        btn = QPushButton("APPLY AUTO SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.apply_auto)

        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addLayout(l3)
        layout.addLayout(l4)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def apply_manual(self):
        s = self.slider_man_speed.value()
        c = self.slider_man_conf.value() / 100.0
        self.app.apply_manual_config(s, c)

    def apply_auto(self):
        s = self.slider_auto_speed.value()
        c = self.slider_auto_conf.value() / 100.0
        t = self.slider_auto_time.value()
        turn_time = self.slider_auto_turn_time.value() / 10.0  # Chuyển từ 0-255 thành 0.0-25.5
        self.app.apply_auto_config(s, c, t, turn_time)