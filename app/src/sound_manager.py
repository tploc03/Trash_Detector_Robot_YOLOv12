# sound_manager.py
# File này giờ chỉ dùng để giữ tên file, việc phát là do Robot lo
class SoundManager:
    def __init__(self, net_thread):
        self.net_thread = net_thread # Cần luồng mạng để gửi lệnh

    def play_remote(self, filename):
        # Đảm bảo tên file có dấu / ở đầu nếu cần
        if not filename.startswith("/"):
            filename = "/" + filename
        
        print(f"📡 Gửi lệnh phát loa: {filename}")
        self.net_thread.send_command({
            "cmd": "SPEAK",
            "file": filename
        })

    def play_startup(self):
        self.play_remote("startup.wav")

    def play_trash_detect(self, trash_name):
        # Ví dụ: plastic.wav
        self.play_remote(f"{trash_name}.wav")