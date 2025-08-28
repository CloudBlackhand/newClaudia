// Claudia Cobranças - Frontend Básico
class ClaudiaCobrancas {
    constructor() {
        this.messages = [];
        this.logs = [];
        this.init();
    }
    
    init() {
        this.createInterface();
        this.setupEventListeners();
        this.startStatusPolling();
        console.log('🚀 Claudia Cobranças - Sistema básico iniciado!');
    }
    
    createInterface() {
        const app = document.createElement('div');
        app.id = 'claudia-app';
        app.innerHTML = `
            <!-- Header -->
            <header class="app-header">
                <div class="header-content">
                    <div class="logo">
                        <span class="logo-icon">🤖</span>
                        <h1>Claudia Cobranças</h1>
                        <span class="version">v2.2 - Sistema Básico</span>
                    </div>
                    <div class="header-actions">
                        <div class="status-indicator" id="systemStatus">
                            <span class="status-dot online"></span>
                            <span class="status-text">Online</span>
                        </div>
                        <button class="btn-refresh" onclick="claudia.refreshStatus()">🔄</button>
                    </div>
                </div>
            </header>

            <!-- Navigation -->
            <nav class="main-nav">
                <div class="nav-container">
                    <button class="nav-btn active" data-tab="dashboard">📊 Dashboard</button>
                    <button class="nav-btn" data-tab="upload">📤 Upload</button>
                    <button class="nav-btn" data-tab="conversation">💬 Conversação</button>
                    <button class="nav-btn" data-tab="logs">📋 Logs</button>
                </div>
            </nav>

            <!-- Main Content -->
            <main class="main-content">
                <!-- Dashboard -->
                <div class="tab-content active" id="dashboard">
                    <div class="dashboard-grid">
                        <div class="status-card system-card">
                            <div class="card-header">
                                <h3>🤖 Sistema</h3>
                            </div>
                            <div class="card-body">
                                <div class="status-info">
                                    <div class="status-item">
                                        <span class="label">Status:</span>
                                        <span class="value" id="botStatus">Ativo</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="label">Versão:</span>
                                        <span class="value">2.2</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="status-card stats-card">
                            <div class="card-header">
                                <h3>📈 Estatísticas</h3>
                            </div>
                            <div class="card-body">
                                <div class="stats-grid">
                                    <div class="stat-item">
                                        <span class="stat-number" id="messagesProcessed">0</span>
                                        <span class="stat-label">Mensagens Processadas</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-number" id="conversations">0</span>
                                        <span class="stat-label">Conversações</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-number" id="faturasDownloaded">0</span>
                                        <span class="stat-label">Faturas Baixadas</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Upload Tab -->
                <div class="tab-content" id="upload">
                    <div class="upload-container">
                        <div class="upload-section">
                            <h2>📤 Upload de Arquivo Excel</h2>
                            <div class="upload-form">
                                <div class="form-group">
                                    <label for="excelFile">Selecione o arquivo Excel:</label>
                                    <input type="file" id="excelFile" accept=".xlsx,.xls" class="form-control">
                                </div>
                                <button class="btn btn-primary" onclick="claudia.uploadFile()">
                                    <i class="fas fa-upload"></i> Enviar Arquivo
                                </button>
                            </div>
                            <div id="uploadResult" class="upload-result"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Conversation Tab -->
                <div class="tab-content" id="conversation">
                    <div class="conversation-container">
                        <div class="conversation-section">
                            <h2>💬 Teste de Conversação</h2>
                            <div class="conversation-form">
                                <div class="form-group">
                                    <label for="testMessage">Digite uma mensagem para testar:</label>
                                    <textarea id="testMessage" class="form-control" rows="3" 
                                              placeholder="Ex: quanto eu devo?"></textarea>
                                </div>
                                <button class="btn btn-primary" onclick="claudia.testConversation()">
                                    <i class="fas fa-paper-plane"></i> Testar Resposta
                                </button>
                            </div>
                            <div id="conversationResult" class="conversation-result"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Logs Tab -->
                <div class="tab-content" id="logs">
                    <div class="logs-container">
                        <div class="logs-section">
                            <h2>📋 Logs do Sistema</h2>
                            <div class="logs-controls">
                                <button class="btn btn-secondary" onclick="claudia.refreshLogs()">
                                    <i class="fas fa-sync"></i> Atualizar
                                </button>
                                <button class="btn btn-secondary" onclick="claudia.clearLogs()">
                                    <i class="fas fa-trash"></i> Limpar
                                </button>
                            </div>
                            <div id="logsContainer" class="logs-content"></div>
                        </div>
                    </div>
                </div>
            </main>
        `;
        
        document.body.appendChild(app);
    }
    
