#include "SonarManager.h"

SonarManager::SonarManager(int trig, int echo)
{
    trigPin = trig;
    echoPin = echo;
}

void SonarManager::begin()
{
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    digitalWrite(trigPin, LOW);
}

float SonarManager::getDistance()
{
    // 1. Tạo xung Trigger ngắn gọn
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    // 2. Đọc xung Echo với Timeout ngắn (5800us ~ 1 mét)
    // Nếu quá 1m coi như không có vật cản để tiết kiệm thời gian CPU
    long duration = pulseIn(echoPin, HIGH, 5800);

    if (duration == 0)
        return 100; // Trả về 100cm nếu không thấy gì (an toàn)

    return duration * 0.034 / 2;
}