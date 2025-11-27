import os
import random
import shutil
from tqdm import tqdm

src_images_root = 'ai/data/new-dataset-trash-type-v3'
src_labels_root = 'ai/data/label_v3'                    

dst_images_root = 'ai/data/new-dataset-trash-type-v6'
dst_labels_root = 'ai/data/label_v6'

def get_random_range(class_name):
    name = class_name.lower()

    if name == "glass":
        return random.randint(950, 1000)

    if name == "battery":
        return random.randint(1200, 1300)

    if name == "plastic":
        return random.randint(1250, 1300)

    return random.randint(1600, 1650)

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

        label_folder = class_name + "_txt"
        src_lbl_dir = os.path.join(src_labels_root, label_folder)

        if not os.path.exists(src_lbl_dir):
            print(f"Không tìm thấy thư mục nhãn '{label_folder}' → bỏ qua lớp '{class_name}'")
            continue

        dst_img_dir = os.path.join(dst_images_root, class_name)
        dst_lbl_dir = os.path.join(dst_labels_root, class_name)

        os.makedirs(dst_img_dir, exist_ok=True)
        os.makedirs(dst_lbl_dir, exist_ok=True)

        all_images = [
            f for f in os.listdir(src_img_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))
        ]

        target_count = get_random_range(class_name)
        final_count = min(len(all_images), target_count)

        selected_images = random.sample(all_images, final_count)

        print(f"Lớp: {class_name} → lấy {final_count} ảnh (rule: {target_count})")

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
                os.remove(dst_img)
                print(f"⚠️ Ảnh '{img_file}' không có nhãn. Đã xóa khỏi dataset.")

    print("\nHoàn tất")

create_random_subset()
