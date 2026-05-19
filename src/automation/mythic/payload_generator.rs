use super::{MythicConfig, MythicAgentType};
use anyhow::Result;
use std::process::Command;
use colored::*;

pub struct PayloadGenerator {
    config: MythicConfig,
    payloads_dir: String,
}

impl PayloadGenerator {
    pub fn new(config: MythicConfig) -> Self {
        Self {
            config,
            payloads_dir: "/opt/kalinova/mythic/payloads".to_string(),
        }
    }

    pub async fn generate_cpp_agent(&self, callback_host: &str, callback_port: u16) -> Result<String> {
        println!("🦀 Generating C++ agent (Kraken) for Mythic...");
        
        let agent_dir = format!("{}/kraken_cpp", self.payloads_dir);
        std::fs::create_dir_all(&agent_dir)?;
        
        // Compilar agente C++
        let status = Command::new("make")
            .current_dir(&agent_dir)
            .arg(format!("HOST={}", callback_host))
            .arg(format!("PORT={}", callback_port))
            .status()?;
        
        if !status.success() {
            return Err(anyhow::anyhow!("Failed to compile C++ agent"));
        }
        
        let payload_path = format!("{}/kraken.exe", agent_dir);
        let metadata = std::fs::metadata(&payload_path)?;
        
        println!("✅ C++ agent generated: {} ({} bytes)", 
                 payload_path.green(), 
                 metadata.len());
        
        Ok(payload_path)
    }

    pub async fn generate_rust_agent(&self, callback_host: &str, callback_port: u16) -> Result<String> {
        println!("🦀 Generating Rust agent (Tetanus) for Mythic...");
        
        let agent_dir = format!("{}/tetanus", self.payloads_dir);
        std::fs::create_dir_all(&agent_dir)?;
        
        // Clonar o usar template de agente Rust
        if !std::path::Path::new(&format!("{}/Cargo.toml", agent_dir)).exists() {
            let status = Command::new("git")
                .arg("clone")
                .arg("https://github.com/MythicAgents/tetanus.git")
                .arg(&agent_dir)
                .status()?;
            
            if !status.success() {
                return Err(anyhow::anyhow!("Failed to clone Tetanus agent"));
            }
        }
        
        // Configurar callback
        let status = Command::new("cargo")
            .arg("build")
            .arg("--release")
            .current_dir(&agent_dir)
            .status()?;
        
        let payload_path = format!("{}/target/release/tetanus.exe", agent_dir);
        println!("✅ Rust agent generated: {}", payload_path.green());
        
        Ok(payload_path)
    }

    pub async fn generate_payload(&self, agent_type: MythicAgentType, config: PayloadConfig) -> Result<String> {
        match agent_type {
            MythicAgentType::Kraken => self.generate_cpp_agent(&config.callback_host, config.callback_port).await,
            MythicAgentType::Tetanus => self.generate_rust_agent(&config.callback_host, config.callback_port).await,
            _ => Err(anyhow::anyhow!("Agent type not yet implemented")),
        }
    }
}

pub struct PayloadConfig {
    pub callback_host: String,
    pub callback_port: u16,
    pub obfuscate: bool,
    pub sleep_time: u32,
    pub jitter: u8,
}