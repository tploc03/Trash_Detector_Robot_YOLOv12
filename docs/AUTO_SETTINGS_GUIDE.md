# 🎮 Hướng dẫn Chi Tiết AUTO MODE Parameters

## 📊 Sơ đồ Scan Mode (Enable Scan Mode = ON)

```
┌─────────────────────────────────────────┐
│ Bắt đầu Scan Mode                       │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ SEARCH_WAIT State    │ ◄─┐
    │ (Đứng yên chờ)       │  │
    │ Thời gian: SEARCH_DELAY │
    │ ❌ không phát hiện     │  │
    └──────────────┬────────┘  │
                   │            │
                   │ Hết timeout│
                   │            │
                   ▼            │
    ┌──────────────────────┐   │
    │ SEARCH_STEP State    │   │
    │ (Quay tìm)           │   │
    │ Thời gian: SCAN_TURN_DURATION
    │ ❓ Có tìm thấy không? │   │
    └────┬─────────────────┘   │
         │                      │
         ├─ ✅ Có: VERIFYING    │
         │                      │
         └─ ❌ Không: quay lại──┘
                                 (loop lại)

✅ Phát hiện rác:
   SEARCH_STEP/WAIT → VERIFYING → ALIGNING → CHASING → REACHED
```

---

## 🔧 Chi tiết từng Parameter

### **📍 NHÓM 1: CƠ BẢN**

#### **Speed** (0-255)

- **Giá trị mặc định**: 65
- **Ý nghĩa**: Tốc độ chạy của xe khi đi vào rác (PWM motor)
- **Ảnh hưởng**:
  - Thấp (20-40): Xe chạy chậm, chính xác hơn
  - Trung bình (60-80): Cân bằng
  - Cao (100-150): Xe chạy nhanh, rủi ro va chạm
- **Khuyến cáo**: 60-80 cho phòng trong nhà

#### **AI Conf** (10%-80%)

- **Giá trị mặc định**: 20%
- **Ý nghĩa**: Độ tin cậy của AI để coi là phát hiện đúng
- **Ảnh hưởng**:
  - Thấp (10%): Dễ phát hiện nhưng có thể sai (false positive)
  - Trung bình (20%): Cân bằng ✅
  - Cao (50%+): Khó phát hiện, có thể bỏ lỡ rác
- **Khuyến cáo**: 20% là tốt

#### **Enable Scan Mode** (Checkbox)

- **OFF** (mặc định): Xe đứng im chờ rác xuất hiện trong frame

  - Phù hợp: Phòng nhỏ, rác gần
  - Logic: `IDLE → (detect) → VERIFYING → ALIGNING → CHASING → REACHED`

- **ON**: Xe xoay tìm rác
  - Phù hợp: Phòng lớn, rác xa
  - Logic: `SEARCH_WAIT → SEARCH_STEP (xoay) → SEARCH_WAIT → ...`

---

### **📍 NHÓM 2: CHIẾN THUẬT SCAN (Step - Scan)**

#### **Step Turn** (0.1s - 5.0s)

- **Giá trị mặc định**: 0.4s
- **Ý nghĩa**: Thời gian xoay **mỗi lần**
- **Ảnh hưởng**:
  - Ngắn (0.2s): Xoay từng chút, quét kỹ nhưng lâu
  - Trung bình (0.4s): Cân bằng ✅
  - Dài (0.8s): Xoay nhiều, quét nhanh nhưng có thể bỏ lỡ
- **Công thức**: Một vòng 360° ≈ 0.4s × (360/25°) ≈ 5.8 giây

#### **Wait/Scan** (0.1s - 5.0s)

- **Giá trị mặc định**: 1.0s
- **⚠️ Hiện tại không dùng trong logic**
- **Tương lai**: Có thể dùng để tăng thời gian chờ giữa các vòng

#### **Verify** (0.1s - 5.0s)

- **Giá trị mặc định**: 2.0s
- **Ý nghĩa**: Thời gian **xác nhận** rác sau khi phát hiện
- **Lý do**: Tránh sai phát hiện khi rác lướt nhanh
- **Ảnh hưởng**:
  - Ngắn (0.5s): Nhanh nhưng dễ sai
  - Trung bình (2.0s): Cân bằng ✅
  - Dài (3-5s): Chắc chắn nhưng có thể mất mục tiêu
- **Logic**:
  ```
  Detect rác → VERIFYING (chờ 2s) →
  Nếu rác vẫn ở → ALIGNING
  Nếu mất → quay lại SEARCH
  ```

