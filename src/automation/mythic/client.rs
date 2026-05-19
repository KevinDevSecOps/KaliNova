use super::{MythicConfig, MythicAgentType};
use serde_json::json;
use reqwest::Client;
use anyhow::Result;
use colored::*;
use std::collections::HashMap;

pub struct MythicClient {
    config: MythicConfig,
    http_client: Client,
    graphql_endpoint: String,
}

#[derive(Debug, Clone)]
pub struct MythicAgent {
    pub id: String,
    pub name: String,
    pub host: String,
    pub user: String,
    pub os: String,
    pub architecture: String,
    pub last_checkin: String,
    pub tasks_pending: Vec<MythicTask>,
}

#[derive(Debug, Clone)]
pub struct MythicTask {
    pub id: String,
    pub command: String,
    pub parameters: String,
    pub status: String,
    pub output: Option<String>,
}

#[derive(Debug, Clone)]
pub struct MythicPayload {
    pub id: String,
    pub name: String,
    pub agent_type: String,
    pub file_path: String,
    pub size: u64,
}

impl MythicClient {
    pub fn new(config: MythicConfig) -> Self {
        Self {
            graphql_endpoint: format!("{}/graphql", config.server_url),
            http_client: Client::new(),
            config,
        }
    }

    pub async fn authenticate(&self) -> Result<String> {
        println!("🔑 Authenticating to Mythic...");
        
        let query = r#"
        mutation Login($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                auth_token
                success
                error
            }
        }
        "#;
        
        let variables = json!({
            "username": "mythic_admin",
            "password": "KaliNova2024!"
        });
        
        let response = self.http_client
            .post(&self.graphql_endpoint)
            .json(&json!({ "query": query, "variables": variables }))
            .send()
            .await?;
        
        let response_json: serde_json::Value = response.json().await?;
        let token = response_json["data"]["login"]["auth_token"]
            .as_str()
            .ok_or_else(|| anyhow::anyhow!("Authentication failed"))?
            .to_string();
        
        println!("✅ Authenticated successfully");
        Ok(token)
    }

    pub async fn list_agents(&self, token: &str) -> Result<Vec<MythicAgent>> {
        println!("📡 Fetching agents from Mythic...");
        
        let query = r#"
        query {
            agents {
                id
                display_name
                host
                user
                os
                architecture
                last_checkin
                tasks {
                    id
                    command
                    status
                    parameters
                }
            }
        }
        "#;
        
        let response = self.http_client
            .post(&self.graphql_endpoint)
            .header("Authorization", format!("Bearer {}", token))
            .json(&json!({ "query": query }))
            .send()
            .await?;
        
        let response_json: serde_json::Value = response.json().await?;
        let agents_data = response_json["data"]["agents"].as_array().unwrap_or(&vec![]);
        
        let mut agents = Vec::new();
        for agent_data in agents_data {
            let tasks = agent_data["tasks"].as_array().unwrap_or(&vec![]);
            let pending_tasks = tasks.iter()
                .map(|t| MythicTask {
                    id: t["id"].as_str().unwrap_or("").to_string(),
                    command: t["command"].as_str().unwrap_or("").to_string(),
                    parameters: t["parameters"].as_str().unwrap_or("").to_string(),
                    status: t["status"].as_str().unwrap_or("").to_string(),
                    output: None,
                })
                .collect();
            
            agents.push(MythicAgent {
                id: agent_data["id"].as_str().unwrap_or("").to_string(),
                name: agent_data["display_name"].as_str().unwrap_or("").to_string(),
                host: agent_data["host"].as_str().unwrap_or("").to_string(),
                user: agent_data["user"].as_str().unwrap_or("").to_string(),
                os: agent_data["os"].as_str().unwrap_or("").to_string(),
                architecture: agent_data["architecture"].as_str().unwrap_or("").to_string(),
                last_checkin: agent_data["last_checkin"].as_str().unwrap_or("").to_string(),
                tasks_pending: pending_tasks,
            });
        }
        
        println!("✅ Found {} agents", agents.len());
        Ok(agents)
    }

    pub async fn send_task(&self, token: &str, agent_id: &str, command: &str, parameters: &str) -> Result<String> {
        println!("📤 Sending task to agent {}: {}", agent_id.cyan(), command.green());
        
        let query = r#"
        mutation CreateTask($agent_id: String!, $command: String!, $parameters: String!) {
            create_task(agent_id: $agent_id, command: $command, parameters: $parameters) {
                id
                success
                error
            }
        }
        "#;
        
        let variables = json!({
            "agent_id": agent_id,
            "command": command,
            "parameters": parameters
        });
        
        let response = self.http_client
            .post(&self.graphql_endpoint)
            .header("Authorization", format!("Bearer {}", token))
            .json(&json!({ "query": query, "variables": variables }))
            .send()
            .await?;
        
        let response_json: serde_json::Value = response.json().await?;
        let task_id = response_json["data"]["create_task"]["id"]
            .as_str()
            .unwrap_or("")
            .to_string();
        
        println!("✅ Task created with ID: {}", task_id);
        Ok(task_id)
    }

    pub async fn execute_on_all_agents(&self, token: &str, command: &str, parameters: &str) -> Result<Vec<String>> {
        let agents = self.list_agents(token).await?;
        let mut task_ids = Vec::new();
        
        println!("🎯 Executing '{}' on {} agents", command.cyan(), agents.len());
        
        for agent in agents {
            let task_id = self.send_task(token, &agent.id, command, parameters).await?;
            task_ids.push(task_id);
            tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
        }
        
        Ok(task_ids)
    }
}