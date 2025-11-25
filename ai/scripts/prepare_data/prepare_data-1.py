import os
import random
import shutil
from tqdm import tqdm

# --- CẤU HÌNH ĐƯỜNG DẪN (Bạn sửa lại chỗ này nhé) ---
# Folder gốc chứa dữ liệu CŨ
src_images_root = 'ai/data/new-dataset-trash-type-v3'  # Tên folder ảnh gốc
src_labels_root = 'ai/data/label_v3'                # Tên folder nhãn gốc

# Folder MỚI chứa dữ liệu rút gọn
dst_images_root = 'ai/data/6_class_dataset_simple/images'
dst_labels_root = 'ai/data/6_class_dataset_simple/labels'

def create_random_subset():
    # 1. Kiểm tra folder gốc
    if not os.path.exists(src_images_root) or not os.path.exists(src_labels_root):
        print(f"❌ Lỗi: Không tìm thấy folder gốc '{src_images_root}' hoặc '{src_labels_root}'")
        return

    # 2. Lấy danh sách các lớp từ folder ẢNH (battery, glass, metal...)
    # Chỉ lấy các folder con, bỏ qua file lạ
    classes = [d for d in os.listdir(src_images_root) if os.path.isdir(os.path.join(src_images_root, d))]
    
    print(f"📂 Tìm thấy {len(classes)} lớp ảnh: {classes}")
    print("-" * 50)

    for class_name in classes:
        # --- BƯỚC 1: XÁC ĐỊNH ĐƯỜNG DẪN ---
        # Đường dẫn ảnh nguồn (ví dụ: .../new-dataset-trash-type-v3/battery)
        current_src_img_dir = os.path.join(src_images_root, class_name)
        
        # Đường dẫn nhãn nguồn (Tự động thêm đuôi '_txt' để khớp với folder nhãn)
        # Ví dụ: ảnh là 'battery' -> nhãn là 'battery_txt'
        label_folder_name = class_name + "_txt"
        current_src_lbl_dir = os.path.join(src_labels_root, label_folder_name)
        
        # Kiểm tra xem folder nhãn có tồn tại không
        if not os.path.exists(current_src_lbl_dir):
            print(f"⚠️ Cảnh báo: Không tìm thấy folder nhãn '{label_folder_name}' cho lớp '{class_name}'. Bỏ qua!")
            continue

        # Đường dẫn đích (Nơi lưu file sau khi copy)
        # Lưu ý: Folder đích mình sẽ để tên giống hệt folder nguồn cho gọn (bỏ đuôi _txt đi cũng được)
        current_dst_img_dir = os.path.join(dst_images_root, class_name)
        current_dst_lbl_dir = os.path.join(dst_labels_root, class_name) # Nhãn đích để tên giống ảnh đích luôn cho chuẩn YOLO

        # Tạo folder đích
        os.makedirs(current_dst_img_dir, exist_ok=True)
        os.makedirs(current_dst_lbl_dir, exist_ok=True)

        # --- BƯỚC 2: LẤY DANH SÁCH VÀ RANDOM ---
        # Lấy tất cả file ảnh
        all_images = [f for f in os.listdir(current_src_img_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        # Random số lượng cần lấy (từ 1400 đến 1700)
        target_count = random.randint(1400, 1700)
        
        # Nếu số ảnh thực tế ít hơn target thì lấy hết
        final_count = min(len(all_images), target_count)
        
        # Bốc ngẫu nhiên
        selected_images = random.sample(all_images, final_count)
        
        print(f"🔄 Đang xử lý lớp '{class_name}': Lấy {final_count} ảnh (Random từ 1400-1700)...")

        # --- BƯỚC 3: COPY FILE ---
        for img_file in tqdm(selected_images, desc=f"   Copying {class_name}"):
            # 1. Copy Ảnh
            src_img_path = os.path.join(current_src_img_dir, img_file)
            dst_img_path = os.path.join(current_dst_img_dir, img_file)
            shutil.copy2(src_img_path, dst_img_path)

            # 2. Copy Nhãn
            # Tên file nhãn = Tên file ảnh (bỏ đuôi) + .txt
            file_stem = os.path.splitext(img_file)[0]
            label_file = file_stem + ".txt"
            
            src_lbl_path = os.path.join(current_src_lbl_dir, label_file)
            dst_lbl_path = os.path.join(current_dst_lbl_dir, label_file)

            if os.path.exists(src_lbl_path):
                shutil.copy2(src_lbl_path, dst_lbl_path)
            else:
                # (Tùy chọn) Xóa ảnh vừa copy nếu không có nhãn để đảm bảo dữ liệu sạch 100%
                # os.remove(dst_img_path) 
                pass

    print("\n✅ HOÀN TẤT! Đã tạo xong dataset rút gọn.")

# Chạy hàm
create_random_subset()