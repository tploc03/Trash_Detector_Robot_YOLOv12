#include "SonarManager.h"
#include <algorithm> // Thư viện để sắp xếp mảng
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

// Hàm đọc 1 lần thô (Private helper)
float SonarManager::readRaw()
{
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    // Timeout 25000us (~4m)
    long duration = pulseIn(echoPin, HIGH, 25000);

    if (duration == 0)
        return 0; // Trả về 0 nếu timeout
    return duration * 0.034 / 2;
}

// HÀM CHÍNH: Đọc 5 lần và lấy trung vị (Median Filter)
float SonarManager::getDistance()
{
    std::vector<float> samples;

    // 1. Lấy 5 mẫu liên tiếp
    for (int i = 0; i < 5; i++)
    {
        float val = readRaw();
        if (val > 0 && val < 400)
        { // Chỉ lấy giá trị hợp lệ (0-4m)
            samples.push_back(val);
        }
        delay(3); // Nghỉ cực ngắn giữa các lần bắn để sóng cũ tan bớt
    }

    // 2. Nếu không có mẫu nào hợp lệ
    if (samples.empty())
        return 999;

    // 3. Sắp xếp từ bé đến lớn
    std::sort(samples.begin(), samples.end());

    // 4. Lấy giá trị ở giữa (Trung vị)
    // Ví dụ: [18, 19, 20, 200, 500] -> Lấy 20. Số 200, 500 bị loại.
    return samples[samples.size() / 2];
}