#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

#include "SPIFFS.h"
#include "AudioFileSourceSPIFFS.h"
#include "AudioGeneratorWAV.h"
#include "AudioOutputI2S.h"

#include "SonarManager.h"

const char *ssid = "Nha Tro Kieu Trinh 2.4G";
const char *password = "88888888";
const int localPort = 8888;

#define ENA 27
#define IN1 33
#define IN2 32
#define IN3 16
#define IN4 17
#define ENB 14

// Audio
AudioGeneratorWAV *wav;
AudioFileSourceSPIFFS *file;
AudioOutputI2S *out;

// Sensors (Trig, Echo)
SonarManager sonarFront(18, 34);
SonarManager sonarLeft(23, 35);
SonarManager sonarRight(5, 36);

// Network
WiFiUDP udp;
char packetBuffer[512];
unsigned long lastSensorTime = 0;
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
  if (wav && wav->isRunning())
  {
    wav->stop();
  }

  file = new AudioFileSourceSPIFFS(filename);
  if (!file->isOpen())
  {
    Serial.printf("Không tìm thấy file: %s\n", filename);
    delete file;
    return;
  }

  Serial.printf("Đang phát: %s\n", filename);
  wav = new AudioGeneratorWAV();
  wav->begin(file, out);
}

void setup()
{
  Serial.begin(115200);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  setMotor(0, 0);

  sonarFront.begin();
  sonarLeft.begin();
  sonarRight.begin();

  if (!SPIFFS.begin(true))
  {
    return;
  }

  out = new AudioOutputI2S(0, 1);
  out->SetOutputModeMono(true);
  out->SetGain(0.5);

  Serial.print("Connecting Wifi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected: " + WiFi.localIP().toString());
  udp.begin(localPort);

  playSound("/startup.wav");
}

void loop()
{
  if (wav && wav->isRunning())
  {
    if (!wav->loop())
    {
      wav->stop();
      delete wav;
      wav = NULL;
      delete file;
      file = NULL;
    }
  }

  int packetSize = udp.parsePacket();
  if (packetSize)
  {
    int len = udp.read(packetBuffer, 511);
    if (len > 0)
      packetBuffer[len] = 0;

    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, packetBuffer);

    if (!error)
    {
      lastCmdTime = millis();
      const char *cmd = doc["cmd"];

      if (strcmp(cmd, "MOVE") == 0)
      {
        int l = doc["L"];
        int r = doc["R"];
        setMotor(l, r);
      }
      else if (strcmp(cmd, "SPEAK") == 0)
      {
        const char *fname = doc["file"];
        playSound(fname);
      }
      else if (strcmp(cmd, "STOP") == 0)
      {
        setMotor(0, 0);
      }
    }
  }

  if (millis() - lastCmdTime > 2000)
  {
    setMotor(0, 0);
  }

  if (millis() - lastSensorTime > 150)
  {
    lastSensorTime = millis();

    float dF = sonarFront.getDistance();
    float dL = sonarLeft.getDistance();
    float dR = sonarRight.getDistance();

    StaticJsonDocument<200> docOut;
    docOut["F"] = (int)dF;
    docOut["L"] = (int)dL;
    docOut["R"] = (int)dR;

    char outputBuffer[200];
    serializeJson(docOut, outputBuffer);

    if (udp.remotePort() > 0)
    {
      udp.beginPacket(udp.remoteIP(), udp.remotePort());
      udp.write((const uint8_t *)outputBuffer, strlen(outputBuffer));
      udp.endPacket();
    }
  }
}