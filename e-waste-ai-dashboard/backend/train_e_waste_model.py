import os
import sys
import io
import time
import numpy as np

# Fix Windows console UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import tensorflow as tf
from tensorflow.keras import layers, models
from PIL import Image, ImageDraw

def generate_synthetic_samples_for_class(class_id: int, num_samples: int = 50):
    """Generates synthetic training patterns exhibiting visual characteristics of each e-waste class."""
    samples = []
    for _ in range(num_samples):
        img = Image.new("RGB", (224, 224), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)

        if class_id == 0:  # Battery
            # Cylindrical / rectangular battery shape with terminals
            draw.rectangle([50, 60, 170, 180], fill=(20, 20, 20), outline=(200, 30, 30), width=4)
            draw.rectangle([90, 40, 130, 60], fill=(220, 220, 220))  # positive terminal
            draw.text((70, 110), "Li-Ion 3.7V", fill=(255, 200, 0))

        elif class_id == 1:  # Cable & Wires
            # Curving and tangled thin wire lines
            colors = [(200, 40, 40), (40, 40, 200), (220, 220, 40), (40, 200, 40), (20, 20, 20)]
            for i in range(12):
                c = colors[i % len(colors)]
                y_start = np.random.randint(20, 200)
                y_end = np.random.randint(20, 200)
                draw.line([(0, y_start), (70, y_start + 30), (150, y_end - 20), (224, y_end)], fill=c, width=np.random.randint(3, 8))

        elif class_id == 2:  # Charger & Power Adapter
            # Heavy wall adapter cube with 2 prongs and cable tail
            draw.rounded_rectangle([70, 70, 154, 154], radius=10, fill=(240, 240, 245), outline=(160, 160, 170), width=2)
            draw.rectangle([90, 45, 100, 70], fill=(180, 180, 190))
            draw.rectangle([124, 45, 134, 70], fill=(180, 180, 190))
            draw.line([(112, 154), (112, 210), (140, 224)], fill=(40, 40, 40), width=5)

        elif class_id == 3:  # Circuit Board / PCB
            # Deep green PCB background with gold/copper traces and black ICs
            img = Image.new("RGB", (224, 224), color=(15, 65, 30))
            draw = ImageDraw.Draw(img)
            for i in range(15):
                draw.line([(10, 15 * i + 10), (90, 15 * i + 10), (130, 15 * i + 30), (210, 15 * i + 30)], fill=(34, 197, 94), width=2)
            draw.rectangle([70, 70, 150, 150], fill=(25, 25, 25), outline=(180, 180, 180), width=2)
            draw.rectangle([160, 30, 200, 60], fill=(20, 20, 20))
            draw.rectangle([20, 160, 60, 200], fill=(20, 20, 20))

        elif class_id == 4:  # Headphones & Audio Gear
            # Headband arc and 2 large ear cups or earbuds
            draw.arc([40, 40, 184, 180], start=180, end=0, fill=(180, 40, 40), width=8)
            draw.ellipse([30, 110, 70, 170], fill=(30, 30, 35), outline=(180, 40, 40), width=3)
            draw.ellipse([154, 110, 194, 170], fill=(30, 30, 35), outline=(180, 40, 40), width=3)

        elif class_id == 5:  # Keyboard & Mouse
            # Grid of small square keys
            draw.rectangle([20, 70, 204, 154], fill=(35, 35, 40), outline=(100, 100, 110), width=2)
            for row in range(4):
                for col in range(12):
                    draw.rectangle([26 + col * 14, 76 + row * 18, 36 + col * 14, 90 + row * 18], fill=(60, 60, 70))

        elif class_id == 6:  # Laptop & Computer (includes Printers/Scanners)
            # Clamshell top display and bottom keyboard base or boxy printer
            draw.rectangle([40, 30, 184, 130], fill=(15, 25, 35), outline=(140, 150, 160), width=3)
            draw.polygon([(20, 180), (204, 180), (184, 130), (40, 130)], fill=(45, 55, 65), outline=(140, 150, 160))
            draw.rectangle([90, 155, 134, 175], fill=(30, 35, 45))

        elif class_id == 7:  # Mobile Phone & Tablet
            # Rounded rectangle dark glass screen with camera notch
            draw.rounded_rectangle([60, 20, 164, 204], radius=16, fill=(10, 10, 15), outline=(100, 110, 130), width=4)
            draw.ellipse([108, 30, 116, 38], fill=(40, 40, 60))
            draw.rounded_rectangle([70, 50, 154, 180], radius=4, fill=(20, 40, 60))

        elif class_id == 8:  # Monitor & Display
            # Large rectangular panel with stand
            draw.rectangle([30, 30, 194, 150], fill=(10, 15, 20), outline=(80, 90, 100), width=5)
            draw.rectangle([105, 150, 119, 185], fill=(90, 95, 105))
            draw.rectangle([70, 185, 154, 198], fill=(90, 95, 105))

        elif class_id == 9:  # Storage Devices (HDD / SSD / CD)
            # Metallic rectangular hard disk drive enclosure with disk platter
            draw.rectangle([45, 35, 179, 189], fill=(120, 125, 135), outline=(60, 65, 75), width=3)
            draw.ellipse([65, 55, 159, 149], fill=(180, 185, 195), outline=(100, 105, 115), width=2)
            draw.ellipse([97, 87, 127, 117], fill=(60, 65, 75))

        # Random slight rotation
        img = img.rotate(np.random.uniform(-10, 10))
        arr = np.array(img, dtype=np.float32) / 255.0
        # MobileNetV2 expects normalized input [-1, 1] or [0, 1]
        noise = np.random.normal(0, 0.02, arr.shape)
        arr = np.clip(arr + noise, 0.0, 1.0)
        samples.append(arr)

    return np.array(samples, dtype=np.float32)


