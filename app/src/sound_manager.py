import time

class SoundManager:
    def __init__(self, net_thread):
        self.net_thread = net_thread
        self.last_played = 0
        
        self.trash_map = {
            "battery": "battery.wav",
            "glass": "glass.wav",
            "metal": "metal.wav",
            "paper": "paper.wav",
            "plastic": "plastic.wav"
        }

    def play_remote(self, filename):
        # Cooldown 2s
        if time.time() - self.last_played < 2.0:
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
        fname = self.trash_map.get(label, "detect.wav")
        self.play_remote(fname)
    
    def play_moving(self):
        self.play_remote("moving_to_trash.wav") 
    
    def play_done(self):
        self.play_remote("done.wav")

    def play_auto(self):
        self.play_remote("auto.wav") 

    def play_manual(self):
        self.play_remote("manual.wav")