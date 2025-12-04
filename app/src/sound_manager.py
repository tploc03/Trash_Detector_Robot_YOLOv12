# sound_manager.py
import time
import os

class SoundManager:
    def __init__(self, net_thread):
        self.net_thread = net_thread
        self.last_played = 0
        # Mapping tên rác (YOLO class) sang tên file wav (nếu khác nhau)
        self.trash_map = {
            "battery": "battery.wav",
            "glass": "glass.wav",
            "metal": "metal.wav",
            "organic": "organic.wav",
            "paper": "paper.wav",
            "plastic": "plastic.wav",
            "paper_cardboard": "paper.wav" # Ví dụ map nhiều tên về 1 file
        }

    def play_remote(self, filename):
        """Gửi lệnh phát âm thanh xuống ESP32"""
        if time.time() - self.last_played < 0.5:
            return

        if not filename.startswith("/"):
            filename = "/" + filename
        
        print(f"SOUND REQUEST: {filename}")
        self.net_thread.send_command({
            "cmd": "SPEAK",
            "file": filename
        })
        self.last_played = time.time()

    def play_startup(self):
        self.play_remote("startup.wav")

    def play_trash_detect(self, label):
        fname = self.trash_map.get(label, f"{label}.wav")
        self.play_remote(fname)