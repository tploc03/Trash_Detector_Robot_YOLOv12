import cv2
import time
import os
from datetime import datetime

STREAM_URL = "http://10.230.248.174:81/stream" 
SAVE_FOLDER = "ai/data/cam1/plastic"
CLIP_DURATION = 0.5

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    print(f"Created folder: {SAVE_FOLDER}")

def main():
    print(f"Connecting to camera: {STREAM_URL}...")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("Cannot connect to camera! Check IP or Wifi.")
        return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    is_recording = False
    start_time = 0
    out = None
    
    print("\nSYSTEM READY!")
    print(f"Press 'R' to record a {CLIP_DURATION}s clip.")
    print("Press 'Q' to quit.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.5)
            cap.open(STREAM_URL)
            continue

        if is_recording:
            elapsed = time.time() - start_time
            remaining = CLIP_DURATION - elapsed
            
            if remaining > 0:
                out.write(frame)
                
                cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1) # Chấm đỏ
                cv2.putText(frame, f"REC {remaining:.1f}s", (50, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print(f"\rRecording {remaining:.1f}s", end="")
            else:
                is_recording = False
                out.release()
                print(f"\nSaved clip!")
        
        cv2.imshow("Data Recorder - Press 'R'", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        
        elif key == ord('r'):
            if not is_recording:
                # Tạo tên filetheo thời gian: data/video_Năm-Tháng-Ngày_Giờ-Phút-Giây.avi
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{SAVE_FOLDER}/clip_{timestamp}.mp4"
                
                fourcc = cv2.VideoWriter_fourcc(*'MJPG') 
                fps = 20.0
                h, w = frame.shape[:2]
                
                out = cv2.VideoWriter(filename, fourcc, fps, (w, h))
                
                is_recording = True
                start_time = time.time()
                print(f"\nStarted recording: {filename}")

    cap.release()
    if out: out.release()
    cv2.destroyAllWindows()
    print("\nExited.")

if __name__ == "__main__":
    main()