---

### **📍 NHÓM 3: CHUYỂN ĐỘNG & CẢM BIẾN (Movement - Sensor)**

#### **Scan Spd** (10% - 100%)

- **Giá trị mặc định**: 90%
- **Ý nghĩa**: Tốc độ **xoay** khi tìm kiếm (PWM motor)
- **Ảnh hưởng**:
  - Thấp (30%): Xoay chậm, quét kỹ
  - Cao (90%): Xoay nhanh, quét nhanh ✅
- **Lưu ý**: Khác với "Speed" (Speed là chạy vào, Scan Spd là xoay tìm)

#### **Search Dly** (0s - 3.0s) ⭐ **KEY PARAMETER**

- **Giá trị mặc định**: 1.5s (vừa sửa)
- **Ý nghĩa**: Thời gian **đứng yên** để AI scan trước khi xoay
- **Quy trình**:
  ```
  Đứng yên → chờ Search Dly → AI scan → không tìm thấy → xoay → đứng yên → lặp lại
  ```
- **Ảnh hưởng**:
  - Ngắn (0.3s): Xe xoay liên tục, scan kém ❌
  - Trung bình (1.5s): Cân bằng ✅ (VỪA SỬA)
  - Dài (2.5s+): Xe chờ lâu, nhưng scan kỹ

#### **Align Tol** (10-100px)

- **Giá trị mặc định**: 40px
- **Ý nghĩa**: **Sai số cho phép** để coi là căn chỉnh đúng
- **Ảnh hưởng**:
  - Nhỏ (10px): Yêu cầu chính xác, có thể lâu
  - Trung bình (40px): Cân bằng ✅
  - Lớn (80px): Chấp nhận sai, nhanh nhưng có thể va
- **Logic**:
  ```
  |target_x - center_x| < Align Tol → CHASING
  |target_x - center_x| >= Align Tol → ALIGNING (xoay)
  ```

#### **Align Speed** (10-100)

- **Giá trị mặc định**: 40
- **Ý nghĩa**: Tốc độ **xoay để căn chỉnh** khi rác lệch
- **Ảnh hưởng**:
  - Thấp (20): Xoay chậm, chính xác
  - Trung bình (40): Cân bằng ✅
  - Cao (60+): Xoay nhanh, có thể vượt
- **Khác với Scan Spd**: Scan Spd = xoay tìm, Align Speed = xoay căn chỉnh

#### **Turn Sens** (0.1 - 5.0)

- **Giá trị mặc định**: 0.2
- **Ý nghĩa**: **Độ nhạy** quay theo sai lệch của rác
- **Công thức**: `turn = error × Turn Sens`
- **Ảnh hưởng**:
  - Thấp (0.1): Quay chậm, đi lệch
  - Trung bình (0.2): Cân bằng ✅
  - Cao (0.5+): Quay nhiều, dao động
- **Ví dụ**:
  - Rác lệch 50px, Turn Sens = 0.2 → quay 10
  - Rác lệch 50px, Turn Sens = 0.5 → quay 25 (nhanh hơn)

#### **Stop Dist** (1-50cm)

- **Giá trị mặc định**: 10cm
- **Ý nghĩa**: Khoảng cách **dừng** (từ sonar FRONT)
- **Ảnh hưởng**:
  - Nhỏ (5cm): Xe chạy gần, rủi ro
  - Trung bình (10cm): Cân bằng ✅
  - Lớn (20cm+): Xe dừng xa, an toàn
- **Logic**: Khi sonar Front < Stop Dist → REACHED (dừng)

#### **Motor Balance** (0.8 - 1.2)

- **Giá trị mặc định**: 1.0
- **Ý nghĩa**: Cân bằng 2 motor trái/phải
- **Ảnh hưởng**:
  - < 1.0 (VD: 0.9): Motor trái yếu hơn → xe lệch trái ← điều chỉnh tăng
  - = 1.0: Cân bằng ✅
  - > 1.0 (VD: 1.1): Motor trái mạnh hơn → xe lệch phải ← điều chỉnh giảm
- **Cách test**: Chạy thẳng, nếu lệch thì điều chỉnh slider

#### **Lost Timeout** (0.1 - 3.0s)

