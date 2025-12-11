#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#include "SPIFFS.h"
#include "AudioFileSourceSPIFFS.h"
#include "AudioGeneratorWAV.h"
#include "AudioOutputI2S.h"

#include "SonarManager.h"

const char *ssid = "Tề Tĩnh Xuân";
const char *password = "123454321";
const int localPort = 8888;

#define ENA 27
#define IN1 33
#define IN2 32
#define IN3 16
#define IN4 17
#define ENB 14

AudioGeneratorWAV *wav;
AudioFileSourceSPIFFS *file;
AudioOutputI2S *out;
bool isSpeaking = false;

// Sonar Sensors
SonarManager sonarFront(18, 34);
SonarManager sonarLeft(23, 35);
SonarManager sonarRight(5, 36);

volatile int sharedDistF = 0;
volatile int sharedDistL = 0;
volatile int sharedDistR = 0;

WiFiUDP udp;
char packetBuffer[512];
unsigned long lastCmdTime = 0;

void setMotor(int speedL, int speedR)
{
  if (speedL > 0)
  {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  }
  else if (speedL < 0)
  {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    speedL = -speedL;
  }
  else
  {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }

  if (speedR > 0)
  {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }
  else if (speedR < 0)
  {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    speedR = -speedR;
  }
  else
  {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
  }

  analogWrite(ENA, constrain(speedL, 0, 255));
  analogWrite(ENB, constrain(speedR, 0, 255));
}

void playSound(const char *filename)
{
  Serial.printf("Request: %s\n", filename);

  // Stop current playback
  if (wav && wav->isRunning())
  {
    Serial.println("Stopping current playback");
    wav->stop();
    delay(50);
    isSpeaking = false;
  }

  // Cleanup
  if (file)
  {
    file->close();
    delete file;
    file = NULL;
  }

  delay(50); // delay between stop and play

  String fullPath = filename;
  if (!fullPath.startsWith("/"))
    fullPath = "/" + fullPath;

  Serial.printf("Opening: %s\n", fullPath.c_str());
  file = new AudioFileSourceSPIFFS(fullPath.c_str());

  if (!file || !file->isOpen())
  {
    Serial.printf("Failed to open: %s\n", fullPath.c_str());
    if (file)
    {
      file->close();
      delete file;
      file = NULL;
    }
    return;
  }

  Serial.println("Creating WAV decoder");
  if (!wav)
    wav = new AudioGeneratorWAV();

  Serial.println("Starting playback");
  if (wav->begin(file, out))
  {
    isSpeaking = true;
    Serial.printf("Playing: %s\n", fullPath.c_str());
  }
  else
  {
    Serial.println("Failed to begin playback");
    isSpeaking = false;
  }
}

void TaskSensors(void *pvParameters)
{
  (void)pvParameters;
  for (;;)
  {
    sharedDistF = (int)sonarFront.getDistance();
    sharedDistL = (int)sonarLeft.getDistance();
    sharedDistR = (int)sonarRight.getDistance();
    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void setup()
{
  Serial.begin(115200);

  // Motor Setup
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  setMotor(0, 0);

  // Sensor Setup
  sonarFront.begin();
  sonarLeft.begin();
  sonarRight.begin();

  // Audio Setup
  if (!SPIFFS.begin(true))
  {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  Serial.println("Initializing DAC audio output (Internal)");
  out = new AudioOutputI2S(0, 1);
  out->SetOutputModeMono(true);
  out->SetGain(1);
  Serial.println("DAC initialized");

  // WiFi Setup
  Serial.print("Connecting WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20)
  {
    delay(500);
    Serial.print(".");
    retry++;
  }
  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("\WiFi Connected: " + WiFi.localIP().toString());
    udp.begin(localPort);
  }

  xTaskCreatePinnedToCore(TaskSensors, "Sensors", 4096, NULL, 1, NULL, 0);

  playSound("/startup.wav");
}

void loop()
{
  // Audio Loop
  if (wav && wav->isRunning())
  {
    if (!wav->loop())
    {
      wav->stop();
      isSpeaking = false;
    }
  }

  // WiFi Reconnect
  if (WiFi.status() != WL_CONNECTED)
  {
    static unsigned long lastWifiCheck = 0;
    if (millis() - lastWifiCheck > 5000 && !isSpeaking)
    {
      lastWifiCheck = millis();
      WiFi.reconnect();
    }
    return;
  }

  // UDP Receive
  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    int len = udp.read(packetBuffer, 511);
    if (len > 0)
      packetBuffer[len] = 0;

    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, packetBuffer);

    if (!error)
    {
      lastCmdTime = millis();
      const char *cmd = doc["cmd"];

      if (strcmp(cmd, "MOVE") == 0)
        setMotor(doc["L"], doc["R"]);
      else if (strcmp(cmd, "SPEAK") == 0)
        playSound(doc["file"]);
      else if (strcmp(cmd, "STOP") == 0)
        setMotor(0, 0);
    }
  }

  // UDP Send Telemetry (Sensors)
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 150)
  {
    lastSendTime = millis();
    StaticJsonDocument<128> docOut;
    docOut["F"] = sharedDistF;
    docOut["L"] = sharedDistL;
    docOut["R"] = sharedDistR;

    char outputBuffer[128];
    serializeJson(docOut, outputBuffer);

    if (udp.remoteIP() != IPAddress(0, 0, 0, 0) && udp.remotePort() > 0)
    {
      udp.beginPacket(udp.remoteIP(), udp.remotePort());
      udp.write((const uint8_t *)outputBuffer, strlen(outputBuffer));
      udp.endPacket();
    }
  }

  // Failsafe
  if (millis() - lastCmdTime > 500)
    setMotor(0, 0);
}