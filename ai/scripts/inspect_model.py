import sys
import torch
import traceback
import pprint
from pathlib import Path


def inspect_model(path):
    path = Path(path)
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return

    print(f"Inspecting: {path}\n")

    # 1) Try to torch.load the checkpoint and print top-level keys
    try:
        chk = torch.load(str(path), map_location='cpu')
    except Exception as e:
        print("--- Exception while torch.load ---")
        traceback.print_exc()
        print("\nIf torch.load fails due to custom classes, try the YOLO loader next to capture its traceback.")
        chk = None

    if chk is not None:
        print("--- torch.load succeeded. Top-level object type and keys/attrs: ---")
        print(type(chk))
        try:
            if isinstance(chk, dict):
                print("dict keys:")
                pprint.pprint(list(chk.keys()))
                # Common metadata fields
                for k in ['model', 'state_dict', 'ema', 'optimizer', 'epoch', 'yaml', 'ultralytics_version']:
                    if k in chk:
                        print(f"\n-- {k} present: type={type(chk[k])}")
                        if k == 'yaml':
                            print(chk[k])
                        if k == 'ultralytics_version':
                            print('Ultralytics version in checkpoint:', chk[k])
            else:
                print('Loaded object repr:')
                print(repr(chk)[:1000])
        except Exception:
            print('Exception while inspecting checkpoint content:')
            traceback.print_exc()

    # 2) Try to load with ultralytics.YOLO to reproduce the exact error and traceback
    try:
        print('\n--- Attempting to load with ultralytics.YOLO(...) to reproduce error (will import ultralytics) ---')
        from ultralytics import YOLO
        model = YOLO(str(path))
        print('YOLO(...) loaded successfully. Model summary:')
        try:
            print(model.model)  # may be large
        except Exception:
            print('Loaded model object (print failed).')
    except Exception as e:
        print('--- Exception while loading via ultralytics.YOLO ---')
        traceback.print_exc()
        print('\nThis traceback will show where the AttributeError or missing attribute occurs.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python inspect_model.py <path/to/best.pt>')
        sys.exit(1)
    inspect_model(sys.argv[1])
