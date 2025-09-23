import asyncio
from scapy.all import ARP, Ether, IP, TCP, UDP, ICMP, srp, sr1
from core.scanner import BaseScanner

class NetworkScanner(BaseScanner):
    def __init__(self, target: str, config: Dict[str, Any]):
        super().__init__(target, config)
    
    async def run_scan(self):
        """Escaneo completo de red"""
        tasks = [
            self.ping_sweep(),
            self.port_scan(),
            self.os_detection(),
            self.service_detection()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.compile_results(results)
    
    async def ping_sweep(self) -> Dict[str, Any]:
        """Escaneo de hosts activos en la red"""
        print(f"[+] Realizando ping sweep en {self.target}")
        
        # Implementación con scapy
        result = self.execute_command(['nmap', '-sn', self.target])
        
        active_hosts = []
        if result['success']:
            for line in result['stdout'].split('\n'):
                if 'Nmap scan report for' in line:
                    host = line.split()[-1]
                    active_hosts.append(host)
        
        return {'active_hosts': active_hosts}
    
    async def port_scan(self) -> Dict[str, Any]:
        """Escaneo de puertos"""
        print(f"[+] Escaneando puertos en {self.target}")
        
        scan_types = {
            'tcp_syn': '-sS',
            'tcp_connect': '-sT',
            'udp': '-sU'
        }
        
        scan_results = {}
        for scan_name, flag in scan_types.items():
            command = ['nmap', flag, '-p-', '--open', self.target]
            result = self.execute_command(command)
            
            if result['success']:
                open_ports = self.parse_nmap_output(result['stdout'])
                scan_results[scan_name] = open_ports
        
        return {'port_scan': scan_results}
    
    def parse_nmap_output(self, output: str) -> List[Dict]:
        """Parsea la salida de nmap para extraer puertos abiertos"""
        open_ports = []
        for line in output.split('\n'):
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                port_info = {
                    'port': parts[0].split('/')[0],
                    'state': parts[1],
                    'service': parts[2] if len(parts) > 2 else 'unknown'
                }
                open_ports.append(port_info)
        return open_ports