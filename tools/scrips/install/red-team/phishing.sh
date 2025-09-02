#!/bin/bash
set -e

echo "🎣 Installing Phishing Tools..."

KALINOVA_BASE="/opt/kalinova"
PHISHING_DIR="$KALINOVA_BASE/phishing"
LOG_FILE="/var/log/kalinova/phishing_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting phishing tools installation..."

# Install GoPhish
log "Installing GoPhish..."
if [ ! -d "$PHISHING_DIR/gophish" ]; then
    wget -O /tmp/gophish.zip https://github.com/gophish/gophish/releases/latest/download/gophish-v0.12.1-linux-64bit.zip
    unzip /tmp/gophish.zip -d $PHISHING_DIR/gophish
fi

# Install Social Engineering Toolkit
log "Installing SET..."
apt-get install -y setoolkit

# Install King Phisher
log "Installing King Phisher..."
if [ ! -d "$PHISHING_DIR/king-phisher" ]; then
    git clone https://github.com/securestate/king-phisher.git $PHISHING_DIR/king-phisher
    cd $PHISHING_DIR/king-phisher
    pip3 install -r requirements.txt
fi

# Install Evilginx2
log "Installing Evilginx2..."
if [ ! -d "$PHISHING_DIR/evilginx2" ]; then
    git clone https://github.com/kgretzky/evilginx2.git $PHISHING_DIR/evilginx2
    cd $PHISHING_DIR/evilginx2
    make
fi

# Install Modlishka
log "Installing Modlishka..."
if [ ! -d "$PHISHING_DIR/modlishka" ]; then
    git clone https://github.com/drk1wi/Modlishka.git $PHISHING_DIR/modlishka
    cd $PHISHING_DIR/modlishka
    go build
fi

# Install phishing frameworks
log "Installing phishing frameworks..."
if [ ! -d "$PHISHING_DIR/blackeye" ]; then
    git clone https://github.com/An0nUD4Y/blackeye.git $PHISHING_DIR/blackeye
fi

if [ ! -d "$PHISHING_DIR/zphisher" ]; then
    git clone https://github.com/htr-tech/zphisher.git $PHISHING_DIR/zphisher
fi

log "✅ Phishing tools installation completed"