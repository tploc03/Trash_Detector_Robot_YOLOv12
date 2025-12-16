# ui/panels.py - FLEXIBLE LAYOUT VERSION
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                            QSlider, QGroupBox, QLineEdit, QPushButton, 
                            QListWidget, QListWidgetItem, QHBoxLayout, 
                            QTabWidget, QFormLayout, QCheckBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.widgets import VisualKey
from styles import BTN_STYLE, INPUT_STYLE, PRIMARY_COLOR, TEXT_SECONDARY, BG_TERTIARY, TEXT_PRIMARY, CHECKBOX_STYLE

# --- 1. MANUAL PANEL ---
class ManualPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app 
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("KEYBOARD CONTROL")
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_info = QLabel("AUTO MODE")
        self.lbl_info.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.lbl_info.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setMaximumHeight(80)
        layout.addWidget(self.lbl_info)
        
        self.list_detect = QListWidget()
        self.list_detect.setStyleSheet("border-radius: 10px; background: #EEE; font-size: 11px; color: #000;")
        self.list_detect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(5)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #DDD; border-radius: 6px; }}
            QTabBar::tab {{ padding: 8px 15px; font-weight: bold; min-width: 80px; color: {TEXT_PRIMARY}; }}
            QTabBar::tab:selected {{ background: {PRIMARY_COLOR}; color: white; }}
        """)

        self.tabs.addTab(self.create_connection_tab(), "CONNECT")
        self.tabs.addTab(self.create_manual_tab(), "MANUAL")
        self.tabs.addTab(self.create_auto_tab(), "AUTO")

        layout.addWidget(self.tabs)

    def create_connection_tab(self):
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        robot_label = QLabel("Robot IP Address")
        robot_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        robot_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        layout.addWidget(robot_label)
        
        self.txt_robot_ip = QLineEdit("10.230.248.1") 
        self.txt_robot_ip.setStyleSheet(INPUT_STYLE)
        self.txt_robot_ip.setMinimumHeight(40)
        self.txt_robot_ip.setMaximumHeight(50)
        layout.addWidget(self.txt_robot_ip)
        
        btn_robot = QPushButton("APPLY ROBOT IP")
        btn_robot.setStyleSheet(BTN_STYLE)
        btn_robot.setMinimumHeight(40)
        btn_robot.setMaximumHeight(50)
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
        self.txt_cam_ip.setMaximumHeight(50)
        layout.addWidget(self.txt_cam_ip)
        
        btn_layout = QHBoxLayout()
        
        btn_cam = QPushButton("APPLY CAM IP")
        btn_cam.setStyleSheet(BTN_STYLE)
        btn_cam.setMinimumHeight(40)
        btn_cam.setMaximumHeight(50)
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
        self.btn_flash.setMaximumHeight(50)
        self.btn_flash.clicked.connect(lambda: self.app.toggle_flash(self.txt_cam_ip.text()))
        
        btn_layout.addWidget(btn_cam, 70)
        btn_layout.addWidget(self.btn_flash, 30)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_manual_tab(self):
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(70)
        lbl_speed_title.setFont(QFont("Segoe UI", 10))
        self.slider_man_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_man_speed.setRange(0, 255)
        self.slider_man_speed.setValue(80)
        lbl_speed = QLabel("80")
        lbl_speed.setMinimumWidth(40)
        lbl_speed.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_speed.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.slider_man_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title)
        l1.addWidget(self.slider_man_speed)
        l1.addWidget(lbl_speed)
        
        l2 = QHBoxLayout()
        lbl_motor_title = QLabel("Balance:")
        lbl_motor_title.setMinimumWidth(70)
        lbl_motor_title.setFont(QFont("Segoe UI", 10))
        self.slider_man_motor = QSlider(Qt.Orientation.Horizontal)
        self.slider_man_motor.setRange(80, 120)  # 0.8 - 1.2
        self.slider_man_motor.setValue(100)  # 1.0 (neutral)
        lbl_motor = QLabel("1.0")
        lbl_motor.setMinimumWidth(40)
        lbl_motor.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_motor.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.slider_man_motor.valueChanged.connect(lambda v: lbl_motor.setText(f"{v/100:.2f}"))
        l2.addWidget(lbl_motor_title)
        l2.addWidget(self.slider_man_motor)
        l2.addWidget(lbl_motor)
        
        btn = QPushButton("APPLY MANUAL SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.setMaximumHeight(50)
        btn.clicked.connect(self.apply_manual)

        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def create_auto_tab(self):
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- NHÓM 1: CƠ BẢN ---
        l1 = QHBoxLayout()
        lbl_speed_title = QLabel("Speed:")
        lbl_speed_title.setMinimumWidth(70)
        self.slider_auto_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_speed.setRange(0, 255)
        self.slider_auto_speed.setValue(65)
        lbl_speed = QLabel("65")
        lbl_speed.setMinimumWidth(35)
        lbl_speed.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_auto_speed.valueChanged.connect(lambda v: lbl_speed.setText(str(v)))
        l1.addWidget(lbl_speed_title); l1.addWidget(self.slider_auto_speed); l1.addWidget(lbl_speed)
        
        l2 = QHBoxLayout()
        lbl_conf_title = QLabel("AI Conf:")
        lbl_conf_title.setMinimumWidth(70)
        self.slider_auto_conf = QSlider(Qt.Orientation.Horizontal)
        self.slider_auto_conf.setRange(10, 80)
        self.slider_auto_conf.setValue(20)
        lbl_conf = QLabel("20%")
        lbl_conf.setMinimumWidth(35)
        lbl_conf.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_auto_conf.valueChanged.connect(lambda v: lbl_conf.setText(f"{v}%"))
        l2.addWidget(lbl_conf_title); l2.addWidget(self.slider_auto_conf); l2.addWidget(lbl_conf)

        l_frame = QHBoxLayout()
        lbl_frame_title = QLabel("AI Frame:")
        lbl_frame_title.setMinimumWidth(70)
        self.slider_ai_frame = QSlider(Qt.Orientation.Horizontal)
        self.slider_ai_frame.setRange(1, 10)
        self.slider_ai_frame.setValue(1)
        lbl_frame = QLabel("1")
        lbl_frame.setMinimumWidth(35)
        lbl_frame.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_ai_frame.valueChanged.connect(lambda v: lbl_frame.setText(f"{v}"))
        l_frame.addWidget(lbl_frame_title); l_frame.addWidget(self.slider_ai_frame); l_frame.addWidget(lbl_frame)

        self.chk_spin = QCheckBox("Enable Scan Mode")
        self.chk_spin.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.chk_spin.setStyleSheet(CHECKBOX_STYLE)
        self.chk_spin.setChecked(False)
        
        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addLayout(l_frame)
        layout.addWidget(self.chk_spin)
        self.chk_spin.setChecked(False)
        
        # --- NHÓM 2: CHIẾN THUẬT ---
        grp_strat = QGroupBox("Step - Scan")
        grp_strat.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        grp_strat.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        strat_layout = QVBoxLayout()
        strat_layout.setSpacing(8)
        
        # Scan Duration
        l_scan = QHBoxLayout()
        lbl_scan = QLabel("Turn Time:")
        lbl_scan.setMinimumWidth(70)
        self.slider_scan_dur = QSlider(Qt.Orientation.Horizontal)
        self.slider_scan_dur.setRange(1, 50)
        self.slider_scan_dur.setValue(4)
        lbl_scan_val = QLabel("0.4s")
        lbl_scan_val.setMinimumWidth(35)
        lbl_scan_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_scan_dur.valueChanged.connect(lambda v: lbl_scan_val.setText(f"{v/10:.1f}s"))
        l_scan.addWidget(lbl_scan); l_scan.addWidget(self.slider_scan_dur); l_scan.addWidget(lbl_scan_val)
        
        # Wait Duration
        l_wait = QHBoxLayout()
        lbl_wait = QLabel("Wait/Scan:")
        lbl_wait.setMinimumWidth(70)
        self.slider_wait_dur = QSlider(Qt.Orientation.Horizontal)
        self.slider_wait_dur.setRange(1, 50)
        self.slider_wait_dur.setValue(10)
        lbl_wait_val = QLabel("1.0s")
        lbl_wait_val.setMinimumWidth(35)
        lbl_wait_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_wait_dur.valueChanged.connect(lambda v: lbl_wait_val.setText(f"{v/10:.1f}s"))
        l_wait.addWidget(lbl_wait); l_wait.addWidget(self.slider_wait_dur); l_wait.addWidget(lbl_wait_val)
        
        # Confirm Time
        l_conf = QHBoxLayout()
        lbl_conf_time = QLabel("Verify Time:")
        lbl_conf_time.setMinimumWidth(70)
        self.slider_confirm = QSlider(Qt.Orientation.Horizontal)
        self.slider_confirm.setRange(1, 50)
        self.slider_confirm.setValue(10)
        lbl_conf_val = QLabel("1.0s")
        lbl_conf_val.setMinimumWidth(35)
        lbl_conf_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_confirm.valueChanged.connect(lambda v: lbl_conf_val.setText(f"{v/10:.1f}s"))
        l_conf.addWidget(lbl_conf_time); l_conf.addWidget(self.slider_confirm); l_conf.addWidget(lbl_conf_val)

        strat_layout.addLayout(l_scan)
        strat_layout.addLayout(l_wait)
        strat_layout.addLayout(l_conf)
        grp_strat.setLayout(strat_layout)
        
        # --- NHÓM 3: CHUYỂN ĐỘNG ---
        grp_move = QGroupBox("Movement - Sensor")
        grp_move.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        grp_move.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        move_layout = QVBoxLayout()
        move_layout.setSpacing(8)
        
        # Scan Speed
        l_scan_speed = QHBoxLayout()
        lbl_ss = QLabel("Scan Speed:")
        lbl_ss.setMinimumWidth(70)
        self.slider_scan_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_scan_speed.setRange(10, 100)
        self.slider_scan_speed.setValue(90)
        lbl_scan_speed = QLabel("90%")
        lbl_scan_speed.setMinimumWidth(35)
        lbl_scan_speed.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_scan_speed.valueChanged.connect(lambda v: lbl_scan_speed.setText(f"{v}%"))
        l_scan_speed.addWidget(lbl_ss); l_scan_speed.addWidget(self.slider_scan_speed); l_scan_speed.addWidget(lbl_scan_speed)
        
        # Search Delay
        l_search_delay = QHBoxLayout()
        lbl_sd = QLabel("Search Delay:")
        lbl_sd.setMinimumWidth(70)
        self.slider_search_delay = QSlider(Qt.Orientation.Horizontal)
        self.slider_search_delay.setRange(0, 500)
        self.slider_search_delay.setValue(100)
        lbl_search_delay = QLabel("10s")
        lbl_search_delay.setMinimumWidth(35)
        lbl_search_delay.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_search_delay.valueChanged.connect(lambda v: lbl_search_delay.setText(f"{v/10:.1f}s"))
        l_search_delay.addWidget(lbl_sd); l_search_delay.addWidget(self.slider_search_delay); l_search_delay.addWidget(lbl_search_delay)
        
        # Align Tolerance
        l_align = QHBoxLayout()
        lbl_at = QLabel("Align Tolerance:")
        lbl_at.setMinimumWidth(70)
        self.slider_align = QSlider(Qt.Orientation.Horizontal)
        self.slider_align.setRange(10, 100)
        self.slider_align.setValue(40)
        lbl_align = QLabel("40px")
        lbl_align.setMinimumWidth(35)
        lbl_align.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_align.valueChanged.connect(lambda v: lbl_align.setText(f"{v}px"))
        l_align.addWidget(lbl_at); l_align.addWidget(self.slider_align); l_align.addWidget(lbl_align)
        
        l_align_speed = QHBoxLayout()
        l_align_speed.addWidget(QLabel("Align Speed:"))
        self.slider_align_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_align_speed.setRange(10, 100)
        self.slider_align_speed.setValue(40)
        lbl_align_speed = QLabel("40")
        lbl_align_speed.setMinimumWidth(35)
        lbl_align_speed.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_align_speed.valueChanged.connect(lambda v: lbl_align_speed.setText(f"{v}"))
        l_align_speed.addWidget(self.slider_align_speed)
        l_align_speed.addWidget(lbl_align_speed)
        move_layout.addLayout(l_align_speed)

        # Align Sensitivity
        l_turn_sens = QHBoxLayout()
        lbl_ts = QLabel("Align Sens:")
        lbl_ts.setMinimumWidth(70)
        self.slider_turn_sens = QSlider(Qt.Orientation.Horizontal)
        self.slider_turn_sens.setRange(1, 50)
        self.slider_turn_sens.setValue(2)
        lbl_turn_sens = QLabel("0.2")
        lbl_turn_sens.setMinimumWidth(35)
        lbl_turn_sens.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_turn_sens.valueChanged.connect(lambda v: lbl_turn_sens.setText(f"{v/10:.1f}"))
        l_turn_sens.addWidget(lbl_ts); l_turn_sens.addWidget(self.slider_turn_sens); l_turn_sens.addWidget(lbl_turn_sens)
        
        # Stop Distance
        l_stop_dist = QHBoxLayout()
        lbl_stpdist = QLabel("Stop Distance:")
        lbl_stpdist.setMinimumWidth(70)
        self.slider_stop_dist = QSlider(Qt.Orientation.Horizontal)
        self.slider_stop_dist.setRange(1, 50)
        self.slider_stop_dist.setValue(10)
        lbl_stop_dist = QLabel("10")
        lbl_stop_dist.setMinimumWidth(35)
        lbl_stop_dist.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_stop_dist.valueChanged.connect(lambda v: lbl_stop_dist.setText(f"{v}"))
        l_stop_dist.addWidget(lbl_stpdist); l_stop_dist.addWidget(self.slider_stop_dist); l_stop_dist.addWidget(lbl_stop_dist)


        l_timeout = QHBoxLayout()
        self.slider_timeout = QSlider(Qt.Orientation.Horizontal)
        self.slider_timeout.setRange(1, 30)
        self.slider_timeout.setValue(10)
        lbl_timeout = QLabel("1.0s")
        lbl_timeout.setMinimumWidth(35)
        lbl_timeout.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_timeout.valueChanged.connect(lambda v: lbl_timeout.setText(f"{v/10:.1f}s"))
        l_timeout.addWidget(QLabel("Lost Timeout:"))
        l_timeout.addWidget(self.slider_timeout)
        l_timeout.addWidget(lbl_timeout)
        move_layout.addLayout(l_timeout)
        
        l_motor_balance = QHBoxLayout()
        lbl_motor = QLabel("Balance:")
        lbl_motor.setMinimumWidth(70)
        self.slider_motor_left = QSlider(Qt.Orientation.Horizontal)
        self.slider_motor_left.setRange(80, 120)  # 0.8 - 1.2
        self.slider_motor_left.setValue(100)  # 1.0 (neutral)
        lbl_motor_val = QLabel("1.0")
        lbl_motor_val.setMinimumWidth(35)
        lbl_motor_val.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.slider_motor_left.valueChanged.connect(lambda v: lbl_motor_val.setText(f"{v/100:.2f}"))
        l_motor_balance.addWidget(lbl_motor); l_motor_balance.addWidget(self.slider_motor_left); l_motor_balance.addWidget(lbl_motor_val)
        move_layout.addLayout(l_motor_balance)

        move_layout.addLayout(l_scan_speed)
        move_layout.addLayout(l_search_delay)
        move_layout.addLayout(l_align)
        move_layout.addLayout(l_turn_sens)
        move_layout.addLayout(l_stop_dist)
        grp_move.setLayout(move_layout)

        btn = QPushButton("APPLY ALL SETTINGS")
        btn.setStyleSheet(BTN_STYLE)
        btn.setMinimumHeight(40)
        btn.setMaximumHeight(50)
        btn.clicked.connect(self.apply_auto)

        layout.addLayout(l1)
        layout.addLayout(l2)
        layout.addLayout(l_frame)
        layout.addWidget(self.chk_spin)
        layout.addWidget(grp_strat)
        layout.addWidget(grp_move)
        layout.addStretch()
        layout.addWidget(btn)
        widget.setLayout(layout)
        return widget

    def apply_manual(self):
        s = self.slider_man_speed.value()
        motor_balance = self.slider_man_motor.value() / 100.0
        self.app.apply_manual_config(s, motor_balance)

    def apply_auto(self):
        speed = self.slider_auto_speed.value()
        conf = self.slider_auto_conf.value() / 100.0
        spin_enabled = self.chk_spin.isChecked()
        
        scan_dur = self.slider_scan_dur.value() / 10.0
        wait_dur = self.slider_wait_dur.value() / 10.0
        verify_time = self.slider_confirm.value() / 10.0
        
        scan_speed = self.slider_scan_speed.value()
        search_delay = self.slider_search_delay.value() / 10.0
        align_tol = self.slider_align.value()
        turn_sens = self.slider_turn_sens.value() / 10.0
        stop_dist = self.slider_stop_dist.value()
        align_speed = self.slider_align_speed.value()
        timeout = self.slider_timeout.value() / 10.0
        motor_left_boost = self.slider_motor_left.value() / 100.0  # ✅ NEW: Motor balance
        ai_frame_interval = self.slider_ai_frame.value()  # ✅ NEW: AI Frame Interval
        
        self.app.apply_auto_config(speed, conf, spin_enabled, scan_dur, wait_dur, verify_time, 
                                   scan_speed, search_delay, align_tol, turn_sens, stop_dist,
                                   align_speed, timeout, motor_left_boost, ai_frame_interval)