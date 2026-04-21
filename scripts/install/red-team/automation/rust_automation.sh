#!/bin/bash
set -e

echo "🦀 Installing Rust Automation Engine..."

KALINOVA_BASE="/opt/kalinova"
AUTOMATION_DIR="$KALINOVA_BASE/automation"
LOG_FILE="/var/log/kalinova/rust_automation.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Installing Rust automation engine..."

# Install Rust if not present
if ! command -v rustc &> /dev/null; then
    log "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

# Build automation module
log "Building automation module..."
cd $AUTOMATION_DIR
cargo build --release

# Install binary
cp target/release/kalinova-automation /usr/local/bin/

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/kalinova-automation.service << EOF
[Unit]
Description=KaliNova Automation Engine
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/kalinova
ExecStart=/usr/local/bin/kalinova-automation
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

log "✅ Rust automation engine installed successfully"