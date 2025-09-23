import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import json
from collections import deque
import warnings
warnings.filterwarnings('ignore')

class RealTimeThreatDetector:
    def __init__(self, model_path=None, threshold=0.8):
        self.model = self.load_model(model_path)
        self.threshold = threshold
        self.detection_history = deque(maxlen=1000)
        self.alerts = []
        self.stats = {
            'total_packets': 0,
            'threats_detected': 0,
            'false_positives': 0
        }
    
    def load_model(self, model_path):
        """Carga el modelo ML entrenado"""
        if model_path:
            try:
                return joblib.load(model_path)
            except:
                print("[-] No se pudo cargar el modelo, usando detector básico")
        return self.create_basic_detector()
    
    def create_basic_detector(self):
        """Crea un detector básico basado en reglas"""
        from sklearn.ensemble import IsolationForest
        return IsolationForest(contamination=0.1)
    
    async def analyze_packet(self, packet_data: dict):
        """Analiza un paquete en tiempo real"""
        self.stats['total_packets'] += 1
        
        # Extraer características
        feature_engineer = ThreatFeatureEngineer()
        features = feature_engineer.extract_network_features(packet_data)
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        
        # Realizar predicción
        try:
            if hasattr(self.model, 'predict_proba'):
                probability = self.model.predict_proba(feature_vector)[0, 1]
                is_threat = probability > self.threshold
            else:
                prediction = self.model.predict(feature_vector)
                is_threat = prediction[0] == 1
            
            # Registrar detección
            detection_record = {
                'timestamp': datetime.now(),
                'features': features,
                'is_threat': bool(is_threat),
                'probability': probability if 'probability' in locals() else None,
                'packet_data': packet_data
            }
            
            self.detection_history.append(detection_record)
            
            if is_threat:
                await self.handle_threat_detection(detection_record)
            
            return detection_record
            
        except Exception as e:
            print(f"[-] Error en análisis: {e}")
            return None
    
    async def handle_threat_detection(self, detection: dict):
        """Maneja la detección de una amenaza"""
        self.stats['threats_detected'] += 1
        
        alert = {
            'id': len(self.alerts) + 1,
            'timestamp': detection['timestamp'],
            'severity': self.calculate_severity(detection),
            'type': self.classify_threat_type(detection),
            'evidence': detection['features'],
            'packet_summary': {
                'src_ip': detection['packet_data'].get('src_ip', 'unknown'),
                'dst_ip': detection['packet_data'].get('dst_ip', 'unknown'),
                'protocol': detection['packet_data'].get('protocol', 'unknown')
            }
        }
        
        self.alerts.append(alert)
        
        # Notificación inmediata
        await self.send_alert_notification(alert)
        
        # Acciones de mitigación automáticas
        await self.auto_mitigate(alert)
    
    def calculate_severity(self, detection: dict) -> str:
        """Calcula la severidad de la amenaza"""
        probability = detection.get('probability', 0)
        features = detection['features']
        
        if probability > 0.9:
            return 'CRITICAL'
        elif probability > 0.7:
            return 'HIGH'
        elif probability > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def classify_threat_type(self, detection: dict) -> str:
        """Clasifica el tipo de amenaza"""
        features = detection['features']
        
        if features.get('dst_port') in [22, 23, 3389]:
            return 'Brute Force Attack'
        elif features.get('packet_size', 0) > 1500:
            return 'DDoS Attack'
        elif features.get('suspicious_headers', 0) > 2:
            return 'Web Attack'
        else:
            return 'Suspicious Activity'
    
    async def send_alert_notification(self, alert: dict):
        """Envía notificación de alerta"""
        print(f"🚨 ALERTA #{alert['id']} - {alert['severity']} - {alert['type']}")
        print(f"   📍 Origen: {alert['packet_summary']['src_ip']}")
        print(f"   🎯 Destino: {alert['packet_summary']['dst_ip']}")
        print(f"   ⏰ Hora: {alert['timestamp']}")
    
    async def auto_mitigate(self, alert: dict):
        """Acciones automáticas de mitigación"""
        if alert['severity'] in ['CRITICAL', 'HIGH']:
            # Ejemplo: Bloquear IP temporalmente
            src_ip = alert['packet_summary']['src_ip']
            print(f"   🛡️  Mitigación: Bloqueando IP {src_ip} temporalmente")
            
            # Aquí iría la lógica real de bloqueo
            # await self.block_ip_address(src_ip)
    
    def get_detection_stats(self) -> dict:
        """Obtiene estadísticas de detección"""
        return {
            **self.stats,
            'detection_rate': self.stats['threats_detected'] / max(self.stats['total_packets'], 1),
            'recent_alerts': len([a for a in self.alerts if 
                                (datetime.now() - a['timestamp']).total_seconds() < 3600])
        }