import asyncio
from datetime import datetime
import json
from typing import Dict, List
import smtplib
from email.mime.text import MimeText

class AutomatedIncidentResponse:
    def __init__(self):
        self.incidents = []
        self.response_rules = self.load_response_rules()
        self.mitigation_actions = {}
    
    def load_response_rules(self) -> Dict:
        """Carga reglas de respuesta automática"""
        return {
            'malware_detection': {
                'severity': 'high',
                'actions': ['isolate_host', 'block_network', 'alert_admin'],
                'threshold': 0.8
            },
            'brute_force_attack': {
                'severity': 'medium', 
                'actions': ['block_ip', 'increase_monitoring'],
                'threshold': 5  # intentos fallidos
            },
            'data_exfiltration': {
                'severity': 'critical',
                'actions': ['block_traffic', 'disable_account', 'alert_ciso'],
                'threshold': 100  # MB transferidos
            },
            'privilege_escalation': {
                'severity': 'high',
                'actions': ['disable_account', 'revert_changes', 'alert_admin'],
                'threshold': 1  # cualquier intento
            }
        }
    
    async def handle_incident(self, incident_data: Dict):
        """Maneja un incidente de seguridad"""
        incident_id = len(self.incidents) + 1
        incident = {
            'id': incident_id,
            'timestamp': datetime.now(),
            'type': incident_data['type'],
            'severity': incident_data.get('severity', 'medium'),
            'source': incident_data.get('source', 'unknown'),
            'details': incident_data.get('details', {}),
            'status': 'open',
            'actions_taken': []
        }
        
        self.incidents.append(incident)
        
        print(f"🚨 INCIDENTE #{incident_id} - {incident['type']} - {incident['severity']}")
        
        # Ejecutar respuesta automática
        await self.execute_automated_response(incident)
        
        # Notificar equipos relevantes
        await self.notify_teams(incident)
        
        return incident_id
    
    async def execute_automated_response(self, incident: Dict):
        """Ejecuta respuesta automática basada en reglas"""
        incident_type = incident['type']
        rules = self.response_rules.get(incident_type, {})
        
        if not rules:
            print(f"[-] No hay reglas definidas para tipo: {incident_type}")
            return
        
        # Ejecutar acciones definidas
        for action in rules.get('actions', []):
            success = await self.execute_mitigation_action(action, incident)
            
            incident['actions_taken'].append({
                'action': action,
                'timestamp': datetime.now(),
                'success': success
            })
            
            if success:
                print(f"   ✅ Acción ejecutada: {action}")
            else:
                print(f"   ❌ Falló acción: {action}")
    
    async def execute_mitigation_action(self, action: str, incident: Dict) -> bool:
        """Ejecuta una acción de mitigación específica"""
        try:
            if action == 'block_ip':
                return await self.block_ip_address(incident['details'].get('source_ip'))
            
            elif action == 'isolate_host':
                return await self.isolate_host(incident['details'].get('hostname'))
            
            elif action == 'disable_account':
                return await self.disable_user_account(incident['details'].get('username'))
            
            elif action == 'alert_admin':
                return await self.send_alert_notification(incident, 'admin')
            
            elif action == 'block_network':
                return await self.block_network_traffic(incident['details'].get('network'))
            
            else:
                print(f"[-] Acción no implementada: {action}")
                return False
                
        except Exception as e:
            print(f"[-] Error ejecutando {action}: {e}")
            return False
    
    async def block_ip_address(self, ip_address: str) -> bool:
        """Bloquea una dirección IP"""
        if not ip_address:
            return False
        
        print(f"   🛡️  Bloqueando IP: {ip_address}")
        # Implementar bloqueo real (iptables, firewall, etc.)
        # Ejemplo: subprocess.run(['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'])
        return True
    
    async def isolate_host(self, hostname: str) -> bool:
        """Aísla un host de la red"""
        if not hostname:
            return False
        
        print(f"   🛡️  Aislando host: {hostname}")
        # Implementar aislamiento real (segmentación de red)
        return True
    
    async def send_alert_notification(self, incident: Dict, recipient: str) -> bool:
        """Envía notificación de alerta"""
        subject = f"🚨 Incidente de Seguridad #{incident['id']}"
        body = f"""
        Tipo: {incident['type']}
        Severidad: {incident['severity']}
        Fuente: {incident['source']}
        Hora: {incident['timestamp']}
        
        Detalles:
        {json.dumps(incident['details'], indent=2)}
        
        Acciones tomadas:
        {[action['action'] for action in incident['actions_taken']]}
        """
        
        print(f"   📧 Enviando alerta a {recipient}")
        # Implementar envío real de email/notificación
        return True
    
    def get_incident_stats(self) -> Dict:
        """Obtiene estadísticas de incidentes"""
        open_incidents = [i for i in self.incidents if i['status'] == 'open']
        closed_incidents = [i for i in self.incidents if i['status'] == 'closed']
        
        return {
            'total_incidents': len(self.incidents),
            'open_incidents': len(open_incidents),
            'closed_incidents': len(closed_incidents),
            'by_severity': {
                'critical': len([i for i in self.incidents if i['severity'] == 'critical']),
                'high': len([i for i in self.incidents if i['severity'] == 'high']),
                'medium': len([i for i in self.incidents if i['severity'] == 'medium']),
                'low': len([i for i in self.incidents if i['severity'] == 'low'])
            }
        }