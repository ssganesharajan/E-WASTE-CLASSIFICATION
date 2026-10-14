import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

ADMIN_USER = os.getenv("ADMIN_USER", "Admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345678")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "ecosort_admin_token_2026")

ESP32_CAM_URL = os.getenv("ESP32_CAM_URL", "http://10.111.211.153")
MODEL_DIR = BASE_DIR / "model"
def get_default_model_path() -> str:
    best_path = MODEL_DIR / "e_waste_best_model.tflite"
    if best_path.exists():
        return str(best_path)
    v3_path = MODEL_DIR / "e_waste_v3.tflite"
    if v3_path.exists():
        return str(v3_path)
    v2_path = MODEL_DIR / "e_waste_v2.tflite"
    if v2_path.exists():
        return str(v2_path)
    custom_path = MODEL_DIR / "custom_e_waste_v2.tflite"
    if custom_path.exists():
        return str(custom_path)
    return str(MODEL_DIR / "e_waste_classifier.tflite")

MODEL_PATH = os.getenv("MODEL_PATH", get_default_model_path())
DEFAULT_MODEL_PATH = get_default_model_path()
CLASSES_PATH = str(BASE_DIR / "classes.json")
def find_frontend_dir() -> Path:
    candidates = [
        BASE_DIR.parent / "frontend",
        BASE_DIR / "frontend",
        Path.cwd() / "frontend",
        Path.cwd()
    ]
    for p in candidates:
        if p.exists() and (p / "index.html").exists():
            return p
    return BASE_DIR.parent / "frontend"

FRONTEND_DIR = str(find_frontend_dir())

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))


