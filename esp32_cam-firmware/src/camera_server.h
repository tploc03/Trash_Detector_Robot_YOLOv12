#ifndef CAMERA_SERVER_H
#define CAMERA_SERVER_H

#include <Arduino.h>
#include <WiFi.h>
#include "esp_camera.h"
#include <WebServer.h>

static WebServer server(81);

void startCameraServer()
{
    server.on("/stream", HTTP_GET, []()
              {
        WiFiClient client = server.client();
        
        String response = "HTTP/1.1 200 OK\r\n";
        response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n";
        response += "Connection: keep-alive\r\n";
        response += "Cache-Control: no-cache\r\n";
        response += "Pragma: no-cache\r\n\r\n";
        client.print(response);
        
        uint32_t timeout = 0;
        while (client.connected()) {
            camera_fb_t *fb = esp_camera_fb_get();
            
            if (!fb) {
                Serial.println("❌ Camera capture failed");
                delay(100);
                continue;
            }
            
            // Send frame
            client.print("--frame\r\n");
            client.print("Content-Type: image/jpeg\r\n");
            client.print("Content-Length: " + String(fb->len) + "\r\n");
            client.print("X-Timestamp: " + String(millis()) + "\r\n\r\n");
            
            size_t sent = client.write(fb->buf, fb->len);
            client.print("\r\n");
            
            esp_camera_fb_return(fb);
            
            if (sent != fb->len) {
                Serial.println("⚠️  Failed to send complete frame");
                break;
            }
            
            timeout++;
            if (timeout > 500) { // ~5 seconds
                timeout = 0;
                Serial.println("✓ Stream active...");
            }
        }
        
        Serial.println("Client disconnected");
        client.stop(); });

    server.on("/", HTTP_GET, []()
              {
        String html = R"(
        <!DOCTYPE html>
        <html>
        <head>
            <title>ESP32-CAM Stream</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { text-align: center; background: #222; }
                img { max-width: 100%; height: auto; margin: 20px auto; border: 2px solid #0078D4; }
            </style>
        </head>
        <body>
            <h1>📷 ESP32-CAM Stream</h1>
            <img src="/stream" width="640" height="480">
        </body>
        </html>
        )";
        server.send(200, "text/html", html); });

    server.begin();
    Serial.println("✓ Camera server started on port 81");
}

void handleCameraLoop()
{
    server.handleClient();
}

#endif