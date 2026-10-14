# E-Waste Classification & Recycling System (IoT + DNN)

An end-to-end intelligent IoT and Deep Neural Network (DNN) Electronic Waste Classification and Sustainability Management Platform. This repository integrates edge-device camera capture via **ESP32-CAM** with an AI-powered classification engine and interactive industrial telemetry dashboard.

---

## 📁 Repository Overview

```
├── CameraWebServer/             # ESP32-CAM Firmware & HTTP Web Server
│   ├── CameraWebServer.ino      # Main Arduino sketch & camera setup
│   ├── app_httpd.cpp            # HTTP server handler & image capture endpoints
│   ├── board_config.h           # Camera model configuration (AI-Thinker, etc.)
│   ├── camera_index.h           # Web interface static assets
│   ├── camera_pins.h            # Pin definitions for ESP32-CAM models
│   ├── ci.yml                   # GitHub Actions CI workflow for ESP32
│   └── partitions.csv           # Flash partition configuration
│
├── e-waste-ai-dashboard/        # AI Inference Engine, Backend & Telemetry Dashboard
│   ├── backend/                 # FastAPI REST API & TensorFlow Lite Inference
│   │   ├── main.py              # Application entry point & endpoints
│   │   ├── config.py            # App & IoT configuration
│   │   ├── classes.json         # 10 E-Waste categories with recycling recommendations
│   │   ├── model/               # Trained TFLite models
│   │   └── requirements.txt     # Python dependencies
│   ├── frontend/                # Interactive Industrial Dashboard
│   │   ├── index.html           # Dark-mode telemetry & admin UI
│   │   ├── css/style.css        # Responsive styling & themes
│   │   └── js/app.js            # Real-time WebSocket/REST client logic
│   ├── EcoSort_AI_Presentation.pptx # Project overview presentation
│   ├── generate_ppt.py          # Script for presentation generation
│   ├── Procfile                 # Deployment process config
│   ├── render.yaml              # Render cloud deployment blueprint
│   └── README.md                # Dashboard specific documentation
│
└── .gitignore                   # Project-wide Git ignore rules
```

---

## 🚀 Key Modules

### 1. `CameraWebServer` (ESP32-CAM Edge Node)
- Real-time video streaming and on-demand high-resolution snapshot capture (`/capture`).
- Configured for AI-Thinker ESP32-CAM module with PSRAM support.
- Communicates directly with the AI classification backend via WiFi.

### 2. `e-waste-ai-dashboard` (AI Inference & Industrial Dashboard)
- **AI Classification**: MobileNetV2 quantized TFLite model classifying 10 e-waste categories (Motherboards, Mobile Phones, Batteries, Cables, CRT/LCD Monitors, PCBs, Transformers, etc.).
- **Multi-Source Ingestion**: ESP32-CAM live capture stream, local webcam, and manual drag-and-drop image upload.
- **Dynamic Model Management**: Model upload hub with instant hot-swapping and validation.
- **Recycling Engine**: Hazard warnings, valuable material breakdown, toxin detection, and carbon offset analytics.
- **Secure Dashboard**: Protected telemetry, historical scan records with CSV export, and hardware status monitor.

---

## 🛠️ Getting Started

### Prerequisites
- **ESP32-CAM**: Arduino IDE with ESP32 board definitions installed.
- **Backend**: Python 3.10+ or 3.11+.
- **Frontend**: Modern web browser (Chrome, Edge, Firefox).

### 1. ESP32-CAM Setup
1. Open [`CameraWebServer/CameraWebServer.ino`](file:///CameraWebServer/CameraWebServer.ino) in Arduino IDE.
2. Update the WiFi credentials (`ssid` and `password`).
3. Select board `AI Thinker ESP32-CAM` and flash with Partition Scheme `Huge APP (3MB No OTA/1MB SPIFFS)`.
4. Note down the IP address output in the Serial Monitor (e.g., `http://192.168.x.x`).

### 2. Backend & Dashboard Setup
1. Navigate to `e-waste-ai-dashboard`:
   ```bash
   cd e-waste-ai-dashboard/backend
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Open `e-waste-ai-dashboard/frontend/index.html` in your browser or serve it via any static HTTP server.

---

## 👤 Author
- **ssganesharajan** ([GitHub Profile](https://github.com/ssganesharajan))
