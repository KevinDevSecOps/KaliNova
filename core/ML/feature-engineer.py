import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from datetime import datetime

class ThreatFeatureEngineer:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
    
    def extract_network_features(self, packet_data: dict) -> dict:
        """Extrae características de tráfico de red"""
        features = {}
        
        # Características básicas del paquete
        features['packet_size'] = packet_data.get('length', 0)
        features['protocol'] = self.encode_protocol(packet_data.get('protocol', 'unknown'))
        features['src_port'] = packet_data.get('src_port', 0)
        features['dst_port'] = packet_data.get('dst_port', 0)
        
        # Características temporales
        timestamp = packet_data.get('timestamp', datetime.now())
        features['hour'] = timestamp.hour
        features['day_of_week'] = timestamp.weekday()
        
        # Características de frecuencia
        features['packets_per_second'] = self.calculate_pps(packet_data)
        features['bytes_per_second'] = self.calculate_bps(packet_data)
        
        # Características de comportamiento
        features['port_entropy'] = self.calculate_port_entropy(packet_data)
        features['size_variance'] = self.calculate_size_variance(packet_data)
        
        return features
    
    def extract_web_features(self, http_data: dict) -> dict:
        """Extrae características de tráfico HTTP/HTTPS"""
        features = {}
        
        # Características de la solicitud
        features['request_method'] = self.encode_method(http_data.get('method', 'GET'))
        features['uri_length'] = len(http_data.get('uri', ''))
        features['user_agent_length'] = len(http_data.get('user_agent', ''))
        features['content_type'] = self.encode_content_type(http_data.get('content_type', ''))
        
        # Análisis de parámetros
        params = http_data.get('parameters', {})
        features['num_parameters'] = len(params)
        features['parameter_length_avg'] = np.mean([len(str(v)) for v in params.values()]) if params else 0
        
        # Características de headers
        headers = http_data.get('headers', {})
        features['num_headers'] = len(headers)
        features['suspicious_headers'] = self.detect_suspicious_headers(headers)
        
        return features
    
    def extract_system_features(self, log_data: dict) -> dict:
        """Extrae características de logs del sistema"""
        features = {}
        
        # Características de eventos
        features['event_type'] = self.encode_event_type(log_data.get('event_type', ''))
        features['log_level'] = self.encode_log_level(log_data.get('level', 'INFO'))
        features['process_id'] = log_data.get('pid', 0)
        
        # Análisis de frecuencia temporal
        features['events_per_minute'] = self.calculate_epm(log_data)
        features['unique_processes'] = len(set(log_data.get('process_list', [])))
        
        # Características de seguridad
        features['failed_logins'] = log_data.get('failed_attempts', 0)
        features['privilege_escalation'] = int(log_data.get('privilege_change', False))
        
        return features
    
    def create_feature_vector(self, raw_data: dict, data_type: str) -> np.array:
        """Crea vector de características unificado"""
        if data_type == 'network':
            features = self.extract_network_features(raw_data)
        elif data_type == 'web':
            features = self.extract_web_features(raw_data)
        elif data_type == 'system':
            features = self.extract_system_features(raw_data)
        else:
            raise ValueError(f"Tipo de datos no soportado: {data_type}")
        
        # Convertir a array numpy
        feature_vector = np.array(list(features.values()))
        self.feature_names = list(features.keys())
        
        return feature_vector
    
    def calculate_pps(self, packet_data: dict) -> float:
        """Calcula paquetes por segundo"""
        # Implementación simplificada
        return packet_data.get('packet_count', 1) / max(packet_data.get('time_window', 1), 1)
    
    def detect_suspicious_headers(self, headers: dict) -> int:
        """Detecta headers HTTP sospechosos"""
        suspicious_patterns = [
            'x-forwarded-for', 'x-real-ip', 'x-powered-by', 
            'server', 'x-aspnet-version'
        ]
        return sum(1 for header in headers.keys() 
                  if any(pattern in header.lower() for pattern in suspicious_patterns))