#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "SonarManager.h" // Thêm thư viện vừa tạo

// --- CẤU HÌNH WIFI & KẾT NỐI ---
const char *ssid = "Nha Tro Kieu Trinh 2.4G"; // <--- ĐỔI LẠI
const char *password = "88888888";            // <--- ĐỔI LẠI
const int localPort = 8888;
IPAddress remoteIP; // Lưu IP của máy tính để gửi lại dữ liệu
int remotePort = 0;

// --- KHAI BÁO CHÂN MOTOR (GIỮ NGUYÊN) ---
#define ENA       \
  27;             \
  #define IN1 33; \
  #define IN2 32;
#define IN3       \
  16;             \
  #define IN4 17; \
  #define ENB 14;
// (Bạn copy lại hàm setMotor từ code cũ vào đây nhé, tôi viết tắt cho gọn)

// --- KHAI BÁO CẢM BIẾN (Theo sơ đồ của bạn) ---
SonarManager sonarFront(18, 34); // Trig 18, Echo 34
SonarManager sonarLeft(23, 35);  // Trig 23, Echo 35
SonarManager sonarRight(5, 36);  // Trig 5,  Echo 36

WiFiUDP udp;
char packetBuffer[255];
unsigned long lastSensorTime = 0;

// --- COPY HÀM setMotor CŨ VÀO ĐÂY ---
void setMotor(int pinIn1, int pinIn2, int pinEn, int speed)
{
  if (speed > 0)
  {
    digitalWrite(pinIn1, HIGH);
    digitalWrite(pinIn2, LOW);
  }
  else if (speed < 0)
  {
    digitalWrite(pinIn1, LOW);
    digitalWrite(pinIn2, HIGH);
    speed = -speed;
  }
  else
  {
    digitalWrite(pinIn1, LOW);
    digitalWrite(pinIn2, LOW);
  }
  if (speed > 255)
    speed = 255;
  analogWrite(pinEn, speed);
}

void setup()
{
  Serial.begin(115200);

  // Setup Motor
  pinMode(27, OUTPUT);
  pinMode(33, OUTPUT);
  pinMode(32, OUTPUT);
  pinMode(14, OUTPUT);
  pinMode(16, OUTPUT);
  pinMode(17, OUTPUT);

  // Setup Sensor
  sonarFront.begin();
  sonarLeft.begin();
  sonarRight.begin();

  // Wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
    delay(500);
  Serial.println(WiFi.localIP());
  udp.begin(localPort);
}

void loop()
{
  // 1. NHẬN LỆNH ĐIỀU KHIỂN (Code cũ)
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    remoteIP = udp.remoteIP(); // Lưu lại IP máy tính để gửi trả
    remotePort = udp.remotePort();

    int len = udp.read(packetBuffer, 255);
    if (len > 0)
      packetBuffer[len] = 0;

    StaticJsonDocument<200> doc;
    deserializeJson(doc, packetBuffer);
    if (doc["cmd"] == "MOVE")
    {
      setMotor(33, 32, 27, doc["L"]); // Cập nhật lại chân cho đúng
      setMotor(16, 17, 14, doc["R"]);
    }
  }

  // 2. GỬI DỮ LIỆU CẢM BIẾN VỀ MÁY TÍNH (Mỗi 100ms)
  if (millis() - lastSensorTime > 200)
  { // Tăng lên 200ms để đỡ spam
    lastSensorTime = millis();

    // Đọc tuần tự và CÓ NGHỈ để tránh nhiễu chéo (Crosstalk)
    float dFront = sonarFront.getDistance();
    delay(15); // Chờ 15ms cho sóng trước tắt hẳn

    float dLeft = sonarLeft.getDistance();
    delay(15);

    float dRight = sonarRight.getDistance();

    // Gói tin JSON gửi đi
    StaticJsonDocument<200> docOut;
    docOut["F"] = (int)dFront;
    docOut["L"] = (int)dLeft;
    docOut["R"] = (int)dRight;

    char outputBuffer[200];
    serializeJson(docOut, outputBuffer);

    if (remotePort > 0)
    { // Chỉ gửi khi đã biết IP máy tính
      udp.beginPacket(remoteIP, remotePort);
      udp.write((const uint8_t *)outputBuffer, strlen(outputBuffer));
      udp.endPacket();
    }
  }
}