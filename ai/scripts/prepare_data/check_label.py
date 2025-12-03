import os
from collections import Counter

def count_class_ids_in_folder(target_folder):
    """
    Đọc tất cả các file .txt trong một thư mục,
    đếm số lượng của mỗi Class ID (số đầu tiên của mỗi dòng).
    """
    
    # Counter là một công cụ đặc biệt để đếm
    id_counter = Counter()
    files_processed = 0
    total_instances = 0

    print(f"--- Bắt đầu thống kê thư mục: {target_folder} ---")

    if not os.path.isdir(target_folder):
        print(f"LỖI: Thư mục '{target_folder}' không tồn tại.")
        return

    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            files_processed += 1
            
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    # Đếm các file trống (ảnh không có nhãn - negative images)
                    id_counter['[FILE_RONG]'] += 1
                    continue

                for line in lines:
                    parts = line.strip().split()
                    if parts: # Đảm bảo dòng không trống
                        class_id = parts[0]
                        id_counter[class_id] += 1
                        total_instances += 1

            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")

    print(f"\n✅ Hoàn tất! Đã xử lý {files_processed} file.")
    print(f"Tổng số vật thể (instances) đã đếm: {total_instances}\n")
    print("--- Kết quả thống kê Class ID ---")
    
    if not id_counter:
        print("Không tìm thấy Class ID nào.")
        return

    # Sắp xếp kết quả cho dễ đọc
    sorted_ids = sorted(id_counter.items(), key=lambda item: item[0])
    
    for class_id, count in sorted_ids:
        if class_id == '[FILE_RONG]':
            print(f"Các file không có nhãn (ảnh nền): {count} file")
        else:
            print(f"Class ID '{class_id}': {count} vật thể (instances)")

# --- CẤU HÌNH CỦA BẠN ---

# Đặt đường dẫn ĐÚNG đến thư mục nhãn bạn muốn KIỂM TRA
# Ví dụ: 'D:/LuanVan/dataset_raw/glass_lb' (để kiểm tra sau khi sửa)
# Hoặc: 'D:/LuanVan/trash_yolo_dataset/labels/train' (để kiểm tra bộ gộp)
THU_MUC_CAN_KIEM_TRA = 'ai/data/6_class_dataset_v7/labels/train'

# --- GỌI HÀM ĐỂ CHẠY ---
if __name__ == "__main__":
    count_class_ids_in_folder(THU_MUC_CAN_KIEM_TRA)