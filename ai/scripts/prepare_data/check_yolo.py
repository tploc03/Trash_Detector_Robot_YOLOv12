import os

def check_yolo_label(path):
    with open(path, "r") as f:
        lines = f.read().strip().splitlines()

    for i, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 5:
            print(f"[ERROR] {path} - line {i}: Wrong number of fields ({len(parts)})")
            continue

        cls, xc, yc, w, h = parts

        # class_id phải là số nguyên
        if not cls.isdigit():
            print(f"[ERROR] {path} - line {i}: class_id '{cls}' is not integer")

        # 4 giá trị còn lại phải là số float
        try:
            xc, yc, w, h = map(float, [xc, yc, w, h])
        except:
            print(f"[ERROR] {path} - line {i}: coordinates must be float")
            continue

        # giá trị phải nằm trong [0,1]
        for v, name in zip([xc, yc, w, h], ["xc", "yc", "w", "h"]):
            if not (0 <= v <= 1):
                print(f"[ERROR] {path} - line {i}: {name}={v} out of range [0,1]")

    print(f"[OK] Finished checking: {path}")

# chạy cho 1 folder
folder = "ai/data/label_v3/glass_txt"
for file in os.listdir(folder):
    if file.endswith(".txt"):
        check_yolo_label(os.path.join(folder, file))
