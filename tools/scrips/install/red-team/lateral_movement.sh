#!/bin/bash
set -e

echo "🔄 Installing Lateral Movement Tools..."

KALINOVA_BASE="/opt/kalinova"
LM_DIR="$KALINOVA_BASE/lateral-movement"
LOG_FILE="/var/log/kalinova/lateral_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting lateral movement tools installation..."

# Install CrackMapExec
log "Installing CrackMapExec..."
apt-get install -y crackmapexec

# Install BloodHound
log "Installing BloodHound..."
apt-get install -y bloodhound

# Install Impacket
log "Installing Impacket..."
pip3 install impacket

# Install Evil-WinRM
log "Installing Evil-WinRM..."
gem install evil-winrm

# Install Responder
log "Installing Responder..."
apt-get install -y responder

# Install additional tools
log "Installing additional tools..."
apt-get install -y \
    enum4linux \
    ldapdomaindump \
    smbmap \
    smbclient \
    nbtscan

# Install PowerSploit
log "Installing PowerSploit..."
if [ ! -d "$LM_DIR/PowerSploit" ]; then
    git clone https://github.com/PowerShellMafia/PowerSploit.git $LM_DIR/PowerSploit
fi

# Install AD modules
log "Installing AD modules..."
if [ ! -d "$LM_DIR/SharpHound" ]; then
    git clone https://github.com/BloodHoundAD/SharpHound.git $LM_DIR/SharpHound
fi

log "✅ Lateral movement tools installation completed"