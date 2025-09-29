import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import json

class UserBehaviorAnalyzer:
    def __init__(self):
        self.user_profiles = {}
        self.behavior_model = IsolationForest(contamination=0.1)
        self.is_trained = False
    
    def track_user_activity(self, user_id: str, activity: dict):
        """Rastrea actividad de usuario"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'first_seen': datetime.now(),
                'last_seen': datetime.now(),
                'activities': [],
                'sessions': [],
                'risk_score': 0.0
            }
        
        profile = self.user_profiles[user_id]
        profile['last_seen'] = datetime.now()
        profile['activities'].append({
            'timestamp': datetime.now(),
            'activity_type': activity.get('type', 'unknown'),
            'details': activity.get('details', {}),
            'risk_level': activity.get('risk_level', 0)
        })
        
        # Actualizar score de riesgo
        self.update_risk_score(user_id)
    
    def update_risk_score(self, user_id: str):
        """Actualiza el score de riesgo del usuario"""
        profile = self.user_profiles[user_id]
        activities = profile['activities']
        
        if len(activities) < 5:  # Muy pocas actividades para analizar
            profile['risk_score'] = 0.1
            return
        
        # Calcular métricas de comportamiento
        recent_activities = [a for a in activities 
                           if datetime.now() - a['timestamp'] < timedelta(hours=24)]
        
        metrics = {
            'activity_frequency': len(recent_activities),
            'avg_risk_level': np.mean([a['risk_level'] for a in recent_activities]),
            'unique_activity_types': len(set(a['activity_type'] for a in recent_activities)),
            'unusual_hours': self.count_unusual_hours(recent_activities),
            'failed_attempts': len([a for a in recent_activities 
                                  if a['activity_type'] == 'failed_login'])
        }
        
        # Calcular score compuesto
        risk_score = (
            metrics['avg_risk_level'] * 0.4 +
            (metrics['failed_attempts'] / max(metrics['activity_frequency'], 1)) * 0.3 +
            (metrics['unusual_hours'] / max(metrics['activity_frequency'], 1)) * 0.3
        )
        
        profile['risk_score'] = min(risk_score, 1.0)
    
    def count_unusual_hours(self, activities: list) -> int:
        """Cuenta actividades en horas inusuales"""
        unusual_count = 0
        for activity in activities:
            hour = activity['timestamp'].hour
            if hour < 6 or hour > 22:  # Horario nocturno
                unusual_count += 1
        return unusual_count
    
    def detect_anomalous_behavior(self, user_id: str) -> dict:
        """Detecta comportamiento anómalo"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {'anomaly': False, 'reason': 'User not found'}
        
        risk_factors = []
        
        # Verificar múltiples factores de riesgo
        if profile['risk_score'] > 0.8:
            risk_factors.append(f"High risk score: {profile['risk_score']:.2f}")
        
        if self.check_impossible_travel(user_id):
            risk_factors.append("Impossible travel detected")
        
        if self.check_privilege_escalation(user_id):
            risk_factors.append("Rapid privilege escalation")
        
        if self.check_data_exfiltration(user_id):
            risk_factors.append("Possible data exfiltration")
        
        is_anomalous = len(risk_factors) > 0
        
        return {
            'anomaly': is_anomalous,
            'risk_factors': risk_factors,
            'risk_score': profile['risk_score'],
            'recommendation': 'Investigate immediately' if is_anomalous else 'Normal behavior'
        }
    
    def check_impossible_travel(self, user_id: str) -> bool:
        """Detecta viajes imposibles (múltiples ubicaciones en poco tiempo)"""
        # Implementación simplificada
        activities = self.user_profiles[user_id]['activities']
        locations = []
        
        for activity in activities[-10:]:  # Últimas 10 actividades
            location = activity['details'].get('location')
            if location and location not in locations:
                locations.append(location)
        
        # Si hay más de 2 ubicaciones en menos de 1 hora
        if len(locations) > 2 and len(activities) >= 3:
            time_span = activities[-1]['timestamp'] - activities[0]['timestamp']
            return time_span.total_seconds() < 3600  # 1 hora
        
        return False
    
    def check_privilege_escalation(self, user_id: str) -> bool:
        """Detecta escalada rápida de privilegios"""
        activities = self.user_profiles[user_id]['activities']
        privilege_changes = []
        
        for activity in activities:
            if activity['activity_type'] in ['privilege_granted', 'role_change']:
                privilege_changes.append(activity['timestamp'])
        
        # Si hay múltiples cambios de privilegio en poco tiempo
        if len(privilege_changes) >= 3:
            time_span = privilege_changes[-1] - privilege_changes[0]
            return time_span.total_seconds() < 3600  # 1 hora
        
        return False