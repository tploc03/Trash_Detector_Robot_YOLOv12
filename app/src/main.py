# main.py - FINAL STABLE VERSION
import sys
import os
import requests
import datetime
import traceback # Thêm thư viện để báo lỗi
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QStackedWidget, QTabWidget, QLabel, 
                            QGroupBox, QGridLayout, QPushButton, QSizePolicy,
                            QMessageBox, QDialog)
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
    # sys.exit(1) # Tùy chọn: Có thể không thoát để debug

sys.excepthook = exception_hook
# ---------------------------------------------

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
        # Fix lỗi icon: Kiểm tra file tồn tại mới set
        icon_path = "app/resources/icons/rover.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.setWindowTitle("Trash Detector Robot - STABLE")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)  # 🆕 Min window size để responsive work
        self.setStyleSheet(MAIN_THEME)
        
        # --- CONFIG ---
        self.man_speed = 80
        self.auto_speed = 65
        self.auto_conf = 0.20
        self.is_auto = False
        
        self.keys_pressed = set()
        self.is_processing = False
        
        # 🆕 FIX #1: Flash khởi tạo = 1 (vì ESP32 boot với flash=ON)
        self.flash_state = 1
        
        # Fix lỗi đường dẫn Model
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Giả sử cấu trúc: Project/app/src/main.py -> Model ở Project/app/models/best.pt
        # parent_dir = app/src/.. = app
        self.MODEL_PATH = os.path.join(base_dir, "..", "models", "best.pt")
        # Fallback nếu chạy từ thư mục gốc
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
        
        # Video Thread
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
        
        # LEFT PANEL
        left_lay = QVBoxLayout()
        info_lay = QHBoxLayout()
        self.lbl_fps = QLabel("FPS: 0")
        self.lbl_fps.setStyleSheet("color: #0078D4; font-weight: bold;")
        self.lbl_ping = QLabel("Ping: --")
        self.lbl_ping.setStyleSheet("color: #0078D4; font-weight: bold; margin-left: 15px;")
        
        # self.lbl_state = QLabel("IDLE")
        # self.lbl_state.setStyleSheet("color: #888; font-weight: bold; margin-left: 15px; background: #222; padding: 2px 8px; border-radius: 4px;")

        info_lay.addWidget(self.lbl_fps)
        info_lay.addWidget(self.lbl_ping)
        # info_lay.addWidget(self.lbl_state)
        info_lay.addStretch()
        left_lay.addLayout(info_lay)

        self.lbl_video = QLabel("NO SIGNAL")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setStyleSheet("background: #000; border: 2px solid #0078D4; color: #555;")
        # 🆕 FIX: Responsive - dùng setMinimumSize với giá trị nhỏ hơn, Expanding size policy
        self.lbl_video.setMinimumSize(320, 240)
        self.lbl_video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_lay.addWidget(self.lbl_video, 1)
        
        self.lbl_info = QLabel("System Ready")
        self.lbl_info.setStyleSheet("background: #1E1E1E; color: #0FF; padding: 8px; border-radius: 5px;")
        self.lbl_info.setWordWrap(True)
        left_lay.addWidget(self.lbl_info)
        
        main_lay.addLayout(left_lay, 65)

        # RIGHT PANEL
        right_lay = QVBoxLayout()
        right_container = QWidget()
        right_container.setLayout(right_lay)
        # 🆕 FIX: Responsive - giảm minimum width từ 380 -> 280, add max width để co dãn tốt
        right_container.setMinimumWidth(280)
        right_container.setMaximumWidth(500)
        right_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

        # Sensor
        grp_sens = QGroupBox("RADAR")
        # ... (Giữ nguyên style) ...
        # 🆕 FIX: Responsive - giảm minimum height từ 160 -> 100
        grp_sens.setMinimumHeight(100)
        grp_sens.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        g_lay = QHBoxLayout()
        self.box_L = SensorBox("LEFT")
        self.box_F = SensorBox("FRONT")
        self.box_R = SensorBox("RIGHT")
        g_lay.addWidget(self.box_L); g_lay.addWidget(self.box_F); g_lay.addWidget(self.box_R)
        grp_sens.setLayout(g_lay)
        right_lay.addWidget(grp_sens)
        
        # Tabs
        self.main_tabs = QTabWidget()
        tab_op = QWidget()
        op_lay = QVBoxLayout(tab_op)
        
        self.btn_mode = QPushButton("SWITCH TO AUTO MODE")
        self.btn_mode.setCheckable(True)
        # 🆕 FIX: Responsive - giảm minimum height từ 50 -> 40
        self.btn_mode.setMinimumHeight(40)
        self.btn_mode.clicked.connect(self.request_toggle_mode)
        op_lay.addWidget(self.btn_mode)

        self.stack = QStackedWidget()
        self.panel_man = ManualPanel(self)
        self.panel_auto = AutoPanel()
        self.stack.addWidget(self.panel_man)
        self.stack.addWidget(self.panel_auto)
        op_lay.addWidget(self.stack)
        
        self.main_tabs.addTab(tab_op, "OPERATION")
        self.panel_set = SettingsPanel(self)
        self.main_tabs.addTab(self.panel_set, "SETTINGS")
        right_lay.addWidget(self.main_tabs)

        btn_stop = QPushButton("EMERGENCY STOP (SPACE)")
        btn_stop.setStyleSheet(BTN_STOP_STYLE)
        btn_stop.clicked.connect(self.emergency_stop)
        right_lay.addWidget(btn_stop)
        
        main_lay.addWidget(right_container, 35)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # --- SETTINGS ---
    def update_robot_ip(self, ip):
        self.show_loading(f"ROBOT IP: {ip}", 1000)
        self.net_thread.update_target_ip(ip)

    def update_cam_ip(self, url):
        self.show_loading(f"CAM URL: {url}", 1000)
        # Reset AI mode và reconnect video thread
        print(f"Updating camera URL: {url}")
        
        # Tắt AI mode tạm thời để reset model
        was_auto = self.is_auto
        if was_auto:
            self.video_thread.set_ai_mode(False)
        
        # Update camera URL
        self.video_thread.update_source(url)
        
        # Đợi reconnect hoàn thành
        QTimer.singleShot(1500, lambda: self._resume_after_cam_update(was_auto))
    
    def _resume_after_cam_update(self, was_auto):
        """Helper: Resume AI mode sau khi camera reconnect"""
        if was_auto:
            self.video_thread.set_ai_mode(True)
            print("Camera reconnected, AI mode resumed")

    def apply_manual_config(self, speed):
        self.man_speed = speed
        self.show_loading("MANUAL CONFIG SET", 800)

    def apply_auto_config(self, speed, conf, spin_enabled, scan_dur, wait_dur, verify_time, 
                          scan_speed, search_delay, align_tol, turn_sens, stop_dist):
        self.auto_speed = speed
        self.auto_conf = conf
        self.robot.base_speed = speed
        
        # 🆕 Cập nhật tất cả parameters
        self.robot.SCAN_TURN_DURATION = scan_dur
        self.robot.SCAN_WAIT_DURATION = wait_dur
        self.robot.CONFIRM_TIME = verify_time
        self.robot.SCAN_SPEED = scan_speed
        self.robot.SEARCH_DELAY = search_delay
        self.robot.ALIGN_TOLERANCE = align_tol
        self.robot.TURN_SENSITIVITY = turn_sens
        self.robot.STOP_DISTANCE = stop_dist
        
        if self.is_auto:
            self.video_thread.update_conf(conf)
            self.robot.enable_search(spin_enabled)
        
        # Log cập nhật settings
        print(f"⚙️  AUTO CONFIG UPDATED:")
        print(f"   Speed: {speed}, Confidence: {conf:.2f}")
        print(f"   Scan: {scan_dur}s / Wait: {wait_dur}s / Verify: {verify_time}s")
        print(f"   Scan Speed: {scan_speed}%, Delay: {search_delay}s")
        print(f"   Align Tol: {align_tol}px, Turn Sens: {turn_sens}, Stop: {stop_dist}cm")
        
        self.show_loading("AUTO CONFIG APPLIED", 1000)

    def toggle_flash(self, stream_url):
        try:
            base_url = stream_url.replace("/stream", "").split(":81")[0]
            self.flash_state = 1 - self.flash_state  # Toggle state
            
            # Gửi request trong thread riêng hoặc dùng timeout cực ngắn
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
            
            # Config Robot
            spin_enabled = self.panel_set.chk_spin.isChecked()
            self.robot.state = RobotState.SEARCH_STEP if spin_enabled else RobotState.IDLE
            self.robot.search_enabled = spin_enabled
            self.robot.state_timer = __import__('time').time()
            
            # 🆕 Log rõ ràng chế độ nào
            if spin_enabled:
                print("AUTO MODE: SEARCH ROTATION - Robot will spin to find trash")
            else:
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
        
        # Logic âm thanh & UI
        if old_state == RobotState.VERIFYING and self.robot.state == RobotState.ALIGNING:
            label = self.robot.current_label
            self.sound.play_trash_detect(label)
            self.panel_auto.add_trash_item(label, datetime.datetime.now().strftime("%H:%M:%S"))
        
        self.lbl_info.setText(info)
        self.panel_auto.lbl_info.setText(info)
        
        # Update State Label Color
        # self.lbl_state.setText(self.robot.state.value)
        # self.lbl_state.setStyleSheet(f"color: {self.robot.get_state_color()}; font-weight: bold; margin-left: 15px; background: #222; padding: 2px 8px; border-radius: 4px;")

        if self.robot.state == RobotState.REACHED:
            self.handle_trash_reached()
            return
        
        self.net_thread.send_command({"cmd": "MOVE", "L": int(L), "R": int(R)})

    def handle_ai_detection(self, result):
        if self.is_auto:
            detections = result.get('detections', [])
            # DEBUG: In ra để xem có nhận detection không
            if detections:
                print(f"Auto Mode - Received {len(detections)} detections")
                for d in detections:
                    print(f"   - {d['label']} ({d['conf']:.2f}) at x={d['center_x']}")
            self.robot.update_detection(detections)

    def handle_trash_reached(self):
        """Xử lý khi đến đích an toàn"""
        self.auto_timer.stop()
        self.net_thread.send_command({"cmd": "STOP", "L": 0, "R": 0})
        self.sound.play_done()
        
        trash_name = self.robot.current_label
        
        # Dùng QTimer để hiển thị Dialog sau 1 chút để tránh kẹt UI
        QTimer.singleShot(200, lambda: self.show_completion_dialog(trash_name))

    def show_completion_dialog(self, trash_name):
        dialog = DetectionCompleteDialog(trash_name, self)
        result = dialog.exec()
        
        # Sau khi đóng dialog, chuyển về Manual
        self.switch_to_manual_after_detection()

    def switch_to_manual_after_detection(self):
        # Properly uncheck AUTO button khi switch về manual
        self.btn_mode.blockSignals(True)  # Tránh infinite loop
        self.btn_mode.setChecked(False)   # Uncheck button
        self.btn_mode.blockSignals(False)
        
        self.set_mode(False)  # Switch mode
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
        scaled = img.scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio)
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
        
        # Mixer đơn giản
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
        self.set_mode(False) # Reset về Manual an toàn
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