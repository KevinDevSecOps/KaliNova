#!/bin/bash
set -e

echo "🔥🔥🔥 KALINOVA RED TEAM ULTIMATE INSTALLATION 🔥🔥🔥"
echo "===================================================="

KALINOVA_BASE="/opt/kalinova"
LOG_FILE="/var/log/kalinova/full_redteam_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Banner
cat << "EOF"
   ▄████████  ▄█   ▄█          ▄████████ ███▄▄▄▄      ▄████████ 
  ███    ███ ███  ███         ███    ███ ███▀▀▀██▄   ███    ███ 
  ███    █▀  ███▌ ███         ███    █▀  ███   ███   ███    █▀  
  ███        ███▌ ███        ▄███▄▄▄     ███   ███   ███        
▀███████████ ███▌ ███       ▀▀███▀▀▀     ███   ███ ▀███████████ 
         ███ ███  ███         ███    █▄  ███   ███          ███ 
   ▄█    ███ ███  ███▌    ▄   ███    ███ ███   ███    ▄█    ███ 
 ▄████████▀  █▀   █████▄▄██   ██████████  ▀█   █▀   ▄████████▀  
                 ▀                                                
EOF

log "Starting KaliNova Red Team Ultimate Installation..."

# Install base system
log "Updating system..."
apt-get update && apt-get upgrade -y

# Install all modules
modules=(
    "command-control"
    "lateral-movement"
    "persistence"
    "evasion"
    "exfiltration"
    "osint-recon"
    "phishing"
    "privilege-escalation"
    "kerberos-attacks"
    "cloud-pentest"
    "container-escape"
    "active-directory"
    "wireless-attacks"
    "iot-hacking"
    "payload-generation"
    "reverse-engineering"
)

for module in "${modules[@]}"; do
    log "Installing module: $module"
    kalinova-installer install "$module"
done

# Configure environment
log "Configuring environment..."
cat > /etc/profile.d/kalinova.sh << 'EOF'
# KaliNova Red Team Environment
export KALINOVA_HOME=/opt/kalinova
export PATH=$PATH:$KALINOVA_HOME/bin
export PATH=$PATH:$KALINOVA_HOME/scripts

# Red Team aliases
alias c2-start='systemctl start cobalt-strike'
alias c2-stop='systemctl stop cobalt-strike'
alias privesc='linpeas.sh'
alias kerberoast='kerberoast-attack'
alias cloud-scan='scoutsuite'
alias k8s-hunt='kube-hunter'
alias ad-scan='bloodhound'
EOF

source /etc/profile.d/kalinova.sh

log "✅ KaliNova Red Team Ultimate Installation Completed!"
log "🎯 Your system is now ready for Red Team operations!"

# Final message
cat << "EOF"

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎯 KALINOVA RED TEAM ULTIMATE IS READY 🎯                  ║
║                                                              ║
║   Commands available:                                        ║
║   • kalinova-installer list    - List all modules           ║
║   • kalinova-installer install - Install specific module    ║
║   • c2-start/stop              - Control C2 framework       ║
║   • privesc                    - Run privilege escalation   ║
║   • kerberoast                 - Run Kerberoast attack      ║
║   • cloud-scan                 - Scan cloud environment     ║
║                                                              ║
║   For help: kalinova-installer --help                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF