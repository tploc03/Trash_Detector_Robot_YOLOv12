import os
from ultralytics import YOLO
import torch

DATA_YAML_PATH = r"D:/LocTP/data.yaml"

def train_local():
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"Thiết bị huấn luyện: {device} ({torch.cuda.get_device_name(0) if device == '0' else 'CPU'})")

    model = YOLO('yolov12n.pt') 

    print("Start")

    results = model.train(
        data=DATA_YAML_PATH,
        
        epochs=300,
        patience=40,
        batch=16,
        imgsz=640,
        workers=2,
        device=device,
        
        cache=False,
        amp=True,
        
        close_mosaic=20,
        flipud=0.0,
        fliplr=0.5,
        
        project='Trash_Detection_Project',
        name='yolov12_trash_detection',
        exist_ok=True,
        plots=True,
        save=True
    )

    print(f"Done, Save at: {results.save_dir}")

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    
    train_local()