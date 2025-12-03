# styles.py
"""
Windows 11 Light Mode Theme - Clean, Bright, Professional
Color Palette:
  Primary (Accent): #0078D4 (Windows Blue)
  Background: #FFFFFF (Pure White)
  Surface: #F5F5F5 (Light Gray)
  Tertiary: #ECECEC (Medium Gray)
  Text Primary: #000000 (Pure Black)
  Text Secondary: #666666 (Medium Gray)
  Danger: #DC3545 (Bright Red)
  Warning: #FFC107 (Bright Yellow)
"""

# Windows 11 Light Mode Color Palette
PRIMARY_COLOR = "#0078D4"      # Windows Blue Accent
PRIMARY_DARK = "#005A9E"       # Darker Blue
PRIMARY_LIGHT = "#50B4F5"      # Lighter Blue
SECONDARY_COLOR = "#0078D4"    # Windows Blue
DANGER_COLOR = "#DC3545"       # Bright Red
BG_PRIMARY = "#FFFFFF"         # Pure White
BG_SURFACE = "#F5F5F5"         # Light Gray
BG_TERTIARY = "#ECECEC"        # Medium Gray
TEXT_PRIMARY = "#000000"        # Pure Black
TEXT_SECONDARY = "#666666"      # Medium Gray

MAIN_THEME = f"""
/* Global Theme */
QMainWindow, QWidget {{ 
    background-color: {BG_PRIMARY}; 
    color: {TEXT_PRIMARY}; 
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}}

/* TAB WIDGET - Modern Flat Design */
QTabWidget::pane {{ 
    border: none; 
    background: transparent;
    border-radius: 12px; 
}}
QTabWidget::tab-bar {{ 
    alignment: left;
}}
QTabBar::tab {{
    background: {BG_SURFACE}; 
    color: {TEXT_SECONDARY}; 
    padding: 12px 24px;
    margin-right: 2px;
    border-bottom: 3px solid transparent;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.5px;
}}
QTabBar::tab:hover {{
    background: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border-bottom-color: {PRIMARY_LIGHT};
}}
QTabBar::tab:selected {{ 
    background: {PRIMARY_COLOR}; 
    color: #000; 
    border-bottom: 3px solid {PRIMARY_DARK};
    font-weight: 700;
}}

/* GROUP BOX - Elegant Styling */
QGroupBox {{ 
    border: 2px solid {BG_TERTIARY}; 
    border-radius: 12px; 
    margin-top: 20px; 
    padding-top: 15px;
    font-weight: bold; 
    color: {PRIMARY_COLOR}; 
    background: {BG_SURFACE};
}}
QGroupBox::title {{ 
    subcontrol-origin: margin; 
    left: 15px; 
    padding: 0 8px; 
    background: {BG_SURFACE};
    color: {PRIMARY_COLOR};
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
}}

/* LINE EDIT - Modern Input */
QLineEdit {{ 
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 10px 12px; 
    border-radius: 8px;
    selection-background-color: {PRIMARY_COLOR};
    selection-color: #000;
    font-size: 12px;
}}
QLineEdit:focus {{ 
    border: 2px solid {PRIMARY_COLOR};
    background-color: {BG_SURFACE};
}}
QLineEdit:hover {{
    border: 2px solid {PRIMARY_LIGHT};
}}

/* SLIDER - Custom Groove and Handle */
QSlider::groove:horizontal {{ 
    height: 8px; 
    background: {BG_TERTIARY}; 
    border-radius: 4px;
    margin: 2px 0;
}}
QSlider::sub-page:horizontal {{
    background: {PRIMARY_COLOR};
    border-radius: 4px;
}}
QSlider::handle:horizontal {{ 
    background: {PRIMARY_COLOR}; 
    width: 18px; 
    height: 18px;
    margin: -5px 0; 
    border-radius: 9px;
    border: 2px solid {PRIMARY_DARK};
}}
QSlider::handle:horizontal:hover {{
    background: {PRIMARY_LIGHT};
    border: 2px solid {PRIMARY_COLOR};
}}
QSlider::handle:horizontal:pressed {{
    background: {PRIMARY_DARK};
}}

/* LABELS */
QLabel {{ 
    color: {TEXT_PRIMARY};
    background: transparent;
}}

/* COMBO BOX */
QComboBox {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 8px 10px; 
    border-radius: 8px;
}}
QComboBox:focus {{
    border: 2px solid {PRIMARY_COLOR};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
}}

/* SPINBOX */
QSpinBox, QDoubleSpinBox {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 8px 10px; 
    border-radius: 8px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 2px solid {PRIMARY_COLOR};
}}
"""

# Modern Button Style with Gradient Effect
BTN_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY_COLOR}; 
    color: #000; 
    border: none;
    border-radius: 8px; 
    padding: 12px 24px; 
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.5px;
}}
QPushButton:hover {{ 
    background-color: {PRIMARY_LIGHT}; 
    padding: 12px 24px;
}}
QPushButton:pressed {{ 
    background-color: {PRIMARY_DARK};
}}
QPushButton:disabled {{
    background-color: {BG_TERTIARY};
    color: {TEXT_SECONDARY};
}}
"""

# Secondary Button Style
BTN_SECONDARY = f"""
QPushButton {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {PRIMARY_COLOR};
    border-radius: 8px; 
    padding: 10px 20px; 
    font-weight: 600;
}}
QPushButton:hover {{ 
    background-color: {PRIMARY_COLOR};
    color: #000;
}}
QPushButton:pressed {{ 
    background-color: {PRIMARY_DARK};
}}
"""

# Input Field Style
INPUT_STYLE = f"""
QLineEdit {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 10px 12px; 
    border-radius: 8px;
}}
QLineEdit:focus {{
    border: 2px solid {PRIMARY_COLOR};
}}
"""

# Emergency Stop Button - Danger Color with Pulse Effect
BTN_STOP_STYLE = f"""
QPushButton {{ 
    background-color: {DANGER_COLOR}; 
    color: white; 
    border-radius: 10px; 
    font-weight: 700; 
    font-size: 14px;
    letter-spacing: 0.5px;
    padding: 16px 20px;
    border: none;
}}
QPushButton:hover {{ 
    background-color: #FF5A7E;
    padding: 16px 20px;
}}
QPushButton:pressed {{ 
    background-color: #D63042;
    padding: 16px 20px;
}}
"""

# Status Box Style (for Sensor Display)
STATUS_BOX = f"""
QFrame {{
    background-color: {BG_SURFACE}; 
    border: 2px solid {PRIMARY_COLOR};
    border-radius: 10px;
    padding: 12px;
}}
"""