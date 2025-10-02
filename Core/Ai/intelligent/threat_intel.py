import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List
import hashlib

class AdvancedThreatIntelligence:
    def __init__(self):
        self.sources = {
            'alienvault': 'https://otx.alienvault.com/api/v1/indicators/',
            'virustotal': 'https://www.virustotal.com/api/v3/',
            'shodan': 'https://api.shodan.io/',
            'threatcrowd': 'https://www.threatcrowd.org/searchApi/v2/'
        }
        self.local_intel_db = {}
        self.ioc_cache = {}
    
    async def enrich_ioc(self, ioc: str, ioc_type: str) -> Dict:
        """Enriquece un Indicador de Compromiso (IOC)"""
        print(f"[+] Enriquenciendo IOC: {ioc} ({ioc_type})")
        
        enrichment_tasks = [
            self.check_virustotal(ioc, ioc_type),
            self.check_alienvault(ioc, ioc_type),
            self.check_shodan(ioc, ioc_type),
            self.analyze_local_intel(ioc, ioc_type)
        ]
        
        results = await asyncio.gather(*enrichment_tasks, return_exceptions=True)
        
        enriched_data = {
            'ioc': ioc,
            'type': ioc_type,
            'enriched_at': datetime.now(),
            'sources': {}
        }
        
        # Combinar resultados
        source_names = ['virustotal', 'alienvault', 'shodan', 'local']
        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                enriched_data['sources'][source_names[i]] = result
        
        # Calcular score de amenaza
        enriched_data['threat_score'] = self.calculate_threat_score(enriched_data)
        enriched_data['verdict'] = self.determine_verdict(enriched_data['threat_score'])
        
        # Cachear resultado
        ioc_hash = hashlib.md5(f"{ioc}{ioc_type}".encode()).hexdigest()
        self.ioc_cache[ioc_hash] = enriched_data
        
        return enriched_data
    
    async def check_virustotal(self, ioc: str, ioc_type: str) -> Dict:
        """Consulta VirusTotal API"""
        try:
            # Simulación - en producción usarías API key real
            if ioc_type == 'ip':
                return {
                    'malicious_detections': random.randint(0, 5),
                    'suspicious_detections': random.randint(0, 3),
                    'reputation': random.randint(-100, 100),
                    'last_analysis': datetime.now().isoformat()
                }
            elif ioc_type == 'hash':
                return {
                    'malicious_detections': random.randint(0, 60),
                    'suspicious_detections': random.randint(0, 10),
                    'file_type': 'PE32 executable',
                    'signature': 'Trojan.Win32.Generic' if random.random() > 0.7 else None
                }
        except Exception as e:
            return {'error': str(e)}
        
        return {}
    
    async def check_alienvault(self, ioc: str, ioc_type: str) -> Dict:
        """Consulta AlienVault OTX"""
        try:
            # Simulación
            pulse_count = random.randint(0, 50)
            return {
                'pulse_count': pulse_count,
                'related_malware': ['Emotet', 'Cobalt Strike'] if pulse_count > 10 else [],
                'threat_score': min(pulse_count / 50.0, 1.0),
                'industries_targeted': ['Finance', 'Healthcare'] if pulse_count > 5 else []
            }
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_threat_score(self, enriched_data: Dict) -> float:
        """Calcula un score de amenaza unificado"""
        score = 0.0
        weight = 0.0
        
        # VirusTotal
        vt_data = enriched_data['sources'].get('virustotal', {})
        if 'malicious_detections' in vt_data:
            malicious = vt_data['malicious_detections']
            score += (malicious / 10.0) * 0.4
            weight += 0.4
        
        # AlienVault
        otx_data = enriched_data['sources'].get('alienvault', {})
        if 'threat_score' in otx_data:
            score += otx_data['threat_score'] * 0.3
            weight += 0.3
        
        # Inteligencia local
        local_data = enriched_data['sources'].get('local', {})
        if 'seen_in_attacks' in local_data:
            score += (local_data['seen_in_attacks'] / 10.0) * 0.3
            weight += 0.3
        
        return score / weight if weight > 0 else 0.0
    
    def determine_verdict(self, threat_score: float) -> str:
        """Determina el veredicto basado en el score"""
        if threat_score > 0.8:
            return 'MALICIOUS'
        elif threat_score > 0.6:
            return 'SUSPICIOUS'
        elif threat_score > 0.3:
            return 'UNKNOWN'
        else:
            return 'CLEAN'
    
    async def bulk_ioc_analysis(self, iocs: List[Dict]) -> Dict:
        """Analiza múltiples IOCs en paralelo"""
        print(f"[+] Analizando {len(iocs)} IOCs...")
        
        tasks = []
        for ioc_data in iocs:
            task = self.enrich_ioc(ioc_data['ioc'], ioc_data['type'])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        analysis_summary = {
            'total_iocs': len(iocs),
            'malicious_count': len([r for r in results if r.get('verdict') == 'MALICIOUS']),
            'suspicious_count': len([r for r in results if r.get('verdict') == 'SUSPICIOUS']),
            'clean_count': len([r for r in results if r.get('verdict') == 'CLEAN']),
            'average_threat_score': np.mean([r.get('threat_score', 0) for r in results]),
            'results': results
        }
        
        return analysis_summary