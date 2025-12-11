import cv2
import time
import os
from datetime import datetime

# --- CẤU HÌNH ---
# Thay IP này bằng IP thực tế của Camera bạn (xem trong App hoặc Serial Monitor)
STREAM_URL = "http://10.230.248.174:81/stream" 
SAVE_FOLDER = "ai/cam/glass"  # Thư mục lưu video
CLIP_DURATION = 3  # Độ dài mỗi clip (giây)

# Tạo thư mục lưu nếu chưa có
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    print(f"📂 Created folder: {SAVE_FOLDER}")

def main():
    print(f"🔄 Connecting to camera: {STREAM_URL}...")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("❌ Cannot connect to camera! Check IP or Wifi.")
        return

    # Cài đặt buffer thấp để giảm độ trễ
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # Biến trạng thái quay
    is_recording = False
    start_time = 0
    out = None
    
    print("\n✅ SYSTEM READY!")
    print(f"👉 Press 'R' to record a {CLIP_DURATION}s clip.")
    print("👉 Press 'Q' to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Lost signal...")
            time.sleep(0.5)
            # Thử kết nối lại nếu mất tín hiệu
            cap.open(STREAM_URL)
            continue

        # Resize nhẹ để hiển thị cho mượt (nếu cần)
        # frame = cv2.resize(frame, (640, 480))

        # --- XỬ LÝ GHI HÌNH ---
        if is_recording:
            # Tính thời gian đã quay
            elapsed = time.time() - start_time
            remaining = CLIP_DURATION - elapsed
            
            if remaining > 0:
                # Vẫn còn thời gian -> Ghi frame
                out.write(frame)
                
                # Hiển thị dấu chấm đỏ REC và thời gian đếm ngược
                cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1) # Chấm đỏ
                cv2.putText(frame, f"REC {remaining:.1f}s", (50, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print(f"\r🎥 Recording... {remaining:.1f}s", end="")
            else:
                # Hết giờ -> Dừng quay
                is_recording = False
                out.release()
                print(f"\n✅ Saved clip!")
        
        # --- HIỂN THỊ ---
        cv2.imshow("Data Recorder - Press 'R'", frame)

        # --- XỬ LÝ PHÍM BẤM ---
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'): # Thoát
            break
        
        elif key == ord('r'): # Bắt đầu quay
            if not is_recording:
                # Tạo tên file theo thời gian: data/video_Năm-Tháng-Ngày_Giờ-Phút-Giây.avi
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{SAVE_FOLDER}/clip_{timestamp}.mp4"
                
                # Khởi tạo VideoWriter
                # MJPG là codec phổ biến, nếu lỗi có thể thử 'XVID'r
                fourcc = cv2.VideoWriter_fourcc(*'MJPG') 
                fps = 20.0 # FPS giả định của ESP32-CAM (thường là 10-25 tùy mạng)
                h, w = frame.shape[:2]
                
                out = cv2.VideoWriter(filename, fourcc, fps, (w, h))
                
                is_recording = True
                start_time = time.time()
                print(f"\n🚀 Started recording: {filename}")

    # Dọn dẹp
    cap.release()
    if out: out.release()
    cv2.destroyAllWindows()
    print("\n👋 Exited.")

if __name__ == "__main__":
    main()