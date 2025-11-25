import os
import shutil
import random

# Thư mục nhãn
LABEL_DIR = "ai/data/label_v4"

# Thư mục ảnh
IMAGE_DIR = "ai/data/new-dataset-trash-type-v4"

# Thư mục output theo format YOLO
OUTPUT_DIR = "6_class_dataset_v2"

# Danh sách class theo đúng thứ tự bạn dùng để gán ID
CLASSES = [
    "battery",
    "glass",
    "metal",
    "organic",
    "paper_cardboard",
    "plastic"
]

TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

def ensure_dirs():
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(OUTPUT_DIR, "images", split), exist_ok=True)
        os.makedirs(os.path.join(OUTPUT_DIR, "labels", split), exist_ok=True)

def process_class(class_name, class_id):
    print(f"Processing class: {class_name} (ID={class_id})")

    img_folder = os.path.join(IMAGE_DIR, class_name)
    lbl_folder = os.path.join(LABEL_DIR, class_name)

    img_files = sorted(os.listdir(img_folder))

    paired_list = []
    for img in img_files:
        base = os.path.splitext(img)[0]
        label_file = base + ".txt"
        label_path = os.path.join(lbl_folder, label_file)
        img_path = os.path.join(img_folder, img)

        if not os.path.exists(label_path):
            print(f"[WARN] Missing label for {img}")
            continue

        paired_list.append((img_path, label_path))

    random.shuffle(paired_list)

    total = len(paired_list)
    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    splits = {
        "train": paired_list[:train_end],
        "val": paired_list[train_end:val_end],
        "test": paired_list[val_end:]
    }

    for split_name, items in splits.items():
        for img_path, lbl_path in items:

            img_name = os.path.basename(img_path)
            lbl_name = os.path.basename(lbl_path)

            # Copy ảnh
            shutil.copy(img_path, os.path.join(OUTPUT_DIR, "images", split_name, img_name))

            # Copy label
            shutil.copy(lbl_path, os.path.join(OUTPUT_DIR, "labels", split_name, lbl_name))

    print(f" -> Finished {class_name}: {total} files")

def write_classes_txt():
    with open(os.path.join(OUTPUT_DIR, "classes.txt"), "w") as f:
        for c in CLASSES:
            f.write(c + "\n")

def main():
    ensure_dirs()
    write_classes_txt()

    for idx, class_name in enumerate(CLASSES):
        process_class(class_name, idx)

    print("\n✔ Dataset chuẩn YOLO đã sẵn sàng tại thư mục:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