    setupEventListeners() {
        // Navegação por tabs
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        // Drag and drop para upload
        const fileInput = document.getElementById('excelFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelect(e.target.files[0]);
            });
        }
    }
    
    switchTab(tabName) {
        // Remover active de todas as tabs
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Ativar tab selecionada
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');
    }
    
    startStatusPolling() {
        // Atualizar status a cada 30 segundos
        setInterval(() => {
            this.refreshStatus();
        }, 30000);
        
        // Primeira atualização
        this.refreshStatus();
    }
    
    async refreshStatus() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.stats);
                this.updateSystemStatus(data.bot_active);
            }
        } catch (error) {
            console.error('Erro ao atualizar status:', error);
            this.addLog('Erro ao atualizar status: ' + error.message, 'error');
        }
    }
    
    updateStats(stats) {
        document.getElementById('messagesProcessed').textContent = stats.messages_processed || 0;
        document.getElementById('conversations').textContent = stats.conversations || 0;
        document.getElementById('faturasDownloaded').textContent = stats.faturas_downloaded || 0;
    }
    
    updateSystemStatus(botActive) {
        const statusElement = document.getElementById('botStatus');
        const statusDot = document.querySelector('#systemStatus .status-dot');
        
        if (botActive) {
            statusElement.textContent = 'Ativo';
            statusDot.className = 'status-dot online';
        } else {
            statusElement.textContent = 'Inativo';
            statusDot.className = 'status-dot offline';
        }
    }
    
    handleFileSelect(file) {
        if (file) {
            this.addLog(`Arquivo selecionado: ${file.name}`, 'info');
        }
    }
    
    async uploadFile() {
        const fileInput = document.getElementById('excelFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showUploadResult('Por favor, selecione um arquivo.', 'error');
            return;
        }
        
        if (!file.name.match(/\.(xlsx|xls)$/)) {
            this.showUploadResult('Por favor, selecione um arquivo Excel (.xlsx ou .xls).', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showUploadResult('Enviando arquivo...', 'info');
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showUploadResult('Arquivo processado com sucesso!', 'success');
                this.addLog(`Arquivo ${file.name} processado com sucesso`, 'success');
            } else {
                this.showUploadResult('Erro ao processar arquivo: ' + result.message, 'error');
                this.addLog(`Erro ao processar ${file.name}: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showUploadResult('Erro ao enviar arquivo: ' + error.message, 'error');
            this.addLog(`Erro no upload: ${error.message}`, 'error');
        }
    }
    
    showUploadResult(message, type) {
        const resultDiv = document.getElementById('uploadResult');
        resultDiv.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    }
    
    async testConversation() {
        const messageInput = document.getElementById('testMessage');
        const message = messageInput.value.trim();
        
        if (!message) {
            this.showConversationResult('Por favor, digite uma mensagem.', 'error');
            return;
        }
        
        try {
            this.showConversationResult('Processando...', 'info');
            
            const response = await fetch('/api/conversation/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showConversationResult(`
                    <div class="conversation-test">
                        <div class="original-message">
                            <strong>Mensagem:</strong> ${result.original_message}
                        </div>
                        <div class="bot-response">
                            <strong>Resposta:</strong> ${result.response}
                        </div>
                    </div>
                `, 'success');
                this.addLog(`Teste de conversação: "${message}"`, 'info');
            } else {
                this.showConversationResult('Erro ao processar mensagem: ' + result.message, 'error');
                this.addLog(`Erro no teste: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showConversationResult('Erro ao testar conversação: ' + error.message, 'error');
            this.addLog(`Erro no teste: ${error.message}`, 'error');
        }
    }
    
    showConversationResult(content, type) {
        const resultDiv = document.getElementById('conversationResult');
        if (type === 'success') {
            resultDiv.innerHTML = content;
        } else {
            resultDiv.innerHTML = `<div class="alert alert-${type}">${content}</div>`;
        }
    }
    
    async refreshLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            if (data.success) {
                this.displayLogs(data.logs);
            }
        } catch (error) {
            this.addLog('Erro ao carregar logs: ' + error.message, 'error');
        }
    }
    
    displayLogs(logs) {
        const container = document.getElementById('logsContainer');
        
        if (!logs || logs.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum log disponível</p>';
            return;
        }
        
        const logsHtml = logs.map(log => `
            <div class="log-entry log-${log.level.toLowerCase()}">
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-level">${log.level}</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('');
        
        container.innerHTML = logsHtml;
    }
    
    clearLogs() {
        document.getElementById('logsContainer').innerHTML = '<p class="text-muted">Logs limpos</p>';
        this.addLog('Logs limpos pelo usuário', 'info');
    }
    
    addLog(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const log = { timestamp, level, message };
        
        this.logs.push(log);
        
        // Manter apenas últimos 100 logs
        if (this.logs.length > 100) {
            this.logs = this.logs.slice(-100);
        }
        
        console.log(`[${level.toUpperCase()}] ${message}`);
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.claudia = new ClaudiaCobrancas();
});
 