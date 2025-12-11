import cv2
import os
import glob

def extract_frames(video_dir, output_dir, frame_interval=3):
    # Tạo thư mục đầu ra nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Đã tạo thư mục: {output_dir}")

    # Lấy danh sách các file video (hỗ trợ mp4, avi, mov, mkv)
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(video_dir, ext)))

    if not video_files:
        print("Không tìm thấy video nào trong thư mục nguồn!")
        return

    print(f"Tìm thấy {len(video_files)} video. Bắt đầu xử lý...")

    total_images_saved = 0

    for video_path in video_files:
        filename = os.path.basename(video_path).split('.')[0]
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Không thể mở video: {filename}")
            continue

        frame_count = 0
        saved_count = 0
        
        while True:
            success, frame = cap.read()
            
            if not success:
                break # Hết video
            
            # Kiểm tra điều kiện frame (lấy mỗi frame thứ 3)
            if frame_count % frame_interval == 0:
                # Tạo tên file: tenvideo_frame001.jpg
                output_filename = f"{filename}_f{frame_count}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                
                cv2.imwrite(output_path, frame)
                saved_count += 1
                total_images_saved += 1
            
            frame_count += 1

        cap.release()
        print(f"Đã xong video: {filename} -> Lưu được {saved_count} ảnh.")

    print("---")
    print(f"HOÀN TẤT! Tổng cộng đã lưu {total_images_saved} ảnh vào thư mục '{output_dir}'.")

# --- CẤU HÌNH ĐƯỜNG DẪN TẠI ĐÂY ---
input_folder = "ai/cam/plastic"   # Tên thư mục chứa video quay được
output_folder = "ai/data/final_dataset_image/plastic"   # Tên thư mục muốn lưu ảnh
frames_step = 4

# Chạy hàm
extract_frames(input_folder, output_folder, frames_step)