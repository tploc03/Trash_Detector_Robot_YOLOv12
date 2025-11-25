import os

def find_empty_label_files(target_folder):
    """
    Quét qua thư mục target_folder và in ra tên của
    bất kỳ file .txt nào rỗng (không có nội dung).
    """
    
    print(f"--- Bắt đầu tìm file nhãn rỗng trong: {target_folder} ---")

    if not os.path.isdir(target_folder):
        print(f"LỖI: Thư mục '{target_folder}' không tồn tại.")
        return

    empty_files_found = []

    # Lặp qua tất cả các file trong thư mục
    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            
            try:
                # Kiểm tra kích thước file
                # os.path.getsize(file_path) == 0 là cách nhanh nhất
                if os.path.getsize(file_path) == 0:
                    empty_files_found.append(filename)
                
                # Cách kiểm tra an toàn hơn (đọc file)
                # with open(file_path, 'r') as f:
                #     content = f.read()
                #     if not content.strip(): # Nếu nội dung trống hoặc chỉ có khoảng trắng
                #         empty_files_found.append(filename)
                         
            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")

    # In kết quả
    if empty_files_found:
        print(f"\n✅ Đã tìm thấy {len(empty_files_found)} file nhãn rỗng:")
        for name in empty_files_found:
            print(f"  -> {name}")
    else:
        print("\n✅ Không tìm thấy file nhãn rỗng nào.")

# --- CẤU HÌNH CỦA BẠN ---

# Đặt đường dẫn ĐÚNG đến thư mục nhãn bạn muốn KIỂM TRA
# Ví dụ: 'D:/LuanVan/dataset_raw/glass_lb'
# Hoặc: 'D:/LuanVan/trash_yolo_dataset/labels/train'
THU_MUC_CAN_KIEM_TRA = 'yolo_dataset/labels/train'

# --- GỌI HÀM ĐỂ CHẠY ---
if __name__ == "__main__":
    find_empty_label_files(THU_MUC_CAN_KIEM_TRA)