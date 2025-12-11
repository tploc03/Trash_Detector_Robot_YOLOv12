# network.py - SAFE PORT BINDING
import socket
import json
import time
from PyQt6.QtCore import QThread, pyqtSignal

class NetworkThread(QThread):
    data_received = pyqtSignal(dict) 
    ping_signal = pyqtSignal(str) 

    def __init__(self, target_ip, port=9999):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # --- FIX LỖI KẸT CỔNG (Bind Error) ---
        bound = False
        while not bound:
            try:
                self.sock.bind(("0.0.0.0", port))
                bound = True
                print(f"✅ Socket bound to port {port}")
            except OSError:
                print(f"⚠️ Port {port} is busy. Trying {port + 1}...")
                port += 1 # Tự động nhảy sang cổng tiếp theo
                if port > 10050: # Giới hạn thử
                    print("❌ Could not bind any port!")
                    break
        # -------------------------------------

        self.sock.settimeout(0.1) 
        self.target_ip = target_ip 
        self.target_port = 8888
        self.running = True
        self.last_packet_time = 0 

    def run(self):
        print("✅ Network Thread Started")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                
                # Tính Ping
                now = time.time()
                if self.last_packet_time != 0:
                    delta_ms = int((now - self.last_packet_time) * 1000)
                    self.ping_signal.emit(f"{delta_ms}ms")
                self.last_packet_time = now

                try:
                    msg = json.loads(data.decode())
                    self.data_received.emit(msg)
                except json.JSONDecodeError:
                    pass # Bỏ qua gói tin lỗi
                
            except socket.timeout:
                pass 
            except OSError:
                break 
            except Exception as e:
                print(f"Net Error: {e}")
        
        print("🛑 Network Thread Exited")

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
        if self.sock:
            self.sock.close()
        self.wait(1000)