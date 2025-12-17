import os
from collections import Counter

def count_class_ids_in_folder(target_folder):
    id_counter = Counter()
    files_processed = 0
    total_instances = 0

    print(f"Start counting in folder: {target_folder}")

    if not os.path.isdir(target_folder):
        print(f"ERROR: Folder '{target_folder}' not found.")
        return

    for filename in os.listdir(target_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(target_folder, filename)
            files_processed += 1
            
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                if not lines:
                    id_counter['[EMPTY]'] += 1
                    continue

                for line in lines:
                    parts = line.strip().split()
                    if parts: 
                        class_id = parts[0]
                        id_counter[class_id] += 1
                        total_instances += 1

            except Exception as e:
                print(f"Error reading file {filename}: {e}")

    print(f"\nDone: {files_processed} file.")
    print(f"Total instances: {total_instances}\n")
    print("Class ID")
    
    if not id_counter:
        print("Can not find any Class ID.")
        return

    sorted_ids = sorted(id_counter.items(), key=lambda item: item[0])
    
    for class_id, count in sorted_ids:
        if class_id == '[EMPTY]':
            print(f"File dont have label: {count} file")
        else:
            print(f"Class ID '{class_id}': {count} instances")


THU_MUC_CAN_KIEM_TRA = 'ai/data/6_class_dataset_v7/labels/train'

if __name__ == "__main__":
    count_class_ids_in_folder(THU_MUC_CAN_KIEM_TRA)