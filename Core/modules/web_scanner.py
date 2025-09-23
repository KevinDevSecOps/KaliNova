import aiohttp
import asyncio
from urllib.parse import urljoin
from core.scanner import BaseScanner
from bs4 import BeautifulSoup

class WebScanner(BaseScanner):
    def __init__(self, target: str, config: Dict[str, Any]):
        super().__init__(target, config)
        self.discovered_urls = set()
        self.vulnerabilities = []
    
    async def run_scan(self):
        """Ejecuta escaneo web completo"""
        tasks = [
            self.dir_enumeration(),
            self.subdomain_enumeration(),
            self.technology_detection(),
            self.xss_scan(),
            self.sql_injection_scan()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.compile_results(results)
    
    async def dir_enumeration(self) -> Dict[str, Any]:
        """Enumeración de directorios y archivos"""
        print(f"[+] Iniciando enumeración de directorios en {self.target}")
        
        with open(self.config.get('wordlist', '/usr/share/wordlists/dirb/common.txt'), 'r') as f:
            paths = [line.strip() for line in f if line.strip()]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for path in paths[:100]:  # Limitar para demo
                url = urljoin(self.target, path)
                tasks.append(self.async_http_request(session, url))
            
            responses = await asyncio.gather(*tasks)
            
            found_paths = []
            for resp in responses:
                if resp.get('success') and resp.get('status') in [200, 301, 302]:
                    found_paths.append(resp['url'])
            
            return {'dir_enumeration': found_paths}
    
    async def xss_scan(self) -> Dict[str, Any]:
        """Detección básica de vulnerabilidades XSS"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "'\"><script>alert(1)</script>"
        ]
        
        vulnerabilities = []
        async with aiohttp.ClientSession() as session:
            for payload in payloads:
                test_url = f"{self.target}?q={payload}"
                response = await self.async_http_request(session, test_url)
                
                if response.get('success') and payload in response.get('body', ''):
                    vulnerabilities.append({
                        'type': 'XSS',
                        'payload': payload,
                        'url': test_url
                    })
        
        return {'xss_vulnerabilities': vulnerabilities}
    
    async def sql_injection_scan(self) -> Dict[str, Any]:
        """Detección básica de SQL Injection"""
        payloads = [
            "' OR '1'='1",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE users--"
        ]
        
        vulnerabilities = []
        async with aiohttp.ClientSession() as session:
            for payload in payloads:
                test_url = f"{self.target}?id={payload}"
                response = await self.async_http_request(session, test_url)
                
                # Análisis básico de respuestas
                if response.get('success'):
                    body = response.get('body', '').lower()
                    error_indicators = ['sql', 'syntax', 'mysql', 'ora-']
                    
                    if any(indicator in body for indicator in error_indicators):
                        vulnerabilities.append({
                            'type': 'SQL Injection',
                            'payload': payload,
                            'url': test_url
                        })
        
        return {'sql_injection_vulnerabilities': vulnerabilities}