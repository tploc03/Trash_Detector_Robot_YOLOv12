# 🤖 Trash Detection Robot - Giải Thích Code Overview

## 📁 Cấu Trúc Dự Án

```
TrashDetectionCar/
├── esp32_cam-firmware/       ← Camera server (stream video)
├── esp32-firmware/           ← Robot control (motor + sonar + voice)
└── app/src/                  ← PC application (PyQt6)
    ├── main.py              ← Main app window & control loop
    ├── robot_controller.py   ← AI state machine (auto mode)
    ├── video.py             ← Video stream + YOLO AI
    ├── network.py           ← WiFi UDP communication
    ├── ui/                  ← UI panels & widgets
    ├── styles.py            ← CSS-like styling
    └── sound_manager.py      ← Audio playback
```

---

## 🔌 **PHẦN 1: ESP32 CAM FIRMWARE** (`esp32_cam-firmware/src/main.cpp`)

### **Mục đích:** Streaming video từ camera OV2640 qua WiFi

### **Các thành phần chính:**

#### 1️⃣ **Cấu hình Camera**

```cpp
const char *ssid = "Tề Tĩnh Xuân";    // WiFi name
const char *password = "123454321";    // WiFi password

// Định nghĩa GPIO pins của camera (do ESP32-CAM sử dụng các pin cụ thể)
#define PWDN_GPIO_NUM 32      // Power down
#define XCLK_GPIO_NUM 0       // Clock
#define SIOD_GPIO_NUM 26      // I2C data
#define SIOC_GPIO_NUM 27      // I2C clock
#define Y9_GPIO_NUM 35        // Camera data pins
// ... (nhiều pin khác)
#define FLASH_GPIO_NUM 4      // Flash LED
```

#### 2️⃣ **Flash Control**

```cpp
void setFlash(bool state)
{
  flash_state = state;
  digitalWrite(FLASH_GPIO_NUM, state ? HIGH : LOW);
  // Toggle flash LED khi bật/tắt
}
```

#### 3️⃣ **Stream Handler (HTTP Server)**

```cpp
static esp_err_t stream_handler(httpd_req_t *req)
{
  // Lặp vô hạn, capture frame → encode JPEG → gửi qua HTTP streaming
  while (true)
  {
    fb = esp_camera_fb_get();              // Lấy frame từ camera

    // Chuyển đổi sang JPEG nếu cần
    frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);

    // Gửi frame qua HTTP (multipart streaming)
    httpd_resp_send_chunk(req, _STREAM_BOUNDARY, ...);
    httpd_resp_send_chunk(req, _STREAM_PART, ...);
    httpd_resp_send_chunk(req, _jpg_buf, _jpg_buf_len);
  }
}
```

#### 4️⃣ **Control Handler (Flash toggle)**

```cpp
// GET /control?var=flash&val=1
// Người dùng gửi request để bật/tắt flash
if (GET parameter "flash" = 1) → setFlash(true)
```

### **Flow:**

```
Boot → WiFi connect → Start HTTP server
        ↓
Client (app) connect: GET http://10.230.248.174:81/stream
        ↓
Loop: Capture JPEG → Send frame → Repeat @ ~30 FPS
        ↓
If GET /control?var=flash&val=1 → setFlash(true)
```

---

## 🎮 **PHẦN 2: ESP32 DEVKIT FIRMWARE** (`esp32-firmware/src/main.cpp`)

### **Mục đích:** Điều khiển motor, sonar, và voice playback

### **Các thành phần chính:**

#### 1️⃣ **Motor Control**

```cpp
#define ENA 27    // Left motor speed (PWM)
#define IN1 33    // Left motor direction 1
#define IN2 32    // Left motor direction 2
#define ENB 14    // Right motor speed (PWM)
#define IN3 16    // Right motor direction 1
#define IN4 17    // Right motor direction 2

void setMotor(int speedL, int speedR)
{
  // speedL, speedR: -255 to 255
  // Nếu speedL > 0 → IN1=HIGH, IN2=LOW (tiến)
  // Nếu speedL < 0 → IN1=LOW, IN2=HIGH (lùi)
  // analogWrite(ENA, |speedL|) → điều chỉnh PWM (0-255)

  // Tương tự cho right motor
}
```

#### 2️⃣ **Sonar Sensor Management** (`SonarManager.h`)

```cpp
class SonarManager
{
  int trigPin, echoPin;

public:
  int getDistance()
  {
    // Gửi pulse 10µs → đo thời gian echo
    // Distance = (echo_time * speed_of_sound) / 2
    // Trả về distance in cm
  }
};

// 3 sonar sensors
SonarManager sonarFront(18, 34);  // Front
SonarManager sonarLeft(23, 35);   // Left
SonarManager sonarRight(5, 36);   // Right
```

