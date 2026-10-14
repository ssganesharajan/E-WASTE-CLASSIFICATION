"""Test script for verifying E-Waste TFLite model inference and recommendation pipeline."""
import sys
import io
import json
import numpy as np
from PIL import Image

# Fix Windows console UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import config
from main import run_classification, CLASSES_DB

def create_class_sample_image(class_id: int) -> bytes:
    """Generates a representative synthetic workbench image for a given class ID."""
    arr = np.full((224, 224, 3), 115, dtype=np.uint8)

    if class_id == 0:  # Battery: cylindrical cell with red wrap and terminal
        arr[30:194, 85:139, 0] = 200
        arr[30:194, 85:139, 1] = 30
        arr[30:194, 85:139, 2] = 30
        arr[15:30, 100:124, :] = 210
    elif class_id == 1:  # Cable & Wires: multi-colored curving lines
        for i in range(20, 200):
            x1 = int(112 + 40 * np.sin(i / 15))
            x2 = int(90 + 35 * np.cos(i / 15))
            x3 = int(130 + 30 * np.sin(i / 10))
            arr[i, max(0, x1 - 2):min(224, x1 + 3), 0] = 220
            arr[i, max(0, x2 - 2):min(224, x2 + 3), 1] = 220
            arr[i, max(0, x3 - 2):min(224, x3 + 3), 2] = 220
    elif class_id == 2:  # Charger: white wall adapter with metal prongs
        arr[60:174, 60:164, :] = 240
        arr[25:60, 80:95, :] = 160
        arr[25:60, 125:140, :] = 160
    elif class_id == 3:  # Circuit Board / PCB: green solder mask + dark chip + copper traces
        arr[30:194, 30:194, 1] = 160
        arr[30:194, 30:194, 0] = 20
        arr[30:194, 30:194, 2] = 40
        arr[70:154, 70:154, :] = 30
        arr[40:50, 40:184, 0] = 220
        arr[40:50, 40:184, 1] = 180
        arr[40:50, 40:184, 2] = 20
    elif class_id == 4:  # Headphones & Audio: headband arc and two earcups
        for i in range(50, 174):
            arr[40, i, :] = 35
        arr[70:150, 40:70, :] = 25
        arr[70:150, 154:184, :] = 25
    elif class_id == 5:  # Keyboard & Mouse: key grid
        arr[50:174, 30:194, :] = 40
        for r in range(4):
            for c in range(8):
                arr[60 + r * 25:75 + r * 25, 40 + c * 18:52 + c * 18, :] = 80
    elif class_id == 6:  # Laptop & Computer: screen above + deck below
        arr[30:110, 40:184, :] = 20
        arr[110:180, 20:204, :] = 70
    elif class_id == 7:  # Mobile Phone & Tablet: vertical dark screen rectangle
        arr[20:204, 70:154, :] = 20
        arr[15:20, 100:124, :] = 70
    elif class_id == 8:  # Monitor & Display: horizontal widescreen with stand
        arr[30:150, 20:204, :] = 20
        arr[150:185, 102:122, :] = 90
        arr[185:198, 75:149, :] = 90
    elif class_id == 9:  # Storage Devices: metallic hard disk with circular platter
        arr[30:194, 40:184, :] = 160
        for y in range(60, 164):
            for x in range(60, 164):
                if (x - 112)**2 + (y - 112)**2 < 45**2:
                    arr[y, x, :] = 220

    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG")
    return buf.getvalue()


def run_tests():
    print("========================================")
    print("  E-WASTE AI CLASSIFIER INFERENCE TEST  ")
    print("========================================")
    print(f"Total Registered Classes: {len(CLASSES_DB)}")
    for c in CLASSES_DB:
        print(f" - [{c['id']}] {c['name']} (Hazard: {c['hazard_level']})")

    print("\n------------------------------------------------------------")
    print(" Running Neuro-Symbolic Inference on 10 E-Waste Categories  ")
    print("------------------------------------------------------------")

    passed = 0
    total = len(CLASSES_DB)
    for cid in range(total):
        target_name = CLASSES_DB[cid]["name"]
        sample_bytes = create_class_sample_image(cid)
        res = run_classification(sample_bytes, source=f"Unit Test Class {cid}")
        pred_name = res["prediction"]["name"]
        pred_conf = res["prediction"]["confidence_percent"]
        pred_hazard = res["prediction"]["hazard_level"]
        latency = res["inference_time_ms"]
        is_match = (res["prediction"]["class_id"] == cid)
        if is_match:
            passed += 1
        match_symbol = "✅" if is_match else "⚠️"
        print(f"{match_symbol} Target [{cid} - {target_name:<25}] -> Predicted: {pred_name:<25} ({pred_conf}) [Lat: {latency}ms, Haz: {pred_hazard}]")

    print(f"\n[RESULTS] Accuracy: {passed}/{total} classes ({passed/total*100:.1f}%)")
    assert passed >= 8, f"Expected at least 8/10 matches, got {passed}/{total}"
    print("[SUCCESS] Multi-Class Inference Verification Complete!")


if __name__ == "__main__":
    run_tests()
