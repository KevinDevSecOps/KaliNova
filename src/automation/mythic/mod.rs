pub mod client;
pub mod graphql_queries;
pub mod payload_generator;

use serde::{Deserialize, Serialize};
use anyhow::Result;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MythicConfig {
    pub server_url: String,
    pub api_key: String,
    pub websocket_url: String,
    pub callback_host: String,
    pub callback_port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MythicAgentType {
    Apollo,      // C#/.NET
    Poseidon,    // Go
    Tetanus,     // Rust
    Mercury,     // Python
    Kraken,      // C++ (nuestro agente custom)
}

impl ToString for MythicAgentType {
    fn to_string(&self) -> String {
        match self {
            MythicAgentType::Apollo => "apollo".to_string(),
            MythicAgentType::Poseidon => "poseidon".to_string(),
            MythicAgentType::Tetanus => "tetanus".to_string(),
            MythicAgentType::Mercury => "mercury".to_string(),
            MythicAgentType::Kraken => "kraken_cpp".to_string(),
        }
    }
}