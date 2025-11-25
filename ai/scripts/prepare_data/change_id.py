import os

def update_class_id_in_folder(target_folder, new_class_id):
    """
    Quét qua tất cả các file .txt trong một thư mục và
    thay thế chữ số đầu tiên (class ID) của mỗi dòng bằng new_class_id.
    """
    
    # Đảm bảo new_class_id là một chuỗi (string) để ghi vào file
    new_id_str = str(new_class_id)
    
    print(f"Bắt đầu xử lý thư mục: {target_folder}")
    print(f"Sẽ thay thế tất cả Class ID thành: {new_id_str}")
    
    file_count = 0
    
    # Lặp qua tất cả các file trong thư mục
    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            
            new_lines = []
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                # Đọc từng dòng, sửa, rồi lưu vào list new_lines
                for line in lines:
                    parts = line.strip().split()
                    
                    if len(parts) > 1: # Đảm bảo dòng có nội dung (ít nhất là ID + 1 tọa độ)
                        # Giữ nguyên 4 tọa độ cuối, chỉ thay ID đầu tiên
                        new_line = f"{new_id_str} {parts[1]} {parts[2]} {parts[3]} {parts[4]}\n"
                        new_lines.append(new_line)
                    else:
                        # Giữ nguyên các dòng trống (nếu có)
                        new_lines.append(line)
                
                # Ghi đè file cũ với nội dung đã được sửa
                with open(file_path, 'w') as f:
                    f.writelines(new_lines)
                
                file_count += 1

            except Exception as e:
                print(f"Lỗi khi xử lý file {filename}: {e}")

    print(f"Hoàn tất! Đã cập nhật {file_count} file trong thư mục.")

ID_MOI_MONG_MUON = 5

# 2. Đặt đường dẫn ĐÚNG đến thư mục nhãn bạn muốn SỬA
# (Nhớ dùng dấu / hoặc \\)
THU_MUC_CAN_SUA = 'ai/data/label_v3/plastic_txt' 

# --- GỌI HÀM ĐỂ CHẠY ---
if __name__ == "__main__":
    if not os.path.isdir(THU_MUC_CAN_SUA):
        print(f"LỖI: Thư mục '{THU_MUC_CAN_SUA}' không tồn tại. Hãy kiểm tra lại đường dẫn.")
    else:
        update_class_id_in_folder(THU_MUC_CAN_SUA, ID_MOI_MONG_MUON)