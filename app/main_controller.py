import tkinter as tk
import socket
import json
import threading
import time

# --- CẤU HÌNH ---
ROBOT_IP = "192.168.1.12"
ROBOT_PORT = 8888
LOCAL_PORT = 9999
SPEED = 255

class RobotControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Control & Monitor")
        self.root.geometry("500x400")
        
        # Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", LOCAL_PORT)) # Lắng nghe dữ liệu về
        self.sock.settimeout(0.05) # Non-blocking read
        self.target_address = (ROBOT_IP, ROBOT_PORT)

        # Biến
        self.speed_L = 0
        self.speed_R = 0
        self.is_running = True

        # GIAO DIỆN
        # 1. Phần hiển thị cảm biến
        frame_sensor = tk.LabelFrame(root, text="Sensor Data (cm)", font=("Arial", 12, "bold"))
        frame_sensor.pack(pady=10, fill="x", padx=10)

        self.lbl_left = tk.Label(frame_sensor, text="Left: --", fg="blue", font=("Arial", 14))
        self.lbl_left.pack(side="left", padx=20)
        
        self.lbl_front = tk.Label(frame_sensor, text="Front: --", fg="red", font=("Arial", 16, "bold"))
        self.lbl_front.pack(side="left", padx=20)
        
        self.lbl_right = tk.Label(frame_sensor, text="Right: --", fg="blue", font=("Arial", 14))
        self.lbl_right.pack(side="left", padx=20)

        # 2. Phần điều khiển
        tk.Label(root, text="Controls: W A S D", font=("Arial", 10)).pack(pady=20)
        self.btn_update = tk.Button(root, text="Set IP", command=self.update_ip)
        self.btn_update.pack()
        self.entry_ip = tk.Entry(root); self.entry_ip.insert(0, ROBOT_IP); self.entry_ip.pack()

        # Input Handling
        root.bind('<KeyPress>', self.on_key_press)
        root.bind('<KeyRelease>', self.on_key_release)

        # Threads
        threading.Thread(target=self.send_loop, daemon=True).start()
        threading.Thread(target=self.receive_loop, daemon=True).start() # Thread mới để nhận data

    def update_ip(self):
        self.target_address = (self.entry_ip.get(), ROBOT_PORT)

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key == 'w': self.speed_L = SPEED; self.speed_R = SPEED
        elif key == 's': self.speed_L = -SPEED; self.speed_R = -SPEED
        elif key == 'a': self.speed_L = -SPEED; self.speed_R = SPEED
        elif key == 'd': self.speed_L = SPEED; self.speed_R = -SPEED

    def on_key_release(self, event):
        if event.keysym.lower() in ['w','a','s','d']:
            self.speed_L = 0; self.speed_R = 0

    def send_loop(self):
        while self.is_running:
            data = {"cmd": "MOVE", "L": self.speed_L, "R": self.speed_R}
            try:
                self.sock.sendto(json.dumps(data).encode(), self.target_address)
            except: pass
            time.sleep(0.1)

    def receive_loop(self):
        while self.is_running:
            try:
                data, _ = self.sock.recvfrom(1024)
                msg = json.loads(data.decode())
                
                # Cập nhật GUI (cần dùng after để an toàn luồng)
                if "F" in msg:
                    self.root.after(0, self.update_labels, msg["F"], msg["L"], msg["R"])
            except socket.timeout:
                pass
            except Exception as e:
                print("Rx Error:", e)

    def update_labels(self, f, l, r):
        self.lbl_front.config(text=f"Front: {f}")
        self.lbl_left.config(text=f"Left: {l}")
        self.lbl_right.config(text=f"Right: {r}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotControllerApp(root)
    root.mainloop()