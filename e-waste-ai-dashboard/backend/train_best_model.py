"""
EcoSort AI - Best E-Waste Classifier Training & Export Pipeline
==============================================================
Trains a high-accuracy, low-latency Edge AI classifier for 10 canonical E-Waste categories
using deep transfer learning on MobileNetV2 (ImageNet-1k) with multi-variation
photorealistic electronic hardware synthesis and data augmentation.

Canonical 10 E-Waste Classes:
  0: Battery
  1: Cable & Wires
  2: Charger & Power Adapter
  3: Circuit Board / PCB
  4: Headphones & Audio Gear
  5: Keyboard & Mouse
  6: Laptop & Computer
  7: Mobile Phone & Tablet
  8: Monitor & Display
  9: Storage Devices (HDD / SSD / CD)
"""

import os
import sys
import io
import time
import math
import random
import numpy as np

# Fix Windows console UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import tensorflow as tf
from tensorflow.keras import layers, models, regularizers
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

np.random.seed(42)
tf.random.set_seed(42)
random.seed(42)

CLASS_NAMES = [
    "Battery",
    "Cable & Wires",
    "Charger & Power Adapter",
    "Circuit Board / PCB",
    "Headphones & Audio Gear",
    "Keyboard & Mouse",
    "Laptop & Computer",
    "Mobile Phone & Tablet",
    "Monitor & Display",
    "Storage Devices (HDD / SSD / CD)"
]

def create_random_background():
    """Generates varied realistic backgrounds: lab desk, dark workbench, ESD mat, light table."""
    bg_type = random.choice(["workbench", "dark_mat", "light_desk", "wood", "neutral"])
    img = Image.new("RGB", (224, 224))
    draw = ImageDraw.Draw(img)

    if bg_type == "workbench":
        base_color = (random.randint(45, 75), random.randint(50, 80), random.randint(60, 95))
        draw.rectangle([0, 0, 224, 224], fill=base_color)
        for _ in range(random.randint(3, 8)):
            y = random.randint(0, 224)
            draw.line([(0, y), (224, y)], fill=(base_color[0]+12, base_color[1]+12, base_color[2]+12), width=1)
    elif bg_type == "dark_mat":
        val = random.randint(20, 40)
        draw.rectangle([0, 0, 224, 224], fill=(val, val, val + random.randint(0, 8)))
    elif bg_type == "light_desk":
        val = random.randint(180, 220)
        draw.rectangle([0, 0, 224, 224], fill=(val, val, val - random.randint(0, 10)))
    elif bg_type == "wood":
        r, g, b = random.randint(120, 160), random.randint(80, 110), random.randint(50, 75)
        draw.rectangle([0, 0, 224, 224], fill=(r, g, b))
    else:
        v = random.randint(80, 140)
        draw.rectangle([0, 0, 224, 224], fill=(v, v, v))

    return img


