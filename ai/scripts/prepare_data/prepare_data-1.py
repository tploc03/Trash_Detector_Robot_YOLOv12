import os
import random
import shutil
from tqdm import tqdm

src_images_root = 'ai/data/new-dataset-trash-type-v3'
src_labels_root = 'ai/data/label_v3'                    

dst_images_root = 'ai/data/new-dataset-trash-type-v7'
dst_labels_root = 'ai/data/label_v7'

def get_random_range(class_name):
    name = class_name.lower()
    
    # Cấu hình số lượng ảnh cần lấy để đạt được ~3500-3600 vật thể cho mỗi lớp
    # Dựa trên mật độ vật thể đã thống kê
    target_counts = {
        "paper_cardboard": 2500, # Mật độ thấp (~1.4), cần lấy nhiều ảnh
        "metal":           2500, # Mật độ thấp (~1.4), cần lấy nhiều ảnh
        "organic":         2200, # Mật độ trung bình (~1.6)
        "battery":         1500, # Mật độ cao (~2.3)
        "plastic":         1700, # Mật độ cao (~2.5)
        "glass":           1100  # Mật độ rất cao (~3.2), cần ít ảnh
    }

    # Lấy giá trị target, cộng trừ một chút random (khoảng +/- 10 ảnh) để tự nhiên hơn
    base_count = target_counts.get(name, 1500) # Mặc định 1500 nếu tên không khớp
    return random.randint(base_count - 10, base_count + 10)

def create_random_subset():
    if not os.path.exists(src_images_root):
        print("Không tìm thấy thư mục ảnh nguồn:", src_images_root)
        return

    if not os.path.exists(src_labels_root):
        print("Không tìm thấy thư mục nhãn nguồn:", src_labels_root)
        return

    classes = [
        d for d in os.listdir(src_images_root)
        if os.path.isdir(os.path.join(src_images_root, d))
    ]

    print("Các lớp tìm thấy:", classes)

    for class_name in classes:

        src_img_dir = os.path.join(src_images_root, class_name)

        # Xử lý tên thư mục label (thường thêm _txt)
        label_folder = class_name + "_txt"
        src_lbl_dir = os.path.join(src_labels_root, label_folder)

        # Fallback nếu tên thư mục label không có đuôi _txt (đề phòng)
        if not os.path.exists(src_lbl_dir):
            if os.path.exists(os.path.join(src_labels_root, class_name)):
                src_lbl_dir = os.path.join(src_labels_root, class_name)
            else:
                print(f"Không tìm thấy thư mục nhãn cho '{class_name}' → bỏ qua")
                continue

        dst_img_dir = os.path.join(dst_images_root, class_name)
        dst_lbl_dir = os.path.join(dst_labels_root, class_name) # Label đầu ra thường giữ nguyên tên class

        os.makedirs(dst_img_dir, exist_ok=True)
        os.makedirs(dst_lbl_dir, exist_ok=True)

        all_images = [
            f for f in os.listdir(src_img_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
        ]

        # Tính toán số lượng cần lấy
        target_count = get_random_range(class_name)
        
        # Đảm bảo không lấy quá số lượng file gốc đang có
        final_count = min(len(all_images), target_count)

        selected_images = random.sample(all_images, final_count)

        print(f"Lớp: {class_name:15} | Tổng gốc: {len(all_images):4} | Lấy: {final_count:4}")

        for img_file in tqdm(selected_images, desc=f"   Copying {class_name}"):
            src_img = os.path.join(src_img_dir, img_file)
            dst_img = os.path.join(dst_img_dir, img_file)
            shutil.copy2(src_img, dst_img)

            stem = os.path.splitext(img_file)[0]
            label_file = stem + ".txt"

            src_lbl = os.path.join(src_lbl_dir, label_file)
            dst_lbl = os.path.join(dst_lbl_dir, label_file)

            if os.path.exists(src_lbl):
                shutil.copy2(src_lbl, dst_lbl)
            else:
                # Nếu copy ảnh mà không có nhãn thì xóa ảnh đó đi để tránh lỗi data rỗng
                if os.path.exists(dst_img):
                    os.remove(dst_img)
                # print(f"⚠️ Ảnh '{img_file}' không có nhãn. Đã bỏ qua.") 

    print("\n✅ Hoàn tất tạo dataset v6 cân bằng!")

if __name__ == "__main__":
    create_random_subset()