"""
Integraciones con APIs de seguridad externas
"""

import requests
from typing import Dict, List

class SecurityAPIIntegration:
    def __init__(self):
        self.vt_api_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.shodan_api_key = os.getenv('SHODAN_API_KEY')
        
    def check_virustotal(self, ip: str) -> Dict:
        """Consultar IP en VirusTotal"""
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {"x-apikey": self.vt_api_key}
        
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def shodan_scan(self, target: str) -> Dict:
        """Escaneo con Shodan"""
        url = f"https://api.shodan.io/shodan/host/{target}?key={self.shodan_api_key}"
        
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def check_all_threat_intel(self, target: str) -> Dict:
        """Consultar múltiples fuentes de threat intelligence"""
        results = {
            'virustotal': self.check_virustotal(target),
            'shodan': self.shodan_scan(target),
            'abuseipdb': self.check_abuseipdb(target)
        }
        
        return results