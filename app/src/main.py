# main.py - FLEXIBLE UI VERSION
import sys
import os
import requests
import datetime
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton, QSizePolicy,
                            QMessageBox, QDialog, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon

from network import NetworkThread
from styles import MAIN_THEME, BTN_STOP_STYLE
from ui.widgets import SensorBox, LoadingOverlay
from ui.panels import ManualPanel, AutoPanel, SettingsPanel
from video import VideoThread
from sound_manager import SoundManager
from robot_controller import RobotController, RobotState

# --- CƠ CHẾ BẮT LỖI TOÀN CỤC (QUAN TRỌNG) ---
def exception_hook(exctype, value, tb):
    """Hiện bảng lỗi thay vì tự tắt app"""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print("CRITICAL ERROR:", error_msg)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("Application Error")
    msg.setInformativeText("An unexpected error occurred.")
    msg.setDetailedText(error_msg)
    msg.exec()

sys.excepthook = exception_hook

class DetectionCompleteDialog(QDialog):
    """Dialog thông báo hoàn thành"""
    def __init__(self, trash_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Done")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; border: 2px solid #0078D4; border-radius: 10px; }
            QLabel { color: #333; background: transparent; }
            QPushButton {
                background-color: #0078D4; color: white; border-radius: 6px;
                padding: 10px 20px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #005A9E; }
        """)
        
        layout = QVBoxLayout(self)
        
        lbl_icon = QLabel("✅")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 48px;")
        layout.addWidget(lbl_icon)
        
        lbl_title = QLabel(f"{trash_name.upper()}")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(lbl_title)
        
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        lbl_time = QLabel(f"Time: {time_str}")
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_time)
        
        btn_ok = QPushButton("Return to Manual")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

class RobotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = "app/resources/icons/rover.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setWindowTitle("Trash Detector Robot")
        self.resize(1280, 800)
        self.setStyleSheet(MAIN_THEME)
        
        # --- CONFIG ---
        self.man_speed = 80
        self.auto_speed = 65
        self.auto_conf = 0.20
        self.is_auto = False
        
        self.keys_pressed = set()
        self.is_processing = False
        self.flash_state = 1
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.MODEL_PATH = os.path.join(base_dir, "..", "models", "best.pt")
        if not os.path.exists(self.MODEL_PATH):
             self.MODEL_PATH = "app/models/best.pt"

        # --- CONTROLLER ---
        self.robot = RobotController(base_speed=self.auto_speed, screen_width=640)

        # --- THREADS ---
        self.net_thread = NetworkThread("10.230.248.1")
        self.net_thread.data_received.connect(self.update_sensors)
        self.net_thread.ping_signal.connect(self.update_ping)
        self.net_thread.start()
        
        self.sound = SoundManager(self.net_thread)
        
        self.video_thread = VideoThread("http://10.230.248.174:81/stream", self.MODEL_PATH)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.ai_results_signal.connect(self.handle_ai_detection)
        self.video_thread.fps_signal.connect(self.update_fps)
        self.video_thread.start()

        # Timers
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.auto_control_loop)

        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self.send_manual_command)
        self.control_timer.start(100)
        
        # UI
        self.setup_ui()
        self.loader = LoadingOverlay(self)
        QTimer.singleShot(2000, self.sound.play_startup)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setSpacing(10)
        main_lay.setContentsMargins(10, 10, 10, 10)
        
        # ==================== LEFT PANEL (VIDEO) ====================
        left_widget = QWidget()
        left_lay = QVBoxLayout(left_widget)
        left_lay.setSpacing(8)
        left_lay.setContentsMargins(0, 0, 0, 0)
        
        # Info bar (FPS, Ping)
        info_lay = QHBoxLayout()
        self.lbl_fps = QLabel("FPS: 0")
        self.lbl_fps.setStyleSheet("color: #0078D4; font-weight: bold;")
        self.lbl_ping = QLabel("Ping: --")
        self.lbl_ping.setStyleSheet("color: #0078D4; font-weight: bold; margin-left: 15px;")
        
        info_lay.addWidget(self.lbl_fps)
        info_lay.addWidget(self.lbl_ping)
        info_lay.addStretch()
        left_lay.addLayout(info_lay)

        # Video display - SizePolicy để co giãn
        self.lbl_video = QLabel("NO SIGNAL")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setStyleSheet("background: #000; border: 2px solid #0078D4; color: #555;")
        self.lbl_video.setMinimumSize(480, 360)  # Giảm minimum size
        self.lbl_video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_video.setScaledContents(False)
        left_lay.addWidget(self.lbl_video, 1)  # stretch factor = 1
        
        # Info text
        self.lbl_info = QLabel("System Ready")
        self.lbl_info.setStyleSheet("background: #1E1E1E; color: #0FF; padding: 8px; border-radius: 5px;")
        self.lbl_info.setWordWrap(True)
        self.lbl_info.setMaximumHeight(60)
        left_lay.addWidget(self.lbl_info)
        
        main_lay.addWidget(left_widget, 65)  # 65% width

        # ==================== RIGHT PANEL ====================
        right_widget = QWidget()
        right_lay = QVBoxLayout(right_widget)
        right_lay.setSpacing(10)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_widget.setMinimumWidth(350)
        right_widget.setMaximumWidth(500)

        # === RADAR GROUP (Fixed height) ===
        grp_sens = QGroupBox("RADAR")
        grp_sens.setFixedHeight(180)
        grp_sens.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        g_lay = QHBoxLayout()
        g_lay.setSpacing(8)
        self.box_L = SensorBox("LEFT")
        self.box_F = SensorBox("FRONT")
        self.box_R = SensorBox("RIGHT")
        g_lay.addWidget(self.box_L)
        g_lay.addWidget(self.box_F)
        g_lay.addWidget(self.box_R)
        grp_sens.setLayout(g_lay)
        right_lay.addWidget(grp_sens)
        
        # === TABS (Scrollable) ===
        self.main_tabs = QTabWidget()
        self.main_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # --- OPERATION TAB ---
        tab_op = QWidget()
        op_lay = QVBoxLayout(tab_op)
        op_lay.setSpacing(10)
        op_lay.setContentsMargins(10, 10, 10, 10)
        
        self.btn_mode = QPushButton("SWITCH TO AUTO MODE")
        self.btn_mode.setCheckable(True)
        self.btn_mode.setMinimumHeight(50)
        self.btn_mode.setMaximumHeight(60)
        self.btn_mode.clicked.connect(self.request_toggle_mode)
        op_lay.addWidget(self.btn_mode)

        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.panel_man = ManualPanel(self)
        self.panel_auto = AutoPanel()
        self.stack.addWidget(self.panel_man)
        self.stack.addWidget(self.panel_auto)
        op_lay.addWidget(self.stack, 1)  # stretch
        
        self.main_tabs.addTab(tab_op, "OPERATION")
        
        # --- SETTINGS TAB (với ScrollArea) ---
        self.panel_set = SettingsPanel(self)
        
        # Wrap Settings Panel trong ScrollArea
        scroll_settings = QScrollArea()
        scroll_settings.setWidget(self.panel_set)
        scroll_settings.setWidgetResizable(True)
        scroll_settings.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_settings.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical {
                background: #F5F5F5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #0078D4;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #005A9E;
            }
        """)
        
        self.main_tabs.addTab(scroll_settings, "SETTINGS")
        right_lay.addWidget(self.main_tabs, 1)  # stretch

        # === EMERGENCY STOP (Fixed height) ===
        btn_stop = QPushButton("EMERGENCY STOP (SPACE)")
        btn_stop.setStyleSheet(BTN_STOP_STYLE)
        btn_stop.setMinimumHeight(50)
        btn_stop.setMaximumHeight(60)
        btn_stop.clicked.connect(self.emergency_stop)
        right_lay.addWidget(btn_stop)
        
        main_lay.addWidget(right_widget, 35)  # 35% width
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # --- SETTINGS ---
    def update_robot_ip(self, ip):
        self.show_loading(f"ROBOT IP: {ip}", 1000)
        self.net_thread.update_target_ip(ip)

    def update_cam_ip(self, url):
        self.show_loading(f"CAM URL: {url}", 1000)
        print(f"Updating camera URL: {url}")
        
        was_auto = self.is_auto
        if was_auto:
            self.video_thread.set_ai_mode(False)
        
        self.video_thread.update_source(url)
        QTimer.singleShot(1500, lambda: self._resume_after_cam_update(was_auto))
    
    def _resume_after_cam_update(self, was_auto):
        if was_auto:
            self.video_thread.set_ai_mode(True)
            print("Camera reconnected, AI mode resumed")

    def apply_manual_config(self, speed, motor_balance=1.0):
        self.man_speed = speed
        self.robot.MOTOR_LEFT_BOOST = motor_balance
        self.robot.MOTOR_RIGHT_BOOST = 1.0 / motor_balance if motor_balance != 0 else 1.0
        self.show_loading("MANUAL CONFIG SET", 800)

    def apply_auto_config(self, speed, conf, spin_enabled, scan_dur, wait_dur, verify_time,
                      scan_speed, search_delay, align_tol, turn_sens, stop_dist, align_speed, timeout, motor_left_boost=1.0):
        self.auto_speed = speed
        self.auto_conf = conf
        self.robot.base_speed = speed
        self.robot.confidence_threshold = conf
        self.robot.ALIGN_SPEED = align_speed
        self.robot.LOST_TARGET_TIMEOUT = timeout
        self.robot.SCAN_TURN_DURATION = scan_dur
        self.robot.SCAN_WAIT_DURATION = wait_dur
        self.robot.CONFIRM_TIME = verify_time
        self.robot.SCAN_SPEED = scan_speed
        self.robot.SEARCH_DELAY = search_delay
        self.robot.ALIGN_TOLERANCE = align_tol
        self.robot.TURN_SENSITIVITY = turn_sens
        self.robot.STOP_DISTANCE = stop_dist
        # ✅ NEW: Motor balance
        self.robot.MOTOR_LEFT_BOOST = motor_left_boost
        self.robot.MOTOR_RIGHT_BOOST = 1.0 / motor_left_boost  # Inverse để giữ power
        
        if self.is_auto:
            self.video_thread.update_conf(conf)
            self.robot.enable_search(spin_enabled)
        
        print(f"AUTO CONFIG UPDATED:")
        print(f"   Speed: {speed}, Confidence: {conf:.2f}")
        print(f"   Scan: {scan_dur}s / Wait: {wait_dur}s / Verify: {verify_time}s")
        print(f"   Scan Speed: {scan_speed}%, Delay: {search_delay}s")
        print(f"   Align Tol: {align_tol}px, Turn Sens: {turn_sens}, Stop: {stop_dist}cm")
        print(f"   Motor Balance: L={self.robot.MOTOR_LEFT_BOOST:.2f}, R={self.robot.MOTOR_RIGHT_BOOST:.2f}")
        
        self.show_loading("AUTO CONFIG APPLIED", 1000)

    def toggle_flash(self, stream_url):
        try:
            base_url = stream_url.replace("/stream", "").split(":81")[0]
            self.flash_state = 1 - self.flash_state
            requests.get(f"{base_url}/control?var=flash&val={self.flash_state}", timeout=0.5)
            self.show_loading(f"FLASH {'ON' if self.flash_state else 'OFF'}", 500)
            print(f"Flash toggled to: {self.flash_state}")
        except Exception as e:
            print(f"Flash Error: {e}")
            self.show_loading("FLASH ERROR", 500)

    # --- MODE CONTROL ---
    def request_toggle_mode(self):
        if self.btn_mode.isChecked():
            self.set_mode(True)
        else:
            self.set_mode(False)

    def set_mode(self, auto):
        self.is_auto = auto
        self.video_thread.set_ai_mode(auto)
        
        if auto:
            self.control_timer.stop()
            self.btn_mode.setText("AUTO MODE ACTIVE")
            self.btn_mode.setStyleSheet("background-color: #06D6A0; color: #000; font-weight: bold;")
            self.stack.setCurrentIndex(1)
            self.sound.play_auto()
            
            spin_enabled = self.panel_set.chk_spin.isChecked()
            # self.robot.state = RobotState.SEARCH_STEP if spin_enabled else RobotState.IDLE
            # self.robot.search_enabled = spin_enabled
            # self.robot.state_timer = __import__('time').time()
            
            if spin_enabled:
                self.robot.enable_search(True)
                print("AUTO MODE: SEARCH ROTATION - Robot will spin to find trash")
            else:
                self.robot.state = RobotState.IDLE
                self.robot.search_started_time = __import__('time').time()
                self.robot.search_enabled = False
                print("AUTO MODE: STANDING DETECTION - Robot waits for trash in current view")
        
            
            self.video_thread.update_conf(self.auto_conf)
            self.auto_timer.start(50)
        else:
            self.auto_timer.stop()
            self.control_timer.start(100)
            self.btn_mode.setText("SWITCH TO AUTO MODE")
            self.btn_mode.setStyleSheet("")
            self.stack.setCurrentIndex(0)
            self.sound.play_manual()
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
            self.robot.emergency_stop()

    # --- AUTO LOOP ---
    def auto_control_loop(self):
        if not self.is_auto: return
        
        self.robot.update_sensors(self.box_F.current_value, self.box_L.current_value, self.box_R.current_value)
        old_state = self.robot.state
        L, R, info = self.robot.compute_control()
        
        if old_state == RobotState.VERIFYING and self.robot.state == RobotState.ALIGNING:
            label = self.robot.current_label
            self.sound.play_trash_detect(label)
            self.panel_auto.add_trash_item(label, datetime.datetime.now().strftime("%H:%M:%S"))
        
        self.lbl_info.setText(info)
        self.panel_auto.lbl_info.setText(info)

        if self.robot.state == RobotState.REACHED:
            self.handle_trash_reached()
            return
        
        self.net_thread.send_command({"cmd": "MOVE", "L": int(L), "R": int(R)})

    def handle_ai_detection(self, result):
        if self.is_auto:
            detections = result.get('detections', [])
            if detections:
                print(f"Auto Mode - Received {len(detections)} detections")
                for d in detections:
                    print(f"   - {d['label']} ({d['conf']:.2f}) at x={d['center_x']}")
            self.robot.update_detection(detections)

    def handle_trash_reached(self):
        self.auto_timer.stop()
        self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        self.sound.play_done()
        
        trash_name = self.robot.current_label
        trash_name = self.robot.current_label or "UNKNOWN"
        if not trash_name:
            trash_name = "TRASH"
    
        QTimer.singleShot(200, lambda: self.show_completion_dialog(trash_name))

    def show_completion_dialog(self, trash_name):
        dialog = DetectionCompleteDialog(trash_name, self)
        result = dialog.exec()
        self.switch_to_manual_after_detection()

    def switch_to_manual_after_detection(self):
        self.btn_mode.blockSignals(True)
        self.btn_mode.setChecked(False)
        self.btn_mode.blockSignals(False)
        
        self.set_mode(False)
        self.lbl_info.setText("Mission Complete - Switched to Manual")

    # --- SENSORS & MANUAL ---
    def update_sensors(self, data):
        if "F" in data: self.box_F.update_val(data["F"])
        if "L" in data: self.box_L.update_val(data["L"])
        if "R" in data: self.box_R.update_val(data["R"])

    def update_ping(self, ping_str):
        self.lbl_ping.setText(f"Ping: {ping_str}")

    def update_image(self, img):
        if not self.lbl_video.isVisible(): return
        scaled = img.scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(QPixmap.fromImage(scaled))

    def update_fps(self, fps):
        self.lbl_fps.setText(f"FPS: {fps}")

    def keyPressEvent(self, e):
        if not e.isAutoRepeat(): self.handle_key(e.key(), True)
    def keyReleaseEvent(self, e):
        if not e.isAutoRepeat(): self.handle_key(e.key(), False)
    
    def handle_key(self, key, pressed):
        if key == Qt.Key.Key_Space: 
            if pressed: self.emergency_stop()
            return
        
        valid = [Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D]
        if key in valid:
            if pressed: self.keys_pressed.add(key)
            elif key in self.keys_pressed: self.keys_pressed.remove(key)
            
            self.panel_man.btn_w.set_active(Qt.Key.Key_W in self.keys_pressed)
            self.panel_man.btn_a.set_active(Qt.Key.Key_A in self.keys_pressed)
            self.panel_man.btn_s.set_active(Qt.Key.Key_S in self.keys_pressed)
            self.panel_man.btn_d.set_active(Qt.Key.Key_D in self.keys_pressed)

    def send_manual_command(self):
        if self.is_auto: return
        speed = self.man_speed
        t, s = 0, 0
        if Qt.Key.Key_W in self.keys_pressed: t += speed
        if Qt.Key.Key_S in self.keys_pressed: t -= speed
        if Qt.Key.Key_A in self.keys_pressed: s -= speed
        if Qt.Key.Key_D in self.keys_pressed: s += speed
        
        L = max(-255, min(255, t + s))
        R = max(-255, min(255, t - s))
        self.net_thread.send_command({"cmd": "MOVE", "L": int(L), "R": int(R)})

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

    def emergency_stop(self):
        self.set_mode(False)
        for _ in range(3):
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        self.show_loading("EMERGENCY STOP!", 1000)

    def closeEvent(self, e):
        if hasattr(self, 'net_thread'):
            self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
            self.net_thread.stop()
        if hasattr(self, 'video_thread'):
            self.video_thread.stop()
        e.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RobotApp()
    win.show()
    sys.exit(app.exec())