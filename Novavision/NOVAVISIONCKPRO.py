#!/usr/bin/env python3
"""
NovaVision Pro - Escáner Ético con IA
by KevDevSecOps
"""
import cv2
import json
from ultralytics import YOLO
from utils.camera import ThermalCamera, setup_camera
from utils.alerts import send_telegram_alert, play_audio_alert

# Configuración
CONFIG = {
    "audio_alerts": True,
    "telegram_alerts": False,
    "save_detections": True
}

class NovaVision:
    def __init__(self):
        self.model = YOLO("models/yolov8n.pt")
        with open("device_database.json") as f:
            self.threat_db = json.load(f)
        
    def analyze_frame(self, frame):
        results = self.model(frame, stream=True)
        for obj in results:
            label = self.model.names[int(obj.boxes.cls)]
            if label in self.threat_db:
                self._process_threat(label, frame)

    def _process_threat(self, device, frame):
        vulns = self.threat_db[device]["vulnerabilities"]
        exploit = self.threat_db[device]["exploit"]
        
        print(f"🔥 {device.upper()} detectado!")
        print(f"📜 Vulnerabilidades: {', '.join(vulns)}")
        print(f"💻 Exploit recomendado: {exploit}")
        
        if CONFIG["save_detections"]:
            cv2.imwrite(f"detections/{device}_{int(time.time())}.jpg", frame)
        
        if CONFIG["audio_alerts"]:
            play_audio_alert(device)
            
        if CONFIG["telegram_alerts"]:
            send_telegram_alert(device, vulns)

def main():
    scanner = NovaVision()
    cap = setup_camera(source=0)  # 0 para cámara USB, "http://ip" para IP
    
    while True:
        _, frame = cap.read()
        scanner.analyze_frame(frame)
        
        cv2.imshow("NovaVision - Modo Hacker", frame)
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
