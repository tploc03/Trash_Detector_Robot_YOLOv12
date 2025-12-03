# network.py
import socket
import json
from PyQt6.QtCore import QThread, pyqtSignal

class NetworkThread(QThread):
    data_received = pyqtSignal(dict) 

    def __init__(self, target_ip, port=9999):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.sock.settimeout(0.05)
        self.target_ip = target_ip  # IP of ESP32 robot
        self.target_port = 8888
        self.running = True

    def run(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = json.loads(data.decode())
                self.data_received.emit(msg)
            except:
                pass
    
    def send_command(self, cmd_dict):
        try:
            msg = json.dumps(cmd_dict).encode()
            self.sock.sendto(msg, (self.target_ip, self.target_port))
        except Exception as e:
            print(f"❌ Network Error: {e}")

    def stop(self):
        self.running = False
        self.sock.close()