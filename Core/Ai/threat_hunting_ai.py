import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import networkx as nx
from datetime import datetime, timedelta

class AIThreatHunter:
    """Sistema de threat hunting impulsado por IA"""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.cluster_analyzer = DBSCAN(eps=0.5, min_samples=2)
        self.scaler = StandardScaler()
        self.behavior_profiles = {}
    
    def analyze_network_behavior(self, network_data: pd.DataFrame) -> Dict:
        """Analiza comportamiento de red usando múltiples técnicas de IA"""
        print("[🤖] Analizando comportamiento de red con IA...")
        
        # Análisis de anomalías
        anomalies = self.detect_anomalies(network_data)
        
        # Análisis de clustering
        clusters = self.cluster_analysis(network_data)
        
        # Análisis temporal
        temporal_patterns = self.temporal_analysis(network_data)
        
        # Análisis de gráficos de red
        network_graph = self.network_graph_analysis(network_data)
        
        return {
            'anomalies_detected': len(anomalies),
            'suspicious_clusters': clusters,
            'temporal_anomalies': temporal_patterns,
            'network_insights': network_graph,
            'risk_assessment': self.calculate_risk_score(anomalies, clusters)
        }
    
    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict]:
        """Detecta anomalías usando Isolation Forest"""
        features = self.extract_features(data)
        scaled_features = self.scaler.fit_transform(features)
        
        predictions = self.anomaly_detector.fit_predict(scaled_features)
        anomaly_scores = self.anomaly_detector.decision_function(scaled_features)
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            if pred == -1:  # Anomalía detectada
                anomalies.append({
                    'index': i,
                    'score': score,
                    'features': features.iloc[i].to_dict(),
                    'timestamp': data.iloc[i].get('timestamp', datetime.now())
                })
        
        return anomalies
    
    def cluster_analysis(self, data: pd.DataFrame) -> Dict:
        """Análisis de clustering para detectar grupos sospechosos"""
        features = self.extract_features(data)
        scaled_features = self.scaler.fit_transform(features)
        
        clusters = self.cluster_analyzer.fit_predict(scaled_features)
        
        # Encontrar clusters sospechosos (grupos pequeños o aislados)
        unique_clusters, counts = np.unique(clusters, return_counts=True)
        suspicious_clusters = []
        
        for cluster_id, count in zip(unique_clusters, counts):
            if cluster_id != -1 and count < 5:  # Clusters pequeños
                cluster_members = data[clusters == cluster_id]
                suspicious_clusters.append({
                    'cluster_id': cluster_id,
                    'size': count,
                    'members': cluster_members[['src_ip', 'dest_ip']].to_dict('records'),
                    'characteristics': self.analyze_cluster_behavior(cluster_members)
                })
        
        return suspicious_clusters
    
    def network_graph_analysis(self, data: pd.DataFrame) -> Dict:
        """Análisis de gráficos de red para detectar patrones"""
        G = nx.Graph()
        
        # Construir grafo de conexiones
        for _, row in data.iterrows():
            G.add_edge(row['src_ip'], row['dest_ip'], 
                      weight=row.get('bytes', 1),
                      timestamp=row.get('timestamp'))
        
        # Métricas de red
        centrality = nx.degree_centrality(G)
        betweenness = nx.betweenness_centrality(G)
        
        # Encontrar nodos sospechosos
        suspicious_nodes = []
        for node in G.nodes():
            if centrality.get(node, 0) > 0.8:  # Alta centralidad
                suspicious_nodes.append({
                    'ip': node,
                    'degree_centrality': centrality[node],
                    'betweenness_centrality': betweenness.get(node, 0),
                    'connections': list(G.neighbors(node))[:10]  # Primeros 10
                })
        
        return {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'suspicious_nodes': suspicious_nodes,
            'network_density': nx.density(G)
        }
    
    def extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extrae características para análisis de ML"""
        features = pd.DataFrame()
        
        # Características básicas
        features['packet_size_avg'] = data.groupby('src_ip')['packet_size'].transform('mean')
        features['connection_frequency'] = data.groupby('src_ip')['timestamp'].transform('count')
        features['unique_dest_ports'] = data.groupby('src_ip')['dest_port'].transform('nunique')
        features['bytes_per_second'] = data.groupby('src_ip')['bytes'].transform('sum') / 3600
        
        # Características temporales
        data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
        features['night_activity'] = data.groupby('src_ip')['hour'].transform(
            lambda x: ((x < 6) | (x > 22)).sum()
        )
        
        return features.fillna(0)
    
    def calculate_risk_score(self, anomalies: List, clusters: List) -> float:
        """Calcula score de riesgo general"""
        anomaly_risk = len(anomalies) * 0.3
        cluster_risk = len(clusters) * 0.4
        temporal_risk = self.assess_temporal_risk(anomalies)
        
        total_risk = anomaly_risk + cluster_risk + temporal_risk
        return min(total_risk / 10.0, 1.0)  # Normalizar a 0-1