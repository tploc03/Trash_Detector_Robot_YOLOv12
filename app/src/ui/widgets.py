# ui/widgets.py
from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal

class VisualKey(QPushButton):
    """Nút bấm mô phỏng bàn phím - Hỗ trợ Click chuột"""
    def __init__(self, text, key_code):
        super().__init__(text)
        self.key_code = key_code
        self.setFixedSize(70, 70)
        self.setStyleSheet("""
            QPushButton { 
                background-color: #333; color: white; border: 2px solid #555; 
                border-radius: 10px; font-size: 24px; font-weight: bold; 
            }
            QPushButton:pressed { background-color: #2ecc71; color: black; border-color: white; }
        """)

    def set_active(self, active):
        if active:
            self.setStyleSheet("background-color: #2ecc71; color: black; border: 2px solid white; border-radius: 10px; font-size: 24px; font-weight: bold;")
        else:
            self.setStyleSheet("background-color: #333; color: white; border: 2px solid #555; border-radius: 10px; font-size: 24px; font-weight: bold;")

class SensorBox(QFrame):
    """Ô hiển thị cảm biến kiểu Radar"""
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("background-color: #222; border: 1px solid #444; border-radius: 8px;")
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("color: #888; font-size: 11px;")
        
        self.lbl_val = QLabel("--")
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_val.setStyleSheet("color: #2ecc71; font-size: 28px; font-weight: bold;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_val)

    def update_val(self, val):
        self.lbl_val.setText(str(val))
        if val < 20: self.lbl_val.setStyleSheet("color: #e74c3c; font-size: 28px; font-weight: bold;") # Red
        elif val < 50: self.lbl_val.setStyleSheet("color: #f1c40f; font-size: 28px; font-weight: bold;") # Yellow
        else: self.lbl_val.setStyleSheet("color: #2ecc71; font-size: 28px; font-weight: bold;") # Green