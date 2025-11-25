import os
from ultralytics import YOLO
import torch

DATA_YAML_PATH = 'D:/ploc/trash_data.yaml'

PROJECT_SAVE_DIR = 'D:/ploc/runs'

RUN_NAME = 'trash_yolov12_v1'

MODEL_TO_USE = 'yolov12n.pt'
EPOCHS = 150
BATCH_SIZE = 8
IMAGE_SIZE = 640
WORKERS = 4      # Số luồng tải dữ liệu (để 8 nếu máy bạn mạnh, giảm xuống 2 nếu yếu)


def main():
    os.makedirs(PROJECT_SAVE_DIR, exist_ok=True)
    
    if torch.cuda.is_available():
        print(f"Đang sử dụng GPU: {torch.cuda.get_device_name(0)}")
        torch.cuda.empty_cache()
    else:
        print("CẢNH BÁO: Không tìm thấy GPU (CUDA). Đang chạy bằng CPU (rất chậm).")

    model = YOLO(MODEL_TO_USE) 
    print(f"Đã tải mô hình {MODEL_TO_USE}, bắt đầu huấn luyện...")

    try:
        results = model.train(
            data=DATA_YAML_PATH,
            epochs=EPOCHS,
            imgsz=IMAGE_SIZE,
            batch=BATCH_SIZE,
            workers=WORKERS,
            
            # FIX 1: Tắt AMP để BỎ QUA hàm check_amp() bị lỗi
            amp=True, 
            
            mosaic=1.0, 
            auto_augment='randaugment',
            copy_paste=0.1,
            mixup=0,
            # ----------------------------------

            project=PROJECT_SAVE_DIR,
            name=RUN_NAME,
            
            # --- Các cài đặt tốt cho huấn luyện local ---
            save=True,        # Lưu checkpoints
            save_period=10,   # Lưu mỗi 10 epochs
            patience=50       # Dừng sớm nếu không cải thiện sau 50 epochs
        )
        
        print("\nHUẤN LUYỆN HOÀN TẤT!")
        print(f"Kết quả được lưu tại: {results.save_dir}")
        print(f"Model tốt nhất: {results.save_dir}/weights/best.pt")

    except Exception as e:
        print("\nĐÃ XẢY RA LỖI KHI HUẤN LUYỆN")
        print(e)
        print("\nHãy kiểm tra lại các bước cài đặt môi trường (venv),")
        print("đặc biệt là thứ tự: 1. Cài yolov12, 2. Hạ cấp numpy==1.26.4")

if __name__ == '__main__':
    main()