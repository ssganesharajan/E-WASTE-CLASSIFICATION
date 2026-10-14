"""
Builds an intelligent real-world E-Waste classifier model by mapping MobileNetV2 ImageNet-1k 
photographic feature distributions into the 10 target E-Waste classes.

Canonical 10 E-Waste Classes:
  0: Battery
  1: Cable & Wires
  2: Charger & Power Adapter
  3: Circuit Board / PCB
  4: Headphones & Audio Gear
  5: Keyboard & Mouse
  6: Laptop & Computer (Laptops, Desktops, Printers, Scanners, Copiers)
  7: Mobile Phone & Tablet (Smartphones, Tablets, Handhelds, iPods)
  8: Monitor & Display (Monitors, Screens, Televisions)
  9: Storage Devices (HDD / SSD / CD)
"""
import os
import sys
import numpy as np

# Fix Windows console UTF-8 output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, decode_predictions
from tensorflow.keras import layers, models

def get_imagenet_to_ewaste_mapping():
    """
    Constructs a robust 1000 -> 10 projection matrix mapping ImageNet-1k classes 
    to the 10 canonical E-Waste categories with high confidence and distinct separation.
    """
    projection_weights = np.zeros((1000, 10), dtype=np.float32)

    # Decode class names for all 1000 indices
    dummy = np.zeros((1, 1000), dtype=np.float32)
    class_names = {}
    for i in range(1000):
        dummy[0, i] = 1.0
        decoded = decode_predictions(dummy, top=1)[0][0]
        dummy[0, i] = 0.0
        class_names[i] = decoded[1].lower()

    # Exact Direct Synset & Index Overrides for Maximum Precision
    exact_index_map = {
        # 0: Battery
        862: 0, # torch / flashlight

        # 1: Cable & Wires
        506: 1, # coil
        616: 1, # knot
        816: 1, # spindle
        489: 1, # chainlink_fence

        # 2: Charger & Power Adapter
        844: 2, # switch
        545: 2, # electric_fan
        740: 2, # power_drill
        859: 2, # toaster
        882: 2, # vacuum
        651: 2, # microwave
        606: 2, # iron

        # 3: Circuit Board / PCB
        662: 3, # modem
        688: 3, # oscilloscope

        # 4: Headphones & Audio Gear
        632: 4, # loudspeaker
        650: 4, # microphone
        481: 4, # cassette
        482: 4, # cassette_player
        485: 4, # CD_player
        754: 4, # radio
        848: 4, # tape_player
        546: 4, # electric_guitar
        823: 4, # stethoscope (in-ear earphones and over-ear headphones)

        # 5: Keyboard & Mouse
        508: 5, # computer_keyboard
        878: 5, # typewriter_keyboard
        810: 5, # space_bar
        673: 5, # mouse (computer mouse)
        613: 5, # joystick

        # 6: Laptop & Computer (includes Laptops, Desktops, Printers, Scanners, Copiers)
        620: 6, # laptop
        681: 6, # notebook
        527: 6, # desktop_computer
        742: 6, # printer
        713: 6, # photocopier
        745: 6, # projector

        # 7: Mobile Phone & Tablet
        487: 7, # cellular_telephone
        590: 7, # hand-held_computer
        605: 7, # iPod
        528: 7, # dial_telephone
        707: 7, # pay-phone
        761: 7, # remote_control

        # 8: Monitor & Display
        664: 8, # monitor
        782: 8, # screen
        851: 8, # television
        598: 8, # home_theater
        781: 8, # scoreboard

        # 9: Storage Devices (HDD / SSD / CD)
        592: 9, # hard_disc
        535: 9, # disk_brake
        635: 9  # magnetic_compass
    }

    for idx, cat_id in exact_index_map.items():
        projection_weights[idx, :] = 0.0
        projection_weights[idx, cat_id] = 1.0

    # Keyword rules for related classes
    category_keywords = {
        0: ["battery", "accumulator", "pack", "torch", "flashlight", "solar_dish"],
        1: ["cord", "cable", "wire", "coil", "knot", "rope", "string", "thread"],
        2: ["transformer", "adapter", "plug", "power", "charger", "socket", "switch", "relay", "blower"],
        3: ["microchip", "circuit", "integrated", "network", "motherboard", "silicon", "modem", "pcb", "switchboard", "printed_circuit"],
        4: ["headphone", "earphone", "loudspeaker", "speaker", "microphone", "audio", "radio", "tape_player", "cassette", "headset", "earpiece", "earbud", "sound", "acoustic"],
        5: ["keyboard", "keypad", "space_bar", "typewriter_keyboard", "mouse", "trackball", "joystick"],
        6: ["laptop", "notebook", "desktop_computer", "desktop", "mainframe", "printer", "photocopier", "scanner", "copier", "workstation"],
        7: ["cellular_telephone", "cellphone", "telephone", "phone", "ipod", "hand-held", "pager", "remote_control", "remote", "smartphone", "tablet", "ipad"],
        8: ["monitor", "television", "tv", "screen", "crt", "flat_panel", "display", "home_theater", "scoreboard"],
        9: ["hard_disc", "disc", "disk", "cd_player", "dvd", "memory", "magnetic", "drive", "floppy"]
    }

    for idx, name in class_names.items():
        if idx in exact_index_map:
            continue
        matched = False
        for cat_id, keywords in category_keywords.items():
            for kw in keywords:
                if kw in name:
                    projection_weights[idx, cat_id] = 1.0
                    matched = True
                    break
        if not matched:
            # Distribute general objects evenly or to their visual closest electronic domain
            if any(k in name for k in ["plastic", "box", "case", "carton", "crate", "file"]):
                projection_weights[idx, 6] = 0.7  # Computer / printer chassis
                projection_weights[idx, 2] = 0.3  # Power adapter brick
            elif any(k in name for k in ["iron", "metal", "steel", "tool"]):
                projection_weights[idx, 9] = 0.6  # Hard drive casing
                projection_weights[idx, 6] = 0.4  # Chassis
            elif any(k in name for k in ["glass", "window", "panel", "lens"]):
                projection_weights[idx, 7] = 0.5  # Smartphone glass
                projection_weights[idx, 8] = 0.5  # Monitor display
            elif any(k in name for k in ["hook", "pin", "needle", "stethoscope"]):
                projection_weights[idx, 4] = 0.6  # Earphone cords / buds
                projection_weights[idx, 1] = 0.4  # Wires
            else:
                projection_weights[idx, :] = 0.1  # Uniform diffuse baseline

    # Normalize rows to sum to 1.0
    row_sums = projection_weights.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    projection_weights = projection_weights / row_sums

    return projection_weights


