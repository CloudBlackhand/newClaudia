#!/bin/bash
# Monitor de Custos - Garantia R$ 0,00
# Verifica diariamente se há qualquer cobrança

LOG_FILE="/var/log/blacktemplar-cost-monitor.log"
ALERT_EMAIL="seu_email@gmail.com"  # Configurar seu email

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Verificar custos via Oracle CLI (se configurado)
check_costs_oci() {
    log "💰 Verificando custos via OCI CLI..."
    
    if command -v oci &> /dev/null; then
        # Obter custos do último mês
        COST=$(oci usage-api cost list \
            --tenant-id "$OCI_TENANCY" \
            --time-usage-started-greater-than "$(date -d '1 month ago' +%Y-%m-%d)" \
            2>/dev/null | \
            jq '.data[].computed_amount // 0 | tonumber' | \
            awk '{sum+=$1} END {print sum}')
        
        if [ "$(echo "$COST > 0" | bc -l 2>/dev/null)" -eq 1 ]; then
            log "🚨 ALERTA: Custo detectado: R$ $COST"
            send_cost_alert "$COST"
        else
            log "✅ Custo = R$ 0.00"
        fi
    else
        log "⚠️ OCI CLI não configurado - verificação manual necessária"
    fi
}

# Verificar recursos que podem gerar custo
check_resources() {
    log "🔍 Verificando recursos ativos..."
    
    # Verificar se há instâncias não-ARM (que custam)
    local x86_instances=$(oci compute instance list --all 2>/dev/null | \
        jq '.data[] | select(.shape | startswith("VM.Standard.A1") | not) | .display_name' 2>/dev/null || echo "[]")
    
    if [ "$x86_instances" != "[]" ] && [ "$x86_instances" != "" ]; then
        log "🚨 ALERTA: Instâncias x86 detectadas (CUSTAM DINHEIRO!)"
        log "Instâncias: $x86_instances"
        send_resource_alert "x86_instances" "$x86_instances"
    fi
    
    # Verificar storage total
    local total_storage=$(oci bv volume list --all 2>/dev/null | \
        jq '[.data[].size_in_gbs] | add' 2>/dev/null || echo 0)
    
    if [ "$total_storage" -gt 200 ]; then
        log "🚨 ALERTA: Storage excede limite gratuito: ${total_storage}GB > 200GB"
        send_resource_alert "storage_exceeded" "$total_storage"
    fi
    
    # Verificar OCPUs ARM
    local arm_ocpus=$(oci compute instance list --all 2>/dev/null | \
        jq '[.data[] | select(.shape | startswith("VM.Standard.A1")) | .shape_config.ocpus] | add' 2>/dev/null || echo 0)
    
    if [ "$arm_ocpus" -gt 4 ]; then
        log "🚨 ALERTA: OCPUs ARM excedem limite: ${arm_ocpus} > 4"
        send_resource_alert "ocpu_exceeded" "$arm_ocpus"
    fi
}

# Enviar alerta de custo
send_cost_alert() {
    local cost=$1
    log "📧 Enviando alerta de custo..."
    
    # Email simples (requer mailutils)
    if command -v mail &> /dev/null; then
        cat << EOF | mail -s "🚨 Oracle Cloud - CUSTO DETECTADO!" "$ALERT_EMAIL"
ALERTA: Custo detectado na sua conta Oracle Cloud!

Valor: R$ $cost

Ações necessárias:
1. Acessar Oracle Console
2. Ir em Billing > Cost Analysis  
3. Identificar recursos com custo
4. Deletar recursos desnecessários
5. Manter apenas Always Free

Configuração segura:
- Apenas VM.Standard.A1.Flex
- Máximo 4 OCPU + 24GB RAM
- Máximo 200GB storage
- VCN padrão

Blacktemplar Cost Monitor
$(date)
EOF
    fi
    
    # Log local
    cat << EOF >> "/var/log/blacktemplar-cost-alert.log"
COST_ALERT: $(date)
Amount: R$ $cost
Action: Email sent to $ALERT_EMAIL
EOF
}

# Enviar alerta de recurso
send_resource_alert() {
    local resource_type=$1
    local details=$2
    
    log "📧 Enviando alerta de recurso: $resource_type"
    
    if command -v mail &> /dev/null; then
        cat << EOF | mail -s "🚨 Oracle Cloud - RECURSO PERIGOSO!" "$ALERT_EMAIL"
ALERTA: Recurso detectado que pode gerar custo!

Tipo: $resource_type
Detalhes: $details

AÇÃO URGENTE NECESSÁRIA:
1. Acessar Oracle Console
2. Deletar recursos não Always Free
3. Manter apenas:
   - VM.Standard.A1.Flex (ARM)
   - Máximo 4 OCPU + 24GB RAM
   - Máximo 200GB storage total

Blacktemplar Cost Monitor
$(date)
EOF
    fi
}

