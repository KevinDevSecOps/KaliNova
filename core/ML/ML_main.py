#!/usr/bin/env python3
import asyncio
import argparse
import pandas as pd
import numpy as np
from ml.feature_engineer import ThreatFeatureEngineer
from ml.model_trainer import ThreatModelTrainer
from ml.deep_threat_detector import DeepThreatDetector
from monitoring.realtime_detector import RealTimeThreatDetector
import json
import joblib

class KaliNovaML:
    def __init__(self):
        self.feature_engineer = ThreatFeatureEngineer()
        self.model_trainer = ThreatModelTrainer()
        self.realtime_detector = None
    
    def generate_sample_data(self, num_samples=10000):
        """Genera datos de ejemplo para entrenamiento"""
        print("[+] Generando datos de entrenamiento...")
        
        features = []
        labels = []
        
        for i in range(num_samples):
            # Datos normales (80%)
            if np.random.random() < 0.8:
                packet_data = {
                    'length': np.random.randint(40, 1500),
                    'protocol': 'TCP',
                    'src_port': np.random.randint(1024, 65535),
                    'dst_port': np.random.choice([80, 443, 22, 53]),
                    'timestamp': datetime.now()
                }
                label = 0  # Normal
            else:
                # Datos maliciosos (20%)
                packet_data = {
                    'length': np.random.randint(1500, 10000),
                    'protocol': 'TCP',
                    'src_port': np.random.randint(1024, 65535),
                    'dst_port': np.random.choice([22, 23, 3389]),  # Puertos comúnmente atacados
                    'timestamp': datetime.now()
                }
                label = 1  # Malicioso
            
            feature_vector = self.feature_engineer.extract_network_features(packet_data)
            features.append(list(feature_vector.values()))
            labels.append(label)
        
        return np.array(features), np.array(labels)
    
    async def train_models(self, X, y):
        """Entrena todos los modelos"""
        print("[+] Iniciando entrenamiento de modelos...")
        
        # Dividir datos
        X_train, X_test, y_train, y_test = self.model_trainer.prepare_dataset(X, y)
        
        # Entrenar modelos tradicionales
        rf_model, rf_metrics = self.model_trainer.train_random_forest(X_train, y_train, X_test, y_test)
        xgb_model, xgb_metrics = self.model_trainer.train_xgboost(X_train, y_train, X_test, y_test)
        ensemble, ensemble_metrics = self.model_trainer.train_ensemble(X_train, y_train, X_test, y_test)
        
        # Entrenar detector de anomalías
        anomaly_detector = self.model_trainer.train_anomaly_detector(X_train)
        
        # Comparar modelos
        comparison = self.model_trainer.compare_models()
        
        # Guardar mejor modelo
        best_model_name = self.model_trainer.best_model
        best_model = self.model_trainer.models[best_model_name]['model']
        joblib.dump(best_model, f'models/trained_models/best_model_{best_model_name}.pkl')
        
        print("[+] Entrenamiento completado!")
        return comparison
    
    async def start_realtime_detection(self, interface='eth0'):
        """Inicia la detección en tiempo real"""
        print(f"[+] Iniciando detección en tiempo real en {interface}...")
        
        self.realtime_detector = RealTimeThreatDetector(
            model_path='models/trained_models/best_model_random_forest.pkl'
        )
        
        # Simular tráfico en tiempo real (en producción usarías un sniffer real)
        await self.simulate_realtime_traffic()
    
    async def simulate_realtime_traffic(self):
        """Simula tráfico en tiempo real para pruebas"""
        print("[+] Simulando tráfico de red...")
        
        for i in range(1000):
            packet_data = {
                'length': np.random.randint(40, 2000),
                'protocol': np.random.choice(['TCP', 'UDP', 'ICMP']),
                'src_port': np.random.randint(1024, 65535),
                'dst_port': np.random.choice([80, 443, 22, 53, 3389]),
                'src_ip': f"192.168.1.{np.random.randint(1, 255)}",
                'dst_ip': "10.0.0.1",
                'timestamp': datetime.now()
            }
            
            await self.realtime_detector.analyze_packet(packet_data)
            
            if i % 100 == 0:
                stats = self.realtime_detector.get_detection_stats()
                print(f"   📊 Estadísticas: {stats}")
            
            await asyncio.sleep(0.1)  # Simular delay entre paquetes

async def main():
    parser = argparse.ArgumentParser(description='KaliNova - Sistema de Detección de Amenazas con ML')
    parser.add_argument('--train', action='store_true', help='Entrenar modelos')
    parser.add_argument('--detect', action='store_true', help='Iniciar detección en tiempo real')
    parser.add_argument('--interface', default='eth0', help='Interfaz de red para monitoreo')
    
    args = parser.parse_args()
    
    kalinovaml = KaliNovaML()
    
    if args.train:
        # Generar datos y entrenar
        X, y = kalinovaml.generate_sample_data(10000)
        results = await kalinovaml.train_models(X, y)
        print(json.dumps(results, indent=2))
    
    if args.detect:
        await kalinovaml.start_realtime_detection(args.interface)

if __name__ == "__main__":
    asyncio.run(main())