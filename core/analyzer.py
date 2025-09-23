import json
from typing import Dict, List, Any
from datetime import datetime

class ResultAnalyzer:
    def __init__(self):
        self.severity_levels = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'info': 1
        }
    
    def analyze_vulnerabilities(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza y clasifica vulnerabilidades"""
        vulnerabilities = []
        
        # Análisis de vulnerabilidades web
        if 'web_scan' in scan_results:
            web_vulns = self.analyze_web_vulnerabilities(scan_results['web_scan'])
            vulnerabilities.extend(web_vulns)
        
        # Análisis de vulnerabilidades de red
        if 'network_scan' in scan_results:
            network_vulns = self.analyze_network_vulnerabilities(scan_results['network_scan'])
            vulnerabilities.extend(network_vulns)
        
        return {
            'vulnerabilities': vulnerabilities,
            'summary': self.generate_summary(vulnerabilities),
            'risk_score': self.calculate_risk_score(vulnerabilities)
        }
    
    def analyze_web_vulnerabilities(self, web_results: Dict[str, Any]) -> List[Dict]:
        """Analiza específicamente vulnerabilidades web"""
        vulns = []
        
        if 'xss_vulnerabilities' in web_results:
            for vuln in web_results['xss_vulnerabilities']:
                vulns.append({
                    'type': 'XSS',
                    'severity': 'high',
                    'description': 'Cross-Site Scripting vulnerability detected',
                    'evidence': vuln,
                    'cvss_score': 7.5
                })
        
        if 'sql_injection_vulnerabilities' in web_results:
            for vuln in web_results['sql_injection_vulnerabilities']:
                vulns.append({
                    'type': 'SQL Injection',
                    'severity': 'critical',
                    'description': 'SQL Injection vulnerability detected',
                    'evidence': vuln,
                    'cvss_score': 9.0
                })
        
        return vulns
    
    def calculate_risk_score(self, vulnerabilities: List[Dict]) -> float:
        """Calcula el score de riesgo total"""
        if not vulnerabilities:
            return 0.0
        
        total_score = sum(vuln.get('cvss_score', 0) for vuln in vulnerabilities)
        return min(total_score / len(vulnerabilities), 10.0)