#### 3️⃣ **WiFi UDP Communication**

```cpp
WiFiUDP udp;
const int localPort = 8888;

// Nhận command từ PC (app)
// Format JSON: {"cmd": "MOVE", "L": 65, "R": 65}

void onReceiveCommand(JSON payload)
{
  if (cmd == "MOVE")
    setMotor(L, R);  // Di chuyển
  else if (cmd == "STOP")
    setMotor(0, 0);  // Dừng
  else if (cmd == "PLAY")
    playSound(soundName);  // Phát âm thanh
}
```

#### 4️⃣ **Audio Playback**

```cpp
AudioGeneratorWAV *wav;
AudioFileSourceSPIFFS *file;  // Từ SPIFFS (built-in storage)
AudioOutputI2S *out;          // I2S speaker

void playSound(String filename)
{
  file = new AudioFileSourceSPIFFS("/startup.wav");
  wav = new AudioGeneratorWAV();
  wav->begin(file, out);

  // Chạy trong task riêng không block main loop
}
```

#### 5️⃣ **Main Loop**

```cpp
void loop()
{
  // Đọc sonar every ~100ms
  sharedDistF = sonarFront.getDistance();
  sharedDistL = sonarLeft.getDistance();
  sharedDistR = sonarRight.getDistance();

  // Kiểm tra WiFi command
  // Nếu có: parse JSON → execute command

  // Audio processing
  if (wav && wav->isRunning()) wav->loop();

  delay(50);  // ~20 Hz loop
}
```

### **Flow:**

```
Boot → WiFi connect → UDP bind port 8888
        ↓
Loop:
  ├─ Read sonar F/L/R every 100ms
  ├─ Listen UDP port for command
  ├─ Execute: setMotor() / playSound()
  └─ Process audio
```

---

## 💻 **PHẦN 3: PC APPLICATION** (`app/src/`)

### **Mục đích:** UI + AI detection + Robot control logic

---

## **3.1 Main App** (`main.py`)

### **Class: RobotApp (QMainWindow)**

**Nhiệm vụ:** Cửa sổ chính, quản lý toàn bộ flow

#### **Constructor (`__init__`)**

```python
def __init__(self):
    # 1. Tạo UI
    self.setup_ui()

    # 2. Tạo controller
    self.robot = RobotController(base_speed=65, screen_width=640)

    # 3. Khởi động threads
    self.net_thread = NetworkThread("10.230.248.1")      # UDP to ESP32
    self.video_thread = VideoThread(camera_url, model)   # Stream + AI

    # 4. Timers
    self.control_timer = QTimer()          # Manual mode (100ms)
    self.control_timer.timeout.connect(self.send_manual_command)

    self.auto_timer = QTimer()             # Auto mode (50ms)
    self.auto_timer.timeout.connect(self.auto_control_loop)
```

#### **UI Setup (`setup_ui`)**

```
┌─────────────────────────────────────────┐
│          LEFT PANEL (65%)                │  RIGHT PANEL (35%)
├────────────────────────┬────────────────┤
│ FPS / Ping Info        │ Radar (SONAR)  │
├────────────────────────┤────────────────┤
│                        │ Tabs:          │
│   Video Stream         │ ├─ OPERATION   │
│   (640x480)            │ │  ├─ Mode btn│
│                        │ │  ├─ Manual   │
│                        │ │  └─ Auto info│
│                        │ └─ SETTINGS    │
│                        │    ├─ CONNECT  │
│  Info Bar              │    ├─ MANUAL   │
│  (System status)       │    └─ AUTO     │
└────────────────────────┴────────────────┘
```

#### **Manual Mode (`send_manual_command`)**

```python
def send_manual_command():
  # Mỗi 100ms:
  #   1. Đọc keys_pressed (W/A/S/D)
  #   2. Tính L, R speed
  #   3. Gửi {"cmd": "MOVE", "L": L, "R": R} tới ESP32

  keys = self.keys_pressed
  if Key_W in keys: L += speed; R += speed  # Forward
  if Key_A in keys: L -= speed              # Left
  if Key_D in keys: R -= speed              # Right
  if Key_S in keys: L -= speed; R -= speed  # Backward

  self.net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})
```

#### **Auto Mode (`auto_control_loop`)**

```python
def auto_control_loop():
  # Mỗi 50ms (20 Hz):

  # 1. Cập nhật cảm biến
  robot.update_sensors(front_dist, left_dist, right_dist)

  # 2. AI detection callback đã gọi robot.update_detection(detections)

  # 3. Compute control từ state machine
  L, R, info = robot.compute_control()

  # 4. Gửi command
  net_thread.send_command({"cmd": "MOVE", "L": L, "R": R})

  # 5. Update UI
  lbl_info.setText(info)
```

