# ⚙️ Auto Mode Settings - Hướng Dẫn Chi Tiết

## 🎚️ Các Settings Mới Trong AUTO Tab

### **Nhóm 1: CƠ BẢN** (Basic)

- **Speed (0-255):** Tốc độ chuyển động của robot
  - Mặc định: 65
  - Khuyến cáo: 50-80
- **AI Conf (10%-80%):** Độ tin cậy để phát hiện rác

  - Mặc định: 20%
  - Thấp (10-20%): Dễ detect nhưng nhiễu
  - Cao (40-60%): Ít nhiễu nhưng dễ miss

- **Enable Scan Mode:** Bật/tắt chế độ xoay tìm kiếm
  - ✅ Bật: Robot xoay 360° tìm rác
  - ❌ Tắt: Robot đứng yên, camera quét frame

---

### **Nhóm 2: CHIẾN THUẬT QUAY** (Step & Scan Tuning)

- **Step Turn Time (0.1s - 5.0s):** Thời gian robot xoay mỗi bước

  - Mặc định: 0.4s
  - **Tăng lên:** Robot xoay chậm hơn (phát hiện tốt hơn)
  - **Giảm xuống:** Robot xoay nhanh hơn (quét nhanh hơn)

- **Wait/Scan Time (0.1s - 5.0s):** Thời gian robot dừng để camera scan frame

  - Mặc định: 1.0s
  - **Tăng lên:** Camera có nhiều thời gian nhìn (phát hiện tốt)
  - **Giảm xuống:** Quá trình scan nhanh hơn

- **Verify Time (0.1s - 5.0s):** Thời gian cần thấy rác liên tục trước khi xác nhận
  - Mặc định: 2.0s
  - **Tăng lên:** Tránh false positive (nhưng chậm hơn)
  - **Giảm xuống:** Phản ứng nhanh (nhưng dễ false positive)

---

### **Nhóm 3: CHUYỂN ĐỘNG & CẢM BIẾN** (Movement & Sensor Tuning) ⭐ MỚI

#### **Scan Speed (10% - 100%)**

Tốc độ quay khi tìm kiếm (chế độ Search)

- Mặc định: 90%
- **Tăng lên (90-100%):** Quay nhanh → Scan nhanh nhưng dễ miss
- **Giảm xuống (50-70%):** Quay chậm → Phát hiện tốt nhưng chậm
- **Khuyến cáo:** 80-90%

#### **Search Delay (0.0s - 3.0s)** ⭐ MỚI

Thời gian delay trước khi bắt đầu quay (tránh quay vội vàng)

- Mặc định: 0.5s
- **Tăng lên:** Delay lâu hơn, robot chuẩn bị kỹ trước khi quay
- **Giảm xuống:** Quay gần như ngay lập tức
- **Khuyến cáo:** 0.3-0.7s

#### **Align Tolerance (10px - 100px)** ⭐ MỚI

Ngưỡng căn chỉnh - khoảng cách từ tâm screen để coi rác đã "căn chỉnh"

- Mặc định: 40px
- **Tăng lên (50-100px):** Dễ căn chỉnh nhưng robot có thể không chạy tới đúng
- **Giảm xuống (20-30px):** Cần căn chỉnh chính xác (có thể rung lắc)
- **Khuyến cáo:** 35-50px

#### **Turn Sensitivity (0.1 - 5.0)** ⭐ MỚI

Độ nhạy xoay khi căn chỉnh (P-Control)

- Mặc định: 0.2
- **Tăng lên (0.3-0.5):** Robot xoay cứng hơn → Phản ứng nhanh
- **Giảm xuống (0.1-0.15):** Robot xoay mềm hơn → Ổn định nhưng chậm
- **Khuyến cáo:** 0.15-0.25

#### **Stop Distance (5cm - 50cm)** ⭐ MỚI

Khoảng cách dừng an toàn (từ sonar)

- Mặc định: 10cm
- **Tăng lên:** Dừng sớm hơn (an toàn hơn)
- **Giảm xuống:** Dừng muộn hơn (gần target hơn)
- **Khuyến cáo:** 10-20cm

---

## 📊 **QUY TRÌNH AUTO MODE**

### **Chế độ SEARCH (Xoay tìm):**

