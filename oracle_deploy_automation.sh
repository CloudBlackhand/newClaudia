#!/bin/bash
# Blacktemplar Bolter - Deploy Automático Oracle Cloud
# Script completo para deploy, backup e monitoramento automatizado

set -e  # Parar em caso de erro

# ==============================================
# CONFIGURAÇÕES
# ==============================================
APP_NAME="blacktemplar-bolter"
DOCKER_IMAGE="blacktemplar-bolter:latest"
BACKUP_DIR="/data/backups"
LOG_FILE="/var/log/blacktemplar-deploy.log"
HEALTH_CHECK_URL="http://localhost:8000/api/status"
MAX_DEPLOY_TIME=300  # 5 minutos
ROLLBACK_BACKUP_COUNT=3

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==============================================
# FUNÇÕES UTILITÁRIAS
# ==============================================
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# ==============================================
# VERIFICAÇÕES PRÉ-DEPLOY
# ==============================================
check_prerequisites() {
    log "🔍 Verificando pré-requisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não encontrado!"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não encontrado!"
        exit 1
    fi
    
    # Verificar espaço em disco (mínimo 2GB)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 2097152 ]; then
        log_error "Espaço em disco insuficiente! Disponível: $(($AVAILABLE_SPACE/1024))MB"
        exit 1
    fi
    
    # Verificar arquivo .env
    if [ ! -f ".env" ]; then
        if [ -f "env-oracle-template.txt" ]; then
            log_warn "Arquivo .env não encontrado. Criando a partir do template..."
            cp env-oracle-template.txt .env
            log_warn "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!"
            read -p "Pressione Enter para continuar após editar o .env..."
        else
            log_error "Arquivo .env não encontrado e template não disponível!"
            exit 1
        fi
    fi
    
    log "✅ Pré-requisitos verificados com sucesso"
}

# ==============================================
# SISTEMA DE BACKUP
# ==============================================
create_backup() {
    log "💾 Criando backup antes do deploy..."
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="blacktemplar_backup_$BACKUP_TIMESTAMP"
    
    # Criar diretório de backup
    mkdir -p "$BACKUP_DIR"
    
    # Backup dos dados
    tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.log' \
        --exclude='node_modules' \
        . 2>/dev/null || true
    
    # Backup do banco de dados (se existir)
    if [ -d "data" ]; then
        tar -czf "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" data/ 2>/dev/null || true
    fi
    
    # Manter apenas os últimos backups
    cd "$BACKUP_DIR"
    ls -t blacktemplar_backup_*.tar.gz | tail -n +$((ROLLBACK_BACKUP_COUNT + 1)) | xargs -r rm
    cd - > /dev/null
    
    echo "$BACKUP_NAME" > ".last_backup"
    log "✅ Backup criado: $BACKUP_NAME"
}

rollback() {
    log_error "🔄 Iniciando rollback..."
    
    if [ ! -f ".last_backup" ]; then
        log_error "Arquivo de backup não encontrado para rollback!"
        return 1
    fi
    
    BACKUP_NAME=$(cat .last_backup)
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Arquivo de backup não encontrado: $BACKUP_FILE"
        return 1
    fi
    
    # Parar containers atuais
    docker-compose down || true
    
    # Restaurar backup
    tar -xzf "$BACKUP_FILE" -C /tmp/rollback_temp/
    rsync -av /tmp/rollback_temp/ ./ --exclude='.git'
    rm -rf /tmp/rollback_temp/
    
    # Restart com versão anterior
    docker-compose up -d
    
    log "✅ Rollback concluído para backup: $BACKUP_NAME"
}

# ==============================================
# DEPLOY
# ==============================================
deploy() {
    log "🚀 Iniciando deploy..."
    
    # Backup antes do deploy
    create_backup
    
    # Parar containers atuais (graceful)
    log "⏹️  Parando containers atuais..."
    docker-compose down --timeout 30 || true
    
    # Limpar imagens antigas
    log "🧹 Limpando imagens antigas..."
    docker image prune -f || true
    
    # Build nova imagem
    log "🔨 Construindo nova imagem..."
    if [ -f "Dockerfile.oracle" ]; then
        docker-compose build --no-cache
    else
        log_error "Dockerfile.oracle não encontrado!"
        rollback
        exit 1
    fi
    
    # Iniciar novos containers
    log "🏃 Iniciando novos containers..."
    docker-compose up -d
    
    # Aguardar serviços ficarem prontos
    log "⏳ Aguardando serviços ficarem prontos..."
    sleep 10
    
    # Health check
    if health_check; then
        log "✅ Deploy concluído com sucesso!"
        
        # Limpar backup temporário (manter apenas o último)
        cleanup_old_backups
        
        # Enviar notificação de sucesso
        send_notification "✅ Deploy realizado com sucesso no Oracle Cloud" "success"
        
    else
        log_error "❌ Health check falhou! Iniciando rollback..."
        rollback
        exit 1
    fi
}

# ==============================================
# HEALTH CHECK
# ==============================================
health_check() {
    log "🏥 Executando health checks..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check tentativa $attempt/$max_attempts..."
        
        # Verificar se container está rodando
        if ! docker ps | grep -q "$APP_NAME"; then
            log_warn "Container não está rodando"
            sleep 10
            ((attempt++))
            continue
        fi
        
        # Verificar endpoint de saúde
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log "✅ Health check passou!"
            return 0
        fi
        
        log_warn "Health check falhou, tentando novamente em 10s..."
        sleep 10
        ((attempt++))
    done
    
    log_error "❌ Health check falhou após $max_attempts tentativas"
    return 1
}

