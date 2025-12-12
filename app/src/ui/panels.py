# ui/panels.py - FIXED STYLESHEET & DEFAULTS
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QSlider, QGroupBox, QLineEdit, QPushButton, 
                            QListWidget, QListWidgetItem, QHBoxLayout, 
                            QTabWidget, QFormLayout, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.widgets import VisualKey
from styles import BTN_STYLE, INPUT_STYLE, PRIMARY_COLOR, TEXT_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, CHECKBOX_STYLE

# --- 1. MANUAL PANEL ---
class ManualPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app 
        main_layout = QVBoxLayout(self)
        
        title = QLabel("KEYBOARD CONTROL")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {PRIMARY_COLOR};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        container = QWidget()
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # Tạo các nút visual
        self.btn_w = VisualKey("W", Qt.Key.Key_W)
        self.btn_a = VisualKey("A", Qt.Key.Key_A)
        self.btn_s = VisualKey("S", Qt.Key.Key_S)
        self.btn_d = VisualKey("D", Qt.Key.Key_D)

        layout.addWidget(self.btn_w, 0, 1)
        layout.addWidget(self.btn_a, 1, 0)
        layout.addWidget(self.btn_s, 1, 1)
        layout.addWidget(self.btn_d, 1, 2)
        
        container.setLayout(layout)
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

# --- 2. AUTO PANEL ---
class AutoPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.lbl_info = QLabel("AUTO MODE")
        self.lbl_info.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_info.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setWordWrap(True)
        layout.addWidget(self.lbl_info)
        
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("border-radius: 10px; background: #EEE; font-size: 11px; color: #000;")
        layout.addWidget(self.list_detect)

    def add_trash_item(self, trash_name, time_str):
        item = QListWidgetItem(f"{trash_name}\n{time_str}")
        self.list_detect.addItem(item)
        self.list_detect.scrollToBottom()

