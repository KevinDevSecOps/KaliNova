#!/bin/bash
set -e

echo "📋 Installing Red Team campaign templates..."

KALINOVA_BASE="/opt/kalinova"
TEMPLATES_DIR="$KALINOVA_BASE/campaign-templates"

mkdir -p $TEMPLATES_DIR

# Create quick campaign script
cat > /usr/local/bin/run-campaign << 'EOF'
#!/bin/bash
# Quick campaign runner

if [ $# -lt 1 ]; then
    echo "Usage: run-campaign <campaign-name>"
    echo "Available campaigns:"
    ls /opt/kalinova/campaign-templates/*.yaml | xargs -n1 basename | sed 's/.yaml//'
    exit 1
fi

CAMPAIGN_NAME=$1
CONFIG_FILE="/opt/kalinova/campaign-templates/${CAMPAIGN_NAME}.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Campaign template not found: $CAMPAIGN_NAME"
    exit 1
fi

echo "🚀 Running campaign: $CAMPAIGN_NAME"
kalinova-automation run --config "$CONFIG_FILE"
EOF

chmod +x /usr/local/bin/run-campaign

# Create custom campaign creator
cat > /usr/local/bin/create-campaign << 'EOF'
#!/bin/bash
# Interactive campaign creator

read -p "Campaign name: " NAME
read -p "Target IP: " TARGET_IP
read -p "Target domain: " TARGET_DOMAIN
read -p "Username (optional): " USERNAME
read -p "Password (optional): " PASSWORD

cat > "/opt/kalinova/campaign-templates/${NAME}.yaml" << YAML
campaigns:
  - name: "$NAME"
    description: "Custom campaign for $TARGET_IP"
    phases:
      - name: "Custom Phase"
        parallel: false
        on_failure: "stop"
        tasks: []
    config:
      target_ip: "$TARGET_IP"
      target_domain: "$TARGET_DOMAIN"
      credentials:
        username: "$USERNAME"
        password: "$PASSWORD"
      c2_server: ""
      report_path: "/opt/kalinova/reports/${NAME}_report.html"
      stealth_mode: true
      max_concurrent: 3
YAML

echo "✅ Campaign created: /opt/kalinova/campaign-templates/${NAME}.yaml"
EOF

chmod +x /usr/local/bin/create-campaign

log "✅ Campaign templates installed"