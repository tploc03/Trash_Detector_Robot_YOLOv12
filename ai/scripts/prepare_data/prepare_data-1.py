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
    
    target_counts = {
        "paper_cardboard": 2500,
        "metal":           2500,
        "organic":         2200,
        "battery":         1500,
        "plastic":         1700,
        "glass":           1100
    }

    base_count = target_counts.get(name, 1500)
    return random.randint(base_count - 10, base_count + 10)

def create_random_subset():
    if not os.path.exists(src_images_root):
        print("Can not find folder:", src_images_root)
        return

    if not os.path.exists(src_labels_root):
        print("Can not find label folder:", src_labels_root)
        return

    classes = [
        d for d in os.listdir(src_images_root)
        if os.path.isdir(os.path.join(src_images_root, d))
    ]

    print("Found classes:", classes)

    for class_name in classes:

        src_img_dir = os.path.join(src_images_root, class_name)

        label_folder = class_name + "_txt"
        src_lbl_dir = os.path.join(src_labels_root, label_folder)

        if not os.path.exists(src_lbl_dir):
            if os.path.exists(os.path.join(src_labels_root, class_name)):
                src_lbl_dir = os.path.join(src_labels_root, class_name)
            else:
                print(f"Can not find label folder for '{class_name}' → skip")
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

        print(f"Class: {class_name:15} | Original count: {len(all_images):4} | Selected: {final_count:4}")

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
                if os.path.exists(dst_img):
                    os.remove(dst_img)

    print("\nDone")

if __name__ == "__main__":
    create_random_subset()