- **Giá trị mặc định**: 1.0s
- **Ý nghĩa**: Thời gian **mất mục tiêu** cho phép trước khi bỏ cuộc
- **Ảnh hưởng**:
  - Ngắn (0.5s): Dễ bỏ cuộc nhanh
  - Trung bình (1.0s): Cân bằng ✅
  - Dài (2.0s): Chờ lâu, có thể giữ rác sau tường
- **Logic**:
  ```
  Nếu không thấy rác > Lost Timeout → quay lại SEARCH
  ```

---

## 📈 Workflow Chi Tiết

### **Scan Mode = OFF (Đứng chờ)**

```
START → IDLE (đứng yên)
        ↓
        Phát hiện rác (confidence > AI Conf)?
        ├─ YES → VERIFYING (chờ Verify thời gian)
        │         ├─ Vẫn thấy → ALIGNING
        │         └─ Mất → IDLE
        │
        │         ALIGNING (xoay căn chỉnh)
        │         ├─ |sai_lệch| < Align Tol → CHASING
        │         └─ |sai_lệch| >= Align Tol → xoay Align Speed
        │
        │         CHASING (chạy vào)
        │         ├─ sonar < Stop Dist → REACHED (xong!)
        │         └─ sonar >= Stop Dist → chạy với P-control
        │
        └─ NO → lặp lại (IDLE)
```

### **Scan Mode = ON (Xoay tìm)** ⭐

```
START → SEARCH_WAIT (đứng yên)
        ├─ Thời gian: SEARCH_DELAY (1.5s) ← VỪA SỬA
        ├─ Phát hiện? → YES → VERIFYING (như trên)
        └─ Không? → SEARCH_STEP (xoay)
                    │
                    ├─ Thời gian: SCAN_TURN_DURATION (0.4s)
                    ├─ Tốc độ: SCAN_SPEED (90%)
                    └─ Xoay xong → quay lại SEARCH_WAIT ← LẶP LẠI
```

---

## 🎯 Khuyến cáo cấu hình

### **Phòng nhỏ (< 5m)**

```
Speed: 50
Scan Mode: OFF (chỉ đứng chờ)
Verify: 1.0s
Align Tol: 30px
Turn Sens: 0.2
Stop Dist: 8cm
Motor Balance: 1.0
```

### **Phòng vừa (5-10m)**

```
Speed: 65
Scan Mode: ON
Search Dly: 1.5s
Step Turn: 0.4s
Scan Spd: 90%
Verify: 2.0s
Align Tol: 40px
Turn Sens: 0.2
Stop Dist: 10cm
Motor Balance: 1.0
```

### **Phòng lớn (10m+)**

```
Speed: 80
Scan Mode: ON
Search Dly: 2.0s (chờ lâu hơn để scan kỹ)
Step Turn: 0.6s (xoay lâu hơn mỗi bước)
Scan Spd: 100%
Verify: 2.5s
Align Tol: 50px
Turn Sens: 0.25
Stop Dist: 12cm
Motor Balance: 1.0
```

---

## 🔍 Debugging

| Vấn đề                 | Nguyên nhân                        | Cách fix                   |
| ---------------------- | ---------------------------------- | -------------------------- |
| Xe xoay liên tục       | Search Dly quá ngắn                | ↑ Tăng Search Dly (2.0s+)  |
| Xe bỏ lỡ rác           | Verify quá ngắn hoặc Scan Spd chậm | ↑ Tăng Verify, Scan Spd    |
| Xe quay từng nhất      | Step Turn quá ngắn                 | ↑ Tăng Step Turn (0.5s+)   |
| Xe quay quá đột ngột   | Align Speed quá cao                | ↓ Giảm Align Speed (20-30) |
| Xe lệch phải/trái      | Motor không cân bằng               | Điều chỉnh Motor Balance   |
| Xe không xoay đến được | Align Tol quá chặt                 | ↑ Tăng Align Tol (50px+)   |
| Xe va vào rác          | Stop Dist quá nhỏ                  | ↑ Tăng Stop Dist (15cm+)   |

---

## ✅ Kiểm tra nhanh

Sau khi điều chỉnh, test các điều sau:

- [ ] Bật Scan Mode → xe đứng yên trước, không xoay liên tục
- [ ] Hết ~1.5s → xe xoay 1 lần (kéo dài 0.4s)
- [ ] Sau xoay → xe đứng yên lại 1.5s (lặp)
- [ ] Đặt rác vào → xe phát hiện → verify → align → chase → stop
- [ ] Chạy thẳng → không lệch phải/trái
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
