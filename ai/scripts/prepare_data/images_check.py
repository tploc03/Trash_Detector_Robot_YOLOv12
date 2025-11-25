# check_images.py
import os
from PIL import Image, UnidentifiedImageError

# 👉 CHỈ CẦN ĐỔI FOLDER Ở ĐÂY
IMAGES_DIR = r"ai/data/6_class_dataset/images/train"

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

def check_image(path):
    info = {"path": path, "ok": True, "error": None, "size": None}
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            w, h = im.size
            info["size"] = (w, h)
    except UnidentifiedImageError:
        info["ok"] = False
        info["error"] = "Ảnh hỏng / không đọc được"
    except Exception as e:
        info["ok"] = False
        info["error"] = str(e)
    return info

def main():
    if not os.path.isdir(IMAGES_DIR):
        print("❌ Folder ảnh không tồn tại:", IMAGES_DIR)
        return

    results = []
    for f in os.listdir(IMAGES_DIR):
        ext = os.path.splitext(f.lower())[1]
        if ext in VALID_EXTS:
            full = os.path.join(IMAGES_DIR, f)
            results.append(check_image(full))

    bad = [r for r in results if not r["ok"]]
    sizes = {}
    for r in results:
        if r["size"]:
            sizes[r["size"]] = sizes.get(r["size"], 0) + 1

    print("===== KẾT QUẢ KIỂM TRA ẢNH =====")
    print("Tổng ảnh:", len(results))
    print("Ảnh lỗi:", len(bad))

    if bad:
        print("\nẢnh lỗi (tối đa 10):")
        for b in bad[:10]:
            print(" -", b["path"], "=>", b["error"])

    print("\nKích thước ảnh gặp phải:")
    for size, count in sizes.items():
        print(f" - {size}: {count} ảnh")

if __name__ == "__main__":
    main()
