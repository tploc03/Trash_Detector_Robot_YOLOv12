import os

def update_class_id_in_folder(target_folder, new_class_id):
    new_id_str = str(new_class_id)
    
    print(f"Starting processing folder: {target_folder}")
    print(f"Will replace all Class ID with: {new_id_str}")
    
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
                print(f"Error processing file {filename}: {e}")

    print(f"Updated {file_count} file.")

ID = 8


FOLDER = 'ai/data/label/trash_txt' 

if __name__ == "__main__":
    if not os.path.isdir(FOLDER):
        print(f"Folder'{FOLDER}' not found.")
    else:
        update_class_id_in_folder(FOLDER, ID)