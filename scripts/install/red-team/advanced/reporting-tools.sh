#!/bin/bash
set -e

echo "📊 Installing Red Team Reporting Tools..."

KALINOVA_BASE="/opt/kalinova"
REPORT_DIR="$KALINOVA_BASE/reporting"
LOG_FILE="/var/log/kalinova/reporting_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting reporting tools installation..."

# Install Dradis
log "Installing Dradis Framework..."
if [ ! -d "$REPORT_DIR/dradis" ]; then
    git clone https://github.com/dradis/dradis-ce.git $REPORT_DIR/dradis
    cd $REPORT_DIR/dradis
    bundle install
fi

# Install Metasploit reporting
log "Installing Metasploit reporting tools..."
gem install msf-json-to-csv

# Install BloodHound reporting
log "Installing BloodHound reporting tools..."
pip3 install bloodhound-import

# Install custom report generator
log "Installing custom report generator..."
cat > /usr/local/bin/redteam-report << 'EOF'
#!/bin/bash
echo "📝 Generating Red Team report..."
echo "Report generated on: $(date)" > /tmp/redteam_report.txt
echo "=================================" >> /tmp/redteam_report.txt
echo "Tools installed: " >> /tmp/redteam_report.txt
ls /opt/kalinova/*/ >> /tmp/redteam_report.txt 2>/dev/null
cat /tmp/redteam_report.txt
EOF
chmod +x /usr/local/bin/redteam-report

log "✅ Reporting tools installation completed"