def build_and_train_model():
    print("\n--- [1/4] Loading Pretrained MobileNetV2 Feature Extractor ---")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        pooling='avg'
    )
    base_model.trainable = False

    print("--- [2/4] Generating Training Datasets Across 10 E-Waste Classes ---")
    X_train_list, y_train_list = [], []
    for c_id in range(10):
        samples = generate_synthetic_samples_for_class(c_id, num_samples=60)
        X_train_list.append(samples)
        y_train_list.extend([c_id] * len(samples))

    X_train = np.vstack(X_train_list)
    y_train = np.array(y_train_list)

    idx = np.random.permutation(len(X_train))
    X_train, y_train = X_train[idx], y_train[idx]

    print("   Extracting Deep MobileNetV2 Feature Embeddings (1280-dim)...")
    # Normalize input: scale [0, 1] -> [-1, 1]
    X_norm = (X_train * 2.0) - 1.0
    features = base_model.predict(X_norm, batch_size=32, verbose=1)

    print("--- [3/4] Training Top E-Waste Classifier Head ---")
    top_head = models.Sequential([
        layers.Input(shape=(1280,)),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(10, activation='softmax', name='ewaste_output')
    ])
    top_head.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    top_head.fit(
        features, y_train,
        epochs=35,
        batch_size=16,
        verbose=1
    )

    print("--- [4/4] Building End-to-End Model & Exporting to TFLite ---")
    inputs = tf.keras.Input(shape=(224, 224, 3), name='input_layer')
    # Rescale [0, 1] to [-1, 1] for MobileNetV2
    rescaled = layers.Rescaling(scale=2.0, offset=-1.0)(inputs)
    feat = base_model(rescaled, training=False)
    outputs = top_head(feat)

    full_model = models.Model(inputs=inputs, outputs=outputs, name='ewaste_mobilenetv2_classifier')

    converter = tf.lite.TFLiteConverter.from_keras_model(full_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    output_dir = "backend/model"
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "custom_e_waste_v2.tflite")

    with open(model_path, "wb") as f:
        f.write(tflite_model)

    print(f"\n✅ Fine-Tuned TFLite model successfully saved to: {model_path} ({len(tflite_model)/1024/1024:.2f} MB)")

    # Run verification test on each class
    print("\n--- Verifying Distinct Class Inference on Test Samples ---")
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        Interpreter = tf.lite.Interpreter

    interpreter = Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()
    inp_idx = interpreter.get_input_details()[0]['index']
    out_idx = interpreter.get_output_details()[0]['index']

    class_names = [
        "Battery", "Cable & Wires", "Charger & Power Adapter", "Circuit Board / PCB",
        "Headphones & Audio Gear", "Keyboard & Mouse", "Laptop & Computer",
        "Mobile Phone & Tablet", "Monitor & Display", "Storage Devices (HDD/SSD)"
    ]

    for test_class in range(10):
        test_img = generate_synthetic_samples_for_class(test_class, num_samples=1)[0:1]
        interpreter.set_tensor(inp_idx, test_img)
        interpreter.invoke()
        preds = interpreter.get_tensor(out_idx)[0]
        top_idx = int(np.argmax(preds))
        conf = float(preds[top_idx]) * 100
        match = "✅ PASS" if top_idx == test_class else f"⚠️ (Expected {test_class}, got {top_idx})"
        print(f"Class {test_class} [{class_names[test_class]:<25}] -> Predicted: {class_names[top_idx]:<25} ({conf:.1f}%) {match}")


if __name__ == "__main__":
    build_and_train_model()
