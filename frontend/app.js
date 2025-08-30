/**
 * Sistema de Cobrança Avançado - Frontend JavaScript
 * Interface responsiva e moderna para gerenciamento do sistema
 */

class BillingSystem {
    constructor() {
        this.apiBase = '/api';
        this.currentTab = 'billing';
        this.selectedFile = null;
        this.validationResult = null;
        this.isProcessing = false;
        this.statusCheckInterval = null;
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.setupFileUpload();
        this.startStatusChecking();
        await this.loadInitialData();
        
        // Mostrar notificação de boas-vindas
        this.showToast('Sistema iniciado com sucesso!', 'success', 'Sistema Online');
    }

    setupEventListeners() {
        // Tab Navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                const tabName = button.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // File input
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelect(e.target.files[0]);
            });
        }

        // Template textarea
        const templateTextarea = document.getElementById('message-template');
        if (templateTextarea) {
            templateTextarea.addEventListener('input', () => {
                this.validationResult = null;
                this.updateProcessButton();
            });
        }
    }

    setupFileUpload() {
        const uploadArea = document.getElementById('upload-area');
        if (!uploadArea) return;

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // Click to upload
        uploadArea.addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'conversations':
                await this.loadConversations();
                break;
            case 'logs':
                await this.loadLogs();
                break;
            case 'stats':
                await this.loadStats();
                break;
        }
    }

    handleFileSelect(file) {
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            this.showToast('Apenas arquivos JSON são aceitos', 'error', 'Arquivo Inválido');
            return;
        }

        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.showToast('Arquivo muito grande (máximo 10MB)', 'error', 'Arquivo Muito Grande');
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        this.validationResult = null;
        this.updateProcessButton();
    }

    displayFileInfo(file) {
        const uploadArea = document.getElementById('upload-area');
        const fileInfo = document.getElementById('file-info');
        const fileName = document.getElementById('file-name');
        const fileSize = document.getElementById('file-size');

        uploadArea.style.display = 'none';
        fileInfo.style.display = 'flex';
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
    }

    clearFile() {
        this.selectedFile = null;
        this.validationResult = null;
        
        document.getElementById('upload-area').style.display = 'block';
        document.getElementById('file-info').style.display = 'none';
        document.getElementById('file-input').value = '';
        
        this.updateProcessButton();
    }

    async validateData() {
        if (!this.selectedFile) {
            this.showToast('Selecione um arquivo JSON primeiro', 'warning', 'Arquivo Necessário');
            return;
        }

        this.showLoading();

        try {
            // Read file content
            const fileContent = await this.readFileContent(this.selectedFile);
            
            // Validate JSON structure
            const jsonValidation = await this.apiCall('GET', '/billing/validate-json', {
                json_data: fileContent
            });

            if (!jsonValidation.is_valid) {
                throw new Error(jsonValidation.error);
            }

            // Validate template
            const template = document.getElementById('message-template').value;
            if (template.trim()) {
                const templateValidation = await this.apiCall('GET', '/billing/validate-template', {
                    template: template
                });

                if (!templateValidation.is_valid) {
                    throw new Error(`Template inválido: ${templateValidation.error}`);
                }
            }

            // Validate billing data
            const billingValidation = await this.apiCall('POST', '/billing/validate-billing-data', {
                json_data: fileContent
            });

            this.validationResult = {
                json: jsonValidation,
                billing: billingValidation,
                template: template
            };

            this.displayValidationResults();
            this.updateProcessButton();

            this.showToast(
                `Validação concluída! ${billingValidation.valid_records} registros válidos de ${billingValidation.total_records}`,
                'success',
                'Dados Validados'
            );

        } catch (error) {
            console.error('Validation error:', error);
            this.showToast(error.message, 'error', 'Erro na Validação');
        } finally {
            this.hideLoading();
        }
    }

    displayValidationResults() {
        // Create or update validation results display
        let resultsDiv = document.getElementById('validation-results');
        if (!resultsDiv) {
            resultsDiv = document.createElement('div');
            resultsDiv.id = 'validation-results';
            resultsDiv.className = 'card';
            
            const validateBtn = document.getElementById('validate-btn');
            validateBtn.parentNode.insertBefore(resultsDiv, validateBtn.nextSibling);
        }

        const { json, billing } = this.validationResult;

        resultsDiv.innerHTML = `
            <div class="card-header">
                <h3><i class="fas fa-check-circle"></i> Resultado da Validação</h3>
            </div>
            <div class="card-body">
                <div class="validation-summary">
                    <div class="validation-stat">
                        <span class="stat-label">Total de Registros:</span>
                        <span class="stat-value">${billing.total_records}</span>
                    </div>
                    <div class="validation-stat">
                        <span class="stat-label">Registros Válidos:</span>
                        <span class="stat-value success">${billing.valid_records}</span>
                    </div>
                    <div class="validation-stat">
                        <span class="stat-label">Registros Inválidos:</span>
                        <span class="stat-value error">${billing.total_records - billing.valid_records}</span>
                    </div>
                </div>
                
                ${billing.errors && billing.errors.length > 0 ? `
                    <div class="validation-errors">
                        <h4><i class="fas fa-exclamation-triangle"></i> Erros Encontrados:</h4>
                        <ul>
                            ${billing.errors.slice(0, 10).map(error => `<li>${error}</li>`).join('')}
                            ${billing.errors.length > 10 ? `<li>... e mais ${billing.errors.length - 10} erros</li>` : ''}
                        </ul>
                    </div>
                ` : ''}
                
                ${billing.warnings && billing.warnings.length > 0 ? `
                    <div class="validation-warnings">
                        <h4><i class="fas fa-exclamation-circle"></i> Avisos:</h4>
                        <ul>
                            ${billing.warnings.slice(0, 5).map(warning => `<li>${warning}</li>`).join('')}
                            ${billing.warnings.length > 5 ? `<li>... e mais ${billing.warnings.length - 5} avisos</li>` : ''}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    async processData() {
        if (!this.validationResult || this.isProcessing) return;

        if (this.validationResult.billing.valid_records === 0) {
            this.showToast('Nenhum registro válido para processar', 'warning', 'Nada para Processar');
            return;
        }

        this.isProcessing = true;
        this.showProgressSection();
        this.updateProcessButton();

        try {
            const fileContent = await this.readFileContent(this.selectedFile);
            const template = document.getElementById('message-template').value.trim() || null;

            // Start processing
            const response = await this.apiCall('POST', '/billing/process-json', {
                json_data: fileContent,
                template: template
            });

            if (response.success) {
                this.showToast(
                    `Processamento iniciado para ${response.records_count} registros`,
                    'success',
                    'Processamento Iniciado'
                );
                
                // Start monitoring progress
                this.monitorProgress();
            } else {
                throw new Error(response.message || 'Erro no processamento');
            }

        } catch (error) {
            console.error('Processing error:', error);
            this.showToast(error.message, 'error', 'Erro no Processamento');
            this.hideProgressSection();
        } finally {
            this.isProcessing = false;
            this.updateProcessButton();
        }
    }

    showProgressSection() {
        const progressSection = document.getElementById('progress-section');
        progressSection.style.display = 'block';
        
        // Reset progress
        this.updateProgress(0, 0, 0, 0);
    }

    hideProgressSection() {
        document.getElementById('progress-section').style.display = 'none';
    }

    updateProgress(percentage, total, sent, failed) {
        document.getElementById('progress-fill').style.width = `${percentage}%`;
        document.getElementById('total-messages').textContent = total;
        document.getElementById('sent-messages').textContent = sent;
        document.getElementById('failed-messages').textContent = failed;
    }

    async monitorProgress() {
        // Simulate progress monitoring
        // In a real implementation, you would poll a progress endpoint
        let progress = 0;
        const total = this.validationResult.billing.valid_records;
        let sent = 0;
        let failed = 0;

        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            sent = Math.floor((progress / 100) * total);
            failed = Math.floor(Math.random() * (sent * 0.1)); // 10% fail rate simulation
            
            if (progress >= 100) {
                progress = 100;
                sent = total - failed;
                clearInterval(progressInterval);
                
                this.showToast(
                    `Processamento concluído! ${sent} mensagens enviadas, ${failed} falhas`,
                    sent > failed ? 'success' : 'warning',
                    'Processamento Finalizado'
                );
            }
            
            this.updateProgress(progress, total, sent, failed);
        }, 500);
    }

    updateProcessButton() {
        const processBtn = document.getElementById('process-btn');
        const hasFile = this.selectedFile !== null;
        const hasValidation = this.validationResult !== null;
        const canProcess = hasFile && hasValidation && !this.isProcessing;
        
        processBtn.disabled = !canProcess;
        
        if (this.isProcessing) {
            processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        } else if (hasValidation) {
            processBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Iniciar Envio';
        } else {
            processBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Iniciar Envio';
        }
    }

    async loadConversations() {
        try {
            const response = await this.apiCall('GET', '/conversation/active-sessions');
            const sessionsCount = response.active_sessions || 0;
            
            document.getElementById('active-sessions-count').textContent = sessionsCount;
            
            // Load conversation list (simulated for now)
            const conversationsListContent = document.getElementById('conversations-list-content');
            if (sessionsCount === 0) {
                conversationsListContent.innerHTML = `
                    <div class="no-conversations">
                        <i class="fas fa-comments"></i>
                        <p>Nenhuma conversa ativa no momento</p>
                    </div>
                `;
            } else {
                // In a real implementation, you would load actual conversations
                conversationsListContent.innerHTML = `
                    <div class="conversation-item active">
                        <div class="conversation-meta">
                            <span class="conversation-phone">+55 11 99999-9999</span>
                            <span class="conversation-time">Há 5 min</span>
                        </div>
                        <div class="conversation-preview">Já fiz o pagamento...</div>
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.showToast('Erro ao carregar conversas', 'error');
        }
    }

    async loadLogs() {
        try {
            const logType = document.getElementById('log-type').value;
            const limit = parseInt(document.getElementById('log-limit').value);
            
            const response = await this.apiCall('GET', '/billing/logs', { limit });
            
            const logsContainer = document.getElementById('logs-container');
            logsContainer.innerHTML = '';
            
            if (response.operation_logs && response.operation_logs.length > 0) {
                response.operation_logs.forEach(log => {
                    const logEntry = this.createLogEntry(log);
                    logsContainer.appendChild(logEntry);
                });
            } else {
                logsContainer.innerHTML = '<div class="no-logs"><p>Nenhum log encontrado</p></div>';
            }
            
        } catch (error) {
            console.error('Error loading logs:', error);
            this.showToast('Erro ao carregar logs', 'error');
        }
    }

    createLogEntry(log) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        const status = log.status || 'info';
        if (status === 'error') entry.classList.add('error');
        else if (status === 'success') entry.classList.add('success');
        
        const timestamp = new Date(log.timestamp).toLocaleString('pt-BR');
        
        entry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-level">${status.toUpperCase()}</span>
            <span class="log-message">${log.operation_type || 'Unknown'} - ${JSON.stringify(log.metadata || {})}</span>
        `;
        
        return entry;
    }

    async loadStats() {
        try {
            // Load system stats
            const billingStats = await this.apiCall('GET', '/billing/stats');
            const botStats = await this.apiCall('GET', '/conversation/bot-stats');
            const wahaStats = await this.apiCall('GET', '/webhooks/waha/status');
            
            // Update stats display
            this.updateStatsDisplay(billingStats, botStats, wahaStats);
            
        } catch (error) {
            console.error('Error loading stats:', error);
            this.showToast('Erro ao carregar estatísticas', 'error');
        }
    }

    updateStatsDisplay(billingStats, botStats, wahaStats) {
        // Update stat cards (simulated values for now)
        document.getElementById('total-messages-stat').textContent = '0';
        document.getElementById('success-rate-stat').textContent = '0%';
        document.getElementById('active-conversations-stat').textContent = botStats.active_sessions || '0';
        document.getElementById('errors-count-stat').textContent = '0';
        
        // Update module status
        const modulesStatus = document.getElementById('modules-status');
        modulesStatus.innerHTML = `
            <div class="module-status ${billingStats.is_healthy ? 'healthy' : 'unhealthy'}">
                <div class="module-name">Sistema de Cobrança</div>
                <div class="module-indicator ${billingStats.is_healthy ? 'healthy' : 'unhealthy'}"></div>
                <span>${billingStats.is_healthy ? 'Funcionando' : 'Com problemas'}</span>
            </div>
            
            <div class="module-status ${botStats.is_healthy ? 'healthy' : 'unhealthy'}">
                <div class="module-name">Bot de Conversação</div>
                <div class="module-indicator ${botStats.is_healthy ? 'healthy' : 'unhealthy'}"></div>
                <span>${botStats.is_healthy ? 'Funcionando' : 'Com problemas'}</span>
            </div>
            
            <div class="module-status ${wahaStats.success ? 'healthy' : 'unhealthy'}">
                <div class="module-name">Integração WhatsApp</div>
                <div class="module-indicator ${wahaStats.success ? 'healthy' : 'unhealthy'}"></div>
                <span>${wahaStats.success ? 'Conectado' : 'Desconectado'}</span>
            </div>
        `;
    }

    async startStatusChecking() {
        await this.checkSystemStatus();
        
        this.statusCheckInterval = setInterval(async () => {
            await this.checkSystemStatus();
        }, 30000); // Check every 30 seconds
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const isHealthy = data.status === 'healthy';
            const statusDot = document.getElementById('connection-status');
            const statusText = document.getElementById('status-text');
            
            if (isHealthy) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Online';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Offline';
            }
            
        } catch (error) {
            console.error('Status check failed:', error);
            const statusDot = document.getElementById('connection-status');
            const statusText = document.getElementById('status-text');
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Erro de Conexão';
        }
    }

    async loadInitialData() {
        // Load data for current tab
        await this.loadTabData(this.currentTab);
    }

    // Utility Methods
    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
            reader.readAsText(file);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async apiCall(method, endpoint, data = null) {
        const url = this.apiBase + endpoint;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            if (method === 'GET') {
                const params = new URLSearchParams(data);
                return fetch(`${url}?${params}`, options).then(r => r.json());
            } else {
                options.body = JSON.stringify(data);
            }
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || `HTTP ${response.status}`);
        }
        
        return response.json();
    }

    showLoading() {
        document.getElementById('loading-overlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    showToast(message, type = 'info', title = null) {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        
        toast.className = `toast ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="${iconMap[type] || iconMap.info}"></i>
            </div>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
}

// Global functions for HTML onclick events
function validateData() {
    window.billingSystem.validateData();
}

function processData() {
    window.billingSystem.processData();
}

function clearFile() {
    window.billingSystem.clearFile();
}

function loadLogs() {
    window.billingSystem.loadLogs();
}

// Initialize the system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.billingSystem = new BillingSystem();
});

// Add CSS for validation results
const style = document.createElement('style');
style.textContent = `
    .validation-summary {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .validation-stat {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .stat-label {
        display: block;
        color: #7f8c8d;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .stat-value.success {
        color: #27ae60;
    }
    
    .stat-value.error {
        color: #e74c3c;
    }
    
    .validation-errors,
    .validation-warnings {
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .validation-errors {
        background: #fdf2f2;
        border-left: 4px solid #e74c3c;
    }
    
    .validation-warnings {
        background: #fffbf0;
        border-left: 4px solid #f39c12;
    }
    
    .validation-errors h4,
    .validation-warnings h4 {
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .validation-errors ul,
    .validation-warnings ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .validation-errors li,
    .validation-warnings li {
        margin-bottom: 0.25rem;
        font-size: 0.9rem;
    }
    
    .no-conversations,
    .no-logs {
        text-align: center;
        padding: 3rem;
        color: #7f8c8d;
    }
    
    .no-conversations i,
    .no-logs i {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
`;

document.head.appendChild(style);
