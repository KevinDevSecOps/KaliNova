"""
Base Module for KaliNova
Todas los módulos deben heredar de esta clase
"""

from abc import ABC, abstractmethod
import subprocess
import sys

class BaseModule(ABC):
    def __init__(self):
        self.name = "base_module"
        self.version = "1.0.0"
        self.requirements = []
        self.description = "Módulo base de KaliNova"
        
    def check_requirements(self) -> bool:
        """Verificar dependencias del módulo"""
        missing = []
        for req in self.requirements:
            try:
                __import__(req)
            except ImportError:
                missing.append(req)
        
        if missing:
            print(f"❌ Dependencias faltantes: {missing}")
            return False
        return True
    
    def run_command(self, command: str) -> str:
        """Ejecutar comando del sistema"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            return result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return "Comando timeout"
        except Exception as e:
            return str(e)
    
    @abstractmethod
    def execute(self, target: str, **kwargs) -> dict:
        """Método principal que debe implementar cada módulo"""
        pass
    
    def __str__(self):
        return f"{self.name} v{self.version} - {self.description}"