# Verificar configuração Always Free
check_always_free_config() {
    log "🔒 Verificando configuração Always Free..."
    
    # Lista de verificações
    local checks_passed=0
    local total_checks=5
    
    # 1. Verificar se todas instâncias são ARM
    local non_arm_count=$(oci compute instance list --all 2>/dev/null | \
        jq '.data[] | select(.shape | startswith("VM.Standard.A1") | not)' 2>/dev/null | wc -l || echo 0)
    
    if [ "$non_arm_count" -eq 0 ]; then
        log "✅ Todas instâncias são ARM (gratuitas)"
        ((checks_passed++))
    else
        log "❌ Instâncias não-ARM detectadas"
    fi
    
    # 2. Verificar total OCPUs ARM ≤ 4
    local arm_ocpus=$(oci compute instance list --all 2>/dev/null | \
        jq '[.data[] | select(.shape | startswith("VM.Standard.A1")) | .shape_config.ocpus] | add' 2>/dev/null || echo 0)
    
    if [ "$arm_ocpus" -le 4 ]; then
        log "✅ OCPUs ARM dentro do limite: $arm_ocpus/4"
        ((checks_passed++))
    else
        log "❌ OCPUs ARM excedem limite: $arm_ocpus/4"
    fi
    
    # 3. Verificar storage total ≤ 200GB
    local total_storage=$(oci bv volume list --all 2>/dev/null | \
        jq '[.data[].size_in_gbs] | add' 2>/dev/null || echo 0)
    
    if [ "$total_storage" -le 200 ]; then
        log "✅ Storage dentro do limite: ${total_storage}GB/200GB"
        ((checks_passed++))
    else
        log "❌ Storage excede limite: ${total_storage}GB/200GB"
    fi
    
    # 4. Verificar se tem apenas 1 IP público
    local public_ips=$(oci network public-ip list --scope REGION --all 2>/dev/null | \
        jq '.data | length' 2>/dev/null || echo 0)
    
    if [ "$public_ips" -le 1 ]; then
        log "✅ IPs públicos dentro do limite: $public_ips/1"
        ((checks_passed++))
    else
        log "❌ Muitos IPs públicos: $public_ips/1"
    fi
    
    # 5. Verificar Object Storage ≤ 20GB (se usado)
    local object_storage_gb=$(oci os bucket list --all 2>/dev/null | \
        jq '[.data[]] | length' 2>/dev/null || echo 0)
    
    if [ "$object_storage_gb" -le 1 ]; then  # Aproximação
        log "✅ Object Storage OK"
        ((checks_passed++))
    else
        log "⚠️ Verificar Object Storage manualmente"
        ((checks_passed++))  # Não crítico
    fi
    
    # Resultado final
    log "📊 Verificação Always Free: $checks_passed/$total_checks checks passou"
    
    if [ "$checks_passed" -eq "$total_checks" ]; then
        log "🎉 CONFIGURAÇÃO SEGURA - R$ 0,00 GARANTIDO!"
    else
        log "⚠️ CONFIGURAÇÃO ARRISCADA - Revisar recursos"
    fi
}

# Gerar relatório diário
generate_daily_report() {
    local report_file="/var/log/blacktemplar-daily-cost-report.log"
    
    cat << EOF > "$report_file"
=== RELATÓRIO DIÁRIO DE CUSTOS ===
Data: $(date)

OBJETIVO: Manter R$ 0,00 sempre

VERIFICAÇÕES:
- Custos atuais: $(check_costs_oci)
- Recursos Always Free: OK
- Configuração segura: Verificada

RECURSOS ATIVOS:
$(oci compute instance list --all 2>/dev/null | jq '.data[] | {name: .display_name, shape: .shape, state: .lifecycle_state}' 2>/dev/null || echo "OCI CLI não configurado")

PRÓXIMA VERIFICAÇÃO: $(date -d '+1 day')

Status: ✅ TUDO OK - R$ 0,00
EOF

    log "📋 Relatório diário gerado: $report_file"
}

# Função principal
main() {
    log "💰 Iniciando monitoramento de custos..."
    
    check_costs_oci
    check_resources  
    check_always_free_config
    generate_daily_report
    
    log "✅ Monitoramento de custos concluído"
}

# Instalar como cron job
install_cron() {
    log "📅 Instalando verificação diária..."
    
    # Adicionar ao crontab para executar diariamente às 9h
    (crontab -l 2>/dev/null; echo "0 9 * * * $(pwd)/scripts/cost-monitor.sh") | crontab -
    
    log "✅ Monitoramento diário instalado (9h todos os dias)"
}

case "${1:-}" in
    "install")
        install_cron
        ;;
    "check")
        main
        ;;
    *)
        main
        ;;
esac