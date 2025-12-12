# 🐛 DEBUG GUIDE - Tại sao app màn hình trắng rồi tắt?

## ✅ Lỗi đã sửa:

1. ✅ `setSizePolicy(1, 1)` → `setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)`
2. ✅ `Qt.QSize(100, 100)` → `QSize(100, 100)`
3. ✅ `self.lbl_state` được khai báo nhưng bị comment → Sửa: Bật khai báo
4. ✅ Thiếu exception handling cho Network & Video threads → Thêm try-catch
5. ✅ `self.sound.play_auto()` / `self.sound.play_manual()` không tồn tại → Thêm vào `sound_manager.py`

## 🔍 Nguyên nhân APP MÀN HÌNH TRẮNG RỒI TẮT:

### **NGUYÊN NHÂN 1: Không kết nối được ROBOT (IP: 10.230.248.1)**

- `NetworkThread` sẽ **báo lỗi nhưng KHÔNG CRASH**
- App vẫn chạy bình thường (chỉ không nhận sensor data)

### **NGUYÊN NHÂN 2: Không kết nối được CAMERA (IP: 10.230.248.174)**

- `VideoThread` sẽ liên tục thử reconnect
- Video label sẽ hiển thị "NO SIGNAL"
- **Này cũng KHÔNG CRASH**

### **NGUYÊN NHÂN 3: Model YOLO không tìm thấy**

- Path: `D:\Program Files\Files\25-26_HK1\LV\TrashDetectionCar\app\src\..\models\best.pt`
- Tức: `D:\Program Files\Files\25-26_HK1\LV\TrashDetectionCar\app\models\best.pt`
- Nếu không tìm thấy → `ai_enabled = False` (AI tắt, nhưng **app vẫn chạy**)

### **NGUYÊN NHÂN 4: SettingsPanel.create_auto_tab() lỗi**

- Xem dòng `create_auto_tab()` trong `ui/panels.py`
- Có thể throw exception khi khởi tạo

### **NGUYÊN NHÂN 5: SensorBox hoặc LoadingOverlay exception**

- Nếu class này lỗi → toàn bộ UI không khởi tạo được

---

## 🔧 CÁCH FIX:

### **BƯỚC 1: Chạy app và xem console output**

```powershell
cd "D:\Program Files\Files\25-26_HK1\LV\TrashDetectionCar"
& ".\.venv\Scripts\python.exe" app/src/main.py
```

**Nếu thấy:**

```
✅ RobotApp created successfully
✅ Window shown successfully
🎮 App running...
```

→ **App hoạt động OK**, nhưng GUI có thể bị ẩn hoặc crash sau đó

---

### **BƯỚC 2: Kiểm tra các thành phần chính**

**Kiểm tra video stream:**

```
Nếu thấy: "⚠️ No Frame. Check IP or Wifi."
→ Camera không kết nối được
```

**Kiểm tra robot connection:**

```
Nếu không thấy "✅ Network Thread Started"
→ Robot không kết nối được
```

**Kiểm tra model:**

```
Nếu không thấy "✅ Model loaded successfully"
→ File best.pt không tìm thấy
```

---

### **BƯỚC 3: Kiểm tra từng module riêng lẻ**

```python
# Test 1: Network Thread
python -c "from app.src.network import NetworkThread; n = NetworkThread('10.230.248.1'); print('✅')"

# Test 2: Video Thread
python -c "from app.src.video import VideoThread; v = VideoThread('http://10.230.248.174:81/stream', 'app/models/best.pt'); print('✅')"

# Test 3: Robot Controller
python -c "from app.src.robot_controller import RobotController; r = RobotController(); print('✅')"

# Test 4: Sound Manager
python -c "from app.src.sound_manager import SoundManager; s = SoundManager(None); print('✅')"
```

---

### **BƯỚC 4: Kiểm tra dependencies**

```powershell
pip list | grep -E "PyQt6|opencv|torch|ultralytics"
```

Cần có:

- ✅ PyQt6
- ✅ opencv-python
- ✅ torch
- ✅ ultralytics (cho YOLO)

---

## 📋 Kiểm tra đơn giản

**Chạy app với một màn hình tiếp tế (minimal version):**

```python
# test_gui.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("Test GUI")
window.resize(400, 300)
label = QLabel("App is running!")
window.setCentralWidget(label)
window.show()
sys.exit(app.exec())
```

Nếu cả cái này chạy được → PyQt6 ổn, vấn đề trong `RobotApp` class

---

## 🎯 Kết luận

**Có khả năng cao là:**

1. App **KHÔNG CRASH**, chỉ là GUI **không hiển thị đầy đủ** (quá nhỏ hoặc bị ẩn)
2. Hoặc app **CRASH BỮA SAU khi khởi động** (exception xảy ra trong threads)

**Cách kiểm tra cuối cùng:**

- Chạy app, **BẤT GIỮ CỬASỔ** (không đóng nó ngay)
- Đợi 5 giây xem có hiện UI không
- Xem console output để tìm exception
