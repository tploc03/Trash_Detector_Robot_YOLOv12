#include "SonarManager.h"
#include <algorithm>
#include <vector>

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

float SonarManager::readRaw()
{
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    // TỐI ƯU: Giảm Timeout xuống 12000us (~200cm/2m)
    // Giúp xe không bị khựng và Loa không bị rè khi không thấy vật cản
    long duration = pulseIn(echoPin, HIGH, 12000);

    if (duration == 0)
        return 0;
    return duration * 0.034 / 2;
}

float SonarManager::getDistance()
{
    std::vector<float> samples;

    // Giảm xuống lấy 3 mẫu là đủ cho robot di động (5 mẫu hơi thừa gây delay)
    for (int i = 0; i < 3; i++)
    {
        float val = readRaw();
        // Lọc nhiễu: Chỉ lấy giá trị trong khoảng 2cm - 200cm
        if (val > 2 && val < 200)
        {
            samples.push_back(val);
        }
        delay(2); // Nghỉ 2ms
    }

    if (samples.empty())
        return 999; // Không thấy gì thì trả về xa vô cực

    std::sort(samples.begin(), samples.end());

    // Lấy trung vị
    return samples[samples.size() / 2];
}