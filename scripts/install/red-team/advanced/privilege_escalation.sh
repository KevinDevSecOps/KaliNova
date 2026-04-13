#!/bin/bash
set -e

echo "👑 Installing Privilege Escalation Tools..."

KALINOVA_BASE="/opt/kalinova"
PRIVESC_DIR="$KALINOVA_BASE/privilege-escalation"
LOG_FILE="/var/log/kalinova/privesc_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting privilege escalation tools installation..."

# Install PEASS
log "Installing PEASS..."
if [ ! -d "$PRIVESC_DIR/peass" ]; then
    git clone https://github.com/carlospolop/PEASS-ng.git $PRIVESC_DIR/peass
fi

# Install LinPEAS
log "Installing LinPEAS..."
cp $PRIVESC_DIR/peass/linPEAS/linpeas.sh /usr/local/bin/

# Install WinPEAS
log "Installing WinPEAS..."
cp $PRIVESC_DIR/peass/winPEAS/winPEAS.bat /usr/local/bin/

# Install Linux Exploit Suggester
log "Installing Linux Exploit Suggester..."
if [ ! -d "$PRIVESC_DIR/les" ]; then
    git clone https://github.com/mzet-/linux-exploit-suggester.git $PRIVESC_DIR/les
    cp $PRIVESC_DIR/les/linux-exploit-suggester.sh /usr/local/bin/
fi

# Install Windows Exploit Suggester
log "Installing Windows Exploit Suggester..."
pip3 install windows-exploit-suggester

# Install beRoot
log "Installing beRoot..."
if [ ! -d "$PRIVESC_DIR/beroot" ]; then
    git clone https://github.com/AlessandroZ/beRoot.git $PRIVESC_DIR/beroot
fi

# Install PowerUp
log "Installing PowerUp..."
if [ ! -d "$PRIVESC_DIR/powerup" ]; then
    git clone https://github.com/PowerShellMafia/PowerSploit.git $PRIVESC_DIR/powerup
fi

# Install Seatbelt
log "Installing Seatbelt..."
if [ ! -d "$PRIVESC_DIR/seatbelt" ]; then
    git clone https://github.com/GhostPack/Seatbelt.git $PRIVESC_DIR/seatbelt
fi

log "✅ Privilege escalation tools installation completed"