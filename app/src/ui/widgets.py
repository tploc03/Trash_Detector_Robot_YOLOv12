# ui/widgets.py
from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

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