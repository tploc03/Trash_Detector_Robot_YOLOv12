# 🤖 Auto Mode Guide - Chế Độ Tự Động

## 📋 Hai Chế Độ Auto Mode

### 1️⃣ **SEARCH ROTATION Mode** (Robot Xoay Tìm Kiếm)

- **Bật "Spin/Quay"** ✅
- Robot sẽ quay 360° để tìm rác
- Khi phát hiện rác → Căn chỉnh → Chạy tới

**Các thông số:**

- `SCAN_TURN_DURATION = 0.4s` - Quay 0.4 giây rồi dừng
- `SCAN_WAIT_DURATION = 1.0s` - Đợi 1 giây rồi quay tiếp
- `SCAN_SPEED = 90` - Tốc độ xoay 90%
- `SEARCH_DELAY = 0.5s` - **Delay 0.5s trước khi bắt đầu quay** (tránh quay vội vàng)
- `CONFIRM_TIME = 2.0s` - Cần thấy rác liên tục 2 giây mới xác nhận

**Quy trình:**

```
IDLE (0.5s delay) → SEARCH_WAIT → SEARCH_STEP (quay) → VERIFYING (2s) → ALIGNING → CHASING → REACHED
```

---

### 2️⃣ **STANDING DETECTION Mode** (Robot Đứng Yên - ĐÂY LÀ TÙY CHỌN MỚI)

- **Không bật "Spin/Quay"** ❌
- Robot đứng yên ở vị trí hiện tại
- Camera liên tục quét frame hiện tại
- **Nếu thấy rác trong khung hình → Tự động căn chỉnh + chạy tới**

**Các thông số:**

- `CONFIRM_TIME = 2.0s` - Cần thấy rác liên tục 2 giây mới xác nhận
- `ALIGN_TOLERANCE = 40px` - Ngưỡng căn chỉnh (±40 pixel từ tâm)
- `TURN_SENSITIVITY = 0.2` - Độ nhạy góc xoay (P-Control)
- Detection chạy **mỗi 2 frame** (tốc độ cao)

**Quy trình:**

```
IDLE (đứng yên) + Camera scan → Phát hiện rác → VERIFYING (2s) → ALIGNING → CHASING → REACHED
```

---

## 🎯 Cách Sử Dụng

### **Chế độ Search Rotation:**

1. Bật "AUTO MODE"
2. ✅ **Check** "Spin/Quay" checkbox
3. Robot sẽ:
   - Đợi 0.5 giây chuẩn bị
   - Bắt đầu quay 360° để tìm rác
   - Khi phát hiện → Căn chỉnh + chạy tới

### **Chế độ Standing Detection:**

1. Bật "AUTO MODE"
2. ❌ **Không check** "Spin/Quay" checkbox
3. Robot sẽ:
   - Đứng yên ở vị trí hiện tại
   - Camera liên tục tìm rác
   - Khi phát hiện rác trong frame → Căn chỉnh + chạy tới

---

## 🔧 Tối Ưu Hóa

### **Detection Speed:**

- `process_every_n_frames = 2` → Chạy AI mỗi 2 frame (nhanh hơn)
- Nếu muốn nhanh hơn nữa, thay đổi trong `video.py`

### **Confidence Threshold:**

- `conf_thres = 0.25` (25%) - Mặc định
- Có thể điều chỉnh ở Settings Tab
- **Khuyến cáo:** Giữ ≥ 0.20 để tránh nhiễu

### **Verify Time:**

- `CONFIRM_TIME = 2.0s` - Cần thấy rác 2 giây mới xác nhận
- **Auto-standing:** Có thể giảm xuống 1.0s để phản ứng nhanh
- **Search mode:** Nên giữ 2.0s để tránh false positive

---

## 📊 Console Output

Khi chạy, bạn sẽ thấy:

```
🤖 AUTO MODE: STANDING DETECTION - Robot waits for trash in current view
🎯 AI Detection ENABLED - Running on every 2 frames
🎯 Auto Mode - Received 1 detections
   - plastic (0.85) at x=320
👀 Spotted plastic (0.85) at x=320 -> Verifying...
⏳ Verifying (1.2s)...
🎯 CONFIRMED!
🎯 Aligning Right...
🚀 LOCKED! CHARGING...
🔥 CHASING! Dist: 45cm
✅ REACHED: plastic
```

---

## ⚠️ Troubleshooting

### **Model không detect rác**

- Kiểm tra: "AUTO MODE ACTIVE" có sáng lên không?
- Xem Console: Có `"🎯 AI Detection ENABLED"` không?
- Thử: Gần camera hơn (phải nhìn thấy rác trong frame)

### **Phát hiện nhưng không xác nhận**

- `CONFIRM_TIME` quá lâu → Giảm xuống 1.0s
- Rác có đang move hay không? → Giữ rác yên lặng

### **Robot không chạy tới được**

- Kiểm tra: Sonar (khoảng cách) có chuẩn không?
- Thử: Giảm `base_speed` từ 65 xuống 50

### **Robot xoay quá nhanh (Search mode)**

- Tăng `SEARCH_DELAY` từ 0.5s lên 1.0s
- Giảm `SCAN_SPEED` từ 90 xuống 70

---

## 💡 Tips & Tricks

1. **Bắt đầu bằng Standing Detection:**

   - Dễ test hơn vì không cần quay
   - Tốc độ phản ứng nhanh

2. **Sử dụng cả 2 chế độ:**

   - Standing: Tìm rác gần
   - Search: Tìm rác xa

3. **Điều chỉnh confidence:**

   - Thấp (0.20): Dễ detect nhưng nhiễu
   - Cao (0.40): Ít nhiễu nhưng dễ miss

4. **Kiểm tra FPS:**
   - ≥ 10 FPS: Tốt
   - &lt; 5 FPS: Giảm resolution hoặc process_every_n_frames

---

**Cập nhật lần cuối:** 2025-12-12
