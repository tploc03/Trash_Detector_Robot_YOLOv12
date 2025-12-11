import time

class SoundManager:
    def __init__(self, net_thread):
        self.net_thread = net_thread
        self.last_played = 0
        
        # Map tên class AI sang tên file âm thanh trong SPIFFS
        self.trash_map = {
            "battery": "battery.wav",
            "glass": "glass.wav",
            "metal": "metal.wav",
            "organic": "organic.wav",
            "paper": "paper.wav",
            "plastic": "plastic.wav"
        }

    def play_remote(self, filename):
        """Gửi lệnh phát âm thanh xuống ESP32"""
        # Cooldown 2s để tránh spam lệnh liên tục làm đơ ESP32
        if time.time() - self.last_played < 2.0:
            return

        # Đảm bảo có dấu / ở đầu tên file (yêu cầu của SPIFFS)
        if not filename.startswith("/"):
            filename = "/" + filename
        
        print(f"🔊 SOUND REQUEST: {filename}")
        self.net_thread.send_command({
            "cmd": "SPEAK",
            "file": filename
        })
        self.last_played = time.time()

    def play_startup(self):
        """Phát khi mở App"""
        self.play_remote("startup.wav")

    def play_trash_detect(self, label):
        """Phát khi phát hiện rác"""
        # Nếu label có trong map thì lấy file tương ứng, không thì lấy detect.wav
        fname = self.trash_map.get(label, "detect.wav")
        self.play_remote(fname)
    
    def play_moving(self):
        self.play_remote("moving_to_trash.wav") 
    
    def play_done(self):
        self.play_remote("done.wav")

    # --- CÁC HÀM CÒN THIẾU ĐÃ ĐƯỢC BỔ SUNG ---
    def play_auto(self):
        # Bạn cần nạp file auto_mode.wav vào ESP32, hoặc đổi tên thành startup.wav nếu chưa có
        self.play_remote("auto.wav") 

    def play_manual(self):
        """Phát khi chuyển sang chế độ Manual"""
        # Bạn cần nạp file manual_mode.wav vào ESP32
        self.play_remote("manual.wav")