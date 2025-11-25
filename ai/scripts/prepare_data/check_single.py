import os

IMAGE_DIR = "new-dataset-trash-type-v2\\metal"   # Thư mục chứa ảnh
LABEL_DIR = "label\\metal_txt"                        # Thư mục chứa txt nhãn

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def get_all_images(root):
    images = {}
    for cls in os.listdir(root):
        folder = os.path.join(root, cls)
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            name, ext = os.path.splitext(f)
            if ext.lower() in IMAGE_EXT:
                images[name] = os.path.join(folder, f)
    return images

def get_all_labels(root):
    labels = {}
    for cls in os.listdir(root):
        folder = os.path.join(root, cls)
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            name, ext = os.path.splitext(f)
            if ext.lower() == ".txt":
                labels[name] = os.path.join(folder, f)
    return labels

def main():
    print("Đang kiểm tra dữ liệu...\n")

    img_dict = get_all_images(IMAGE_DIR)
    lbl_dict = get_all_labels(LABEL_DIR)

    img_names = set(img_dict.keys())
    lbl_names = set(lbl_dict.keys())

    missing_labels = img_names - lbl_names
    missing_images = lbl_names - img_names
    matched = img_names & lbl_names

    print("📌 Tổng số ảnh:", len(img_names))
    print("📌 Tổng số nhãn:", len(lbl_names))
    print("📌 Ảnh & nhãn khớp:", len(matched))
    print("\n====================================\n")

    # 1. Ảnh không có nhãn
    print("❌ ẢNH THIẾU NHÃN:")
    for name in sorted(missing_labels):
        print(" -", img_dict[name])
    if not missing_labels:
        print(" → Không có.")

    print("\n====================================\n")

    # 2. Nhãn không có ảnh
    print("❌ NHÃN THIẾU ẢNH:")
    for name in sorted(missing_images):
        print(" -", lbl_dict[name])
    if not missing_images:
        print(" → Không có.")

    print("\n====================================\n")

    # 3. Những cặp đầy đủ
    print("✔ ẢNH + NHÃN ĐẦY ĐỦ:", len(matched))
    # (Nếu muốn in chi tiết thì mở comment dòng dưới)
    # for name in sorted(matched):
    #     print(" -", name)

if __name__ == "__main__":
    main()
