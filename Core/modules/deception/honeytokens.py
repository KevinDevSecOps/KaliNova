import random
import string
import hashlib
from datetime import datetime
import asyncio
from typing import Dict, List

class AdvancedHoneytokens:
    def __init__(self):
        self.tokens = {}
        self.triggered_tokens = []
        self.token_types = {
            'database_credentials': self.generate_db_credentials,
            'api_keys': self.generate_api_keys,
            'ssh_keys': self.generate_ssh_keys,
            'document_files': self.generate_document_tokens
        }
    
    def generate_db_credentials(self, count=5) -> List[Dict]:
        """Genera credenciales de base de datos falsas"""
        tokens = []
        for i in range(count):
            token = {
                'type': 'database_credentials',
                'username': f'app_user_{random.randint(1000, 9999)}',
                'password': self.generate_random_password(16),
                'database': f'production_db_{random.randint(1, 10)}',
                'host': f'db-server-{random.randint(1, 5)}.internal.company.com',
                'port': random.choice([3306, 5432, 1433]),
                'created_at': datetime.now(),
                'triggered': False
            }
            token_id = hashlib.md5(f"{token['username']}{token['password']}".encode()).hexdigest()
            self.tokens[token_id] = token
            tokens.append(token_id)
        
        return tokens
    
    def generate_api_keys(self, count=10) -> List[Dict]:
        """Genera claves API falsas"""
        tokens = []
        for i in range(count):
            token = {
                'type': 'api_key',
                'service': random.choice(['AWS', 'Stripe', 'Twilio', 'SendGrid', 'Google Cloud']),
                'key': f'sk_live_{"".join(random.choices(string.ascii_letters + string.digits, k=32))}',
                'secret': f'{"".join(random.choices(string.ascii_letters + string.digits, k=64))}',
                'created_at': datetime.now(),
                'triggered': False
            }
            token_id = hashlib.md5(token['key'].encode()).hexdigest()
            self.tokens[token_id] = token
            tokens.append(token_id)
        
        return tokens
    
    def generate_document_tokens(self, count=3) -> List[Dict]:
        """Genera documentos falsos con metadatos"""
        tokens = []
        document_types = [
            'financial_report', 'employee_salaries', 'merger_plan', 
            'source_code', 'infrastructure_diagram'
        ]
        
        for doc_type in document_types[:count]:
            token = {
                'type': 'document',
                'name': f'Confidential_{doc_type.replace("_", " ").title()}_Q4_2024.pdf',
                'content': self.generate_fake_document_content(doc_type),
                'metadata': {
                    'author': random.choice(['CEO Office', 'CFO Team', 'CTO Department']),
                    'classification': 'STRICTLY CONFIDENTIAL',
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'watermark': f'INTERNAL-{random.randint(10000, 99999)}'
                },
                'created_at': datetime.now(),
                'triggered': False
            }
            token_id = hashlib.md5(token['name'].encode()).hexdigest()
            self.tokens[token_id] = token
            tokens.append(token_id)
        
        return tokens
    
    def generate_fake_document_content(self, doc_type: str) -> str:
        """Genera contenido falso para documentos"""
        templates = {
            'financial_report': """
            QUARTERLY FINANCIAL REPORT - STRICTLY CONFIDENTIAL
            
            Revenue: $${millions}
            Profit Margin: {margin}%
            Projected Growth: {growth}%
            
            This document contains forward-looking statements...
            """,
            'employee_salaries': """
            EMPLOYEE COMPENSATION DATA - CONFIDENTIAL
            
            Executive Team Compensation:
            - CEO: ${ceo_salary}
            - CTO: ${cto_salary}
            - CFO: ${cfo_salary}
            
            Department Budget Allocations...
            """,
            'source_code': """
            // PRODUCTION API KEYS - DO NOT COMMIT
            const AWS_ACCESS_KEY = 'AKIA{random_chars}';
            const DATABASE_URL = 'postgresql://user:{password}@prod-db.internal:5432';
            const STRIPE_SECRET_KEY = 'sk_live_{stripe_key}';
            """
        }
        
        return templates.get(doc_type, "CONFIDENTIAL DOCUMENT - INTERNAL USE ONLY")
    
    async def monitor_tokens(self):
        """Monitorea los honeytokens en busca de activación"""
        print("[+] Iniciando monitoreo de honeytokens...")
        
        while True:
            triggered_count = len([t for t in self.tokens.values() if t['triggered']])
            total_count = len(self.tokens)
            
            print(f"   📊 Honeytokens: {triggered_count}/{total_count} activados")
            
            # Simular chequeo de activación (en producción sería con APIs reales)
            await self.simulate_token_checks()
            
            await asyncio.sleep(60)  # Chequear cada minuto
    
    async def simulate_token_checks(self):
        """Simula la verificación de activación de tokens"""
        for token_id, token in self.tokens.items():
            if not token['triggered'] and random.random() < 0.01:  # 1% chance de activación
                await self.handle_token_trigger(token_id, token)
    
    async def handle_token_trigger(self, token_id: str, token: Dict):
        """Maneja la activación de un honeytoken"""
        token['triggered'] = True
        token['triggered_at'] = datetime.now()
        token['trigger_source'] = self.simulate_attack_source()
        
        self.triggered_tokens.append({
            'token_id': token_id,
            **token
        })
        
        print(f"🚨 HONEYTOKEN ACTIVADO!")
        print(f"   🎯 Tipo: {token['type']}")
        print(f"   📍 Fuente: {token['trigger_source']}")
        print(f"   ⏰ Hora: {token['triggered_at']}")
        
        # Alertar inmediatamente
        await self.trigger_incident_response(token)
    
    def simulate_attack_source(self) -> str:
        """Simula la fuente de un ataque"""
        sources = [
            'External IP: 185.143.221.42 (Russia)',
            'Internal Network: 10.2.15.78',
            'Cloud Provider: AWS us-east-1',
            'Compromised Employee Account: john.doe@company.com'
        ]
        return random.choice(sources)
    
    async def trigger_incident_response(self, token: Dict):
        """Activa la respuesta a incidentes"""
        print(f"   🛡️  Activando respuesta a incidentes para {token['type']}")
        
        # Aquí integraríamos con el sistema de respuesta a incidentes
        incident_data = {
            'type': 'honeytoken_triggered',
            'severity': 'high',
            'source': token['trigger_source'],
            'details': {
                'token_type': token['type'],
                'trigger_time': token['triggered_at'],
                'token_content': str(token)[:200] + '...'  # Limitar longitud
            }
        }
        
        # En producción: await incident_response.handle_incident(incident_data)