# network.py
import socket
import json
import time
import subprocess
import platform
from PyQt6.QtCore import QThread, pyqtSignal

class NetworkThread(QThread):
    data_received = pyqtSignal(dict) 
    ping_signal = pyqtSignal(str) # Signal gửi Ping về UI

    def __init__(self, target_ip, port=9999):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.sock.settimeout(0.1)
        self.target_ip = target_ip 
        self.target_port = 8888
        self.running = True
        
        # Timer ảo để đo ping định kỳ
        self.last_ping_time = 0

    def run(self):
        while self.running:
            # 1. Nhận dữ liệu cảm biến
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = json.loads(data.decode())
                self.data_received.emit(msg)
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Net Error: {e}")

            # 2. Thực hiện Ping mỗi 2 giây (Chạy background)
            if time.time() - self.last_ping_time > 2.0:
                self.measure_ping()
                self.last_ping_time = time.time()

    def measure_ping(self):
        # Dùng lệnh ping của hệ điều hành để không chặn socket UDP
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self.target_ip]
        
        try:
            # Chạy lệnh ping, timeout cực ngắn (500ms) để ko đơ
            start = time.time()
            res = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.5)
            end = time.time()
            
            if res.returncode == 0:
                ms = int((end - start) * 1000)
                # Trừ bớt overhead của python process (~20ms)
                ms = max(1, ms - 10) 
                self.ping_signal.emit(f"{ms}ms")
            else:
                self.ping_signal.emit("TIMEOUT")
        except:
             self.ping_signal.emit("ERR")

    def send_command(self, cmd_dict):
        try:
            msg = json.dumps(cmd_dict).encode()
            self.sock.sendto(msg, (self.target_ip, self.target_port))
        except Exception as e:
            print(f"❌ Send Error: {e}")
            
    def update_target_ip(self, new_ip):
        self.target_ip = new_ip

    def stop(self):
        self.running = False
        self.sock.close()
        self.wait()