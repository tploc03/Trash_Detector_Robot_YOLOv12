# ui/widgets.py
from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush

class VisualKey(QPushButton):
    """Modern Visual Key Button - W, A, S, D Control"""
    def __init__(self, text, key_code):
        super().__init__(text)
        self.key_code = key_code
        self.setFixedSize(80, 80)
        self.is_active = False
        
        # Modern Font
        font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        self.setFont(font)
        
        # Inactive State
        self.update_appearance(False)

    def set_active(self, active):
        self.is_active = active
        self.update_appearance(active)

    def update_appearance(self, active):
        if active:
            # Active: Windows Blue
            self.setStyleSheet("""
                QPushButton { 
                    background-color: #0078D4; 
                    color: #FFF; 
                    border: 2px solid #005A9E; 
                    border-radius: 12px; 
                    font-weight: bold;
                }
                QPushButton:pressed {{ 
                    background-color: #005A9E; 
                    border: 2px solid #FFF;
                }}
            """)
        else:
            # Inactive: Light Gray with subtle border
            self.setStyleSheet("""
                QPushButton { 
                    background-color: #F5F5F5; 
                    color: #666666; 
                    border: 2px solid #ECECEC; 
                    border-radius: 12px; 
                    font-weight: bold;
                }
                QPushButton:hover {{ 
                    background-color: #ECECEC;
                    color: #000000;
                    border: 2px solid #0078D4;
                }}
                QPushButton:pressed {{ 
                    background-color: #0078D4; 
                    color: #FFF;
                    border: 2px solid #005A9E;
                }}
            """)

class SensorBox(QFrame):
    """Modern Sensor Display Box with Status Indicator"""
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.current_value = 0
        
        # Modern styling
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5; 
                border: 2px solid #ECECEC; 
                border-radius: 12px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title Label
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        lbl_title.setFont(title_font)
        lbl_title.setStyleSheet("color: #0078D4; letter-spacing: 1px;")
        
        # Value Label
        self.lbl_val = QLabel("--")
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        self.lbl_val.setFont(val_font)
        self.lbl_val.setStyleSheet("color: #0078D4;")
        
        # Unit Label
        self.lbl_unit = QLabel("cm")
        self.lbl_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unit_font = QFont("Segoe UI", 10)
        self.lbl_unit.setFont(unit_font)
        self.lbl_unit.setStyleSheet("color: #666666;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_val)
        layout.addWidget(self.lbl_unit)

    def update_val(self, val):
        """Update sensor value with color coding"""
        self.current_value = val
        self.lbl_val.setText(str(val))
        
        # Color gradient based on distance
        val_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        self.lbl_val.setFont(val_font)
        
        if val < 20:
            # Danger: Bright Red
            self.lbl_val.setStyleSheet("color: #DC3545; font-weight: bold;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5; 
                    border: 2px solid #DC3545; 
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        elif val < 50:
            # Warning: Bright Yellow
            self.lbl_val.setStyleSheet("color: #FFC107; font-weight: bold;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5; 
                    border: 2px solid #FFC107; 
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        else:
            # Safe: Windows Blue
            self.lbl_val.setStyleSheet("color: #0078D4; font-weight: bold;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5; 
                    border: 2px solid #0078D4; 
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
class LoadingOverlay(QWidget):
    """Màn hình chờ chặn thao tác người dùng"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Chặn chuột
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container
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
        
        # Label
        self.lbl_text = QLabel("PROCESSING...")
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_text.setStyleSheet("color: white; font-weight: bold; font-size: 16px; background: transparent; border: none;")
        
        # Sub Label
        self.lbl_sub = QLabel("Please wait for hardware...")
        self.lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_sub.setStyleSheet("color: #CCC; font-size: 12px; background: transparent; border: none;")
        
        vbox.addWidget(self.lbl_text)
        vbox.addWidget(self.lbl_sub)
        layout.addWidget(container)
        
        self.hide()

    def show_msg(self, title, sub=""):
        self.lbl_text.setText(title)
        self.lbl_sub.setText(sub)
        self.resize(self.parent().size()) # Phủ kín màn hình cha
        self.show()
        self.raise_()

    def paintEvent(self, event):
        # Vẽ nền mờ tối
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))