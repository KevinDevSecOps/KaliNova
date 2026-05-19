#!/bin/bash
set -e

echo "🔥 Installing Mythic C2 Framework with C++ Agent..."

KALINOVA_BASE="/opt/kalinova"
MYTHIC_DIR="$KALINOVA_BASE/mythic"
LOG_FILE="/var/log/kalinova/mythic_install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log "Starting Mythic installation..."

# Instalar dependencias
log "Installing dependencies..."
apt-get update && apt-get install -y \
    docker.io \
    docker-compose \
    golang-go \
    nodejs \
    npm \
    python3-pip \
    g++ \
    cmake \
    libssl-dev \
    libcurl4-openssl-dev

# Clonar Mythic
log "Cloning Mythic repository..."
if [ ! -d "$MYTHIC_DIR" ]; then
    git clone https://github.com/its-a-feature/Mythic.git $MYTHIC_DIR
fi

# Instalar Mythic
log "Setting up Mythic..."
cd $MYTHIC_DIR
make install

# Iniciar servicios
log "Starting Mythic services..."
docker-compose -f deployments/mythic/docker-compose.yml up -d

# Compilar agente C++
log "Compiling C++ agent (Kraken)..."
cd $KALINOVA_BASE/src/automation/mythic/agent_cpp
make

# Copiar payload
cp kraken.exe $MYTHIC_DIR/payloads/

# Crear script de control
log "Creating control scripts..."
cat > /usr/local/bin/mythic-control << 'EOF'
#!/bin/bash

case "$1" in
    start)
        cd /opt/kalinova/mythic
        docker-compose -f deployments/mythic/docker-compose.yml up -d
        echo "✅ Mythic started"
        ;;
    stop)
        cd /opt/kalinova/mythic
        docker-compose -f deployments/mythic/docker-compose.yml down
        echo "✅ Mythic stopped"
        ;;
    status)
        cd /opt/kalinova/mythic
        docker-compose -f deployments/mythic/docker-compose.yml ps
        ;;
    logs)
        docker logs -f mythic_server
        ;;
    *)
        echo "Usage: mythic-control {start|stop|status|logs}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/mythic-control

# Mensaje final
cat << "EOF"

╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🦑 MYTHIC C2 FRAMEWORK WITH C++ AGENT INSTALLED 🦑              ║
║                                                                  ║
║   Access URL: https://localhost:7443                             ║
║   Username: mythic_admin                                         ║
║   Password: KaliNova2024!                                        ║
║                                                                  ║
║   C++ Agent (Kraken): /opt/kalinova/mythic/payloads/kraken.exe   ║
║                                                                  ║
║   Commands:                                                      ║
║   • mythic-control start    - Start Mythic                       ║
║   • mythic-control stop     - Stop Mythic                        ║
║   • mythic-control status   - Check status                       ║
║   • mythic-control logs     - View logs                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

EOF

log "✅ Mythic integration completed successfully"