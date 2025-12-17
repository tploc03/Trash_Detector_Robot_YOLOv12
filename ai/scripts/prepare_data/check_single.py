import os

IMAGE_DIR = "new-dataset-trash-type-v2\\metal"
LABEL_DIR = "label\\metal_txt"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def get_all_images(root):
    images = {}
    for cls in os.listdir(root):
        folder = os.path.join(root, cls)
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            name, ext = os.path.splitext(f)
            if ext.lower() in IMAGE_EXT:
                images[name] = os.path.join(folder, f)
    return images

def get_all_labels(root):
    labels = {}
    for cls in os.listdir(root):
        folder = os.path.join(root, cls)
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            name, ext = os.path.splitext(f)
            if ext.lower() == ".txt":
                labels[name] = os.path.join(folder, f)
    return labels

def main():

    img_dict = get_all_images(IMAGE_DIR)
    lbl_dict = get_all_labels(LABEL_DIR)

    img_names = set(img_dict.keys())
    lbl_names = set(lbl_dict.keys())

    missing_labels = img_names - lbl_names
    missing_images = lbl_names - img_names
    matched = img_names & lbl_names

    print("Total image:", len(img_names))
    print("Total labels:", len(lbl_names))
    print("Matched images and labels:", len(matched))

    print("Images missing labels:")
    for name in sorted(missing_labels):
        print(" -", img_dict[name])
    if not missing_labels:
        print("None.")


    print("Labels missing images:")
    for name in sorted(missing_images):
        print(" -", lbl_dict[name])
    if not missing_images:
        print("None.")

    print("Matched images and labels:", len(matched))
    # for name in sorted(matched):
    #     print(" -", name)

if __name__ == "__main__":
    main()
