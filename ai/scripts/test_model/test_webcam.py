import os
import torch
import types
from ultralytics import YOLO


MODEL_PATH = r"ai/runs/yolov12_trash_detection/weights/best.pt"

MODE = "webcam"


SOURCE = r"D:/ploc/test_images" 

IMAGE_SIZE = 640

CONF_THRES = 0.3

SAVE_DIR = r"D:/ploc/test_results"
RUN_NAME = "trash_yolov12_test"


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Can not find model at: {MODEL_PATH}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        device = 0
    else:
        device = "cpu"

    print("Load model from:", MODEL_PATH)
    model = YOLO(MODEL_PATH)

    def fix_aattn_compat(m):
        for mod in m.model.modules():
            if mod.__class__.__name__ == 'AAttn':
                if not hasattr(mod, 'qkv') and hasattr(mod, 'qk') and hasattr(mod, 'v'):
                    def _qkv(self, x):
                        qk_out = self.qk(x)
                        v_out = self.v(x)
                        return torch.cat([qk_out, v_out], dim=1)
                    mod.qkv = types.MethodType(_qkv, mod)

    try:
        fix_aattn_compat(model)
    except Exception:
        pass

    print("Load model successfully.\n")

    return model, device


def run_webcam(model):
    print("'q' to quit.\n")

    results = model.predict(
        source=0,
        show=True,
        stream=True,
        conf=CONF_THRES,
        imgsz=IMAGE_SIZE
    )

    try:
        for r in results:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        import cv2
        cv2.destroyAllWindows()
        print("Quit.")


def run_image_folder_video(model):
    if not os.path.exists(SOURCE):
        raise FileNotFoundError(f"Can not find SOURCE: {SOURCE}")

    print(f"Start predict with SOURCE: {SOURCE}")
    print(f"Results will be saved in: {SAVE_DIR}/{RUN_NAME}")

    results = model.predict(
        source=SOURCE,
        imgsz=IMAGE_SIZE,
        conf=CONF_THRES,
        save=True,
        project=SAVE_DIR,
        name=RUN_NAME,
        exist_ok=True, 
        show=True
    )

    for r in results:
        print("-" * 50)
        print("File:", r.path)
        print("Số bbox:", len(r.boxes))
        if len(r.boxes):
            print("Classes:", r.boxes.cls.tolist())
            print("Conf   :", r.boxes.conf.tolist())


def main():
    model, device = load_model()

    try:
        if MODE.lower() == "webcam":
            run_webcam(model)
        elif MODE.lower() in ["image", "folder", "video"]:
            run_image_folder_video(model)
        else:
            print(f"MODE : {MODE}")
            print("Choose one of: 'image', 'folder', 'video', 'webcam'")
    except Exception as e:
        print("\nERROR TEST MODEL:")
        print(e)


if __name__ == "__main__":
    main()