#### **Mode Switching (`set_mode`)**

```python
if auto:  # Bật Auto Mode
  control_timer.stop()      # Tắt manual timer
  video_thread.set_ai_mode(True)   # Bật AI detection
  robot.enable_search(spin_enabled) # Khởi tạo search
  auto_timer.start(50)      # Bắt đầu auto loop
else:  # Bật Manual Mode
  auto_timer.stop()
  control_timer.start(100)  # Bắt đầu manual timer
  robot.emergency_stop()    # Reset state
```

---

## **3.2 Robot Controller** (`robot_controller.py`)

### **Class: RobotController**

**Mục đích:** State machine + logic điều khiển tự động

#### **States:**

```
IDLE ──(detect)──> VERIFYING ──(2s)──> ALIGNING ──(aligned)──> CHASING ──(close)──> REACHED
 ↑                                                                           │
 └───────────────────── LOST ←───────────────────────────────────────────────┘

SEARCH_WAIT ──(delay 0.5s)──> SEARCH_STEP ──(rotate)──> SEARCH_WAIT (repeat)
```

#### **Main Function: `compute_control()`**

```python
def compute_control():
  now = time.time()

  # 1. Emergency stop: dist_front < 10cm
  if dist_front < STOP_DISTANCE:
    return 0, 0, "REACHED"

  # 2. Lost target timeout: > 1.0s không thấy
  if now - last_seen_time > 1.0:
    if search_enabled: state = SEARCH_WAIT
    else: state = IDLE
    return 0, 0, "Lost Target"

  # 3. State machine
  if state == SEARCH_STEP:
    rotate 90° (L=-90, R=90) @ SCAN_SPEED

  elif state == SEARCH_WAIT:
    wait 1.0s, then rotate

  elif state == VERIFYING:
    wait 2.0s, then ALIGNING

  elif state == ALIGNING:
    # P-control: error = target_x - center_x (320)
    if |error| < 40px: → CHASING
    else: turn left/right @ 40 PWM

  elif state == CHASING:
    # P-control turn
    turn = error * 0.2  # TURN_SENSITIVITY
    L = base_speed + turn
    R = base_speed - turn
    forward to trash
```

#### **AI Detection Callback**

```python
def update_detection(detections):
  if not detections: return

  best = max by confidence

  # 1. Filter: confidence < 0.2 → skip
  if confidence < threshold: return

  # 2. Filter: x outside ±40px tolerance → skip
  if |x - 320| > 40: return

  # 3. Transition
  if state in [IDLE, SEARCH, SEARCH_WAIT]:
    state = VERIFYING
    first_seen_time = now
```

---

## **3.3 Video & AI** (`video.py`)

### **Class: VideoThread (QThread)**

**Mục đích:** Stream video từ camera + run YOLO AI detection

#### **Main Loop**

```python
def run():
  while True:
    # 1. Capture frame từ stream
    response = requests.get(camera_url)  # MJPEG stream
    frame = decode_jpeg()

    # 2. Display
    emit change_pixmap_signal(frame)  # Update UI

    # 3. AI Detection (mỗi 2 frame)
    if frame_count % 2 == 0:
      detections = self.model(frame)  # YOLO

      # Parse results
      for detection in detections:
        label = detection.names[int(detection.cls)]
        conf = float(detection.conf)
        x_center = int(detection.xywh[0][0])

        results.append({
          'label': label,
          'conf': conf,
          'center_x': x_center
        })

      # Emit signal
      emit ai_results_signal({'detections': results})
```

#### **AI Mode Toggle**

```python
def set_ai_mode(enabled):
  if enabled:
    # Load YOLO model lần đầu
    self.model = YOLO("app/models/best.pt")
    fix_aattn_compat(self.model)  # Fix attention bug
    ai_enabled = True
  else:
    ai_enabled = False  # Stop detection
```

---

## **3.4 Network Communication** (`network.py`)

### **Class: NetworkThread (QThread)**

**Mục đích:** WiFi UDP communication với ESP32

#### **Flow**

```python
def __init__(ip):
  self.socket = socket(AF_INET, SOCK_DGRAM)
  self.socket.bind(("0.0.0.0", 9999))  # Listen on port 9999
  self.target_ip = ip  # 10.230.248.1

def run():
  while True:
    # 1. Receive data từ ESP32 (sonar)
    data, addr = socket.recvfrom(1024)
    # Format: {"F": 50, "L": 30, "R": 45}

    emit data_received.signal(data)

    # 2. Receive ping response
    # ...

def send_command(cmd):
  # cmd: {"cmd": "MOVE", "L": 65, "R": 65}
  json_str = json.dumps(cmd)
  socket.sendto(json_str, (target_ip, 8888))
```

