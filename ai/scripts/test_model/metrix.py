import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import yaml
from pathlib import Path

def analyze_yolo_dataset(dataset_path, data_yaml_path=None, img_formats=None):
    """
    Hàm thống kê và vẽ biểu đồ cho dataset YOLO.
    
    Args:
        dataset_path (str): Đường dẫn đến thư mục chứa data (bao gồm images và labels).
        data_yaml_path (str): Đường dẫn file data.yaml để lấy tên class (tùy chọn).
    """
    if img_formats is None:
        img_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']

    # 1. Lấy danh sách tên class (nếu có file yaml)
    class_names = {}
    if data_yaml_path and os.path.exists(data_yaml_path):
        try:
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if 'names' in data:
                    class_names = data['names']
                    print(f"✅ Đã tải tên {len(class_names)} lớp từ {data_yaml_path}")
        except Exception as e:
            print(f"⚠️ Không đọc được file yaml: {e}")

    # 2. Quét file ảnh và nhãn
    print(f"\n🔄 Đang quét thư mục: {dataset_path} ...")
    
    image_files = []
    label_files = []
    
    # Đệ quy tìm tất cả file
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in img_formats:
                image_files.append(os.path.join(root, file))
            elif ext == '.txt' and file != 'classes.txt': # Bỏ qua classes.txt nếu có
                label_files.append(os.path.join(root, file))

    num_images = len(image_files)
    num_labels = len(label_files)

    print(f"📊 TỔNG QUAN:")
    print(f"   - Số lượng ảnh tìm thấy: {num_images}")
    print(f"   - Số lượng file nhãn (.txt): {num_labels}")

    if num_labels == 0:
        print("❌ Không tìm thấy file nhãn nào. Vui lòng kiểm tra đường dẫn.")
        return

    # 3. Đọc nội dung nhãn để thống kê
    class_counts = Counter()
    total_objects = 0
    empty_labels = 0

    for label_file in label_files:
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
                if not lines:
                    empty_labels += 1
                    continue
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 1:
                        class_id = int(parts[0]) # YOLO format: class_id x y w h
                        class_counts[class_id] += 1
                        total_objects += 1
        except Exception as e:
            print(f"⚠️ Lỗi đọc file {label_file}: {e}")

    print(f"   - Tổng số vật thể (Objects): {total_objects}")
    print(f"   - Số ảnh không có vật thể (Empty): {empty_labels}")
    print(f"   - Trung bình vật thể/ảnh: {total_objects/num_images:.2f}" if num_images > 0 else "   - Trung bình: 0")

    # 4. Chuẩn bị dữ liệu vẽ biểu đồ
    # Sắp xếp theo class_id
    sorted_classes = sorted(class_counts.items())
    
    labels = []
    counts = []
    
    print("\n📋 CHI TIẾT TỪNG LỚP:")
    print(f"{'ID':<5} {'Tên Class':<20} {'Số lượng':<10} {'Tỉ lệ':<10}")
    print("-" * 50)
    
    for cls_id, count in sorted_classes:
        # Lấy tên class từ yaml hoặc dùng ID nếu không có
        name = class_names.get(cls_id, str(cls_id))
        if isinstance(class_names, list) and cls_id < len(class_names):
             name = class_names[cls_id]
             
        labels.append(name)
        counts.append(count)
        percentage = (count / total_objects) * 100
        print(f"{cls_id:<5} {name:<20} {count:<10} {percentage:.2f}%")

    # 5. Vẽ biểu đồ
    sns.set_style("whitegrid")
    plt.figure(figsize=(14, 6))

    # Biểu đồ cột (Bar Chart)
    plt.subplot(1, 2, 1)
    barplot = sns.barplot(x=labels, y=counts, palette="viridis", hue=labels, legend=False)
    plt.title("Phân bố số lượng vật thể theo lớp", fontsize=14, fontweight='bold')
    plt.xlabel("Tên lớp")
    plt.ylabel("Số lượng")
    plt.xticks(rotation=45)
    
    # Thêm số liệu trên đỉnh cột
    for p in barplot.patches:
        barplot.annotate(f'{int(p.get_height())}', 
                         (p.get_x() + p.get_width() / 2., p.get_height()), 
                         ha = 'center', va = 'center', 
                         xytext = (0, 9), 
                         textcoords = 'offset points')

    # Biểu đồ tròn (Pie Chart)
    plt.subplot(1, 2, 2)
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title("Tỉ lệ phần trăm các lớp", fontsize=14, fontweight='bold')

    plt.tight_layout()
    
    # Lưu biểu đồ
    save_path = "thong_ke_du_lieu.png"
    plt.savefig(save_path)
    print(f"\n✅ Đã lưu biểu đồ thống kê tại: {save_path}")
    plt.show()

if __name__ == "__main__":
    MY_DATASET_PATH = r"ai/data/final_yolo_trash-dataset" 
    
    MY_YAML_PATH = r"ai/scripts/test_model/final_data copy.yaml"
    
    analyze_yolo_dataset(MY_DATASET_PATH, MY_YAML_PATH)