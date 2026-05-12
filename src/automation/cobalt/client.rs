use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::collections::HashMap;
use anyhow::Result;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CobaltConfig {
    pub server_url: String,
    pub username: String,
    pub password: String,
    pub api_key: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beacon {
    pub id: String,
    pub computer: String,
    pub user: String,
    pub internal_ip: String,
    pub external_ip: String,
    pub pid: u32,
    pub process: String,
    pub arch: String,
    pub last_checkin: DateTime<Utc>,
    pub sleep_time: u32,
    pub session_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Listener {
    pub id: String,
    pub name: String,
    pub bind_host: String,
    pub bind_port: u16,
    pub status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub beacon_id: String,
    pub command: String,
    pub args: Vec<String>,
    pub status: TaskStatus,
    pub result: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
}

pub struct CobaltClient {
    config: CobaltConfig,
    http_client: Client,
    session_token: Option<String>,
}

impl CobaltClient {
    pub fn new(config: CobaltConfig) -> Self {
        Self {
            config,
            http_client: Client::new(),
            session_token: None,
        }
    }

    pub async fn authenticate(&mut self) -> Result<()> {
        let response = self.http_client
            .post(&format!("{}/api/login", self.config.server_url))
            .json(&serde_json::json!({
                "username": self.config.username,
                "password": self.config.password
            }))
            .send()
            .await?;

        let data: HashMap<String, String> = response.json().await?;
        self.session_token = Some(data.get("token").ok_or(anyhow::anyhow!("No token"))?.clone());
        
        Ok(())
    }

    pub async fn list_beacons(&self) -> Result<Vec<Beacon>> {
        let response = self.http_client
            .get(&format!("{}/api/beacons", self.config.server_url))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .send()
            .await?;

        let beacons: Vec<Beacon> = response.json().await?;
        Ok(beacons)
    }

    pub async fn execute_command(&self, beacon_id: &str, command: &str, args: &[String]) -> Result<Task> {
        let task = Task {
            id: uuid::Uuid::new_v4().to_string(),
            beacon_id: beacon_id.to_string(),
            command: command.to_string(),
            args: args.to_vec(),
            status: TaskStatus::Pending,
            result: None,
        };

        let response = self.http_client
            .post(&format!("{}/api/beacons/{}/tasks", self.config.server_url, beacon_id))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .json(&task)
            .send()
            .await?;

        let created_task: Task = response.json().await?;
        Ok(created_task)
    }

    pub async fn upload_file(&self, beacon_id: &str, local_path: &str, remote_path: &str) -> Result<()> {
        let file_content = std::fs::read(local_path)?;
        
        let response = self.http_client
            .post(&format!("{}/api/beacons/{}/upload", self.config.server_url, beacon_id))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .multipart(reqwest::multipart::Form::new()
                .text("remote_path", remote_path.to_string())
                .part("file", reqwest::multipart::Part::bytes(file_content)))
            .send()
            .await?;

        if response.status().is_success() {
            Ok(())
        } else {
            Err(anyhow::anyhow!("Upload failed"))
        }
    }

    pub async fn download_file(&self, beacon_id: &str, remote_path: &str, local_path: &str) -> Result<()> {
        let response = self.http_client
            .get(&format!("{}/api/beacons/{}/download", self.config.server_url, beacon_id))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .query(&[("path", remote_path)])
            .send()
            .await?;

        let bytes = response.bytes().await?;
        std::fs::write(local_path, bytes)?;
        
        Ok(())
    }

    pub async fn create_listener(&self, listener_name: &str, bind_host: &str, bind_port: u16) -> Result<Listener> {
        let listener = Listener {
            id: uuid::Uuid::new_v4().to_string(),
            name: listener_name.to_string(),
            bind_host: bind_host.to_string(),
            bind_port,
            status: "pending".to_string(),
        };

        let response = self.http_client
            .post(&format!("{}/api/listeners", self.config.server_url))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .json(&listener)
            .send()
            .await?;

        let created_listener: Listener = response.json().await?;
        Ok(created_listener)
    }

    pub async fn start_listener(&self, listener_id: &str) -> Result<()> {
        let _response = self.http_client
            .post(&format!("{}/api/listeners/{}/start", self.config.server_url, listener_id))
            .header("Authorization", format!("Bearer {}", self.session_token.as_ref().unwrap()))
            .send()
            .await?;

        Ok(())
    }
}