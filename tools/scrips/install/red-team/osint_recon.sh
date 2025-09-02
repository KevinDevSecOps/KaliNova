#!/bin/bash
set -e

echo "🔍 Installing OSINT & Recon Tools..."

KALINOVA_BASE="/opt/kalinova"
OSINT_DIR="$KALINOVA_BASE/osint"
LOG_FILE="/var/log/kalinova/osint_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting OSINT tools installation..."

# Install TheHarvester
log "Installing TheHarvester..."
apt-get install -y theharvester

# Install Recon-ng
log "Installing Recon-ng..."
apt-get install -y recon-ng

# Install Maltego
log "Installing Maltego..."
wget -O /tmp/maltego.deb https://maltego-downloads.s3.us-east-2.amazonaws.com/linux/Maltego.v4.5.0.deb
apt-get install -y /tmp/maltego.deb

# Install SpiderFoot
log "Installing SpiderFoot..."
if [ ! -d "$OSINT_DIR/spiderfoot" ]; then
    git clone https://github.com/smicallef/spiderfoot.git $OSINT_DIR/spiderfoot
    cd $OSINT_DIR/spiderfoot
    pip3 install -r requirements.txt
fi

# Install Shodan CLI
log "Installing Shodan..."
pip3 install shodan

# Install Amass
log "Installing Amass..."
apt-get install -y amass

# Install Subfinder
log "Installing Subfinder..."
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Install additional recon tools
log "Installing additional recon tools..."
apt-get install -y \
    dnsrecon \
    dnsenum \
    fierce \
    eyewitness

log "✅ OSINT tools installation completed"