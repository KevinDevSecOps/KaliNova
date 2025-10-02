import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
from typing import List, Dict
import re

class AdvancedThreatHunter:
    def __init__(self):
        self.hunting_rules = self.load_hunting_rules()
        self.detection_techniques = {}
    
    def load_hunting_rules(self) -> Dict:
        """Carga reglas avanzadas de caza de amenazas"""
        return {
            'lateral_movement': {
                'description': 'Detección de movimiento lateral en la red',
                'queries': [
                    "SELECT * FROM network_flows WHERE dest_port IN (135, 445, 3389) AND protocol='TCP'",
                    "SELECT * FROM auth_logs WHERE event_type='success' AND src_ip != expected_ip"
                ],
                'score': 85
            },
            'persistence_mechanisms': {
                'description': 'Búsqueda de mecanismos de persistencia',
                'queries': [
                    "SELECT * FROM processes WHERE parent_process='services.exe' AND name LIKE '%.tmp'",
                    "SELECT * FROM registry WHERE path LIKE '%Run%' AND value LIKE '%.scr'"
                ],
                'score': 90
            },
            'data_exfiltration': {
                'description': 'Detección de exfiltración de datos',
                'queries': [
                    "SELECT * FROM network_flows WHERE bytes_out > 1000000 AND dest_ip IN external_ips",
                    "SELECT * FROM dns_queries WHERE length(query) > 100 AND query_count > 1000"
                ],
                'score': 95
            },
            'command_control': {
                'description': 'Detección de comunicación C2',
                'queries': [
                    "SELECT * FROM network_flows WHERE dest_port IN (443, 8080) AND packet_entropy > 7.5",
                    "SELECT * FROM processes WHERE cmdline LIKE '%base64%' OR cmdline LIKE '%encrypt%'"
                ],
                'score': 80
            }
        }
    
    async def conduct_hunting_campaign(self, timeframe_hours=24) -> Dict:
        """Conduce una campaña de caza de amenazas"""
        print(f"[+] Iniciando campaña de threat hunting (últimas {timeframe_hours}h)")
        
        start_time = datetime.now() - timedelta(hours=timeframe_hours)
        
        hunting_results = {}
        
        for rule_name, rule_config in self.hunting_rules.items():
            print(f"   🔍 Ejecutando regla: {rule_name}")
            
            rule_results = await self.execute_hunting_rule(rule_name, rule_config, start_time)
            hunting_results[rule_name] = rule_results
            
            if rule_results['matches_found'] > 0:
                print(f"   🚨 {rule_results['matches_found']} coincidencias encontradas!")
        
        # Análisis consolidado
        campaign_summary = self.analyze_hunting_campaign(hunting_results)
        
        print(f"[+] Campaña completada. Resumen:")
        print(f"   📊 Total de coincidencias: {campaign_summary['total_matches']}")
        print(f"   🎯 Amenazas detectadas: {campaign_summary['threats_detected']}")
        print(f"   ⚠️  Score de riesgo: {campaign_summary['campaign_risk_score']}")
        
        return campaign_summary
    
    async def execute_hunting_rule(self, rule_name: str, rule_config: Dict, start_time: datetime) -> Dict:
        """Ejecuta una regla específica de threat hunting"""
        # Simular ejecución de queries (en producción se conectaría a SIEM/ELK/etc.)
        await asyncio.sleep(1)  # Simular procesamiento
        
        # Generar resultados simulados
        matches_count = random.randint(0, 10)
        matches = []
        
        for i in range(matches_count):
            match = {
                'id': f"{rule_name}_{i}",
                'timestamp': start_time + timedelta(hours=random.randint(1, 24)),
                'severity': random.choice(['low', 'medium', 'high', 'critical']),
                'evidence': self.generate_evidence(rule_name),
                'confidence': random.randint(50, 100) / 100.0
            }
            matches.append(match)
        
        return {
            'rule_name': rule_name,
            'description': rule_config['description'],
            'matches_found': matches_count,
            'matches': matches,
            'rule_score': rule_config['score']
        }
    
    def generate_evidence(self, rule_name: str) -> Dict:
        """Genera evidencia simulada para coincidencias"""
        evidence_templates = {
            'lateral_movement': {
                'source_ip': f"10.1.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'destination_ip': f"10.2.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'service': random.choice(['SMB', 'RDP', 'WinRM']),
                'authentication_method': 'NTLM'
            },
            'persistence_mechanisms': {
                'registry_key': f"HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\{''.join(random.choices(string.ascii_lowercase, k=8))}",
                'file_path': f"C:\\Users\\Public\\{''.join(random.choices(string.ascii_lowercase, k=12))}.exe",
                'schedule_task': f"Task_{random.randint(1000, 9999)}"
            },
            'data_exfiltration': {
                'destination': random.choice(['185.143.221.42', '45.134.165.78', 'transfer.sh']),
                'data_size': random.randint(1000000, 50000000),
                'protocol': random.choice(['HTTP', 'DNS', 'FTP']),
                'encryption_detected': random.choice([True, False])
            }
        }
        
        return evidence_templates.get(rule_name, {'details': 'Unknown activity detected'})
    
    def analyze_hunting_campaign(self, hunting_results: Dict) -> Dict:
        """Analiza los resultados de una campaña de hunting"""
        total_matches = sum(result['matches_found'] for result in hunting_results.values())
        
        # Calcular score de riesgo
        risk_score = 0
        max_possible_score = 0
        
        for rule_name, results in hunting_results.items():
            rule_weight = self.hunting_rules[rule_name]['score']
            matches = results['matches_found']
            
            risk_score += matches * rule_weight
            max_possible_score += 10 * rule_weight  # Asumiendo máximo 10 matches por regla
        
        campaign_risk_score = (risk_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        return {
            'total_matches': total_matches,
            'threats_detected': len([r for r in hunting_results.values() if r['matches_found'] > 0]),
            'campaign_risk_score': campaign_risk_score,
            'high_confidence_findings': sum(
                1 for result in hunting_results.values() 
                for match in result['matches'] 
                if match.get('confidence', 0) > 0.8
            ),
            'detailed_results': hunting_results
        }