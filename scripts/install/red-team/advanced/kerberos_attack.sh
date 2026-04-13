#!/bin/bash
set -e

echo "👑 Installing Kerberos Attack Tools..."

KALINOVA_BASE="/opt/kalinova"
KERBEROS_DIR="$KALINOVA_BASE/kerberos-attacks"
LOG_FILE="/var/log/kalinova/kerberos_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting Kerberos attacks tools installation..."

# Install Impacket
log "Installing Impacket..."
pip3 install impacket

# Install Kerberoast
log "Installing Kerberoast..."
if [ ! -d "$KERBEROS_DIR/kerberoast" ]; then
    git clone https://github.com/nidem/kerberoast.git $KERBEROS_DIR/kerberoast
fi

# Install Rubeus
log "Installing Rubeus..."
if [ ! -d "$KERBEROS_DIR/rubeus" ]; then
    git clone https://github.com/GhostPack/Rubeus.git $KERBEROS_DIR/rubeus
fi

# Install Mimikatz
log "Installing Mimikatz..."
if [ ! -d "$KERBEROS_DIR/mimikatz" ]; then
    git clone https://github.com/gentilkiwi/mimikatz.git $KERBEROS_DIR/mimikatz
fi

# Install ASREPRoast
log "Installing ASREPRoast..."
if [ ! -d "$KERBEROS_DIR/asreproast" ]; then
    git clone https://github.com/HarmJ0y/ASREPRoast.git $KERBEROS_DIR/asreproast
fi

# Create helper scripts
log "Creating helper scripts..."
cat > /usr/local/bin/kerberoast-attack << 'EOF'
#!/bin/bash
echo "🔥 Running Kerberoast attack..."
python3 /opt/kalinova/kerberos-attacks/kerberoast/kerberoast.py "$@"
EOF
chmod +x /usr/local/bin/kerberoast-attack

cat > /usr/local/bin/asreproast-attack << 'EOF'
#!/bin/bash
echo "🎯 Running ASREPRoast attack..."
python3 /opt/kalinova/kerberos-attacks/ASREPRoast/ASREPRoast.py "$@"
EOF
chmod +x /usr/local/bin/asreproast-attack

log "✅ Kerberos attacks tools installation completed"