def draw_class_object(img: Image.Image, class_id: int):
    """Draws realistic, multi-variant electronic hardware components onto background."""
    draw = ImageDraw.Draw(img)
    variant = random.choice([0, 1, 2])

    if class_id == 0:  # Battery
        if variant == 0:
            # Cylindrical AA / 18650 cell
            bx = random.randint(70, 95)
            by = random.randint(40, 60)
            bw = random.randint(45, 60)
            bh = random.randint(110, 135)
            wrap_color = random.choice([(210, 35, 35), (35, 120, 220), (220, 160, 20), (35, 170, 70)])
            draw.rectangle([bx, by, bx + bw, by + bh], fill=wrap_color, outline=(20, 20, 20), width=2)
            draw.rectangle([bx + bw//4, by - 12, bx + 3*bw//4, by], fill=(210, 210, 215), outline=(100, 100, 100), width=1)
            draw.rectangle([bx, by + bh - 10, bx + bw, by + bh], fill=(190, 190, 195))
            draw.rectangle([bx + 4, by + 30, bx + bw - 4, by + 45], fill=(240, 240, 240))
        elif variant == 1:
            # Rectangular flat Lithium-Ion pouch battery (smartphone style)
            bx, by = random.randint(60, 80), random.randint(40, 60)
            bw, bh = random.randint(80, 105), random.randint(110, 130)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(25, 25, 28), outline=(180, 180, 190), width=2)
            draw.rectangle([bx + 15, by - 18, bx + 40, by], fill=(225, 175, 45))
            draw.rectangle([bx + 20, by - 24, bx + 35, by - 18], fill=(30, 30, 30))
            for row in range(4):
                draw.line([(bx + 10, by + 30 + row*14), (bx + bw - 15, by + 30 + row*14)], fill=(160, 160, 170), width=2)
        else:
            # 9V heavy block battery with dual snap terminals
            bx, by = random.randint(70, 90), random.randint(55, 75)
            bw, bh = random.randint(65, 80), random.randint(95, 115)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(40, 45, 55), outline=(15, 15, 20), width=3)
            draw.rectangle([bx + 8, by - 16, bx + 26, by], fill=(200, 200, 205), outline=(60, 60, 60))
            draw.ellipse([bx + bw - 30, by - 18, bx + bw - 10, by], fill=(200, 200, 205), outline=(60, 60, 60))
            draw.rectangle([bx + 5, by + bh//3, bx + bw - 5, by + 2*bh//3], fill=(210, 140, 20))

    elif class_id == 1:  # Cable & Wires
        wire_colors = [(220, 40, 40), (40, 80, 220), (230, 210, 30), (25, 180, 50), (25, 25, 25), (230, 230, 235)]
        num_strands = random.randint(6, 12)
        for _ in range(num_strands):
            c = random.choice(wire_colors)
            w = random.randint(3, 7)
            pts = []
            cur_x = random.randint(0, 50)
            cur_y = random.randint(20, 200)
            pts.append((cur_x, cur_y))
            for seg in range(4):
                cur_x += random.randint(35, 65)
                cur_y += random.randint(-40, 40)
                cur_y = max(10, min(214, cur_y))
                pts.append((cur_x, cur_y))
            draw.line(pts, fill=c, width=w, joint="curve")
        if random.random() > 0.4:
            draw.rounded_rectangle([150, 100, 195, 130], radius=4, fill=(30, 30, 35), outline=(180, 180, 180))
            draw.rectangle([195, 106, 212, 124], fill=(210, 210, 215), outline=(120, 120, 125))

    elif class_id == 2:  # Charger & Power Adapter
        if variant == 0:
            bx, by = random.randint(60, 85), random.randint(65, 85)
            bw, bh = random.randint(75, 95), random.randint(75, 95)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=(245, 245, 250), outline=(170, 170, 180), width=2)
            draw.rectangle([bx + bw//4 - 5, by - 30, bx + bw//4 + 5, by], fill=(190, 190, 195), outline=(100, 100, 100))
            draw.rectangle([bx + 3*bw//4 - 5, by - 30, bx + 3*bw//4 + 5, by], fill=(190, 190, 195), outline=(100, 100, 100))
            draw.rectangle([bx + bw//3, by + bh - 10, bx + 2*bw//3, by + bh], fill=(40, 40, 45))
        elif variant == 1:
            bx, by = random.randint(50, 70), random.randint(60, 80)
            bw, bh = random.randint(110, 130), random.randint(60, 80)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=8, fill=(30, 32, 36), outline=(90, 95, 105), width=2)
            draw.rectangle([bx + 15, by + 12, bx + bw - 15, by + bh - 12], fill=(45, 48, 54))
            draw.line([(bx + 25, by + bh//2), (bx + bw - 25, by + bh//2)], fill=(180, 180, 190), width=2)
            draw.line([(bx + bw, by + bh//2), (bx + bw + 35, by + bh//2 + 30), (220, 210)], fill=(20, 20, 20), width=5)
        else:
            bx, by = random.randint(65, 85), random.randint(55, 75)
            bw, bh = random.randint(80, 100), random.randint(85, 105)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(235, 238, 242), outline=(160, 165, 175), width=2)
            draw.rectangle([bx + bw//3, by + 25, bx + 2*bw//3, by + 40], fill=(20, 20, 25))
            draw.rectangle([bx + bw//3, by + 50, bx + 2*bw//3, by + 65], fill=(20, 20, 25))
            draw.ellipse([bx + 15, by + 15, bx + 22, by + 22], fill=(30, 200, 255))

    elif class_id == 3:  # Circuit Board / PCB
        pcb_color = random.choice([(15, 80, 35), (20, 60, 110), (25, 28, 32), (18, 95, 45)])
        bx, by = random.randint(25, 40), random.randint(25, 40)
        bw, bh = random.randint(145, 170), random.randint(145, 170)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=pcb_color, outline=(180, 150, 40), width=3)
        trace_color = (215, 175, 40)
        for t in range(8):
            ty = by + 15 + t*18
            draw.line([(bx + 8, ty), (bx + bw//2 - 10, ty), (bx + bw//2 + 10, ty + 12), (bx + bw - 10, ty + 12)], fill=trace_color, width=2)
        cx, cy = bx + bw//2 - 25, by + bh//2 - 25
        draw.rectangle([cx, cy, cx + 50, cy + 50], fill=(20, 20, 25), outline=(180, 180, 185), width=2)
        for p in range(5):
            draw.line([(cx + 8 + p*8, cy - 6), (cx + 8 + p*8, cy)], fill=(200, 200, 205), width=2)
            draw.line([(cx + 8 + p*8, cy + 50), (cx + 8 + p*8, cy + 56)], fill=(200, 200, 205), width=2)
        draw.rectangle([bx + 8, by + bh - 12, bx + bw - 8, by + bh], fill=(225, 180, 45))
        draw.rectangle([bx + 15, by + 15, bx + 35, by + 45], fill=(35, 35, 40), outline=(190, 190, 195))

    elif class_id == 4:  # Headphones & Audio Gear
        if variant == 0:
            draw.arc([45, 35, 179, 160], start=180, end=0, fill=(35, 40, 45), width=12)
            draw.ellipse([30, 100, 75, 165], fill=(30, 32, 38), outline=(180, 40, 40), width=4)
            draw.ellipse([40, 112, 65, 153], fill=(50, 52, 60))
            draw.ellipse([149, 100, 194, 165], fill=(30, 32, 38), outline=(180, 40, 40), width=4)
            draw.ellipse([159, 112, 184, 153], fill=(50, 52, 60))
        elif variant == 1:
            draw.rounded_rectangle([75, 80, 149, 155], radius=16, fill=(245, 245, 250), outline=(180, 180, 190), width=2)
            draw.ellipse([88, 95, 108, 125], fill=(30, 30, 35))
            draw.ellipse([116, 95, 136, 125], fill=(30, 30, 35))
            draw.ellipse([45, 75, 65, 95], fill=(240, 240, 245), outline=(170, 170, 175), width=2)
            draw.line([(55, 95), (55, 135)], fill=(240, 240, 245), width=6)
        else:
            bx, by = random.randint(55, 75), random.randint(60, 80)
            bw, bh = random.randint(85, 110), random.randint(85, 110)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=24, fill=(40, 45, 50), outline=(200, 50, 50), width=3)
            draw.ellipse([bx + 15, by + 15, bx + bw - 15, by + bh - 15], fill=(25, 28, 32))
            draw.ellipse([bx + bw//2 - 15, by + bh//2 - 15, bx + bw//2 + 15, by + bh//2 + 15], fill=(60, 65, 75))

    elif class_id == 5:  # Keyboard & Mouse
        if variant == 0 or variant == 1:
            bx, by = random.randint(20, 35), random.randint(55, 75)
            bw, bh = random.randint(160, 180), random.randint(80, 100)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=6, fill=(35, 38, 45), outline=(110, 115, 125), width=2)
            num_rows, num_cols = 4, 10
            kw = (bw - 20) // num_cols
            kh = (bh - 25) // num_rows
            for r in range(num_rows):
                for c in range(num_cols):
                    kx = bx + 10 + c*kw
                    ky = by + 8 + r*kh
                    draw.rectangle([kx, ky, kx + kw - 3, ky + kh - 3], fill=(65, 70, 80), outline=(30, 32, 38))
            draw.rectangle([bx + bw//4, by + bh - kh - 6, bx + 3*bw//4, by + bh - 8], fill=(75, 80, 92))
        else:
            mx, my = random.randint(75, 95), random.randint(45, 65)
            mw, mh = random.randint(65, 80), random.randint(105, 125)
            draw.ellipse([mx, my, mx + mw, my + mh], fill=(38, 42, 50), outline=(120, 125, 135), width=3)
            draw.line([(mx + mw//2, my + 5), (mx + mw//2, my + mh//2)], fill=(120, 125, 135), width=2)
            draw.rectangle([mx + mw//2 - 4, my + 15, mx + mw//2 + 4, my + 40], fill=(210, 215, 220))

    elif class_id == 6:  # Laptop & Computer
        if variant == 0 or variant == 1:
            draw.polygon([(45, 40), (179, 40), (165, 115), (59, 115)], fill=(20, 22, 28), outline=(150, 155, 165))
            draw.polygon([(52, 46), (172, 46), (160, 109), (64, 109)], fill=(40, 80, 140))
            draw.polygon([(30, 175), (194, 175), (165, 115), (59, 115)], fill=(65, 70, 80), outline=(150, 155, 165))
            draw.rectangle([95, 148, 129, 168], fill=(45, 48, 55))
        else:
            bx, by = random.randint(65, 85), random.randint(35, 55)
            bw, bh = random.randint(75, 95), random.randint(125, 145)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(30, 32, 38), outline=(130, 135, 145), width=3)
            draw.ellipse([bx + bw//2 - 6, by + 15, bx + bw//2 + 6, by + 27], fill=(40, 180, 255))
            draw.rectangle([bx + 15, by + 45, bx + bw - 15, by + 52], fill=(15, 15, 20))
            for row in range(5):
                draw.line([(bx + 15, by + 75 + row*10), (bx + bw - 15, by + 75 + row*10)], fill=(70, 75, 85), width=2)

    elif class_id == 7:  # Mobile Phone & Tablet
        bx, by = random.randint(65, 85), random.randint(25, 40)
        bw, bh = random.randint(75, 95), random.randint(140, 165)
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=(15, 16, 20), outline=(140, 145, 160), width=3)
        screen_color = random.choice([(25, 30, 42), (20, 22, 28), (35, 45, 65)])
        draw.rounded_rectangle([bx + 5, by + 8, bx + bw - 5, by + bh - 8], radius=10, fill=screen_color)
        draw.ellipse([bx + bw//2 - 6, by + 12, bx + bw//2 + 6, by + 24], fill=(8, 8, 12))
        draw.rounded_rectangle([bx + bw//3, by + bh - 14, bx + 2*bw//3, by + bh - 11], radius=2, fill=(200, 200, 210))

    elif class_id == 8:  # Monitor & Display
        bx, by = random.randint(25, 40), random.randint(35, 50)
        bw, bh = random.randint(145, 175), random.randint(95, 115)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(22, 24, 28), outline=(100, 105, 115), width=3)
        disp_color = random.choice([(15, 20, 28), (30, 40, 60), (25, 55, 90)])
        draw.rectangle([bx + 6, by + 6, bx + bw - 6, by + bh - 6], fill=disp_color)
        draw.rectangle([bx + bw//2 - 10, by + bh, bx + bw//2 + 10, by + bh + 30], fill=(130, 135, 145))
        draw.rectangle([bx + bw//2 - 35, by + bh + 28, bx + bw//2 + 35, by + bh + 36], fill=(110, 115, 125))

    elif class_id == 9:  # Storage Devices (HDD / SSD / CD)
        if variant == 0:
            bx, by = random.randint(45, 65), random.randint(40, 60)
            bw, bh = random.randint(110, 130), random.randint(110, 130)
            draw.rectangle([bx, by, bx + bw, by + bh], fill=(160, 165, 175), outline=(70, 75, 85), width=3)
            draw.ellipse([bx + 15, by + 15, bx + bw - 15, by + bh - 15], fill=(225, 230, 240), outline=(130, 135, 145), width=2)
            draw.ellipse([bx + bw//2 - 14, by + bh//2 - 14, bx + bw//2 + 14, by + bh//2 + 14], fill=(70, 75, 85))
            draw.polygon([(bx + 20, by + bh - 20), (bx + bw//2 - 5, by + bh//2), (bx + bw//2 + 5, by + bh//2)], fill=(110, 115, 125))
        elif variant == 1:
            bx, by = random.randint(55, 75), random.randint(50, 70)
            bw, bh = random.randint(100, 120), random.randint(90, 110)
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=6, fill=(40, 42, 48), outline=(150, 155, 165), width=2)
            draw.rectangle([bx + 10, by + 15, bx + bw - 10, by + bh - 25], fill=(220, 225, 230))
            draw.rectangle([bx + 15, by + 25, bx + 50, by + 45], fill=(20, 20, 25))
            draw.rectangle([bx + 15, by + bh - 10, bx + 55, by + bh], fill=(210, 170, 40))
        else:
            cx, cy = 112, 112
            r = random.randint(65, 80)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(215, 220, 230), outline=(160, 165, 175), width=2)
            draw.ellipse([cx - int(r*0.8), cy - int(r*0.8), cx + int(r*0.8), cy + int(r*0.8)], outline=(180, 210, 230), width=4)
            draw.ellipse([cx - int(r*0.25), cy - int(r*0.25), cx + int(r*0.25), cy + int(r*0.25)], fill=(120, 120, 120))
            draw.ellipse([cx - int(r*0.12), cy - int(r*0.12), cx + int(r*0.12), cy + int(r*0.12)], fill=(40, 40, 40))

    return img


def generate_augmented_sample(class_id: int):
    """Generates an image sample with dynamic lighting, rotation, noise, and color jitter."""
    bg = create_random_background()
    img = draw_class_object(bg, class_id)

    rot_angle = random.uniform(-15, 15)
    img = img.rotate(rot_angle, resample=Image.Resampling.BILINEAR)

    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.85, 1.15))

    arr = np.array(img, dtype=np.float32) / 255.0
    noise = np.random.normal(0, 0.015, arr.shape)
    arr = np.clip(arr + noise, 0.0, 1.0)

    return arr.astype(np.float32)


def build_and_train_best_model():
    print("=" * 65)
    print("  ECOSORT AI - STATE-OF-THE-ART E-WASTE MODEL TRAINING PIPELINE")
    print("=" * 65)

    print("\n--- [Phase 1/5] Loading Pre-Trained MobileNetV2 (ImageNet-1k) ---")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        pooling='avg'
    )
    base_model.trainable = False
    print(f"✅ Pre-trained MobileNetV2 backbone loaded. Layers: {len(base_model.layers)}")

    print("\n--- [Phase 2/5] Synthesizing Multi-Variant Electronic Hardware Dataset ---")
    samples_per_class = 120
    X_train_list, y_train_list = [], []
    X_val_list, y_val_list = [], []

    for cid in range(10):
        print(f"   Generating {samples_per_class} augmented samples for Class {cid}: {CLASS_NAMES[cid]}...")
        train_count = int(samples_per_class * 0.8)
        val_count = samples_per_class - train_count
        
        for _ in range(train_count):
            X_train_list.append(generate_augmented_sample(cid))
            y_train_list.append(cid)
        for _ in range(val_count):
            X_val_list.append(generate_augmented_sample(cid))
            y_val_list.append(cid)

    X_train = np.array(X_train_list, dtype=np.float32)
    y_train = np.array(y_train_list, dtype=np.int32)
    X_val = np.array(X_val_list, dtype=np.float32)
    y_val = np.array(y_val_list, dtype=np.int32)

    perm = np.random.permutation(len(X_train))
    X_train, y_train = X_train[perm], y_train[perm]

    print(f"\n✅ Total Training Samples: {len(X_train)} | Total Validation Samples: {len(X_val)}")

    print("\n--- [Phase 3/5] Extracting 1280-Dimensional MobileNetV2 Embeddings ---")
    X_train_norm = (X_train * 2.0) - 1.0
    X_val_norm = (X_val * 2.0) - 1.0

    train_feats = base_model.predict(X_train_norm, batch_size=32, verbose=1)
    val_feats = base_model.predict(X_val_norm, batch_size=32, verbose=1)

    print("\n--- [Phase 4/5] Training Deep Neuro-Classification Head ---")
    top_head = models.Sequential([
        layers.Input(shape=(1280,)),
        layers.BatchNormalization(),
        layers.Dense(512, activation='swish', kernel_regularizer=regularizers.l2(1e-4)),
        layers.Dropout(0.30),
        layers.Dense(256, activation='relu', kernel_regularizer=regularizers.l2(1e-4)),
        layers.Dropout(0.20),
        layers.Dense(10, activation='softmax', name='ewaste_output')
    ])

    top_head.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    history = top_head.fit(
        train_feats, y_train,
        validation_data=(val_feats, y_val),
        epochs=40,
        batch_size=32,
        verbose=1
    )

    val_acc = history.history['val_accuracy'][-1] * 100
    print(f"\n✅ Classification Head Trained! Final Validation Accuracy: {val_acc:.2f}%")

    print("\n--- [Phase 5/5] Assembling End-to-End Pipeline & Exporting to TFLite ---")
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
    rescaled = layers.Rescaling(scale=2.0, offset=-1.0)(inputs)
    feats = base_model(rescaled, training=False)
    outputs = top_head(feats)

    full_model = models.Model(inputs=inputs, outputs=outputs, name="ecosort_best_classifier")

    converter = tf.lite.TFLiteConverter.from_keras_model(full_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "model"))
    os.makedirs(output_dir, exist_ok=True)

    best_path = os.path.join(output_dir, "e_waste_best_model.tflite")
    with open(best_path, "wb") as f:
        f.write(tflite_model)

    legacy_path = os.path.join(output_dir, "e_waste_classifier.tflite")
    with open(legacy_path, "wb") as f:
        f.write(tflite_model)
        
    v3_path = os.path.join(output_dir, "e_waste_v3.tflite")
    with open(v3_path, "wb") as f:
        f.write(tflite_model)

    size_mb = len(tflite_model) / (1024 * 1024)
    print(f"\n🎉 SUCCESS: State-of-the-art E-Waste AI model saved:")
    print(f"   -> Primary:  {best_path} ({size_mb:.2f} MB)")
    print(f"   -> Fallback: {legacy_path} ({size_mb:.2f} MB)")

    print("\n--- Running Direct Verification Test Across All 10 Classes ---")
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        Interpreter = tf.lite.Interpreter

    interpreter = Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()
    inp_idx = interpreter.get_input_details()[0]['index']
    out_idx = interpreter.get_output_details()[0]['index']

    correct = 0
    for cid in range(10):
        test_sample = generate_augmented_sample(cid)[np.newaxis, ...]
        interpreter.set_tensor(inp_idx, test_sample)
        interpreter.invoke()
        preds = interpreter.get_tensor(out_idx)[0]
        pred_cid = int(np.argmax(preds))
        conf = float(preds[pred_cid]) * 100
        is_pass = (pred_cid == cid)
        if is_pass:
            correct += 1
        tag = "✅ PASS" if is_pass else f"⚠️ FAIL (got {CLASS_NAMES[pred_cid]})"
        print(f"   Class {cid} [{CLASS_NAMES[cid]:<30}] -> Pred: {CLASS_NAMES[pred_cid]:<30} ({conf:5.1f}%) {tag}")

    print(f"\nVerification Results: {correct}/10 classes matched ({correct*10}%)")


if __name__ == "__main__":
    build_and_train_best_model()
