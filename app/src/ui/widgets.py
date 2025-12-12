# ui/widgets.py - FIXED VERSION
from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter

class VisualKey(QPushButton):
    """Modern Visual Key Button - W, A, S, D Control"""
    def __init__(self, text, key_code):
        super().__init__(text)
        self.key_code = key_code
        self.setFixedSize(80, 80)
        self.is_active = False
        
        font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        self.setFont(font)
        
        self.update_appearance(False)

    def set_active(self, active):
        self.is_active = active
        self.update_appearance(active)

    def update_appearance(self, active):
        if active:
            self.setStyleSheet("""
                QPushButton { 
                    background-color: #0078D4; 
                    color: #FFF; 
                    border: 2px solid #005A9E; 
                    border-radius: 12px; 
                    font-weight: bold;
                }
                QPushButton:pressed { 
                    background-color: #005A9E; 
                    border: 2px solid #FFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton { 
                    background-color: #F5F5F5; 
                    color: #666666; 
                    border: 2px solid #ECECEC; 
                    border-radius: 12px; 
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background-color: #ECECEC;
                    color: #000000;
                    border: 2px solid #0078D4;
                }
                QPushButton:pressed { 
                    background-color: #0078D4; 
                    color: #FFF;
                    border: 2px solid #005A9E;
                }
            """)

class SensorBox(QFrame):
    """Modern Sensor Display with Progress Bar"""
    def __init__(self, title):
        super().__init__()
        self.current_value = 0
        self.max_dist = 200
        
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
            }
        """)
        self.setFixedSize(110, 130)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet("color: #888; border: none; background: transparent;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_title)
        
        self.lbl_val = QLabel("--")
        self.lbl_val.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.lbl_val.setStyleSheet("color: #333; border: none; background: transparent;")
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_val)
        
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(6)
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #F0F0F0;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.bar)

    def update_val(self, val):
        self.current_value = val
        self.lbl_val.setText(str(int(val)))
        
        percent = 0
        if val > 0:
            percent = max(0, min(100, int((1 - (val / self.max_dist)) * 100)))
        
        self.bar.setValue(percent)

        if val == 0 or val >= 200: 
            color = "#BDBDBD"
            bg_val = "#333"
        elif val < 20: 
            color = "#DC3545"
            bg_val = "#DC3545"
        elif val < 50: 
            color = "#FFC107"
            bg_val = "#F57C00"
        else: 
            color = "#0078D4"
            bg_val = "#0078D4"

        self.lbl_val.setStyleSheet(f"color: {bg_val}; border: none; background: transparent;")
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #F0F0F0;
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 200);
                border-radius: 15px;
                border: 2px solid #0078D4;
            }
        """)
        container.setFixedSize(300, 150)
        vbox = QVBoxLayout(container)
        
        self.lbl_text = QLabel("PROCESSING...")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_text.setStyleSheet("""
            QLabel {
                color: white; 
                font-weight: bold; 
                font-size: 16px; 
                background: transparent; 
                border: none;
            }
        """)
        
        self.lbl_sub = QLabel("Please wait...")
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sub.setStyleSheet("""
            QLabel {
                color: #CCC; 
                font-size: 12px; 
                background: transparent; 
                border: none;
            }
        """)
        
        vbox.addWidget(self.lbl_text)
        vbox.addWidget(self.lbl_sub)
        layout.addWidget(container)
        
        self.hide()

    def show_msg(self, msg, sub=""):
        """Hiển thị overlay với message"""
        self.lbl_text.setText(msg)
        if sub:
            self.lbl_sub.setText(sub)
        self.resize(self.parent().size())
        self.show()
        self.raise_()  # Đưa lên trên cùng
    
    def paintEvent(self, event):
        """Vẽ nền mờ"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))