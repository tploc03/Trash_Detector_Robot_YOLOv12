#include "esp_camera.h"
#include <WiFi.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_http_server.h"

const char *ssid = "Tề Tĩnh Xuân";
const char *password = "123454321";

#define PART_BOUNDARY "123456789000000000000987654321"
static const char *_STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char *_STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char *_STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22
#define FLASH_GPIO_NUM 4

httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

// ================== FLASH CONTROL ==================
bool flash_state = true;

void setFlash(bool state)
{
  flash_state = state;
  digitalWrite(FLASH_GPIO_NUM, state ? HIGH : LOW);
  Serial.printf("Flash: %s\n", state ? "ON" : "OFF");
}

// ================== OPTIMIZED STREAM HANDLER ==================
static esp_err_t stream_handler(httpd_req_t *req)
{
  camera_fb_t *fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t *_jpg_buf = NULL;
  char part_buf[64];

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK)
    return res;

  // Disable buffering
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "X-Framerate", "30"); // Hint for client

  while (true)
  {
    fb = esp_camera_fb_get();
    if (!fb)
    {
      Serial.println("Camera capture failed");
      vTaskDelay(10 / portTICK_PERIOD_MS); // ✅ Giảm delay từ 20ms → 10ms
      continue;
    }

    // Luôn dùng JPEG (không convert)
    if (fb->format != PIXFORMAT_JPEG)
    {
      bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
      esp_camera_fb_return(fb);
      fb = NULL;
      if (!jpeg_converted)
      {
        Serial.println("JPEG compression failed");
        continue;
      }
    }
    else
    {
      _jpg_buf_len = fb->len;
      _jpg_buf = fb->buf;
    }

    // Gửi frame ngay lập tức
    if (res == ESP_OK && _jpg_buf_len > 0)
    {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }
    if (res == ESP_OK && _jpg_buf_len > 0)
    {
      size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK && _jpg_buf_len > 0)
    {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }

    // Cleanup
    if (fb)
    {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    }
    else if (_jpg_buf)
    {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }

    if (res != ESP_OK)
      break;

    // Không delay giữa các frame (tối đa FPS)
  }
  return res;
}

// ================== ENHANCED CONTROL HANDLER ==================
static esp_err_t cmd_handler(httpd_req_t *req)
{
  char *buf;
  size_t buf_len;
  char variable[32] = {0};
  char value[32] = {0};

  buf_len = httpd_req_get_url_query_len(req) + 1;
  if (buf_len > 1)
  {
    buf = (char *)malloc(buf_len);
    if (!buf)
    {
      httpd_resp_send_500(req);
      return ESP_FAIL;
    }
    if (httpd_req_get_url_query_str(req, buf, buf_len) == ESP_OK)
    {
      if (httpd_query_key_value(buf, "var", variable, sizeof(variable)) == ESP_OK &&
          httpd_query_key_value(buf, "val", value, sizeof(value)) == ESP_OK)
      {
      }
      else
      {
        free(buf);
        httpd_resp_send_404(req);
        return ESP_FAIL;
      }
    }
    else
    {
      free(buf);
      httpd_resp_send_404(req);
      return ESP_FAIL;
    }
    free(buf);
  }
  else
  {
    httpd_resp_send_404(req);
    return ESP_FAIL;
  }

  int val = atoi(value);

  // Xử lý nhiều command hơn
  if (!strcmp(variable, "flash"))
  {
    setFlash(val == 1);
  }
  else if (!strcmp(variable, "quality"))
  {
    sensor_t *s = esp_camera_sensor_get();
    s->set_quality(s, val);
  }
  else if (!strcmp(variable, "framesize"))
  {
    sensor_t *s = esp_camera_sensor_get();
    s->set_framesize(s, (framesize_t)val);
  }

  httpd_resp_send_chunk(req, NULL, 0);
  return ESP_OK;
}

