#!/bin/bash
set -e

echo "🕹️ Installing Command & Control Tools..."

KALINOVA_BASE="/opt/kalinova"
C2_DIR="$KALINOVA_BASE/c2-tools"
LOG_FILE="/var/log/kalinova/c2_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting C2 tools installation..."

# Install Metasploit
log "Installing Metasploit Framework..."
apt-get install -y metasploit-framework

# Install Sliver C2
log "Installing Sliver C2..."
if [ ! -d "$C2_DIR/sliver" ]; then
    git clone https://github.com/BishopFox/sliver.git $C2_DIR/sliver
    cd $C2_DIR/sliver
    make && make install
fi

# Install Covenant C2
log "Installing Covenant C2..."
if [ ! -d "$C2_DIR/Covenant" ]; then
    git clone --recurse-submodules https://github.com/cobbr/Covenant.git $C2_DIR/Covenant
    cd $C2_DIR/Covenant/Covenant
    dotnet build
fi

# Install PwnCat
log "Installing PwnCat..."
pip3 install pwncat-cs

# Install Red Team infrastructure tools
log "Installing infrastructure tools..."
apt-get install -y \
    nginx \
    socat \
    netcat-traditional \
    proxychains4 \
    tor

# Install C2 redirectors
log "Installing C2 redirectors..."
if [ ! -d "$C2_DIR/redirectors" ]; then
    git clone https://github.com/0xZDH/C2-Redirectors $C2_DIR/redirectors
fi

# Configure proxychains
log "Configuring proxychains..."
cat > /etc/proxychains4.conf << EOF
strict_chain
quiet_mode
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000
[ProxyList]
socks4  127.0.0.1 9050
EOF

log "✅ C2 tools installation completed"