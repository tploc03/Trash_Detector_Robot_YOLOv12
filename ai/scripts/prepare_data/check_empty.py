import os

def find_empty_label_files(target_folder):
    print(f"Start: {target_folder}")

    if not os.path.isdir(target_folder):
        print(f"ERROR: Folder '{target_folder}' not found.")
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
        print(f"\nFound {len(empty_files_found)} empty label files:")
        for name in empty_files_found:
            print(f"  -> {name}")
    else:
        print("\nNo empty label files found.")
FOLDER = 'yolo_dataset/labels/train'

if __name__ == "__main__":
    find_empty_label_files(FOLDER)