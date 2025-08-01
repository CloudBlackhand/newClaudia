#!/bin/bash
# Health Check Script para Blacktemplar Bolter

API_URL="http://localhost:8000"
LOG_FILE="/var/log/blacktemplar-health.log"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

# Verificar se API está respondendo
check_api() {
    log "Verificando API..."
    
    if curl -s --connect-timeout 10 "$API_URL/api/status" > /dev/null; then
        success "API respondendo"
        return 0
    else
        error "API não está respondendo"
        return 1
    fi
}

# Verificar módulos core
check_core_modules() {
    log "Verificando módulos core..."
    
    local response=$(curl -s --connect-timeout 10 "$API_URL/api/captcha/info" 2>/dev/null)
    
    if echo "$response" | grep -q "Blacktemplar Captcha Solver"; then
        success "Captcha solver funcionando"
    else
        error "Captcha solver com problemas"
        return 1
    fi
    
    return 0
}

# Verificar uso de recursos
check_resources() {
    log "Verificando recursos do sistema..."
    
    # CPU
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    log "CPU Usage: ${cpu_usage}%"
    
    # Memória
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    log "Memory Usage: ${mem_usage}%"
    
    # Disco
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    log "Disk Usage: ${disk_usage}%"
    
    # Verificar limites
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        warning "CPU usage alto: ${cpu_usage}%"
    fi
    
    if (( $(echo "$mem_usage > 80" | bc -l) )); then
        warning "Memory usage alto: ${mem_usage}%"
    fi
    
    if [ "$disk_usage" -gt 80 ]; then
        warning "Disk usage alto: ${disk_usage}%"
    fi
}

# Verificar logs de erro
check_error_logs() {
    log "Verificando logs de erro..."
    
    local error_count=$(tail -100 /var/log/blacktemplar.log 2>/dev/null | grep -i error | wc -l)
    
    if [ "$error_count" -gt 10 ]; then
        warning "Muitos erros nos logs: $error_count"
    else
        success "Logs estão normais"
    fi
}

# Health check completo
main() {
    log "🏥 Iniciando health check do Blacktemplar Bolter"
    
    local exit_code=0
    
    check_api || exit_code=1
    check_core_modules || exit_code=1
    check_resources
    check_error_logs
    
    if [ $exit_code -eq 0 ]; then
        success "🎉 Sistema está saudável!"
    else
        error "⚠️ Sistema tem problemas detectados"
    fi
    
    return $exit_code
}

main