"""
Windows 11 Light Mode Theme - Clean, Bright, Professional
"""

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

/* TAB WIDGET */
QTabWidget::pane {{ border: none; background: transparent; }}
QTabBar::tab {{
    background: {BG_SURFACE}; 
    color: {TEXT_SECONDARY}; 
    padding: 12px 24px;
    margin-right: 2px;
    border-bottom: 3px solid transparent;
    font-weight: 600;
}}
QTabBar::tab:selected {{ 
    background: {PRIMARY_COLOR}; 
    color: #000; 
    border-bottom: 3px solid {PRIMARY_DARK};
}}

/* GROUP BOX */
QGroupBox {{ 
    border: 2px solid {BG_TERTIARY}; 
    border-radius: 12px; 
    margin-top: 20px; 
    padding-top: 15px;
    font-weight: bold; 
    color: {PRIMARY_COLOR}; 
    background: {BG_SURFACE};
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 15px; padding: 0 8px; }}

/* LINE EDIT */
QLineEdit {{ 
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 10px 12px; 
    border-radius: 8px;
}}
QLineEdit:focus {{ border: 2px solid {PRIMARY_COLOR}; }}

/* SLIDERS & OTHERS */
QSlider::groove:horizontal {{ height: 8px; background: {BG_TERTIARY}; border-radius: 4px; }}
QSlider::handle:horizontal {{ background: {PRIMARY_COLOR}; width: 18px; margin: -5px 0; border-radius: 9px; }}
QLabel {{ color: {TEXT_PRIMARY}; background: transparent; }}
"""

CHECKBOX_STYLE = f"""
QCheckBox {{
    font-size: 13px;
    font-weight: bold;
    color: {PRIMARY_COLOR};
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid {BG_TERTIARY};
    background-color: {BG_PRIMARY};
}}
QCheckBox::indicator:hover {{
    border: 2px solid {PRIMARY_COLOR};
}}
QCheckBox::indicator:checked {{
    background-color: {PRIMARY_COLOR};
    border: 2px solid {PRIMARY_COLOR};
    /* Không dùng image/content để tránh lỗi */
}}
"""

BTN_STYLE = f"""
QPushButton {{
    background-color: {PRIMARY_COLOR}; 
    color: #000; 
    border: none;
    border-radius: 8px; 
    padding: 12px 24px; 
    font-weight: 700;
}}
QPushButton:hover {{ background-color: {PRIMARY_LIGHT}; }}
QPushButton:pressed {{ background-color: {PRIMARY_DARK}; }}
"""

BTN_SECONDARY = f"""
QPushButton {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {PRIMARY_COLOR};
    border-radius: 8px; 
    padding: 10px 20px; 
    font-weight: 600;
}}
QPushButton:hover {{ background-color: {PRIMARY_COLOR}; color: #000; }}
"""

INPUT_STYLE = f"""
QLineEdit {{
    background-color: {BG_TERTIARY}; 
    color: {TEXT_PRIMARY}; 
    border: 2px solid {BG_TERTIARY}; 
    padding: 10px 12px; 
    border-radius: 8px;
}}
QLineEdit:focus {{ border: 2px solid {PRIMARY_COLOR}; }}
"""

BTN_STOP_STYLE = f"""
QPushButton {{ 
    background-color: {DANGER_COLOR}; 
    color: white; 
    border-radius: 10px; 
    font-weight: 700; 
    font-size: 14px;
    padding: 16px 20px;
    border: none;
}}
QPushButton:hover {{ background-color: #FF5A7E; }}
"""