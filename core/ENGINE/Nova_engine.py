#!/usr/bin/env python3
"""
KaliNova Core Engine
🚀 Ethical Pentesting Platform
"""

import importlib
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

class NovaEngine:
    def __init__(self, config_path: str = None):
        self.modules: Dict[str, Any] = {}
        self.config = self.load_config(config_path)
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('kalinova.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('KaliNova')
        
    def load_config(self, config_path: str = None) -> Dict:
        """Cargar configuración desde archivo"""
        default_config = {
            "max_scan_time": 3600,
            "allowed_modules": ["web", "network"],
            "report_format": "json",
            "legal_disclaimer": True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                print(f"Error loading config: {e}")
                
        return default_config
    
    def load_module(self, module_name: str) -> bool:
        """Cargar un módulo dinámicamente"""
        try:
            module_path = f"modules.{module_name}.scanner"
            module = importlib.import_module(module_path)
            self.modules[module_name] = module.Scanner()
            self.logger.info(f"Módulo {module_name} cargado exitosamente")
            return True
        except ImportError as e:
            self.logger.error(f"Error cargando módulo {module_name}: {e}")
            return False
    
    def run_scan(self, target: str, module_type: str, **kwargs) -> Dict:
        """Ejecutar escaneo con módulo específico"""
        if module_type not in self.modules:
            if not self.load_module(module_type):
                return {"error": f"Módulo {module_type} no disponible"}
        
        # Verificar disclaimer legal
        if not kwargs.get('accept_disclaimer', False):
            return {"error": "Debe aceptar el disclaimer legal"}
        
        try:
            self.logger.info(f"Iniciando escaneo de {target} con {module_type}")
            results = self.modules[module_type].execute(target, **kwargs)
            return results
        except Exception as e:
            self.logger.error(f"Error durante el escaneo: {e}")
            return {"error": str(e)}
    
    def list_modules(self) -> List[str]:
        """Listar módulos disponibles"""
        modules_dir = Path("modules")
        return [d.name for d in modules_dir.iterdir() if d.is_dir()]

# Singleton para acceso global
engine = NovaEngine()