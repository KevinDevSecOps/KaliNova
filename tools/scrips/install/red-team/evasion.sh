#!/bin/bash
set -e

echo "👻 Installing Evasion Tools..."

KALINOVA_BASE="/opt/kalinova"
EVASION_DIR="$KALINOVA_BASE/evasion"
LOG_FILE="/var/log/kalinova/evasion_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting evasion tools installation..."

# Install Go
log "Installing Go..."
apt-get install -y golang

# Install Mingw for cross-compilation
log "Instming Mingw..."
apt-get install -y mingw-w64

# Install UPX packer
log "Installing UPX..."
apt-get install -y upx-ucl

# Install Hyperion crypter
log "Installing Hyperion..."
if [ ! -d "$EVASION_DIR/hyperion" ]; then
    git clone https://github.com/nullsecuritynet/tools.git $EVASION_DIR/hyperion
    cd $EVASION_DIR/hyperion
    make
fi

# Install PE-Cloak
log "Installing PE-Cloak..."
if [ ! -d "$EVASION_DIR/pecloak" ]; then
    git clone https://github.com/segofensiva/PE-Cloak.git $EVASION_DIR/pecloak
fi

# Install Shellcode Compiler
log "Installing SCC..."
if [ ! -d "$EVASION_DIR/scc" ]; then
    git clone https://github.com/NytroRST/ShellcodeCompiler.git $EVASION_DIR/scc
fi

# Install AVET
log "Installing AVET..."
if [ ! -d "$EVASION_DIR/avet" ]; then
    git clone https://github.com/govolution/avet.git $EVASION_DIR/avet
fi

# Install Donut (already in persistence but useful here too)
if [ ! -d "$EVASION_DIR/donut" ]; then
    git clone https://github.com/TheWover/donut.git $EVASION_DIR/donut
    cd $EVASION_DIR/donut
    make
fi

log "✅ Evasion tools installation completed"