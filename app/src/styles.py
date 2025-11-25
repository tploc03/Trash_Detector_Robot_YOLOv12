# styles.py

# Bảng màu:
# Nền chính: #1e1e1e (Xám đậm)
# Nền phụ (Panel): #252526
# Accent (Điểm nhấn): #00b894 (Xanh ngọc hiện đại)
# Text chính: #dfe6e9 (Trắng xám)
# Text phụ: #b2bec3 (Xám nhạt)

MAIN_THEME = """
QMainWindow { 
    background-color: #1e1e1e; 
    color: #dfe6e9; 
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* TAB WIDGET */
QTabWidget::pane { 
    border: 1px solid #333; 
    background: #252526; 
    border-radius: 8px; 
}
QTabWidget::tab-bar { left: 10px; }
QTabBar::tab {
    background: #2d3436; 
    color: #b2bec3; 
    padding: 10px 20px;
    border-top-left-radius: 8px; 
    border-top-right-radius: 8px;
    margin-right: 4px; 
    font-weight: 600;
}
QTabBar::tab:selected { 
    background: #00b894; 
    color: #fff; 
}
QTabBar::tab:hover {
    background: #353b48;
}

/* GROUP BOX */
QGroupBox { 
    border: 1px solid #444; 
    border-radius: 8px; 
    margin-top: 25px; 
    font-weight: bold; 
    color: #00b894; 
    background: #2d3436;
}
QGroupBox::title { 
    subcontrol-origin: margin; 
    left: 15px; 
    padding: 0 5px; 
    background: transparent; 
}

/* INPUTS & SLIDERS */
QLineEdit { 
    background-color: #1e1e1e; 
    color: #fff; 
    border: 1px solid #444; 
    padding: 8px; 
    border-radius: 4px; 
    selection-background-color: #00b894;
}
QSlider::groove:horizontal { 
    height: 6px; 
    background: #1e1e1e; 
    border-radius: 3px; 
}
QSlider::sub-page:horizontal {
    background: #00b894;
    border-radius: 3px;
}
QSlider::handle:horizontal { 
    background: #fff; 
    width: 14px; 
    height: 14px;
    margin: -4px 0; 
    border-radius: 7px; 
}

/* LABELS */
QLabel { color: #dfe6e9; }
"""

BTN_STYLE = """
QPushButton {
    background-color: #353b48; 
    color: #fff; 
    border: 1px solid #444;
    border-radius: 6px; 
    padding: 12px; 
    font-weight: 600;
}
QPushButton:hover { 
    background-color: #3d4655; 
    border-color: #00b894; 
}
QPushButton:pressed { 
    background-color: #00b894; 
}
"""

INPUT_STYLE = """
QLineEdit {
    background-color: #1e1e1e; 
    color: #fff; 
    border: 1px solid #444; 
    padding: 8px; 
    border-radius: 4px; 
}
"""

BTN_STOP_STYLE = """
QPushButton { 
    background-color: #d63031; 
    color: white; 
    border-radius: 8px; 
    font-weight: bold; 
    font-size: 16px; 
    padding: 15px; 
}
QPushButton:hover { background-color: #e17055; }
QPushButton:pressed { background-color: #ff7675; }
"""