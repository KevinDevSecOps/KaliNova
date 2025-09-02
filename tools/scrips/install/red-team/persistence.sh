#!/bin/bash
set -e

echo "🔒 Installing Persistence Tools..."

KALINOVA_BASE="/opt/kalinova"
PERSIST_DIR="$KALINOVA_BASE/persistence"
LOG_FILE="/var/log/kalinova/persistence_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting persistence tools installation..."

# Install PowerShell
log "Installing PowerShell..."
apt-get install -y powershell

# Install Nishang
log "Installing Nishang..."
if [ ! -d "$PERSIST_DIR/nishang" ]; then
    git clone https://github.com/samratashok/nishang.git $PERSIST_DIR/nishang
fi

# Install Empire
log "Installing Empire..."
if [ ! -d "$PERSIST_DIR/Empire" ]; then
    git clone https://github.com/BC-SECURITY/Empire.git $PERSIST_DIR/Empire
    cd $PERSIST_DIR/Empire
    ./setup/install.sh
fi

# Install Donut
log "Installing Donut..."
if [ ! -d "$PERSIST_DIR/donut" ]; then
    git clone https://github.com/TheWover/donut.git $PERSIST_DIR/donut
    cd $PERSIST_DIR/donut
    make
fi

# Install Shellter
log "Installing Shellter..."
apt-get install -y shellter

# Install Veil-Framework
log "Installing Veil-Framework..."
if [ ! -d "$PERSIST_DIR/veil" ]; then
    git clone https://github.com/Veil-Framework/Veil.git $PERSIST_DIR/veil
    cd $PERSIST_DIR/veil
    ./config/setup.sh --force --silent
fi

# Install SharpShooter
log "Installing SharpShooter..."
if [ ! -d "$PERSIST_DIR/SharpShooter" ]; then
    git clone https://github.com/mdsecactivebreach/SharpShooter.git $PERSIST_DIR/SharpShooter
fi

log "✅ Persistence tools installation completed"