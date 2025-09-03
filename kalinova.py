#!/usr/bin/env python3
"""
KaliNova - Main CLI Interface
"""

import argparse
import sys
from core.engine.nova_engine import engine

def show_banner():
    """Mostrar banner de KaliNova"""
    banner = """
    ╔═╗┌─┐┌┬┐┬┌┐┌┌─┐┌─┐┌─┐┬ ┬
    ╠╣ │ │ │ │││││  ├─┤│  ├─┤
    ╚  └─┘ ┴ ┴┘└┘└─┘┴ ┴└─┘┴ ┴
    🚀 Ethical Pentesting Platform
    """
    print(banner)

def legal_disclaimer():
    """Mostrar disclaimer legal"""
    disclaimer = """
    ⚠️  AVISO LEGAL IMPORTANTE ⚠️
    
    KaliNova es una herramienta para:
    ✅ Pentesting autorizado
    ✅ Educación en seguridad
    ✅ Investigación ética
    ✅ Desarrollo defensivo
    
    🚫 NUNCA use esta herramienta para:
    ❌ Acceso no autorizado a sistemas
    ❌ Actividades ilegales
    ❌ Daño a infraestructuras
    ❌ Violación de privacidad
    
    Usted es responsable de cumplir todas las leyes locales.
    """
    print(disclaimer)
    
    response = input("¿Acepta estos términos? (yes/no): ")
    return response.lower() in ['yes', 'y', 'si', 's']

def main():
    """Función principal"""
    show_banner()
    
    parser = argparse.ArgumentParser(description='KaliNova - Ethical Pentesting Platform')
    parser.add_argument('--target', '-t', help='Target to scan')
    parser.add_argument('--module', '-m', help='Module to use', default='web')
    parser.add_argument('--list-modules', '-l', action='store_true', help='List available modules')
    
    args = parser.parse_args()
    
    if args.list_modules:
        modules = engine.list_modules()
        print("📦 Módulos disponibles:")
        for module in modules:
            print(f"  - {module}")
        return
    
    if not args.target:
        print("❌ Error: Debe especificar un target con --target")
        sys.exit(1)
    
    # Verificar disclaimer legal
    if not legal_disclaimer():
        print("❌ Debe aceptar los términos para continuar")
        sys.exit(1)
    
    # Ejecutar escaneo
    print(f"🎯 Iniciando escaneo de {args.target}...")
    results = engine.run_scan(args.target, args.module, accept_disclaimer=True)
    
    # Mostrar resultados
    print("\n📊 Resultados del escaneo:")
    print(f"Target: {results.get('target', 'N/A')}")
    print(f"Tipo: {results.get('scan_type', 'N/A')}")
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"ℹ️  Info encontrada: {len(results.get('info_found', []))}")
        print(f"🛡️  Vulnerabilidades: {len(results.get('vulnerabilities', []))}")

if __name__ == "__main__":
    main()