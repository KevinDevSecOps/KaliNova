#!/bin/bash
set -e

echo "📤 Installing Exfiltration Tools..."

KALINOVA_BASE="/opt/kalinova"
EXFIL_DIR="$KALINOVA_BASE/exfiltration"
LOG_FILE="/var/log/kalinova/exfiltration_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting exfiltration tools installation..."

# Install DNS exfiltration tools
log "Installing DNS exfiltration tools..."
if [ ! -d "$EXFIL_DIR/dnscat2" ]; then
    git clone https://github.com/iagox86/dnscat2.git $EXFIL_DIR/dnscat2
    cd $EXFIL_DIR/dnscat2
    make
fi

# Install Iodine (DNS tunneling)
log "Installing Iodine..."
apt-get install -y iodine

# Install Cloakify
log "Installing Cloakify..."
if [ ! -d "$EXFIL_DIR/cloakify" ]; then
    git clone https://github.com/TryCatchHCF/Cloakify.git $EXFIL_DIR/cloakify
fi

# Install Steganography tools
log "Installing steganography tools..."
apt-get install -y \
    steghide \
    stegsnow \
    outguess \
    exiftool

# Install ICMP exfiltration
log "Installing ICMP tools..."
if [ ! -d "$EXFIL_DIR/icmpsh" ]; then
    git clone https://github.com/inquisb/icmpsh.git $EXFIL_DIR/icmpsh
fi

# Install HTTP exfiltration tools
log "Installing HTTP exfiltration tools..."
pip3 install \
    requests \
    urllib3 \
    http-tunneling

# Install Cloud exfiltration tools
log "Installing cloud tools..."
pip3 install \
    boto3 \
    azure-storage-blob \
    google-cloud-storage

log "✅ Exfiltration tools installation completed"