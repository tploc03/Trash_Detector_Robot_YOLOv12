import os

def find_empty_label_files(target_folder):
    print(f"Bắt đầu tìm file nhãn rỗng trong: {target_folder}")

    if not os.path.isdir(target_folder):
        print(f"LỖI: Thư mục '{target_folder}' không tồn tại.")
        return

    empty_files_found = []

    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            
            try:
                if os.path.getsize(file_path) == 0:
                    empty_files_found.append(filename)
                
                # with open(file_path, 'r') as f:
                #     content = f.read()
                #     if not content.strip():
                #         empty_files_found.append(filename)
                         
            except Exception as e:
                print(f"Lỗi khi đọc file {filename}: {e}")

    if empty_files_found:
        print(f"\n✅ Đã tìm thấy {len(empty_files_found)} file nhãn rỗng:")
        for name in empty_files_found:
            print(f"  -> {name}")
    else:
        print("\n✅ Không tìm thấy file nhãn rỗng nào.")

FOLDER = 'yolo_dataset/labels/train'

if __name__ == "__main__":
    find_empty_label_files(FOLDER)