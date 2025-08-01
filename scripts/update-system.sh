#!/bin/bash
# Blacktemplar Bolter - Sistema de Atualização Automática
# Zero-downtime updates com rollback automático

set -e

# Configurações
APP_NAME="blacktemplar-bolter"
BACKUP_DIR="/data/backups"
LOG_FILE="/var/log/blacktemplar-update.log"
GITHUB_REPO="seu-usuario/blacktemplar-bolter"
HEALTH_CHECK_URL="http://localhost:8000/api/status"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função de log
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Verificar se é root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Este script não deve ser executado como root"
    fi
}

# Verificar conectividade
check_connectivity() {
    log "🌐 Verificando conectividade..."
    
    if ! curl -s --connect-timeout 10 https://github.com > /dev/null; then
        error "Sem conectividade com GitHub"
    fi
    
    if ! curl -s --connect-timeout 10 "$HEALTH_CHECK_URL" > /dev/null; then
        warning "Sistema atual não está respondendo"
    fi
    
    success "Conectividade OK"
}

# Fazer backup
create_backup() {
    log "💾 Criando backup do sistema atual..."
    
    local backup_name="blacktemplar-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup código
    cp -r . "$backup_path/code/"
    
    # Backup dados
    cp -r /data/faturas "$backup_path/faturas/" 2>/dev/null || true
    cp -r /data/uploads "$backup_path/uploads/" 2>/dev/null || true
    cp -r /data/sessions "$backup_path/sessions/" 2>/dev/null || true
    
    # Backup configurações
    cp .env "$backup_path/" 2>/dev/null || true
    
    # Criar metadata do backup
    cat > "$backup_path/metadata.json" << EOF
{
    "backup_date": "$(date -Iseconds)",
    "version": "$(git describe --tags --always 2>/dev/null || echo 'unknown')",
    "commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "hostname": "$(hostname)",
    "user": "$(whoami)"
}
EOF
    
    success "Backup criado: $backup_path"
    echo "$backup_path" > /tmp/last_backup_path
}

# Verificar nova versão
check_new_version() {
    log "🔍 Verificando nova versão disponível..."
    
    local current_version=$(git describe --tags --always 2>/dev/null || echo "unknown")
    local latest_version=$(curl -s "https://api.github.com/repos/$GITHUB_REPO/releases/latest" | grep '"tag_name":' | cut -d'"' -f4)
    
    if [ -z "$latest_version" ]; then
        error "Não foi possível obter a versão mais recente"
    fi
    
    log "Versão atual: $current_version"
    log "Versão disponível: $latest_version"
    
    if [ "$current_version" = "$latest_version" ]; then
        success "Sistema já está na versão mais recente!"
        exit 0
    fi
    
    echo "$latest_version" > /tmp/target_version
}

# Download da nova versão
download_new_version() {
    local target_version=$(cat /tmp/target_version)
    log "⬇️ Baixando versão $target_version..."
    
    # Criar diretório temporário
    local temp_dir="/tmp/blacktemplar-update-$$"
    mkdir -p "$temp_dir"
    
    # Download
    cd "$temp_dir"
    curl -L "https://github.com/$GITHUB_REPO/archive/refs/tags/$target_version.tar.gz" -o release.tar.gz
    tar -xzf release.tar.gz --strip-components=1
    
    success "Nova versão baixada para: $temp_dir"
    echo "$temp_dir" > /tmp/update_temp_dir
}

# Testes pré-atualização
run_tests() {
    local temp_dir=$(cat /tmp/update_temp_dir)
    log "🧪 Executando testes na nova versão..."
    
    cd "$temp_dir"
    
    # Ativar ambiente virtual
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    
    # Instalar dependências
    pip install -r requirements.txt --quiet
    
    # Testes básicos
    python -c "import core; print('✅ Core imports OK')" || error "Falha nos imports básicos"
    python -c "from core.captcha_solver import CaptchaSolver; print('✅ Captcha solver OK')" || error "Falha no captcha solver"
    python -c "from core.fatura_downloader import FaturaDownloader; print('✅ Fatura downloader OK')" || error "Falha no fatura downloader"
    
    # Teste de configuração
    if [ -f "../.env" ]; then
        cp "../.env" .
        python -c "from config import Config; c=Config(); print('✅ Config OK')" || error "Falha na configuração"
    fi
    
    success "Todos os testes passaram!"
}

# Parar serviços
stop_services() {
    log "⏹️ Parando serviços..."
    
    # Parar serviço systemd se existe
    if systemctl is-active --quiet blacktemplar-bolter; then
        sudo systemctl stop blacktemplar-bolter
        log "Serviço systemd parado"
    fi
    
    # Parar processos Python relacionados
    pkill -f "python.*app.py" 2>/dev/null || true
    pkill -f "blacktemplar" 2>/dev/null || true
    
    # Aguardar parada completa
    sleep 5
    
    success "Serviços parados"
}

