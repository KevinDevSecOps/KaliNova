import asyncio
import aiohttp
import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class BaseScanner:
    def __init__(self, target: str, config: Dict[str, Any]):
        self.target = target
        self.config = config
        self.results = {}
        self.start_time = datetime.now()
    
    async def run_scan(self):
        """Método base para ejecutar escaneos"""
        raise NotImplementedError("Debe implementar run_scan")
    
    def execute_command(self, command: List[str]) -> Dict[str, Any]:
        """Ejecuta comandos del sistema de forma segura"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=self.config.get('timeout', 300)
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout expired'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def async_http_request(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Realiza peticiones HTTP asíncronas"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                return {
                    'url': url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'success': True
                }
        except Exception as e:
            return {'url': url, 'success': False, 'error': str(e)}