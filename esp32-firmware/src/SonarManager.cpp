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

float SonarManager::readRaw()
{
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 12000);

    if (duration == 0)
        return 999;
    return duration * 0.034 / 2;
}

float SonarManager::getDistance()
{
    float samples[3];

    for (int i = 0; i < 3; i++)
    {
        samples[i] = readRaw();
        delay(2);
    }

    if (samples[0] > samples[1])
        std::swap(samples[0], samples[1]);
    if (samples[1] > samples[2])
        std::swap(samples[1], samples[2]);
    if (samples[0] > samples[1])
        std::swap(samples[0], samples[1]);

    return samples[1];
}