# ==============================================
# MONITORAMENTO
# ==============================================
monitor_deploy() {
    log "📊 Monitorando deploy..."
    
    local start_time=$(date +%s)
    local timeout=$MAX_DEPLOY_TIME
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log_error "⏰ Timeout do deploy ($timeout segundos)"
            return 1
        fi
        
        # Verificar logs de erro
        if docker-compose logs --tail=50 2>&1 | grep -i "error\|exception\|failed" > /dev/null; then
            log_warn "⚠️  Erros detectados nos logs"
        fi
        
        # Verificar uso de recursos
        local cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" $APP_NAME 2>/dev/null | tr -d '%' || echo "0")
        local mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $APP_NAME 2>/dev/null | tr -d '%' || echo "0")
        
        if (( $(echo "$cpu_usage > 80" | bc -l) )); then
            log_warn "⚠️  Alto uso de CPU: ${cpu_usage}%"
        fi
        
        if (( $(echo "$mem_usage > 80" | bc -l) )); then
            log_warn "⚠️  Alto uso de memória: ${mem_usage}%"
        fi
        
        sleep 30
    done
}

# ==============================================
# NOTIFICAÇÕES
# ==============================================
send_notification() {
    local message="$1"
    local level="${2:-info}"
    
    # Log local
    case $level in
        "success") log "$message" ;;
        "error") log_error "$message" ;;
        "warning") log_warn "$message" ;;
        *) log_info "$message" ;;
    esac
    
    # Webhook Discord (se configurado)
    if [ -n "$DISCORD_WEBHOOK" ]; then
        curl -H "Content-Type: application/json" \
             -d "{\"content\": \"$message\"}" \
             "$DISCORD_WEBHOOK" &>/dev/null || true
    fi
    
    # Email (se configurado)
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "Blacktemplar Bolter - Deploy Notification" "$NOTIFICATION_EMAIL" || true
    fi
}

# ==============================================
# LIMPEZA
# ==============================================
cleanup_old_backups() {
    log "🧹 Limpando backups antigos..."
    
    # Manter apenas últimos N backups
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t blacktemplar_backup_*.tar.gz 2>/dev/null | tail -n +$((ROLLBACK_BACKUP_COUNT + 1)) | xargs -r rm
        cd - > /dev/null
    fi
    
    # Limpar logs antigos (manter últimos 7 dias)
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Limpar Docker
    docker system prune -f --volumes || true
}

# ==============================================
# MENU PRINCIPAL
# ==============================================
show_menu() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║       BLACKTEMPLAR BOLTER - ORACLE DEPLOY      ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    echo "Escolha uma opção:"
    echo "1. 🚀 Deploy completo (recomendado)"
    echo "2. 💾 Apenas backup"
    echo "3. 🔄 Rollback para último backup"
    echo "4. 🏥 Health check"
    echo "5. 📊 Status do sistema"
    echo "6. 🧹 Limpeza de arquivos antigos"
    echo "7. 📋 Logs do deploy"
    echo "8. ⚙️  Configurações"
    echo "9. 🚪 Sair"
    echo ""
    read -p "Opção [1-9]: " option
    
    case $option in
        1)
            check_prerequisites
            deploy
            ;;
        2)
            create_backup
            ;;
        3)
            rollback
            ;;
        4)
            health_check
            ;;
        5)
            show_status
            ;;
        6)
            cleanup_old_backups
            ;;
        7)
            show_logs
            ;;
        8)
            configure_deployment
            ;;
        9)
            log "👋 Saindo..."
            exit 0
            ;;
        *)
            log_error "Opção inválida!"
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
    show_menu
}

# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================
show_status() {
    log "📊 Status do Sistema:"
    echo ""
    
    # Status dos containers
    echo "🐳 Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(blacktemplar|NAMES)"
    echo ""
    
    # Uso de recursos
    echo "📈 Recursos:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "(blacktemplar|CONTAINER)"
    echo ""
    
    # Última atividade
    echo "📋 Logs recentes:"
    docker-compose logs --tail=5
}

show_logs() {
    log "📋 Logs do Deploy:"
    tail -50 "$LOG_FILE"
}

configure_deployment() {
    echo "⚙️  Configurações de Deploy:"
    echo ""
    echo "Arquivo de configuração: .env"
    echo "Logs: $LOG_FILE"
    echo "Backups: $BACKUP_DIR"
    echo "Health check: $HEALTH_CHECK_URL"
    echo ""
    echo "Para editar configurações:"
    echo "nano .env"
}

# ==============================================
# EXECUÇÃO PRINCIPAL
# ==============================================
main() {
    # Criar diretório de logs
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Banner inicial
    log "🚀 Blacktemplar Bolter - Oracle Cloud Deploy Automation"
    log "Versão: 1.0.0 | Data: $(date)"
    log "Diretório: $(pwd)"
    
    # Verificar se é execução direta ou por parâmetro
    if [ $# -eq 0 ]; then
        show_menu
    else
        case $1 in
            "deploy") check_prerequisites && deploy ;;
            "backup") create_backup ;;
            "rollback") rollback ;;
            "health") health_check ;;
            "status") show_status ;;
            "cleanup") cleanup_old_backups ;;
            *) 
                echo "Uso: $0 [deploy|backup|rollback|health|status|cleanup]"
                exit 1
                ;;
        esac
    fi
}

# Trap para cleanup em caso de interrupção
trap 'log_error "Deploy interrompido pelo usuário"; exit 1' INT TERM

# Executar função principal
main "$@"