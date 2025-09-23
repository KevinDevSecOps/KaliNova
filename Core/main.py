#!/usr/bin/env python3
import asyncio
import argparse
import json
from datetime import datetime
from modules.web_scanner import WebScanner
from modules.network_scanner import NetworkScanner
from core.analyzer import ResultAnalyzer
from core.reporter import ReportGenerator

class KaliNovaPentest:
    def __init__(self, target: str):
        self.target = target
        self.config = {
            'threads': 10,
            'timeout': 30,
            'wordlist': '/usr/share/wordlists/dirb/common.txt'
        }
        self.scanners = []
        self.results = {}
    
    def setup_scanners(self, scan_type: str = "full"):
        """Configura los scanners según el tipo de escaneo"""
        if scan_type in ["web", "full"]:
            self.scanners.append(WebScanner(self.target, self.config))
        
        if scan_type in ["network", "full"]:
            self.scanners.append(NetworkScanner(self.target, self.config))
    
    async def run_pentest(self):
        """Ejecuta el pentest completo"""
        print(f"[*] Iniciando pentest en {self.target}")
        print(f"[*] Hora de inicio: {datetime.now()}")
        
        tasks = [scanner.run_scan() for scanner in self.scanners]
        scan_results = await asyncio.gather(*tasks)
        
        # Combinar resultados
        for i, scanner in enumerate(self.scanners):
            scanner_name = scanner.__class__.__name__.replace('Scanner', '').lower()
            self.results[scanner_name] = scan_results[i]
        
        # Analizar resultados
        analyzer = ResultAnalyzer()
        analysis = analyzer.analyze_vulnerabilities(self.results)
        self.results['analysis'] = analysis
        
        # Generar reporte
        reporter = ReportGenerator()
        report = reporter.generate_report(self.results, self.target)
        
        print(f"[+] Pentest completado")
        print(f"[+] Vulnerabilidades encontradas: {len(analysis['vulnerabilities'])}")
        print(f"[+] Score de riesgo: {analysis['risk_score']:.1f}/10.0")
        
        return report

async def main():
    parser = argparse.ArgumentParser(description='KaliNova - Sistema de Automatización de Pentesting')
    parser.add_argument('target', help='Objetivo a escanear (URL o IP)')
    parser.add_argument('-t', '--type', choices=['web', 'network', 'full'], 
                       default='full', help='Tipo de escaneo')
    parser.add_argument('-o', '--output', help='Archivo de salida para el reporte')
    
    args = parser.parse_args()
    
    # Validar target
    if not args.target.startswith(('http://', 'https://')) and not args.target.replace('.', '').isdigit():
        args.target = f"http://{args.target}"
    
    # Ejecutar pentest
    pentest = KaliNovaPentest(args.target)
    pentest.setup_scanners(args.type)
    
    report = await pentest.run_pentest()
    
    # Guardar reporte
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[+] Reporte guardado en: {args.output}")
    else:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())