# --- 3. SETTINGS PANEL ---
class SettingsPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #DDD; border-radius: 6px; }}
            QTabBar::tab {{ padding: 8px 15px; font-weight: bold; min-width: 100px; color: {TEXT_PRIMARY}; }}
            QTabBar::tab:selected {{ background: {PRIMARY_COLOR}; color: white; }}
        """)

        self.tabs.addTab(self.create_connection_tab(), "CONNECT")
        self.tabs.addTab(self.create_manual_tab(), "MANUAL")
        self.tabs.addTab(self.create_auto_tab(), "AUTO")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 🆕 FIX: Responsive - 20 -> 15
        layout.setContentsMargins(20, 20, 20, 20)  # 🆕 FIX: Responsive - 30 -> 20

        robot_label = QLabel("Robot IP Address")
        robot_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        robot_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        layout.addWidget(robot_label)
        
        self.txt_robot_ip = QLineEdit("10.230.248.1") 
        self.txt_robot_ip.setStyleSheet(INPUT_STYLE)
        self.txt_robot_ip.setMinimumHeight(40)
        layout.addWidget(self.txt_robot_ip)
        
        btn_robot = QPushButton("APPLY ROBOT IP")
        btn_robot.setStyleSheet(BTN_STYLE)
        btn_robot.setMinimumHeight(40)
        btn_robot.clicked.connect(lambda: self.app.update_robot_ip(self.txt_robot_ip.text()))
        layout.addWidget(btn_robot)
        
        layout.addSpacing(10)
        
        cam_label = QLabel("Camera URL")
        cam_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cam_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        layout.addWidget(cam_label)
        
        self.txt_cam_ip = QLineEdit("http://10.230.248.174:81/stream")
        self.txt_cam_ip.setStyleSheet(INPUT_STYLE)
        self.txt_cam_ip.setMinimumHeight(40)
        layout.addWidget(self.txt_cam_ip)
        
        btn_layout = QHBoxLayout()
        
        btn_cam = QPushButton("APPLY CAM IP")
        btn_cam.setStyleSheet(BTN_STYLE)
        btn_cam.setMinimumHeight(40)
        btn_cam.clicked.connect(lambda: self.app.update_cam_ip(self.txt_cam_ip.text()))
        
        self.btn_flash = QPushButton("FLASH")
        self.btn_flash.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_TERTIARY}; 
                color: {TEXT_PRIMARY}; 
                border: 2px solid {PRIMARY_COLOR};
                border-radius: 8px; 
                padding: 10px; 
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #DDD; }}
        """)
        self.btn_flash.setMinimumHeight(40)
        self.btn_flash.clicked.connect(lambda: self.app.toggle_flash(self.txt_cam_ip.text()))
        
        btn_layout.addWidget(btn_cam, 70)
        btn_layout.addWidget(self.btn_flash, 30)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_manual_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 🆕 FIX: Responsive - 20 -> 15
        layout.setContentsMargins(20, 20, 20, 20)  # 🆕 FIX: Responsive - 30 -> 20
        
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(50)  # 🆕 FIX: Responsive - 80 -> 50
        self.slider_man_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_man_speed.setRange(0, 255)
        self.slider_man_speed.setValue(80)
        lbl_speed = QLabel("80")
        lbl_speed.setMinimumWidth(30)  # 🆕 FIX: Responsive - 40 -> 30
        lbl_speed.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slider_man_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title)
        l1.addWidget(self.slider_man_speed)
        l1.addWidget(lbl_speed)
        
        btn = QPushButton("APPLY MANUAL SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.apply_manual)

        layout.addLayout(l1)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def create_auto_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)  # 🆕 FIX: Responsive - 15 -> 12
        layout.setContentsMargins(15, 15, 15, 15)  # 🆕 FIX: Responsive - 20 -> 15
        
        # --- NHÓM 1: CƠ BẢN ---
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(50)  # 🆕 FIX: Responsive - 80 -> 50
        self.slider_auto_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_speed.setRange(0, 255)
        self.slider_auto_speed.setValue(65)
        lbl_speed = QLabel("65")
        lbl_speed.setMinimumWidth(30)  # 🆕 FIX: Responsive - 40 -> 30
        self.slider_auto_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title); l1.addWidget(self.slider_auto_speed); l1.addWidget(lbl_speed)
        
        l2 = QHBoxLayout()
        lbl_conf_title = QLabel("AI Conf:")
        lbl_conf_title.setMinimumWidth(50)  # 🆕 FIX: Responsive - 80 -> 50
        self.slider_auto_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_conf.setRange(10, 80)
        self.slider_auto_conf.setValue(20)
        lbl_conf = QLabel("20%")
        lbl_conf.setMinimumWidth(30)  # 🆕 FIX: Responsive - 40 -> 30
        self.slider_auto_conf.valueChanged.connect(lambda v: lbl_conf.setText(f"{v}%"))
        l2.addWidget(lbl_conf_title); l2.addWidget(self.slider_auto_conf); l2.addWidget(lbl_conf)

        self.chk_spin = QCheckBox("Enable Scan Mode")
        self.chk_spin.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.chk_spin.setStyleSheet(CHECKBOX_STYLE)
        self.chk_spin.setChecked(False)
        # self.chk_spin.setStyleSheet(f"color: {PRIMARY_COLOR};")
        
        # --- NHÓM 2: CHIẾN THUẬT (MỚI) ---
        grp_strat = QGroupBox("Step & Scan Tuning")
        grp_strat.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        strat_layout = QVBoxLayout()
        
        # Thời gian xoay (Scan Duration)
        l_scan = QHBoxLayout()
        self.slider_scan_dur = QSlider(Qt.Orientation.Horizontal)
        self.slider_scan_dur.setRange(1, 50) # 0.1s -> 5.0s
        self.slider_scan_dur.setValue(4)     # Default 0.4s
        lbl_scan_val = QLabel("0.4s")
        self.slider_scan_dur.valueChanged.connect(lambda v: lbl_scan_val.setText(f"{v/10:.1f}s"))
        l_scan.addWidget(QLabel("Step Turn Time:")); l_scan.addWidget(self.slider_scan_dur); l_scan.addWidget(lbl_scan_val)
        
        # Thời gian chờ (Wait Duration)
        l_wait = QHBoxLayout()
        self.slider_wait_dur = QSlider(Qt.Orientation.Horizontal)
        self.slider_wait_dur.setRange(1, 50) # 0.1s -> 5.0s
        self.slider_wait_dur.setValue(10)    # Default 1.0s
        lbl_wait_val = QLabel("1.0s")
        self.slider_wait_dur.valueChanged.connect(lambda v: lbl_wait_val.setText(f"{v/10:.1f}s"))
        l_wait.addWidget(QLabel("Wait/Scan Time:")); l_wait.addWidget(self.slider_wait_dur); l_wait.addWidget(lbl_wait_val)
        
        # Thời gian xác thực (Confirm Time)
        l_conf = QHBoxLayout()
        self.slider_confirm = QSlider(Qt.Orientation.Horizontal)
        self.slider_confirm.setRange(1, 50)  # 0.1s -> 5.0s
        self.slider_confirm.setValue(20)     # Default 2.0s
        lbl_conf_val = QLabel("2.0s")
        self.slider_confirm.valueChanged.connect(lambda v: lbl_conf_val.setText(f"{v/10:.1f}s"))
        l_conf.addWidget(QLabel("Verify Time:")); l_conf.addWidget(self.slider_confirm); l_conf.addWidget(lbl_conf_val)

        strat_layout.addLayout(l_scan)
        strat_layout.addLayout(l_wait)
        strat_layout.addLayout(l_conf)
        grp_strat.setLayout(strat_layout)
        
        # --- NHÓM 3: CHUYỂN ĐỘNG & CẢM BIẾN (MỚI) ---
        grp_move = QGroupBox("Movement & Sensor Tuning")
        grp_move.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        move_layout = QVBoxLayout()
        
        # Tốc độ xoay (Scan Speed)
        l_scan_speed = QHBoxLayout()
        self.slider_scan_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_scan_speed.setRange(10, 100)
        self.slider_scan_speed.setValue(90)
        lbl_scan_speed = QLabel("90%")
        self.slider_scan_speed.valueChanged.connect(lambda v: lbl_scan_speed.setText(f"{v}%"))
        l_scan_speed.addWidget(QLabel("Scan Speed:")); l_scan_speed.addWidget(self.slider_scan_speed); l_scan_speed.addWidget(lbl_scan_speed)
        
        # Delay trước quay (Search Delay)
        l_search_delay = QHBoxLayout()
        self.slider_search_delay = QSlider(Qt.Orientation.Horizontal)
        self.slider_search_delay.setRange(0, 30)
        self.slider_search_delay.setValue(5)  # 0.5s
        lbl_search_delay = QLabel("0.5s")
        self.slider_search_delay.valueChanged.connect(lambda v: lbl_search_delay.setText(f"{v/10:.1f}s"))
        l_search_delay.addWidget(QLabel("Search Delay:")); l_search_delay.addWidget(self.slider_search_delay); l_search_delay.addWidget(lbl_search_delay)
        
        # Ngưỡng căn chỉnh (Align Tolerance)
        l_align = QHBoxLayout()
        self.slider_align = QSlider(Qt.Orientation.Horizontal)
        self.slider_align.setRange(10, 100)
        self.slider_align.setValue(40)
        lbl_align = QLabel("40px")
        self.slider_align.valueChanged.connect(lambda v: lbl_align.setText(f"{v}px"))
        l_align.addWidget(QLabel("Align Tol:")); l_align.addWidget(self.slider_align); l_align.addWidget(lbl_align)
        
        # Độ nhạy xoay (Turn Sensitivity)
        l_turn_sens = QHBoxLayout()
        self.slider_turn_sens = QSlider(Qt.Orientation.Horizontal)
        self.slider_turn_sens.setRange(1, 50)
        self.slider_turn_sens.setValue(2)  # 0.2
        lbl_turn_sens = QLabel("0.2")
        self.slider_turn_sens.valueChanged.connect(lambda v: lbl_turn_sens.setText(f"{v/10:.1f}"))
        l_turn_sens.addWidget(QLabel("Turn Sens:")); l_turn_sens.addWidget(self.slider_turn_sens); l_turn_sens.addWidget(lbl_turn_sens)
        
        # Khoảng cách dừng (Stop Distance)
        l_stop_dist = QHBoxLayout()
        self.slider_stop_dist = QSlider(Qt.Orientation.Horizontal)
        self.slider_stop_dist.setRange(5, 50)
        self.slider_stop_dist.setValue(10)
        lbl_stop_dist = QLabel("10cm")
        self.slider_stop_dist.valueChanged.connect(lambda v: lbl_stop_dist.setText(f"{v}cm"))
        l_stop_dist.addWidget(QLabel("Stop Dist:")); l_stop_dist.addWidget(self.slider_stop_dist); l_stop_dist.addWidget(lbl_stop_dist)

        move_layout.addLayout(l_scan_speed)
        move_layout.addLayout(l_search_delay)
        move_layout.addLayout(l_align)
        move_layout.addLayout(l_turn_sens)
        move_layout.addLayout(l_stop_dist)
        grp_move.setLayout(move_layout)

        btn = QPushButton("APPLY ALL SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.apply_auto)

        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addWidget(self.chk_spin)
        layout.addWidget(grp_strat)
        layout.addWidget(grp_move)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def apply_manual(self):
        s = self.slider_man_speed.value()
        self.app.apply_manual_config(s)

    def apply_auto(self):
        # Lấy tất cả giá trị
        speed = self.slider_auto_speed.value()
        conf = self.slider_auto_conf.value() / 100.0
        spin_enabled = self.chk_spin.isChecked()
        
        # Lấy tham số chiến thuật
        scan_dur = self.slider_scan_dur.value() / 10.0
        wait_dur = self.slider_wait_dur.value() / 10.0
        verify_time = self.slider_confirm.value() / 10.0
        
        # 🆕 Lấy tham số chuyển động
        scan_speed = self.slider_scan_speed.value()
        search_delay = self.slider_search_delay.value() / 10.0
        align_tol = self.slider_align.value()
        turn_sens = self.slider_turn_sens.value() / 10.0
        stop_dist = self.slider_stop_dist.value()
        
        self.app.apply_auto_config(speed, conf, spin_enabled, scan_dur, wait_dur, verify_time, 
                                   scan_speed, search_delay, align_tol, turn_sens, stop_dist)