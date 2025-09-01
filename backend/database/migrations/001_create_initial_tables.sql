-- 🚀 MIGRAÇÃO INICIAL - SISTEMA CLAUDIA COMPLETO
-- Cria todas as tabelas necessárias para o funcionamento do sistema

-- ========================================
-- TABELAS DE CONVERSAS E CONTEXTOS
-- ========================================

CREATE TABLE IF NOT EXISTS conversation_contexts (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    session_id VARCHAR(100) NOT NULL,
    user_name VARCHAR(100),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    payment_amount DECIMAL(10,2),
    due_date DATE,
    topics_discussed TEXT[],
    intent_history TEXT[],
    sentiment_history TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_contexts_phone ON conversation_contexts(phone);
CREATE INDEX idx_conversation_contexts_last_activity ON conversation_contexts(last_activity);

-- ========================================
-- TABELAS DE APRENDIZADO E QUALIDADE
-- ========================================

CREATE TABLE IF NOT EXISTS response_quality_scores (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    message_text TEXT NOT NULL,
    intent VARCHAR(50) NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    clarity_score DECIMAL(3,2),
    empathy_score DECIMAL(3,2),
    actionability_score DECIMAL(3,2),
    urgency_score DECIMAL(3,2),
    professionalism_score DECIMAL(3,2),
    overall_score DECIMAL(3,2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_response_quality_phone ON response_quality_scores(phone);
CREATE INDEX idx_response_quality_intent ON response_quality_scores(intent);

CREATE TABLE IF NOT EXISTS template_performance (
    id SERIAL PRIMARY KEY,
    intent VARCHAR(50) NOT NULL,
    template_id VARCHAR(100) NOT NULL,
    response_text TEXT NOT NULL,
    client_reaction VARCHAR(50),
    quality_scores JSONB,
    success_rate DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_template_performance_intent ON template_performance(intent);
CREATE INDEX idx_template_performance_success_rate ON template_performance(success_rate);

-- ========================================
-- TABELAS DE CAMPANHAS E DISPAROS
-- ========================================

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(200) NOT NULL,
    description TEXT,
    file_path VARCHAR(500),
    campaign_config JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total_contacts INTEGER DEFAULT 0,
    valid_contacts INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);

CREATE TABLE IF NOT EXISTS campaign_contacts (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    message_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    response_received BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    response_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaign_contacts_campaign_id ON campaign_contacts(campaign_id);
CREATE INDEX idx_campaign_contacts_phone ON campaign_contacts(phone);
CREATE INDEX idx_campaign_contacts_status ON campaign_contacts(status);

-- ========================================
-- TABELAS DE CLIENTES E COBRANÇAS
-- ========================================

CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200),
    cpf VARCHAR(14),
    city VARCHAR(100),
    state VARCHAR(2),
    vendedor VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_city ON clients(city);

CREATE TABLE IF NOT EXISTS billing_records (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    tipo VARCHAR(10),
    fpd_days INTEGER,
    message_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    response_received BOOLEAN DEFAULT FALSE,
    response_text TEXT,
    response_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_billing_records_client_id ON billing_records(client_id);
CREATE INDEX idx_billing_records_status ON billing_records(status);
CREATE INDEX idx_billing_records_due_date ON billing_records(due_date);

-- ========================================
-- TABELAS DE LOGS E MONITORAMENTO
-- ========================================

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    phone VARCHAR(20),
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_logs_category ON system_logs(category);
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- ========================================
-- TABELAS DE CONFIGURAÇÕES E TEMPLATES
-- ========================================

CREATE TABLE IF NOT EXISTS message_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    intent VARCHAR(50) NOT NULL,
    template_text TEXT NOT NULL,
    variables JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_message_templates_intent ON message_templates(intent);
CREATE INDEX idx_message_templates_active ON message_templates(is_active);

CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    config_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_config_key ON system_config(config_key);

-- ========================================
-- INSERIR CONFIGURAÇÕES INICIAIS
-- ========================================

INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('system_version', '2.0.0', 'string', 'Versão atual do sistema'),
('max_retry_attempts', '3', 'integer', 'Número máximo de tentativas de reenvio'),
('rate_limit_messages_per_minute', '10', 'integer', 'Limite de mensagens por minuto'),
('default_message_template', 'Olá {NOME}! Temos uma mensagem importante sobre sua fatura.', 'string', 'Template padrão de mensagem'),
('system_maintenance_mode', 'false', 'boolean', 'Modo de manutenção do sistema'),
('log_retention_days', '30', 'integer', 'Dias para retenção de logs'),
('campaign_batch_size', '100', 'integer', 'Tamanho do lote para processamento de campanhas'),
('redis_cache_ttl_hours', '24', 'integer', 'TTL do cache Redis em horas'),
('postgres_connection_pool_size', '10', 'integer', 'Tamanho do pool de conexões PostgreSQL'),
('whatsapp_api_timeout_seconds', '30', 'integer', 'Timeout da API WhatsApp em segundos')
ON CONFLICT (config_key) DO NOTHING;

-- ========================================
-- INSERIR TEMPLATES INICIAIS
-- ========================================

INSERT INTO message_templates (name, intent, template_text, variables, priority) VALUES
('Lembrete FPD', 'payment_reminder', 'Olá {NOME}! Sua fatura de R$ {VALOR} venceu há {DIAS_FPD} dias. Para evitar bloqueios, regularize seu pagamento o quanto antes.', '["NOME", "VALOR", "DIAS_FPD"]', 1),
('Negociação', 'negotiation', 'Olá {NOME}! Entendemos sua situação. Podemos oferecer condições especiais para facilitar o pagamento da sua fatura de R$ {VALOR}.', '["NOME", "VALOR"]', 2),
('Confirmação', 'payment_confirmation', 'Olá {NOME}! Confirmamos o recebimento do seu pagamento de R$ {VALOR}. Obrigado pela confiança!', '["NOME", "VALOR"]', 3),
('Suporte', 'support', 'Olá {NOME}! Como posso ajudá-lo com sua fatura de R$ {VALOR}? Estou aqui para esclarecer suas dúvidas.', '["NOME", "VALOR"]', 4)
ON CONFLICT DO NOTHING;

-- ========================================
-- CRIAR FUNÇÕES DE ATUALIZAÇÃO
-- ========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em todas as tabelas com updated_at
CREATE TRIGGER update_conversation_contexts_updated_at BEFORE UPDATE ON conversation_contexts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_template_performance_updated_at BEFORE UPDATE ON template_performance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaign_contacts_updated_at BEFORE UPDATE ON campaign_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_billing_records_updated_at BEFORE UPDATE ON billing_records FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_message_templates_updated_at BEFORE UPDATE ON message_templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- CRIAR VIEWS ÚTEIS
-- ========================================

CREATE OR REPLACE VIEW campaign_summary AS
SELECT 
    c.id,
    c.campaign_name,
    c.status,
    c.total_contacts,
    c.valid_contacts,
    c.messages_sent,
    c.errors,
    c.start_time,
    c.end_time,
    ROUND((c.messages_sent::DECIMAL / NULLIF(c.valid_contacts, 0)) * 100, 2) as success_rate
FROM campaigns c;

CREATE OR REPLACE VIEW client_billing_summary AS
SELECT 
    cl.id,
    cl.phone,
    cl.name,
    cl.city,
    cl.status as client_status,
    COUNT(br.id) as total_bills,
    SUM(CASE WHEN br.status = 'pending' THEN 1 ELSE 0 END) as pending_bills,
    SUM(CASE WHEN br.status = 'paid' THEN 1 ELSE 0 END) as paid_bills,
    SUM(CASE WHEN br.status = 'overdue' THEN 1 ELSE 0 END) as overdue_bills,
    SUM(br.amount) as total_amount,
    MAX(br.due_date) as latest_due_date
FROM clients cl
LEFT JOIN billing_records br ON cl.id = br.client_id
GROUP BY cl.id, cl.phone, cl.name, cl.city, cl.status;

-- ========================================
-- FINALIZAR MIGRAÇÃO
-- ========================================

COMMENT ON DATABASE railway IS 'Sistema Claudia - Sistema de Cobrança Inteligente com IA';
COMMENT ON TABLE conversation_contexts IS 'Contextos de conversa ativos dos usuários';
COMMENT ON TABLE response_quality_scores IS 'Scores de qualidade das respostas da IA';
COMMENT ON TABLE template_performance IS 'Performance dos templates de mensagem';
COMMENT ON TABLE campaigns IS 'Campanhas de disparo de mensagens';
COMMENT ON TABLE campaign_contacts IS 'Contatos das campanhas';
COMMENT ON TABLE clients IS 'Clientes do sistema';
COMMENT ON TABLE billing_records IS 'Registros de cobrança';
COMMENT ON TABLE system_logs IS 'Logs do sistema';
COMMENT ON TABLE message_templates IS 'Templates de mensagem';
COMMENT ON TABLE system_config IS 'Configurações do sistema';

-- Verificar se tudo foi criado
SELECT 'Migration completed successfully!' as status;
