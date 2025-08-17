#!/usr/bin/env python3
"""
NovaVision - Ethical Hacking con Visión por Computadora
Detecta dispositivos IoT vulnerables en tiempo real.
"""
import cv2
from ultralytics import YOLO
from utils.alerts import send_alert
from utils.camera import setup_camera

# Cargar modelo YOLOv8 preentrenado
model = YOLO("yolov8n.pt")  

# Dispositivos objetivo y sus vulnerabilidades conocidas
TARGET_DEVICES = {
    "router": ["CVE-2023-1234", "Default Credentials"],
    "camera": ["CVE-2022-4567", "Unauthorized Access"],
    "smartphone": ["CVE-2024-7890"]
}

def scan_frame(frame):
    results = model(frame)
    for obj in results[0].boxes:
        label = model.names[int(obj.cls)]
        if label in TARGET_DEVICES:
            vulns = TARGET_DEVICES[label]
            print(f"⚠️ {label.upper()} detectado - Vulnerabilidades: {', '.join(vulns)}")
            cv2.imwrite(f"logs/{label}_detection.jpg", frame)
            send_alert(label, vulns)

def main():
    cap = setup_camera()  # Configura cámara (USB/RPi)
    while True:
        _, frame = cap.read()
        scan_frame(frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()

if __name__ == "__main__":
    main()
