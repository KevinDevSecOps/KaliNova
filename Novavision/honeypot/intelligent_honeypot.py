import asyncio
import socket
from datetime import datetime
import json
import random
from typing import Dict, Any
import hashlib

class IntelligentHoneypot:
    def __init__(self, ports=[22, 23, 80, 443, 3389, 5900]):
        self.ports = ports
        self.attacks_log = []
        self.attackers_db = {}
        self.services = {
            22: 'SSH',
            23: 'Telnet', 
            80: 'HTTP',
            443: 'HTTPS',
            3389: 'RDP',
            5900: 'VNC'
        }
        
    async def start_honeypot(self):
        """Inicia el honeypot en múltiples puertos"""
        print(f"[+] Iniciando honeypot inteligente en puertos: {self.ports}")
        
        tasks = []
        for port in self.ports:
            task = asyncio.create_task(self.start_service(port))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def start_service(self, port: int):
        """Inicia un servicio simulado en un puerto específico"""
        server = await asyncio.start_server(
            self.handle_connection, '0.0.0.0', port
        )
        
        print(f"[+] Servicio {self.services.get(port, 'Unknown')} escuchando en puerto {port}")
        
        async with server:
            await server.serve_forever()
    
    async def handle_connection(self, reader, writer):
        """Maneja conexiones entrantes"""
        client_ip = writer.get_extra_info('peername')[0]
        
        print(f"[!] Conexión entrante de {client_ip}")
        
        # Registrar atacante
        attacker_id = self.register_attacker(client_ip)
        
        try:
            # Simular servicio según puerto
            port = writer.get_extra_info('sockname')[1]
            await self.simulate_service(port, reader, writer, attacker_id)
            
        except Exception as e:
            print(f"[-] Error manejando conexión: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def simulate_service(self, port: int, reader, writer, attacker_id: str):
        """Simula diferentes servicios"""
        if port == 22:
            await self.simulate_ssh(reader, writer, attacker_id)
        elif port == 80 or port == 443:
            await self.simulate_http(reader, writer, attacker_id)
        elif port == 3389:
            await self.simulate_rdp(reader, writer, attacker_id)
        else:
            await self.simulate_generic(reader, writer, attacker_id)
    
    async def simulate_ssh(self, reader, writer, attacker_id: str):
        """Simula servidor SSH"""
        banner = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.3\r\n"
        writer.write(banner.encode())
        await writer.drain()
        
        attack_data = {
            'attacker_id': attacker_id,
            'service': 'SSH',
            'timestamp': datetime.now(),
            'activity': []
        }
        
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                command = data.decode('utf-8', errors='ignore')
                attack_data['activity'].append(command)
                
                # Detectar ataques comunes
                if 'root' in command.lower():
                    writer.write(b"Permission denied\r\n".encode())
                    self.log_attack(attack_data, 'SSH Brute Force')
                    break
                else:
                    writer.write(b"Access denied\r\n".encode())
                
                await writer.drain()
                
        except Exception as e:
            print(f"Error en SSH simulation: {e}")
    
    async def simulate_http(self, reader, writer, attacker_id: str):
        """Simula servidor HTTP"""
        attack_data = {
            'attacker_id': attacker_id,
            'service': 'HTTP',
            'timestamp': datetime.now(),
            'requests': []
        }
        
        try:
            data = await reader.read(4096)
            request = data.decode('utf-8', errors='ignore')
            attack_data['requests'].append(request)
            
            # Analizar request HTTP
            if 'wp-admin' in request or 'phpmyadmin' in request:
                self.log_attack(attack_data, 'Web Directory Scanning')
                response = self.generate_http_response(404, 'Not Found')
            elif 'cmd.exe' in request or '/bin/bash' in request:
                self.log_attack(attack_data, 'Command Injection Attempt')
                response = self.generate_http_response(403, 'Forbidden')
            elif 'union select' in request.lower():
                self.log_attack(attack_data, 'SQL Injection Attempt')
                response = self.generate_http_response(500, 'Internal Server Error')
            else:
                response = self.generate_http_response(200, 'OK')
            
            writer.write(response.encode())
            await writer.drain()
            
        except Exception as e:
            print(f"Error en HTTP simulation: {e}")
    
    def generate_http_response(self, status_code: int, message: str) -> str:
        """Genera respuesta HTTP"""
        return f"""HTTP/1.1 {status_code} {message}
Server: nginx/1.18.0
Content-Type: text/html
Connection: close

<html>
<body>
<h1>{status_code} {message}</h1>
</body>
</html>"""
    
    def register_attacker(self, ip: str) -> str:
        """Registra un atacante en la base de datos"""
        attacker_hash = hashlib.md5(ip.encode()).hexdigest()[:8]
        
        if attacker_hash not in self.attackers_db:
            self.attackers_db[attacker_hash] = {
                'ip': ip,
                'first_seen': datetime.now(),
                'last_seen': datetime.now(),
                'attack_count': 0,
                'targeted_ports': set()
            }
        else:
            self.attackers_db[attacker_hash]['last_seen'] = datetime.now()
            self.attackers_db[attacker_hash]['attack_count'] += 1
        
        return attacker_hash
    
    def log_attack(self, attack_data: dict, attack_type: str):
        """Registra un ataque detectado"""
        attack_record = {
            'id': len(self.attacks_log) + 1,
            'type': attack_type,
            **attack_data,
            'timestamp': datetime.now()
        }
        
        self.attacks_log.append(attack_record)
        
        print(f"🚨 ATAQUE DETECTADO - {attack_type}")
        print(f"   📍 IP: {self.attackers_db[attack_data['attacker_id']]['ip']}")
        print(f"   🎯 Servicio: {attack_data['service']}")
        print(f"   ⏰ Hora: {attack_data['timestamp']}")
        
        # Actualizar estadísticas del atacante
        attacker_id = attack_data['attacker_id']
        port = [k for k, v in self.services.items() if v == attack_data['service']][0]
        self.attackers_db[attacker_id]['targeted_ports'].add(port)