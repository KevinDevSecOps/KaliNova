import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict
import asyncio

class Block:
    """Bloque individual en la blockchain de seguridad"""
    def __init__(self, index: int, timestamp: float, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calcula el hash del bloque"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int):
        """Minado del bloque (Proof of Work)"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"   ⛏️  Bloque minado: {self.hash}")

class SecurityBlockchain:
    """Blockchain para registros de seguridad inmutables"""
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
    
    def create_genesis_block(self) -> Block:
        """Crea el bloque génesis"""
        return Block(0, time.time(), {
            "type": "genesis",
            "message": "Blockchain de seguridad inicializada",
            "system": "KaliNova Security Framework"
        }, "0")
    
    def get_latest_block(self) -> Block:
        """Obtiene el último bloque de la cadena"""
        return self.chain[-1]
    
    def add_block(self, new_block: Block):
        """Añade un nuevo bloque a la cadena"""
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
    
    def log_security_event(self, event_data: Dict):
        """Registra un evento de seguridad en la blockchain"""
        block_data = {
            "event_type": event_data.get("type", "security_event"),
            "severity": event_data.get("severity", "medium"),
            "timestamp": datetime.now().isoformat(),
            "source": event_data.get("source", "unknown"),
            "details": event_data.get("details", {}),
            "action_taken": event_data.get("action", "logged"),
            "signature": self.sign_event(event_data)
        }
        
        new_block = Block(
            len(self.chain),
            time.time(),
            block_data,
            self.get_latest_block().hash
        )
        
        self.add_block(new_block)
        print(f"   🔗 Evento registrado en bloque #{new_block.index}")
        
        return new_block.hash
    
    def sign_event(self, event_data: Dict) -> str:
        """Firma digitalmente el evento"""
        event_string = json.dumps(event_data, sort_keys=True)
        return hashlib.sha256(f"KALINOVA_SECRET_SALT{event_string}".encode()).hexdigest()
    
    def is_chain_valid(self) -> bool:
        """Verifica la integridad de la blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verificar hash actual
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Verificar hash anterior
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def audit_events(self, event_type: str = None, start_time: datetime = None) -> List[Dict]:
        """Audita eventos de seguridad en la blockchain"""
        events = []
        
        for block in self.chain[1:]:  # Excluir génesis
            event_time = datetime.fromtimestamp(block.timestamp)
            
            if start_time and event_time < start_time:
                continue
            
            if event_type and block.data.get("event_type") != event_type:
                continue
            
            events.append({
                "block_index": block.index,
                "timestamp": event_time,
                "event_type": block.data.get("event_type"),
                "severity": block.data.get("severity"),
                "details": block.data.get("details"),
                "block_hash": block.hash
            })
        
        return events
    
    async def realtime_monitoring(self):
        """Monitoreo en tiempo real que registra en blockchain"""
        print("[🔗] Iniciando monitoreo con blockchain...")
        
        while True:
            # Simular eventos de seguridad
            security_events = self.simulate_security_events()
            
            for event in security_events:
                self.log_security_event(event)
            
            # Verificar integridad periódicamente
            if not self.is_chain_valid():
                print("   ❌ ALERTA: Integridad de blockchain comprometida!")
            
            await asyncio.sleep(60)  # Chequear cada minuto
    
    def simulate_security_events(self) -> List[Dict]:
        """Simula eventos de seguridad para demo"""
        events = []
        event_types = [
            "failed_login", "malware_detected", "port_scan", 
            "data_exfiltration", "privilege_escalation"
        ]
        
        if random.random() < 0.3:  # 30% chance de evento
            events.append({
                "type": random.choice(event_types),
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "source": f"192.168.1.{random.randint(1, 255)}",
                "details": {
                    "description": f"Evento de seguridad simulado",
                    "risk_score": random.randint(1, 100)
                },
                "action": random.choice(["logged", "blocked", "alerted"])
            })
        
        return events