import os

def update_class_id_in_folder(target_folder, new_class_id):
    new_id_str = str(new_class_id)
    
    print(f"Bắt đầu xử lý thư mục: {target_folder}")
    print(f"Sẽ thay thế tất cả Class ID thành: {new_id_str}")
    
    file_count = 0
    
    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            
            new_lines = []
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    parts = line.strip().split()
                    
                    if len(parts) > 1:
                        new_line = f"{new_id_str} {parts[1]} {parts[2]} {parts[3]} {parts[4]}\n"
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                
                with open(file_path, 'w') as f:
                    f.writelines(new_lines)
                
                file_count += 1

            except Exception as e:
                print(f"Lỗi khi xử lý file {filename}: {e}")

    print(f"Đã cập nhật {file_count} file trong thư mục.")

ID = 5


FOLDER = 'ai/data/label_v3/plastic_txt' 

if __name__ == "__main__":
    if not os.path.isdir(FOLDER):
        print(f"Thư mục '{FOLDER}' không tồn tại.")
    else:
        update_class_id_in_folder(FOLDER, ID)