# Aplicar atualização
apply_update() {
    local temp_dir=$(cat /tmp/update_temp_dir)
    log "🔄 Aplicando atualização..."
    
    # Backup dos arquivos de configuração atuais
    local config_backup="/tmp/config_backup_$$"
    mkdir -p "$config_backup"
    cp .env "$config_backup/" 2>/dev/null || true
    cp -r /data "$config_backup/" 2>/dev/null || true
    
    # Aplicar nova versão
    rsync -av --exclude='.git' --exclude='venv' --exclude='.env' "$temp_dir/" .
    
    # Restaurar configurações
    cp "$config_backup/.env" . 2>/dev/null || true
    
    # Atualizar dependências
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    python -m playwright install chromium --with-deps
    
    # Executar migrações se existirem
    if [ -f "scripts/migrate.sh" ]; then
        bash scripts/migrate.sh
    fi
    
    success "Atualização aplicada"
}

# Iniciar serviços
start_services() {
    log "▶️ Iniciando serviços..."
    
    # Iniciar via systemd se configurado
    if [ -f "/etc/systemd/system/blacktemplar-bolter.service" ]; then
        sudo systemctl start blacktemplar-bolter
        sleep 10
    else
        # Iniciar manualmente em background
        source venv/bin/activate
        nohup python app.py > /var/log/blacktemplar.log 2>&1 &
        sleep 10
    fi
    
    success "Serviços iniciados"
}

# Verificação pós-atualização
verify_update() {
    log "✅ Verificando atualização..."
    
    local max_attempts=12
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --connect-timeout 5 "$HEALTH_CHECK_URL" > /dev/null; then
            success "Sistema está respondendo!"
            
            # Verificar versão
            local new_version=$(git describe --tags --always 2>/dev/null || echo "unknown")
            log "Nova versão ativa: $new_version"
            
            # Testes funcionais básicos
            if curl -s "$HEALTH_CHECK_URL" | grep -q "success"; then
                success "Health check passou!"
                return 0
            fi
        fi
        
        log "Tentativa $attempt/$max_attempts - Aguardando sistema..."
        sleep 10
        ((attempt++))
    done
    
    error "Sistema não está respondendo após atualização"
}

# Rollback em caso de erro
rollback() {
    local backup_path=$(cat /tmp/last_backup_path 2>/dev/null)
    
    if [ -z "$backup_path" ] || [ ! -d "$backup_path" ]; then
        error "Backup não encontrado para rollback"
    fi
    
    warning "🔄 Executando rollback para backup: $backup_path"
    
    # Parar serviços
    stop_services
    
    # Restaurar código
    rsync -av "$backup_path/code/" .
    
    # Restaurar dados
    rsync -av "$backup_path/faturas/" /data/faturas/ 2>/dev/null || true
    rsync -av "$backup_path/uploads/" /data/uploads/ 2>/dev/null || true
    rsync -av "$backup_path/sessions/" /data/sessions/ 2>/dev/null || true
    
    # Restaurar configuração
    cp "$backup_path/.env" . 2>/dev/null || true
    
    # Reinstalar dependências
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    
    # Reiniciar serviços
    start_services
    
    if verify_update; then
        success "Rollback executado com sucesso!"
    else
        error "Rollback falhou - intervenção manual necessária"
    fi
}

# Limpeza
cleanup() {
    log "🧹 Limpeza..."
    
    # Remover arquivos temporários
    rm -rf /tmp/blacktemplar-update-* 2>/dev/null || true
    rm -f /tmp/target_version /tmp/update_temp_dir /tmp/last_backup_path
    
    # Manter apenas últimos 5 backups
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t | tail -n +6 | xargs -r rm -rf
    fi
    
    success "Limpeza concluída"
}

# Função principal
main() {
    log "🚀 Iniciando atualização do Blacktemplar Bolter"
    
    # Verificações iniciais
    check_root
    check_connectivity
    
    # Processo de atualização
    create_backup
    check_new_version
    download_new_version
    run_tests
    
    # Aplicar atualização
    stop_services
    apply_update
    start_services
    
    # Verificar se funcionou
    if ! verify_update; then
        warning "Atualização falhou - executando rollback"
        rollback
        exit 1
    fi
    
    # Limpeza final
    cleanup
    
    success "🎉 Atualização concluída com sucesso!"
    log "Sistema atualizado e funcionando normalmente"
}

# Tratamento de erros
trap 'error "Erro durante atualização - executando rollback"; rollback' ERR

# Executar se chamado diretamente
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "${1:-}" in
        "rollback")
            rollback
            ;;
        "check")
            check_connectivity
            check_new_version
            ;;
        "backup")
            create_backup
            ;;
        *)
            main
            ;;
    esac
fi