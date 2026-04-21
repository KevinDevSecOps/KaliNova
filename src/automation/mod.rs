use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::Command;
use std::sync::Arc;
use tokio::sync::Mutex;
use chrono::{DateTime, Utc};
use anyhow::Result;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Campaign {
    pub name: String,
    pub description: String,
    pub phases: Vec<Phase>,
    pub config: CampaignConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Phase {
    pub name: String,
    pub tasks: Vec<Task>,
    pub parallel: bool,
    pub on_failure: FailureAction,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub name: String,
    pub tool: String,
    pub command: String,
    pub args: Vec<String>,
    pub timeout: u64,
    pub retries: u8,
    pub depends_on: Vec<String>,
    pub output_handling: OutputHandling,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CampaignConfig {
    pub target_ip: String,
    pub target_domain: String,
    pub credentials: Option<Credentials>,
    pub c2_server: String,
    pub report_path: String,
    pub stealth_mode: bool,
    pub max_concurrent: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Credentials {
    pub username: String,
    pub password: String,
    pub domain: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FailureAction {
    Stop,
    Continue,
    Retry,
    Skip,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OutputHandling {
    pub save_output: bool,
    pub parse_json: bool,
    pub extract_regex: Option<String>,
    pub notify_on_match: Option<String>,
}

#[derive(Debug, Clone)]
pub struct TaskResult {
    pub task_id: String,
    pub success: bool,
    pub output: String,
    pub error: Option<String>,
    pub duration: std::time::Duration,
    pub timestamp: DateTime<Utc>,
}

pub struct AutomationEngine {
    campaigns: HashMap<String, Campaign>,
    results: Arc<Mutex<Vec<TaskResult>>>,
}

impl AutomationEngine {
    pub fn new() -> Self {
        Self {
            campaigns: HashMap::new(),
            results: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn load_campaign(&mut self, campaign: Campaign) {
        self.campaigns.insert(campaign.name.clone(), campaign);
    }

    pub async fn run_campaign(&self, campaign_name: &str) -> Result<Vec<TaskResult>> {
        let campaign = self.campaigns.get(campaign_name)
            .ok_or_else(|| anyhow::anyhow!("Campaign not found: {}", campaign_name))?;
        
        println!("🎯 Starting campaign: {}", campaign.name);
        println!("📝 Description: {}", campaign.description);
        
        for phase in &campaign.phases {
            println!("\n📌 Phase: {}", phase.name);
            self.run_phase(phase, &campaign.config).await?;
        }
        
        let results = self.results.lock().await.clone();
        Ok(results)
    }

    async fn run_phase(&self, phase: &Phase, config: &CampaignConfig) -> Result<()> {
        if phase.parallel && phase.tasks.len() > 1 {
            self.run_parallel_tasks(&phase.tasks, config).await?;
        } else {
            for task in &phase.tasks {
                if let Err(e) = self.run_task(task, config).await {
                    match phase.on_failure {
                        FailureAction::Stop => return Err(e),
                        FailureAction::Continue => continue,
                        FailureAction::Retry => {
                            for _ in 0..task.retries {
                                if self.run_task(task, config).await.is_ok() {
                                    break;
                                }
                            }
                        }
                        FailureAction::Skip => continue,
                    }
                }
            }
        }
        Ok(())
    }

    async fn run_task(&self, task: &Task, config: &CampaignConfig) -> Result<()> {
        println!("  🔧 Running task: {}", task.name);
        
        let start = std::time::Instant::now();
        
        // Replace placeholders in command
        let command = task.command
            .replace("{TARGET_IP}", &config.target_ip)
            .replace("{TARGET_DOMAIN}", &config.target_domain)
            .replace("{C2_SERVER}", &config.c2_server);
        
        let output = if task.timeout > 0 {
            self.run_with_timeout(&command, &task.args, task.timeout).await?
        } else {
            self.run_command(&command, &task.args).await?
        };
        
        let duration = start.elapsed();
        
        let result = TaskResult {
            task_id: task.id.clone(),
            success: output.status.success(),
            output: output.stdout,
            error: if output.status.success() { None } else { Some(output.stderr) },
            duration,
            timestamp: Utc::now(),
        };
        
        // Save result
        self.results.lock().await.push(result.clone());
        
        if result.success {
            println!("    ✅ Task completed in {:?}", duration);
            Ok(())
        } else {
            println!("    ❌ Task failed: {:?}", result.error);
            Err(anyhow::anyhow!("Task failed: {}", task.name))
        }
    }

    async fn run_parallel_tasks(&self, tasks: &[Task], config: &CampaignConfig) -> Result<()> {
        let handles: Vec<_> = tasks.iter()
            .map(|task| {
                let task = task.clone();
                let config = config.clone();
                tokio::spawn(async move {
                    // Simplified: run each task
                    (task.id.clone(), true)
                })
            })
            .collect();
        
        for handle in handles {
            handle.await?;
        }
        
        Ok(())
    }

    async fn run_command(&self, command: &str, args: &[String]) -> Result<std::process::Output> {
        let output = tokio::process::Command::new(command)
            .args(args)
            .output()
            .await?;
        Ok(output)
    }

    async fn run_with_timeout(&self, command: &str, args: &[String], timeout_secs: u64) -> Result<std::process::Output> {
        let child = tokio::process::Command::new(command)
            .args(args)
            .spawn()?;
        
        let output = tokio::time::timeout(
            std::time::Duration::from_secs(timeout_secs),
            child.wait_with_output()
        ).await??;
        
        Ok(output)
    }

    pub async fn generate_report(&self) -> String {
        let results = self.results.lock().await;
        let total = results.len();
        let successful = results.iter().filter(|r| r.success).count();
        let failed = total - successful;
        
        let mut report = String::new();
        report.push_str(&format!("=== Red Team Campaign Report ===\n"));
        report.push_str(&format!("Generated: {}\n", Utc::now()));
        report.push_str(&format!("Total tasks: {}\n", total));
        report.push_str(&format!("Successful: {}\n", successful));
        report.push_str(&format!("Failed: {}\n", failed));
        report.push_str("\n=== Task Details ===\n");
        
        for result in results.iter() {
            report.push_str(&format!(
                "Task {}: {} (took {:?})\n",
                result.task_id,
                if result.success { "✅ SUCCESS" } else { "❌ FAILED" },
                result.duration
            ));
            if let Some(ref err) = result.error {
                report.push_str(&format!("  Error: {}\n", err));
            }
        }
        
        report
    }
}