use std::process::Command;
use serde::{Deserialize, Serialize};
use tokio::fs;
use std::path::Path;
use colored::*;
use std::error::Error;

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ToolModule {
    pub name: String,
    pub description: String,
    pub install_script: String,
    pub dependencies: Vec<String>,
    pub category: String,
    pub enabled: bool,
    pub version: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct InstallerConfig {
    pub modules: Vec<ToolModule>,
    pub base_path: String,
    pub log_file: String,
}

pub struct ModularInstaller {
    config: InstallerConfig,
}

impl ModularInstaller {
    pub async fn new(config_path: &str) -> Result<Self, Box<dyn Error>> {
        let config_content = fs::read_to_string(config_path).await?;
        let config: InstallerConfig = serde_yaml::from_str(&config_content)?;
        
        // Crear directorio base si no existe
        if !Path::new(&config.base_path).exists() {
            fs::create_dir_all(&config.base_path).await?;
        }
        
        Ok(Self { config })
    }

    pub async fn install_module(&mut self, module_name: &str) -> Result<(), Box<dyn Error>> {
        if let Some(module) = self.config.modules.iter().find(|m| m.name == module_name && m.enabled) {
            self.print_status(&format!("Instalando módulo: {}", module.name), "start");
            
            // Instalar dependencias
            for dep in &module.dependencies {
                self.install_dependency(dep).await?;
            }
            
            // Ejecutar script de instalación
            self.execute_install_script(&module.install_script).await?;
            
            self.print_status(&format!("Módulo {} instalado", module.name), "success");
            self.log_installation(&module, "success").await?;
        } else {
            return Err(format!("Módulo {} no encontrado o deshabilitado", module_name).into());
        }
        
        Ok(())
    }

    pub async fn install_all(&mut self) -> Result<(), Box<dyn Error>> {
        self.print_status("Instalando todos los módulos", "start");
        
        for module in &self.config.modules {
            if module.enabled {
                if let Err(e) = self.install_module(&module.name).await {
                    self.print_status(&format!("Error instalando {}: {}", module.name, e), "error");
                    self.log_installation(&module, &format!("error: {}", e)).await?;
                }
            }
        }
        
        self.print_status("Instalación completa", "success");
        Ok(())
    }

    async fn install_dependency(&self, dependency: &str) -> Result<(), Box<dyn Error>> {
        self.print_status(&format("Instalando dependencia: {}", dependency), "info");
        
        let status = Command::new("apt-get")
            .arg("update")
            .status()?;
            
        if !status.success() {
            return Err("Error updating package list".into());
        }
        
        let status = Command::new("apt-get")
            .arg("install")
            .arg("-y")
            .arg("--no-install-recommends")
            .arg(dependency)
            .status()?;
            
        if !status.success() {
            return Err(format!("Error instalando dependencia: {}", dependency).into());
        }
        
        Ok(())
    }

    async fn execute_install_script(&self, script_path: &str) -> Result<(), Box<dyn Error>> {
        if !Path::new(script_path).exists() {
            return Err(format!("Script no encontrado: {}", script_path).into());
        }
        
        let status = Command::new("bash")
            .arg(script_path)
            .status()?;
            
        if !status.success() {
            return Err(format!("Script ejecutado con errores: {}", script_path).into());
        }
        
        Ok(())
    }

    fn print_status(&self, message: &str, status_type: &str) {
        match status_type {
            "start" => println!("{} {}", "➡️".yellow(), message.yellow()),
            "success" => println!("{} {}", "✅".green(), message.green()),
            "error" => println!("{} {}", "❌".red(), message.red()),
            "info" => println!("{} {}", "ℹ️".blue(), message.blue()),
            _ => println!("{}", message),
        }
    }

    async fn log_installation(&self, module: &ToolModule, status: &str) -> Result<(), Box<dyn Error>> {
        let log_entry = format!(
            "{} - {} - {} - {}\n",
            chrono::Local::now().to_rfc3339(),
            module.name,
            module.version,
            status
        );
        
        fs::append_to_file(&self.config.log_file, log_entry).await?;
        Ok(())
    }

    pub fn list_modules(&self) -> Vec<&ToolModule> {
        self.config.modules.iter().collect()
    }

    pub fn get_module(&self, name: &str) -> Option<&ToolModule> {
        self.config.modules.iter().find(|m| m.name == name)
    }
}

// Función principal para uso desde CLI
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = std::env::args().collect();
    
    let mut installer = ModularInstaller::new("config/modules.yaml").await?;
    
    match args.get(1).map(String::as_str) {
        Some("install-all") => {
            installer.install_all().await?;
        }
        Some("install") => {
            if let Some(module_name) = args.get(2) {
                installer.install_module(module_name).await?;
            } else {
                println!("Usage: {} install <module-name>", args[0]);
            }
        }
        Some("list") => {
            println!("Available modules:");
            for module in installer.list_modules() {
                println!("  • {} ({}) - {}", 
                    module.name.green(), 
                    module.category.blue(),
                    module.description
                );
            }
        }
        _ => {
            println!("KaliNova Modular Installer");
            println!("Usage:");
            println!("  {} install-all", args[0]);
            println!("  {} install <module-name>", args[0]);
            println!("  {} list", args[0]);
        }
    }
    
    Ok(())
}