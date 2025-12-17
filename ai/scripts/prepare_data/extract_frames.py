import cv2
import os
import glob

def extract_frames(video_dir, output_dir, frame_interval=3):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Đã tạo thư mục: {output_dir}")

    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']
    video_files = []
    for ext in video_extensions:
        video_files.extend(glob.glob(os.path.join(video_dir, ext)))

    if not video_files:
        print("Can not find any video")
        return

    print(f"Found {len(video_files)} video")

    total_images_saved = 0

    for video_path in video_files:
        filename = os.path.basename(video_path).split('.')[0]
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Can not open video: {filename}")
            continue

        frame_count = 0
        saved_count = 0
        
        while True:
            success, frame = cap.read()
            
            if not success:
                break
            
            if frame_count % frame_interval == 0:
                output_filename = f"{filename}_f{frame_count}.jpg"
                output_path = os.path.join(output_dir, output_filename)
                
                cv2.imwrite(output_path, frame)
                saved_count += 1
                total_images_saved += 1
            
            frame_count += 1

        cap.release()
        print(f"Done: {filename} -> Saved {saved_count} images.")

    print(f"Done, Total saved {total_images_saved} images to folder '{output_dir}'.")

input_folder = "ai/data/cam1/plastic"
output_folder = "ai/data/cam1/pic1/plastic"
frames_step = 4

extract_frames(input_folder, output_folder, frames_step)