---

## **3.5 UI Components** (`ui/panels.py` + `ui/widgets.py`)

### **Panels:**

1. **ManualPanel** → W/A/S/D keyboard control buttons
2. **AutoPanel** → Trash detection history list
3. **SettingsPanel** → 3 tabs:
   - CONNECT: Robot IP, Camera URL, Flash toggle
   - MANUAL: Speed slider
   - AUTO: All AI parameters (confidence, timeout, scan speed, etc.)

### **Widgets:**

1. **SensorBox** → Display sonar readings (F/L/R) with progress bars
2. **VisualKey** → W/A/S/D buttons with visual feedback
3. **LoadingOverlay** → Loading dialog

---

## **3.6 Sound Manager** (`sound_manager.py`)

**Mục đích:** Phát âm thanh (startup, detection, done)

```python
def play_startup():
  # Gửi {"cmd": "PLAY", "sound": "startup.wav"} tới ESP32

def play_trash_detect(label):
  # Phát âm thanh "trash_detected.wav" theo loại rác
```

---

## 🔗 **COMMUNICATION FLOW**

### **Manual Mode:**

```
User keys (W/A/S/D)
    ↓
PC app: compute L, R speed
    ↓
Send UDP: {"cmd": "MOVE", "L": 65, "R": 65}
    ↓
ESP32: receive → setMotor(65, 65)
    ↓
Motor move
```

### **Auto Mode (Search + Detection):**

```
PC app: Bật AI mode
    ↓
VideoThread: Capture frame mỗi frame, AI mỗi 2 frame
    ↓
Detection: Nếu thấy rác → emit signal → robot.update_detection()
    ↓
RobotController state machine: IDLE → VERIFYING → ALIGNING → CHASING → REACHED
    ↓
auto_control_loop: Mỗi 50ms compute L, R từ state
    ↓
Send UDP: {"cmd": "MOVE", "L": x, "R": y}
    ↓
ESP32: setMotor(x, y)
    ↓
Motor move
    ↓
Sonar: Send UDP back: {"F": dist, "L": left, "R": right}
    ↓
PC app: update_sensors() → robot.update_sensors()
    ↓
Check: dist < 10cm? → REACHED → Dialog → Quay về Manual
```

---

## 📊 **TIMING & FREQUENCIES**

| Component         | Frequency   | Notes                |
| ----------------- | ----------- | -------------------- |
| Manual command    | 100ms       | 10 Hz                |
| Auto control loop | 50ms        | 20 Hz                |
| Video stream      | ~30 FPS     | ESP32 CAM            |
| AI detection      | Mỗi 2 frame | ~15 FPS detection    |
| Sonar update      | ~100ms      | Reading từ 3 sensors |
| Keyboard input    | Event-based | Real-time            |

---

## ⚙️ **KEY ALGORITHMS**

### **1. Auto Mode - P Control (Proportional)**

```python
# Aligning & Chasing state
error = target_x - center_x  # -320 to +320
turn = error * TURN_SENSITIVITY  # -0.5 to +0.5
turn = clamp(turn, -40, 40)

L = base_speed + turn
R = base_speed - turn
# Nếu rác bên phải (error > 0) → L > R → quay phải
# Nếu rác bên trái (error < 0) → R > L → quay trái
```

### **2. State Transition Rules**

```
VERIFYING → ALIGNING: duration >= CONFIRM_TIME (2.0s)
ALIGNING → CHASING: |error| < ALIGN_TOLERANCE (40px)
CHASING → REACHED: dist_front < STOP_DISTANCE (10cm)
Any → SEARCH_WAIT: lost_duration > LOST_TARGET_TIMEOUT (1.0s)
```

### **3. Detection Filtering**

```
Confidence filter: conf >= threshold (0.2)
Tolerance filter: |x - 320| <= 40px (center-biased)
```

---

## 🎯 **SUMMARY**

| Layer        | Component       | Role                                     |
| ------------ | --------------- | ---------------------------------------- |
| **Hardware** | ESP32-CAM       | Video streaming                          |
|              | ESP32-DevKit    | Motor control + sonar                    |
| **Firmware** | esp32_cam       | HTTP server (30 FPS)                     |
|              | esp32-devkit    | UDP command receive, motor/sonar control |
| **Software** | VideoThread     | Video + AI (YOLO)                        |
|              | NetworkThread   | UDP communication                        |
|              | RobotController | State machine logic                      |
|              | RobotApp (Main) | Orchestrate threads + UI                 |
|              | UI              | Manual/Auto mode switching               |

---

**Đó là tóm tắt toàn bộ system! 🚀**
