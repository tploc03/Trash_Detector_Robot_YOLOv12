# check_labels.py
import os

# 👉 CHỈ CẦN ĐỔI TÊN FOLDER Ở ĐÂY
LABELS_DIR = r"ai/data/6_class_dataset/labels/train"

# 👉 Nếu có n lớp, nhập số lớp vào đây, ví dụ 6 lớp → NUM_CLASSES = 6
NUM_CLASSES = 6  

def check_label(path):
    info = {"path": path, "ok": True, "errors": []}

    with open(path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    if len(lines) == 0:
        info["errors"].append("File rỗng")
        info["ok"] = False
        return info

    for i, line in enumerate(lines, 1):
        parts = line.split()
        if len(parts) != 5:
            info["errors"].append(f"Dòng {i}: Phải có đúng 5 giá trị (class, xc, yc, w, h)")
            info["ok"] = False
            continue

        cls, xc, yc, w, h = parts

        # class id phải là số nguyên
        if not cls.isdigit():
            info["errors"].append(f"Dòng {i}: class_id '{cls}' không phải số nguyên")
            info["ok"] = False
        else:
            cid = int(cls)
            if cid < 0 or cid >= NUM_CLASSES:
                info["errors"].append(f"Dòng {i}: class_id {cid} vượt giới hạn 0–{NUM_CLASSES-1}")
                info["ok"] = False

        # tọa độ phải là số float
        try:
            xc = float(xc); yc = float(yc)
            w = float(w); h = float(h)
        except:
            info["errors"].append(f"Dòng {i}: Tọa độ phải là số thực")
            info["ok"] = False
            continue

        # phải nằm trong [0,1]
        for name, v in zip(["xc","yc","w","h"], [xc,yc,w,h]):
            if not (0 <= v <= 1):
                info["errors"].append(f"Dòng {i}: {name}={v} không nằm trong [0,1]")
                info["ok"] = False

    return info

def main():
    if not os.path.isdir(LABELS_DIR):
        print("❌ Folder nhãn không tồn tại:", LABELS_DIR)
        return

    txts = [os.path.join(LABELS_DIR, f) for f in os.listdir(LABELS_DIR) if f.endswith(".txt")]

    results = []
    for t in txts:
        results.append(check_label(t))

    bad = [r for r in results if not r["ok"]]

    print("===== KẾT QUẢ KIỂM TRA LABEL =====")
    print("Tổng file nhãn:", len(results))
    print("File lỗi:", len(bad))

    if bad:
        print("\nDanh sách tối đa 10 file lỗi:")
        for b in bad[:100]:
            print(" •", b["path"])
            for e in b["errors"][:5]:
                print("    →", e)

if __name__ == "__main__":
    main()