static esp_err_t index_handler(httpd_req_t *req)
{
  httpd_resp_set_type(req, "text/html");
  const char html[] = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robot Eye</title>
<style>
body { background: #111; color: #fff; text-align: center; margin: 0; padding: 20px; font-family: sans-serif; }
h1 { color: #0078D4; margin-bottom: 20px; }
img { max-width: 100%; height: auto; border: 2px solid #333; border-radius: 8px; box-shadow: 0 0 20px rgba(0,120,212,0.4); }
.controls { margin-top: 20px; }
button { background: #0078D4; color: #fff; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; font-size: 14px; }
button:hover { background: #005a9e; }
.status { margin: 10px 0; color: #06D6A0; font-weight: bold; }
</style>
</head>
<body>
<h1>🤖 ROBOT AI VIEW</h1>
<div class="status" id="status">⚡ STREAMING</div>
<img src="" id="stream" onload="updateStatus(true)" onerror="updateStatus(false)">
<div class="controls">
  <button onclick="toggleFlash()">💡 Toggle Flash</button>
  <button onclick="location.reload()">🔄 Reload</button>
</div>
<script>
  var streamUrl = document.location.protocol + '//' + document.location.hostname + ':81/stream';
  document.getElementById('stream').src = streamUrl;
  
  function updateStatus(ok) {
    document.getElementById('status').textContent = ok ? '⚡ STREAMING' : '❌ CONNECTION LOST';
    document.getElementById('status').style.color = ok ? '#06D6A0' : '#FF6B6B';
  }
  
  function toggleFlash() {
    fetch('/control?var=flash&val=' + (Math.random() > 0.5 ? '1' : '0'));
  }
</script>
</body>
</html>
)rawliteral";
  httpd_resp_send(req, html, strlen(html));
  return ESP_OK;
}

void startCameraServer()
{
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;
  config.max_uri_handlers = 12; // ✅ Tăng số handlers
  config.stack_size = 8192;     // ✅ Tăng stack size

  httpd_uri_t index_uri = {.uri = "/", .method = HTTP_GET, .handler = index_handler, .user_ctx = NULL};
  httpd_uri_t cmd_uri = {.uri = "/control", .method = HTTP_GET, .handler = cmd_handler, .user_ctx = NULL};
  httpd_uri_t stream_uri = {.uri = "/stream", .method = HTTP_GET, .handler = stream_handler, .user_ctx = NULL};

  if (httpd_start(&camera_httpd, &config) == ESP_OK)
  {
    httpd_register_uri_handler(camera_httpd, &index_uri);
    httpd_register_uri_handler(camera_httpd, &cmd_uri);
  }

  config.server_port += 1;
  config.ctrl_port += 1;
  if (httpd_start(&stream_httpd, &config) == ESP_OK)
  {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

// ================== CAMERA OPTIMIZATION ==================
void optimizeCameraSettings()
{
  sensor_t *s = esp_camera_sensor_get();
  if (s == NULL)
  {
    Serial.println("Failed to get camera sensor");
    return;
  }

  // CRITICAL: Tối ưu cho tốc độ & độ trễ thấp
  s->set_brightness(s, 0); // -2 to 2
  s->set_contrast(s, 0);   // -2 to 2
  s->set_saturation(s, 0); // -2 to 2

  // Tắt các tính năng tự động (giảm processing time)
  s->set_whitebal(s, 1); // 0=disable, 1=enable (giữ ON để ảnh đẹp hơn)
  s->set_awb_gain(s, 1); // 0=disable, 1=enable
  s->set_wb_mode(s, 0);  // 0 to 4 (Auto white balance mode)

  s->set_exposure_ctrl(s, 1); // 0=disable, 1=enable (AUTO exposure)
  s->set_aec2(s, 0);          // 0=disable, 1=enable (tắt AEC DSP)
  s->set_ae_level(s, 0);      // -2 to 2
  s->set_aec_value(s, 300);   // 0 to 1200 (manual exposure value)

  s->set_gain_ctrl(s, 1);                  // 0=disable, 1=enable (AUTO gain)
  s->set_agc_gain(s, 0);                   // 0 to 30
  s->set_gainceiling(s, (gainceiling_t)0); // 0 to 6

  s->set_bpc(s, 0);     // 0=disable, 1=enable (Black pixel correction)
  s->set_wpc(s, 1);     // 0=disable, 1=enable (White pixel correction)
  s->set_raw_gma(s, 1); // 0=disable, 1=enable (Gamma correction)
  s->set_lenc(s, 1);    // 0=disable, 1=enable (Lens correction)

  s->set_hmirror(s, 0); // 0=disable, 1=enable (Horizontal mirror)
  s->set_vflip(s, 0);   // 0=disable, 1=enable (Vertical flip)
  s->set_dcw(s, 1);     // 0=disable, 1=enable (Downsize EN)

  s->set_colorbar(s, 0); // 0=disable, 1=enable (Test pattern)

  // SPECIAL: Giảm special effects processing
  s->set_special_effect(s, 0); // 0=No effect, 1=Negative, 2=Grayscale...

  Serial.println("Camera optimized for LOW LATENCY");
}

void setup()
{
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector
  Serial.begin(115200);
  Serial.setDebugOutput(false);
  Serial.println("\n\n========== ESP32-CAM ROBOT ==========");

  // ================== CAMERA CONFIG ==================
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // CRITICAL OPTIMIZATION: Độ phân giải & Quality
  if (psramFound())
  {
    config.frame_size = FRAMESIZE_VGA;     // 640x480
    config.jpeg_quality = 15;              // 10-63, thấp hơn = nén nhiều hơn = nhanh hơn
    config.fb_count = 2;                   // Double buffer cho smooth stream
    config.grab_mode = CAMERA_GRAB_LATEST; // Luôn lấy frame mới nhất
  }
  else
  {
    config.frame_size = FRAMESIZE_CIF; // 400x296
    config.jpeg_quality = 15;
    config.fb_count = 1;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  // Init camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.printf("Camera init failed: 0x%x\n", err);
    ESP.restart();
    return;
  }
  Serial.println("Camera initialized");

  // Apply optimization settings
  optimizeCameraSettings();

  // ================== WIFI SETUP ==================
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 30)
  {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("\nWiFi connection failed!");
    ESP.restart();
    return;
  }

  Serial.println("\nWiFi Connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Stream URL: http://");
  Serial.print(WiFi.localIP());
  Serial.println(":81/stream");

  // ================== START SERVER ==================
  startCameraServer();

  // ================== FLASH SETUP ==================
  pinMode(FLASH_GPIO_NUM, OUTPUT);
  setFlash(true);

  Serial.println("========== SYSTEM READY ==========\n");
}

void loop()
{
  // Heartbeat: Kiểm tra WiFi connection
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck > 10000) // Mỗi 10s
  {
    lastCheck = millis();
    if (WiFi.status() != WL_CONNECTED)
    {
      Serial.println("WiFi disconnected, reconnecting...");
      WiFi.reconnect();
    }
    else
    {
      Serial.printf("Heartbeat - Free heap: %d bytes\n", ESP.getFreeHeap());
    }
  }

  delay(1000);
}