// Sistema de Cobrança Inteligente - Frontend
// Aplicação JavaScript pura para interface web

class BillingApp {
    constructor() {
        this.currentTab = 'billing';
        this.fileData = null;
        this.apiBase = '/api';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkSystemHealth();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab-button').dataset.tab);
            });
        });

        // File upload
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleFileDrop.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Remove file
        document.getElementById('remove-file').addEventListener('click', this.removeFile.bind(this));

        // Buttons
        document.getElementById('validate-btn').addEventListener('click', this.validateData.bind(this));
        document.getElementById('send-btn').addEventListener('click', this.sendBatch.bind(this));
        
        // Conversation features
        document.getElementById('refresh-conversations').addEventListener('click', this.loadConversations.bind(this));
        document.getElementById('test-ai-btn').addEventListener('click', this.testAI.bind(this));
        
        // Modal
        document.getElementById('modal-close').addEventListener('click', this.closeModal.bind(this));
        document.getElementById('modal-cancel').addEventListener('click', this.closeModal.bind(this));
        document.getElementById('modal').addEventListener('click', (e) => {
            if (e.target.id === 'modal') this.closeModal();
        });
        
        // Configuration
        document.getElementById('confidence-threshold').addEventListener('input', (e) => {
            document.getElementById('confidence-value').textContent = e.target.value;
        });
        
        // Database management
        document.getElementById('clear-db-btn').addEventListener('click', this.clearDatabase.bind(this));
        document.getElementById('export-db-btn').addEventListener('click', this.exportDatabase.bind(this));
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        switch(tabName) {
            case 'conversation':
                this.loadConversations();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    // File handling
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.currentTarget.classList.remove('dragover');
    }

    handleFileDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        if (!file.name.endsWith('.json')) {
            this.showToast('error', 'Erro', 'Por favor, selecione um arquivo JSON válido');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                this.fileData = JSON.parse(e.target.result);
                this.displayFileInfo(file);
                this.displayVendasPreview(this.fileData);
                this.enableButtons();
            } catch (error) {
                this.showToast('error', 'Erro', 'Arquivo JSON inválido');
                console.error('JSON parse error:', error);
            }
        };
        reader.readAsText(file);
    }

    displayFileInfo(file) {
        document.getElementById('upload-area').style.display = 'none';
        document.getElementById('file-info').classList.remove('hidden');
        document.getElementById('file-name').textContent = file.name;
        document.getElementById('file-size').textContent = this.formatFileSize(file.size);
    }

    displayVendasPreview(data) {
        const previewContent = document.getElementById('preview-content');
        
        // ✅ NOVO FORMATO: Dados de vendas com "dados_vendas"
        let vendasList = [];
        
        if (Array.isArray(data)) {
            // Processar cada registro
            for (const record of data) {
                if (record.dados_vendas && Array.isArray(record.dados_vendas)) {
                    for (const vendas of record.dados_vendas) {
                        if (vendas.NOME && vendas.DOCUMENTO && vendas.TELEFONE1) {
                            vendasList.push({
                                nome: vendas.NOME,
                                documento: vendas.DOCUMENTO,
                                telefone: vendas.TELEFONE1,
                                cidade: vendas.CIDADE || 'N/A',
                                fpd: vendas.fpd || '0',
                                status: vendas.STATUS || 'N/A',
                                aba_origem: vendas.aba_origem || 'N/A'
                            });
                        }
                    }
                }
            }
        }
        
        if (vendasList.length === 0) {
            previewContent.innerHTML = `
                <div class="preview-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Nenhum registro de vendas válido encontrado no arquivo.</p>
                    <p class="text-muted">Verifique se o arquivo contém a estrutura 'dados_vendas'</p>
                </div>
            `;
            return;
        }
        
        const previewVendas = vendasList.slice(0, 10); // Preview primeiros 10
        
        previewContent.innerHTML = `
            <div style="margin-bottom: 1rem;">
                <strong>Total de registros de vendas:</strong> ${vendasList.length}
                ${vendasList.length > 10 ? `<span style="color: var(--text-muted);">(mostrando primeiros 10)</span>` : ''}
            </div>
            <table class="preview-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Documento</th>
                        <th>Telefone</th>
                        <th>Cidade</th>
                        <th>FPD</th>
                        <th>Status</th>
                        <th>Origem</th>
                    </tr>
                </thead>
                <tbody>
                    ${previewVendas.map(venda => `
                        <tr>
                            <td>${this.escapeHtml(venda.nome || 'N/A')}</td>
                            <td>${this.escapeHtml(venda.documento || 'N/A')}</td>
                            <td>${this.escapeHtml(venda.telefone || 'N/A')}</td>
                            <td>${this.escapeHtml(venda.cidade || 'N/A')}</td>
                            <td>${venda.fpd || '0'}</td>
                            <td>${this.escapeHtml(venda.status || 'N/A')}</td>
                            <td>${this.escapeHtml(venda.aba_origem || 'N/A')}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    removeFile() {
        this.fileData = null;
        document.getElementById('upload-area').style.display = 'block';
        document.getElementById('file-info').classList.add('hidden');
        document.getElementById('preview-content').innerHTML = `
            <div class="preview-empty">
                <i class="fas fa-inbox"></i>
                <p>Faça upload de um arquivo para ver o preview</p>
            </div>
        `;
        this.disableButtons();
        document.getElementById('file-input').value = '';
    }

    enableButtons() {
        document.getElementById('validate-btn').disabled = false;
        document.getElementById('send-btn').disabled = false;
    }

    disableButtons() {
        document.getElementById('validate-btn').disabled = true;
        document.getElementById('send-btn').disabled = true;
    }

    // API calls
    async validateData() {
        if (!this.fileData) {
            this.showToast('warning', 'Aviso', 'Nenhum arquivo selecionado');
            return;
        }

        this.showLoading(true);
        
        try {
            // ✅ NOVO FORMATO: Enviar dados de vendas para validação
            const response = await fetch(`${this.apiBase}/vendas/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.fileData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showVendasValidationResults(result);
                this.showToast('success', 'Sucesso', `Validação concluída: ${result.total_valid} válidos, ${result.total_invalid} inválidos`);
            } else {
                this.showToast('error', 'Erro', result.error || 'Falha na validação');
            }
        } catch (error) {
            this.showToast('error', 'Erro', 'Falha na validação dos dados');
            console.error('Validation error:', error);
        }

        this.showLoading(false);
    }

    showVendasValidationResults(result) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');

        const summary = result.processing_summary;
        const successRate = summary.success_rate.toFixed(1);

        resultsContent.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 1.5rem;">
                <div class="stat-item">
                    <div class="stat-value">${summary.total_records}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--success);">${summary.valid_records}</div>
                    <div class="stat-label">Válidos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--error);">${summary.invalid_records}</div>
                    <div class="stat-label">Inválidos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${successRate}%</div>
                    <div class="stat-label">Taxa de Sucesso</div>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <h4>Distribuição por Cidade (Top 5):</h4>
                <div class="city-stats">
                    ${Object.entries(summary.cities_distribution)
                        .slice(0, 5)
                        .map(([city, count]) => `
                            <div class="city-stat">
                                <span class="city-name">${this.escapeHtml(city)}</span>
                                <span class="city-count">${count}</span>
                            </div>
                        `).join('')}
                </div>
            </div>

            <div style="margin-bottom: 1rem;">
                <h4>Distribuição por FPD:</h4>
                <div class="fpd-stats">
                    ${Object.entries(summary.fpd_distribution)
                        .map(([fpd, count]) => `
                            <div class="fpd-stat">
                                <span class="fpd-value">FPD ${fpd}</span>
                                <span class="fpd-count">${count}</span>
                            </div>
                        `).join('')}
                </div>
            </div>

            ${result.preview_data && result.preview_data.length > 0 ? `
                <div style="margin-top: 1rem;">
                    <h4>Preview dos Dados Válidos:</h4>
                    <div class="preview-table-container">
                        <table class="preview-table">
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>Documento</th>
                                    <th>Telefone</th>
                                    <th>Cidade</th>
                                    <th>FPD</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${result.preview_data.map(venda => `
                                    <tr>
                                        <td>${this.escapeHtml(venda.nome)}</td>
                                        <td>${this.escapeHtml(venda.documento)}</td>
                                        <td>${this.escapeHtml(venda.telefone)}</td>
                                        <td>${this.escapeHtml(venda.cidade)}</td>
                                        <td>${venda.fpd}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            ` : ''}
        `;

        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async sendBatch() {
        if (!this.fileData) {
            this.showToast('warning', 'Aviso', 'Nenhum arquivo selecionado');
            return;
        }

        this.showLoading(true);
        
        try {
            // ✅ NOVO FORMATO: Enviar dados de vendas para processamento
            const response = await fetch(`${this.apiBase}/vendas/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.fileData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showVendasProcessingResults(result);
                this.showToast('success', 'Sucesso', `Processamento concluído: ${result.inserted_count} registros inseridos`);
            } else {
                this.showToast('error', 'Erro', result.error || 'Falha no processamento');
            }
        } catch (error) {
            this.showToast('error', 'Erro', 'Falha no processamento dos dados');
            console.error('Processing error:', error);
        }

        this.showLoading(false);
    }

    showVendasProcessingResults(result) {
        const resultsSection = document.getElementById('results-section');
        const resultsContent = document.getElementById('results-content');

        const summary = result.processing_summary;
        const successRate = summary.success_rate.toFixed(1);

        resultsContent.innerHTML = `
            <div class="stats-grid" style="margin-bottom: 1.5rem;">
                <div class="stat-item">
                    <div class="stat-value">${summary.total_records}</div>
                    <div class="stat-label">Total Processados</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--success);">${result.inserted_count}</div>
                    <div class="stat-label">Inseridos no Banco</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: var(--error);">${summary.invalid_records}</div>
                    <div class="stat-label">Inválidos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${successRate}%</div>
                    <div class="stat-label">Taxa de Sucesso</div>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <h4>Resumo do Processamento:</h4>
                <p><strong>Total de registros:</strong> ${summary.total_records}</p>
                <p><strong>Registros válidos:</strong> ${summary.valid_records}</p>
                <p><strong>Registros inseridos:</strong> ${result.inserted_count}</p>
                <p><strong>Erros de inserção:</strong> ${result.insertion_errors.length}</p>
            </div>

            ${result.insertion_errors && result.insertion_errors.length > 0 ? `
                <div style="margin-top: 1rem;">
                    <h4 style="color: var(--error); margin-bottom: 0.5rem;">Erros de Inserção:</h4>
                    <ul style="margin: 0; padding-left: 1.5rem;">
                        ${result.insertion_errors.map(error => `<li style="color: var(--text-secondary);">${this.escapeHtml(error)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            <div style="margin-top: 1rem;">
                <h4>Distribuição por Cidade:</h4>
                <div class="city-stats">
                    ${Object.entries(summary.cities_distribution)
                        .slice(0, 8)
                        .map(([city, count]) => `
                            <div class="city-stat">
                                <span class="city-name">${this.escapeHtml(city)}</span>
                                <span class="city-count">${count}</span>
                            </div>
                        `).join('')}
                </div>
            </div>
        `;

        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Conversation features
    async loadConversations() {
        const conversationsList = document.getElementById('conversations-list');
        
        conversationsList.innerHTML = `
            <div class="loading-state">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Carregando conversas...</p>
            </div>
        `;

        try {
            const response = await fetch(`${this.apiBase}/conversation/contexts?limit=20`);
            const result = await response.json();

            if (response.ok && result.contexts) {
                this.displayConversations(result.contexts);
            } else {
                conversationsList.innerHTML = `
                    <div class="preview-empty">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erro ao carregar conversas</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Load conversations error:', error);
            conversationsList.innerHTML = `
                <div class="preview-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Falha na conexão</p>
                </div>
            `;
        }
    }

    displayConversations(conversations) {
        const conversationsList = document.getElementById('conversations-list');

        if (conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="preview-empty">
                    <i class="fas fa-comments"></i>
                    <p>Nenhuma conversa ativa</p>
                </div>
            `;
            return;
        }

        conversationsList.innerHTML = conversations.map(conv => `
            <div class="conversation-item" data-phone="${conv.phone}">
                <div class="conversation-info">
                    <div class="conversation-phone">${conv.phone}</div>
                    <div class="conversation-preview">
                        ${conv.user_name ? `${conv.user_name} • ` : ''}
                        ${conv.message_count} mensagens
                    </div>
                    <div class="conversation-meta">
                        <span>Iniciada: ${this.formatDateTime(conv.started_at)}</span>
                        <span>Última atividade: ${this.formatDateTime(conv.last_activity)}</span>
                    </div>
                </div>
                <div class="conversation-actions">
                    <button class="btn btn-secondary" onclick="app.viewConversation('${conv.phone}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-error" onclick="app.deleteConversation('${conv.phone}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    async viewConversation(phone) {
        try {
            const response = await fetch(`${this.apiBase}/conversation/contexts/${encodeURIComponent(phone)}`);
            const result = await response.json();

            if (response.ok && result.context) {
                this.showModal('Detalhes da Conversa', this.formatConversationDetails(result.context));
            } else {
                this.showToast('error', 'Erro', 'Falha ao carregar detalhes da conversa');
            }
        } catch (error) {
            this.showToast('error', 'Erro', 'Falha na conexão');
            console.error('View conversation error:', error);
        }
    }

    async deleteConversation(phone) {
        const confirmed = await this.showConfirmModal(
            'Confirmar Exclusão',
            `Deseja excluir a conversa com ${phone}?`
        );

        if (!confirmed) return;

        try {
            const response = await fetch(`${this.apiBase}/conversation/contexts/${encodeURIComponent(phone)}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('success', 'Sucesso', 'Conversa excluída');
                this.loadConversations();
            } else {
                this.showToast('error', 'Erro', 'Falha ao excluir conversa');
            }
        } catch (error) {
            this.showToast('error', 'Erro', 'Falha na conexão');
            console.error('Delete conversation error:', error);
        }
    }

    formatConversationDetails(context) {
        return `
            <div style="font-family: monospace; font-size: 0.875rem;">
                <p><strong>Telefone:</strong> ${context.phone}</p>
                <p><strong>Nome:</strong> ${context.user_name || 'N/A'}</p>
                <p><strong>Sessão:</strong> ${context.session_id}</p>
                <p><strong>Mensagens:</strong> ${context.message_count}</p>
                <p><strong>Iniciada:</strong> ${this.formatDateTime(context.started_at)}</p>
                <p><strong>Última atividade:</strong> ${this.formatDateTime(context.last_activity)}</p>
                
                ${context.payment_amount ? `<p><strong>Valor:</strong> R$ ${context.payment_amount.toFixed(2)}</p>` : ''}
                ${context.due_date ? `<p><strong>Vencimento:</strong> ${context.due_date}</p>` : ''}
                
                <div style="margin-top: 1rem;">
                    <p><strong>Tópicos discutidos:</strong></p>
                    <div style="margin: 0.5rem 0;">
                        ${context.topics_discussed.map(topic => `<span class="badge intent" style="margin-right: 0.5rem;">${topic}</span>`).join('')}
                    </div>
                </div>
                
                <div style="margin-top: 1rem;">
                    <p><strong>Histórico de sentimentos:</strong></p>
                    <div style="margin: 0.5rem 0;">
                        ${context.sentiment_history.slice(-10).map(sentiment => `<span class="badge sentiment" style="margin-right: 0.5rem;">${sentiment}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    async testAI() {
        const phone = document.getElementById('test-phone').value;
        const message = document.getElementById('test-message').value;

        if (!phone || !message) {
            this.showToast('warning', 'Aviso', 'Preencha telefone e mensagem');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/conversation/process-message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phone: phone,
                    message: message,
                    auto_reply: false
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.displayAIResponse(result.response);
            } else {
                this.showToast('error', 'Erro', result.message || 'Falha no teste da IA');
            }
        } catch (error) {
            this.showToast('error', 'Erro', 'Falha na conexão');
            console.error('Test AI error:', error);
        }
    }

    displayAIResponse(response) {
        const aiResponseDiv = document.getElementById('ai-response');
        
        aiResponseDiv.innerHTML = `
            <h4>Resposta da IA:</h4>
            <p>"${response.text}"</p>
            
            <div class="analysis-info">
                <span class="badge intent">${response.type}</span>
                <span>Confiança: ${(response.confidence * 100).toFixed(1)}%</span>
                ${response.should_escalate ? '<span style="color: var(--warning);">⚠️ Requer escalação</span>' : ''}
            </div>
            
            ${response.suggested_actions && response.suggested_actions.length > 0 ? `
                <div style="margin-top: 1rem;">
                    <strong>Ações sugeridas:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                        ${response.suggested_actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        aiResponseDiv.classList.remove('hidden');
    }

    // Analytics
    async loadAnalytics() {
        await Promise.all([
            this.loadSystemStats(),
            this.loadRecentLogs()
        ]);
    }

    async loadSystemStats() {
        try {
            const [billingResponse, conversationResponse] = await Promise.all([
                fetch(`${this.apiBase}/billing/statistics`),
                fetch(`${this.apiBase}/conversation/statistics`)
            ]);

            const billingStats = await billingResponse.json();
            const conversationStats = await conversationResponse.json();

            this.displaySystemStats(billingStats, conversationStats);
        } catch (error) {
            console.error('Load stats error:', error);
        }
    }

    displaySystemStats(billingStats, conversationStats) {
        const systemStatsDiv = document.getElementById('system-stats');
        
        const sentMessages = billingStats.billing_stats?.sent_messages || 0;
        const activeConversations = conversationStats.conversation_stats?.active_contexts || 0;
        const totalMessages = billingStats.billing_stats?.total_messages || 0;
        const successRate = totalMessages > 0 ? ((sentMessages / totalMessages) * 100).toFixed(1) : 0;

        systemStatsDiv.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${sentMessages}</div>
                <div class="stat-label">Mensagens Enviadas</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${activeConversations}</div>
                <div class="stat-label">Conversas Ativas</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${successRate}%</div>
                <div class="stat-label">Taxa de Sucesso</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">Online</div>
                <div class="stat-label">Status</div>
            </div>
        `;
    }

    async loadRecentLogs() {
        const logsContainer = document.getElementById('recent-logs');
        
        // Mock logs - em uma implementação real, viria da API
        const mockLogs = [
            { level: 'info', timestamp: new Date(), message: 'Sistema iniciado com sucesso' },
            { level: 'info', timestamp: new Date(Date.now() - 60000), message: 'Mensagem de cobrança enviada para +5511999999999' },
            { level: 'warning', timestamp: new Date(Date.now() - 120000), message: 'Taxa de API atingindo limite' },
            { level: 'info', timestamp: new Date(Date.now() - 180000), message: 'Nova conversa iniciada' },
            { level: 'error', timestamp: new Date(Date.now() - 240000), message: 'Falha na conexão com Waha' }
        ];

        logsContainer.innerHTML = mockLogs.map(log => `
            <div class="log-entry ${log.level}">
                [${this.formatDateTime(log.timestamp.toISOString())}] ${log.level.toUpperCase()}: ${log.message}
            </div>
        `).join('');
    }

    // Settings
    async loadSettings() {
        await Promise.all([
            this.loadTemplates(),
            this.loadSystemConfig(),
            this.loadDatabaseStats()
        ]);
    }

    async loadTemplates() {
        const templatesList = document.getElementById('templates-list');
        
        try {
            const response = await fetch(`${this.apiBase}/billing/templates`);
            const result = await response.json();

            if (response.ok && result.templates) {
                this.displayTemplates(result.templates);
            } else {
                templatesList.innerHTML = `
                    <div class="preview-empty">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Erro ao carregar templates</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Load templates error:', error);
            templatesList.innerHTML = `
                <div class="preview-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Falha na conexão</p>
                </div>
            `;
        }
    }

    displayTemplates(templates) {
        const templatesList = document.getElementById('templates-list');
        
        templatesList.innerHTML = Object.values(templates).map(template => `
            <div class="template-item">
                <div class="template-header">
                    <div class="template-title">${template.subject}</div>
                    <div class="template-type">${template.type}</div>
                </div>
                <div class="template-content">${template.content}</div>
                <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--text-muted);">
                    <strong>Variáveis:</strong> ${template.variables.join(', ')}
                </div>
            </div>
        `).join('');
    }

    async loadSystemConfig() {
        // Mock configuration display
        document.getElementById('waha-url').value = 'http://localhost:3000';
        document.getElementById('waha-status').innerHTML = '<span class="status-badge checking">Verificando...</span>';
        
        // Simulate Waha status check
        setTimeout(() => {
            document.getElementById('waha-status').innerHTML = '<span class="status-badge healthy">Conectado</span>';
        }, 1000);
    }

    // System health check
    async checkSystemHealth() {
        const statusIndicator = document.getElementById('system-status');
        
        try {
            const response = await fetch('/health');
            
            if (response.ok) {
                statusIndicator.className = 'status-badge healthy';
                statusIndicator.innerHTML = '<i class="fas fa-check-circle"></i><span>Online</span>';
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            statusIndicator.className = 'status-badge unhealthy';
            statusIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Offline</span>';
        }
    }

    async loadInitialData() {
        // Load initial data for the current tab
        if (this.currentTab === 'conversation') {
            this.loadConversations();
        }
    }

    // Modal management
    showModal(title, content, showButtons = false) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = content;
        
        const footer = document.querySelector('.modal-footer');
        footer.style.display = showButtons ? 'flex' : 'none';
        
        document.getElementById('modal').classList.add('show');
    }

    closeModal() {
        document.getElementById('modal').classList.remove('show');
    }

    showConfirmModal(title, message) {
        return new Promise((resolve) => {
            this.showModal(title, `<p>${message}</p>`, true);
            
            const confirmBtn = document.getElementById('modal-confirm');
            const cancelBtn = document.getElementById('modal-cancel');
            
            const handleConfirm = () => {
                this.closeModal();
                cleanup();
                resolve(true);
            };
            
            const handleCancel = () => {
                this.closeModal();
                cleanup();
                resolve(false);
            };
            
            const cleanup = () => {
                confirmBtn.removeEventListener('click', handleConfirm);
                cancelBtn.removeEventListener('click', handleCancel);
            };
            
            confirmBtn.addEventListener('click', handleConfirm);
            cancelBtn.addEventListener('click', handleCancel);
        });
    }

    // Loading overlay
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }

    // Toast notifications
    showToast(type, title, message) {
        const container = document.getElementById('toast-container');
        const toastId = 'toast-' + Date.now();
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="toast-icon ${icons[type] || icons.info}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                toastElement.remove();
            }
        }, 5000);
    }

    // Utility functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return null;
        try {
            return new Date(dateString).toLocaleDateString('pt-BR');
        } catch {
            return dateString;
        }
    }

    formatDateTime(dateString) {
        if (!dateString) return null;
        try {
            return new Date(dateString).toLocaleString('pt-BR');
        } catch {
            return dateString;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Database management functions
    async loadDatabaseStats() {
        try {
            // Atualizar status do banco
            document.getElementById('db-status').innerHTML = '<span class="status-badge checking">Verificando...</span>';
            
            // Buscar estatísticas do banco
            const response = await fetch(`${this.apiBase}/admin/database/stats`);
            
            if (response.ok) {
                const stats = await response.json();
                
                // Atualizar contadores
                document.getElementById('clients-count').textContent = stats.clients_count || 0;
                document.getElementById('conversations-count').textContent = stats.conversations_count || 0;
                
                // Atualizar status
                document.getElementById('db-status').innerHTML = '<span class="status-badge healthy">Conectado</span>';
            } else {
                throw new Error('Falha ao carregar estatísticas');
            }
        } catch (error) {
            console.error('Database stats error:', error);
            
            // Atualizar status com erro
            document.getElementById('db-status').innerHTML = '<span class="status-badge unhealthy">Erro</span>';
            document.getElementById('clients-count').textContent = '?';
            document.getElementById('conversations-count').textContent = '?';
        }
    }

    async clearDatabase() {
        // Mostrar modal de confirmação
        const confirmed = await this.showConfirmModal(
            '⚠️ Limpar Banco de Dados',
            `
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🗑️</div>
                <h3 style="color: #e53e3e; margin-bottom: 1rem;">ATENÇÃO!</h3>
                <p style="margin-bottom: 1rem; font-size: 1.1rem;">
                    Esta ação irá <strong>PERMANENTEMENTE</strong> remover todos os dados do banco:
                </p>
                <ul style="text-align: left; margin: 1rem 0; padding-left: 2rem;">
                    <li>✅ Todos os clientes cadastrados</li>
                    <li>✅ Todas as conversas e histórico</li>
                    <li>✅ Todos os contextos de cobrança</li>
                    <li>✅ Todas as estatísticas e métricas</li>
                </ul>
                <p style="color: #e53e3e; font-weight: 600; margin-top: 1rem;">
                    ⚠️ Esta ação é <strong>IRREVERSÍVEL</strong> e não pode ser desfeita!
                </p>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                    Digite <strong>"LIMPAR"</strong> para confirmar:
                </p>
                <input type="text" id="confirm-clear" placeholder="Digite LIMPAR" 
                       style="width: 100%; padding: 0.5rem; margin: 1rem 0; border: 2px solid #e53e3e; border-radius: 4px; text-align: center; font-weight: 600;">
            </div>
            `,
            true
        );

        if (!confirmed) return;

        // Verificar se digitou "LIMPAR"
        const confirmInput = document.getElementById('confirm-clear');
        if (confirmInput.value.trim() !== 'LIMPAR') {
            this.showToast('error', 'Confirmação Inválida', 'Você deve digitar "LIMPAR" para confirmar a ação.');
            return;
        }

        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/admin/database/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('success', 'Banco Limpo', `Banco de dados limpo com sucesso! ${result.removed_count} registros removidos.`);
                
                // Recarregar estatísticas
                await this.loadDatabaseStats();
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Erro ao limpar banco');
            }
        } catch (error) {
            console.error('Clear database error:', error);
            this.showToast('error', 'Erro', `Falha ao limpar banco: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    async exportDatabase() {
        try {
            this.showLoading(true);
            
            const response = await fetch(`${this.apiBase}/admin/database/export`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `database_backup_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showToast('success', 'Exportação Concluída', 'Dados do banco exportados com sucesso!');
            } else {
                const error = await response.json();
                throw new Error(error.message || 'Erro ao exportar dados');
            }
        } catch (error) {
            console.error('Export database error:', error);
            this.showToast('error', 'Erro', `Falha ao exportar dados: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BillingApp();
});
