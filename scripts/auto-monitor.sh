#!/bin/bash
# Auto-Monitor para Blacktemplar Bolter
# Monitora sistema e executa atualizações automáticas

HEALTH_CHECK_INTERVAL=300  # 5 minutos
UPDATE_CHECK_INTERVAL=3600 # 1 hora
LOG_FILE="/var/log/blacktemplar-monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Monitoramento contínuo
monitor_loop() {
    log "🔄 Iniciando monitoramento automático..."
    
    local last_update_check=0
    
    while true; do
        # Health check a cada 5 minutos
        if ! ./scripts/health-check.sh > /dev/null 2>&1; then
            log "⚠️ Health check falhou - investigando..."
            
            # Tentar restart automático
            sudo systemctl restart blacktemplar-bolter 2>/dev/null || {
                log "❌ Restart automático falhou"
            }
        fi
        
        # Verificar atualizações a cada hora
        local current_time=$(date +%s)
        if [ $((current_time - last_update_check)) -gt $UPDATE_CHECK_INTERVAL ]; then
            log "🔍 Verificando atualizações disponíveis..."
            
            if ./scripts/update-system.sh check > /dev/null 2>&1; then
                log "📥 Nova versão disponível - iniciando atualização..."
                ./scripts/update-system.sh
            fi
            
            last_update_check=$current_time
        fi
        
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# Instalar como serviço systemd
install_service() {
    log "📦 Instalando serviço de monitoramento..."
    
    sudo tee /etc/systemd/system/blacktemplar-monitor.service > /dev/null << EOF
[Unit]
Description=Blacktemplar Bolter Auto Monitor
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/scripts/auto-monitor.sh
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable blacktemplar-monitor
    sudo systemctl start blacktemplar-monitor
    
    log "✅ Serviço de monitoramento instalado e iniciado"
}

case "${1:-}" in
    "install")
        install_service
        ;;
    "start")
        monitor_loop
        ;;
    *)
        monitor_loop
        ;;
esac