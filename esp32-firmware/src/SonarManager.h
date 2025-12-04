#ifndef SONAR_MANAGER_H
#define SONAR_MANAGER_H

#include <Arduino.h>

class SonarManager
{
private:
    int trigPin;
    int echoPin;
    float readRaw();

public:
    SonarManager(int trig, int echo);
    void begin();
    float getDistance();
};

#endif