def build_real_world_model():
    print("--- [1/3] Loading Pretrained MobileNetV2 (ImageNet-1k) ---")
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=True,
        weights='imagenet'
    )
    base_model.trainable = False

    print("--- [2/3] Constructing Semantic E-Waste Projection Layer ---")
    proj_matrix = get_imagenet_to_ewaste_mapping()

    inputs = tf.keras.Input(shape=(224, 224, 3), name="image_input")
    # Rescaling [0, 1] to [-1, 1] for MobileNetV2 standard input
    rescaled = layers.Rescaling(scale=2.0, offset=-1.0)(inputs)
    imagenet_preds = base_model(rescaled)  # (batch, 1000)

    # Dense layer initialized with our semantic projection weights
    projection_layer = layers.Dense(
        10,
        use_bias=False,
        trainable=False,
        name="ewaste_projection"
    )
    ewaste_outputs = projection_layer(imagenet_preds)

    full_model = models.Model(inputs=inputs, outputs=ewaste_outputs, name="real_world_ewaste_model")
    full_model.get_layer("ewaste_projection").set_weights([proj_matrix])

    print("--- [3/3] Exporting to TensorFlow Lite (.tflite) ---")
    converter = tf.lite.TFLiteConverter.from_keras_model(full_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "model"))
    os.makedirs(output_dir, exist_ok=True)
    model_path_v3 = os.path.abspath(os.path.join(output_dir, "e_waste_v3.tflite"))

    with open(model_path_v3, "wb") as f:
        f.write(tflite_model)

    print(f"\n✅ Real-World E-Waste TFLite model saved: {model_path_v3} ({len(tflite_model)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    build_real_world_model()
