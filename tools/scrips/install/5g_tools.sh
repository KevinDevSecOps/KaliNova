#!/bin/bash
set -e

echo "📡 Installing 5G Pentesting Tools..."

KALINOVA_BASE="/opt/kalinova"
TOOLS_DIR="$KALINOVA_BASE/5g-tools"
LOG_FILE="/var/log/kalinova/5g_install.log"

# Log function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log "❌ Please run as root"
    exit 1
fi

log "Starting 5G tools installation..."

# Create directories
mkdir -p $TOOLS_DIR
mkdir -p $KALINOVA_BASE/bin
mkdir -p $KALINOVA_BASE/lib

# Install basic RF tools
log "Installing RF and SDR tools..."
apt-get install -y --no-install-recommends \
    gqrx-sdr \
    rtl-sdr \
    urh \
    inspectrum \
    cubicsdr \
    sigdigger

# Clone and install 5G specific tools
log "Cloning 5G security tools..."
if [ ! -d "$TOOLS_DIR/5g-RF-Hack-RedTeam" ]; then
    git clone https://github.com/KevinDevSecOps/5g-RF-Hack-RedTeam.git $TOOLS_DIR/5g-RF-Hack-RedTeam
fi

cd $TOOLS_DIR/5g-RF-Hack-RedTeam

# Install Python dependencies
log "Installing Python dependencies..."
pip3 install -r requirements.txt

# Build Rust components
log "Building Rust components..."
if [ -d "src/native/rust" ]; then
    cd src/native/rust
    cargo build --release
    cp target/release/*.so $KALINOVA_BASE/lib/
    cd ../..
fi

# Create symbolic links
log "Creating symbolic links..."
ln -sf $TOOLS_DIR/5g-RF-Hack-RedTeam/main.py /usr/local/bin/5g-scan
ln -sf $TOOLS_DIR/5g-RF-Hack-RedTeam/src/dashboard/app.py /usr/local/bin/5g-dashboard

# Set permissions
chmod +x /usr/local/bin/5g-*
chown -R root:root $TOOLS_DIR

# Create desktop entry
log "Creating desktop entries..."
cat > /usr/share/applications/kalinova-5g.desktop << EOF
[Desktop Entry]
Version=1.0
Name=KaliNova 5G Tools
Comment=5G Security and Pentesting Tools
Exec=5g-dashboard
Icon=/usr/share/icons/hicolor/48x48/apps/kalinova.png
Terminal=false
Type=Application
Categories=Security;Network;
EOF

log "✅ 5G tools installation completed successfully"