```
START
  ↓
WAIT {Search Delay} (0.5s)
  ↓
SEARCH_STEP (xoay {Step Turn Time})
  ↓
SEARCH_WAIT (chờ {Wait/Scan Time} để camera scan)
  ↓ (nếu thấy rác)
VERIFYING (xác nhận trong {Verify Time})
  ↓
ALIGNING (căn chỉnh, ngưỡng {Align Tolerance})
  ↓
CHASING (chạy tới, dùng {Turn Sensitivity})
  ↓
REACHED (khi khoảng cách < {Stop Distance})
```

### **Chế độ STANDING (Đứng yên):**

```
START (đứng yên)
  ↓
Camera scan frame liên tục (mỗi 2 frame)
  ↓ (nếu thấy rác)
VERIFYING (xác nhận trong {Verify Time})
  ↓
ALIGNING (căn chỉnh, ngưỡng {Align Tolerance})
  ↓
CHASING (chạy tới, dùng {Turn Sensitivity})
  ↓
REACHED (khi khoảng cách < {Stop Distance})
```

---

## 💡 **CÔNG THỨC TẠO TỐC ĐỘ CHẠY**

Khi ở trạng thái **CHASING** (chạy tới):

```
error = target_center_x - screen_center_x
turn = error * {Turn Sensitivity}
turn = clamp(turn, -40, 40)

L = {base_speed} + turn
R = {base_speed} - turn
```

**Ví dụ:**

- Rác ở **bên phải** (error = +100px)

  - turn = 100 × 0.2 = 20
  - L = 65 + 20 = 85
  - R = 65 - 20 = 45
  - → Motor trái nhanh hơn → Robot quay sang phải

- Rác ở **bên trái** (error = -100px)
  - turn = -100 × 0.2 = -20
  - L = 65 - 20 = 45
  - R = 65 + 20 = 85
  - → Motor phải nhanh hơn → Robot quay sang trái

---

## 🎯 **KHUYẾN CÁO CHO TỪNG TÌNH HUỐNG**

### **1. Rác gần camera:**

```
Scan Speed: 70% (xoay chậm để phát hiện tốt)
Verify Time: 1.0s (dễ detect, giảm verify time)
Align Tolerance: 50px (rảng hơn, dễ căn chỉnh)
Stop Distance: 15cm (dừng sớm để an toàn)
```

### **2. Rác xa camera:**

```
Scan Speed: 90% (xoay nhanh để quét diện tích lớn)
Verify Time: 2.5s (khó detect, tăng verify time)
Align Tolerance: 40px (chặt hơn, chính xác)
Stop Distance: 10cm
```

### **3. Môi trường nhiễu (nhiều vật khác):**

```
AI Conf: 30-40% (tăng threshold phát hiện)
Verify Time: 3.0s (xác nhận kỹ hơn)
Turn Sensitivity: 0.15 (mềm hơn để tránh rung lắc)
```

### **4. Cần phản ứng nhanh:**

```
Search Delay: 0.2s (giảm delay)
Verify Time: 1.0s (tăng tốc độ verify)
Turn Sensitivity: 0.3 (cứng hơn, nhanh hơn)
```

---

## 📝 **CÁCH APPLY SETTINGS**

1. Đi đến tab **"AUTO"** trong Settings
2. Điều chỉnh các slider theo ý muốn
3. Ấn nút **"APPLY ALL SETTINGS"**
4. Kiểm tra console output:
   ```
   ⚙️  AUTO CONFIG UPDATED:
      Speed: 65, Confidence: 0.20
      Scan: 0.4s / Wait: 1.0s / Verify: 2.0s
      Scan Speed: 90%, Delay: 0.5s
      Align Tol: 40px, Turn Sens: 0.2, Stop: 10cm
   ```

---

## ⚠️ **CẢNH BÁO**

- **Turn Sensitivity quá cao** → Robot rung lắc, khó căn chỉnh
- **Stop Distance quá nhỏ** → Robot có thể va chạm target
- **Verify Time quá ngắn** → Nhiễu sẽ làm robot chạy lạc hướng
- **Scan Speed quá thấp** → Quá trình scan quá lâu

---

**Cập nhật:** 2025-12-12
