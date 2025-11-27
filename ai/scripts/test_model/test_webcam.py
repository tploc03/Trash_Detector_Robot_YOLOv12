import os
import torch
import types
from ultralytics import YOLO


# ================== CẦN SỬA CHO PHÙ HỢP MÁY BẠN ==================

# Đường dẫn tới model đã train xong (best.pt)
MODEL_PATH = r"ai/runs/6_class_model/yolov12_trash_detection/weights/best.pt"

# Chọn chế độ test: "image", "folder", "video", "webcam"
MODE = "webcam"

# Nếu MODE là "image", "folder" hoặc "video" thì sửa SOURCE cho hợp
# - image:  path tới 1 file ảnh .jpg/.png
# - folder: path tới folder chứa nhiều ảnh
# - video:  path tới file .mp4/.avi
# - webcam: bỏ qua SOURCE, luôn dùng 0
SOURCE = r"D:/ploc/test_images"   # ví dụ folder ảnh test

# Kích thước ảnh input (nên trùng lúc train)
IMAGE_SIZE = 640

# Ngưỡng confidence để hiển thị bbox
CONF_THRES = 0.3

# Thư mục lưu kết quả (chỉ dùng cho image/folder/video)
SAVE_DIR = r"D:/ploc/test_results"
RUN_NAME = "trash_yolov12_test"

# ================================================================


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Không tìm thấy model tại: {MODEL_PATH}")

    # In thông tin device
    if torch.cuda.is_available():
        print(f"Đang sử dụng GPU: {torch.cuda.get_device_name(0)}")
        device = 0
    else:
        print("Đang sử dụng CPU (sẽ chậm hơn).")
        device = "cpu"

    print("Đang tải mô hình...")
    model = YOLO(MODEL_PATH)

    # Khắc phục tương thích cho các checkpoint cũ:
    # Một số checkpoint cũ có AAttn chứa 'qk' và 'v' thay vì 'qkv'.
    # Nếu module AAttn của model hiện tại thiếu thuộc tính 'qkv'
    # chúng ta thêm một phương thức tổng hợp để tránh AttributeError.
    def fix_aattn_compat(m):
        for mod in m.model.modules():
            # Kiểm tra tên lớp để tránh import trực tiếp
            if mod.__class__.__name__ == 'AAttn':
                if not hasattr(mod, 'qkv') and hasattr(mod, 'qk') and hasattr(mod, 'v'):
                    # Tạo method qkv tương thích: nối qk và v theo chiều channel
                    def _qkv(self, x):
                        qk_out = self.qk(x)
                        v_out = self.v(x)
                        return torch.cat([qk_out, v_out], dim=1)
                    mod.qkv = types.MethodType(_qkv, mod)

    try:
        fix_aattn_compat(model)
    except Exception:
        # Không gây lỗi nếu việc vá không thành công
        pass

    print("Đã tải mô hình thành công!\n")

    return model, device


def run_webcam(model):
    print("Bắt đầu test bằng WEBCAM")
    print(">>> Nhấn 'q' trên cửa sổ webcam để thoát <<<")

    # Ultralytics sẽ tự mở cửa sổ hiển thị khi show=True
    results = model.predict(
        source=0,
        show=True,
        stream=True,
        conf=CONF_THRES,
        imgsz=IMAGE_SIZE
    )

    try:
        for r in results:
            # Nếu muốn xem thông tin dự đoán từng frame:
            # print(r.boxes.cls, r.boxes.conf)
            pass
    except KeyboardInterrupt:
        print("\nĐã dừng webcam bằng Ctrl+C.")
    finally:
        import cv2
        cv2.destroyAllWindows()
        print("Đã đóng cửa sổ webcam.")


def run_image_folder_video(model):
    if not os.path.exists(SOURCE):
        raise FileNotFoundError(f"Không tìm thấy SOURCE: {SOURCE}")

    print(f"Bắt đầu predict với SOURCE: {SOURCE}")
    print(f"Kết quả sẽ được lưu trong: {SAVE_DIR}/{RUN_NAME}")

    results = model.predict(
        source=SOURCE,
        imgsz=IMAGE_SIZE,
        conf=CONF_THRES,
        save=True,           # lưu ảnh/video đã vẽ bbox
        project=SAVE_DIR,
        name=RUN_NAME,
        exist_ok=True,       # không tạo run mới nếu đã tồn tại
        show=True            # nếu muốn xem trực tiếp
    )

    # In thông tin cơ bản của từng file
    for r in results:
        print("-" * 50)
        print("File:", r.path)
        print("Số bbox:", len(r.boxes))
        if len(r.boxes):
            print("Classes:", r.boxes.cls.tolist())
            print("Conf   :", r.boxes.conf.tolist())

    print("\nXONG! Kết quả đã được lưu.")


def main():
    model, device = load_model()

    try:
        if MODE.lower() == "webcam":
            run_webcam(model)
        elif MODE.lower() in ["image", "folder", "video"]:
            run_image_folder_video(model)
        else:
            print(f"MODE không hợp lệ: {MODE}")
            print("Hãy chọn 1 trong: 'image', 'folder', 'video', 'webcam'")
    except Exception as e:
        print("\nĐÃ XẢY RA LỖI KHI TEST MODEL:")
        print(e)


if __name__ == "__main__":
    main()
