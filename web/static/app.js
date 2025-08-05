// Blacktemplar Bolter - JavaScript Avançado

class BlacktemplarBot {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.isConnected = false;
        this.stats = {
            sent: 0,
            failed: 0,
            conversations: 0
        };
        
        this.init();
    }
    
    init() {
        this.createInterface();
        this.initWebSocket();
        this.setupEventListeners();
        this.setupNotifications();
        this.startStatusUpdater();
        this.initAdvancedFeatures();
        
        console.log('🤖 Blacktemplar Bolter iniciado com funcionalidades avançadas!');
    }
    
    // Criar interface dinamicamente - Nova função
    createInterface() {
        const appContainer = document.createElement('div');
        appContainer.id = 'app';
        appContainer.className = 'container-fluid';
        
        // Cabeçalho
        const header = document.createElement('header');
        header.className = 'p-3 mb-4 bg-dark text-white';
        header.innerHTML = `
            <div class="container">
                <div class="d-flex align-items-center">
                    <img src="/static/icon.png" alt="Logo" height="40" class="mr-3">
                    <h1 class="m-0">Blacktemplar Bolter</h1>
                    <small class="ml-2">v2.2 - 100% Gratuito</small>
                    <div class="ml-auto" id="connectionIndicator" title="Status da conexão" class="status-offline"></div>
                </div>
            </div>
        `;
        
        // Navegação
        const nav = document.createElement('nav');
        nav.className = 'nav-tabs';
        nav.innerHTML = `
            <button class="nav-tab active" data-tab="dashboard">📊 Dashboard</button>
            <button class="nav-tab" data-tab="logs">📝 Logs</button>
            <button class="nav-tab" data-tab="metricas">📈 Métricas</button>
            <button class="nav-tab" data-tab="mensagens">💬 Mensagens</button>
            <button class="nav-tab" data-tab="configuracoes">⚙️ Configurações</button>
        `;
        
        // Conteúdo principal
        const main = document.createElement('main');
        main.className = 'container mt-4';
        
        // Dashboard tab
        const dashboard = document.createElement('div');
        dashboard.id = 'dashboard';
        dashboard.className = 'tab-content active';
        dashboard.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <div class="card mb-4">
                        <div class="card-header">Status do Sistema</div>
                        <div class="card-body">
                            <div class="status-grid">
                                <div class="status-item">
                                    <div class="status-card" data-status="whatsapp">
                                        <div class="status-header">
                                            <h5>WhatsApp</h5>
                                            <div class="status-icon offline">
                                                <i class="fas fa-mobile-alt"></i>
                                            </div>
                                        </div>
                                        <div class="status-content">
                                            <div class="status-text">Desconectado</div>
                                            <button onclick="connectWhatsApp()" class="btn btn-sm btn-primary">Conectar</button>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="status-item">
                                    <div class="status-card" data-status="fpd">
                                        <div class="status-header">
                                            <h5>FPD</h5>
                                            <div class="status-icon offline">
                                                <i class="fas fa-file-excel"></i>
                                            </div>
                                        </div>
                                        <div class="status-content">
                                            <div class="status-text">Não carregado</div>
                                            <div class="upload-area" id="fpdUpload">
                                                <label for="fpdFile" class="btn btn-sm btn-primary">Carregar FPD</label>
                                                <input type="file" id="fpdFile" style="display:none">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="status-item">
                                    <div class="status-card" data-status="vendas">
                                        <div class="status-header">
                                            <h5>VENDAS</h5>
                                            <div class="status-icon offline">
                                                <i class="fas fa-chart-line"></i>
                                            </div>
                                        </div>
                                        <div class="status-content">
                                            <div class="status-text">Não carregado</div>
                                            <div class="upload-area" id="vendasUpload">
                                                <label for="vendasFile" class="btn btn-sm btn-primary">Carregar VENDAS</label>
                                                <input type="file" id="vendasFile" style="display:none">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="status-item">
                                    <div class="status-card" data-status="bot">
                                        <div class="status-header">
                                            <h5>Bot</h5>
                                            <div class="status-icon offline">
                                                <i class="fas fa-robot"></i>
                                            </div>
                                        </div>
                                        <div class="status-content">
                                            <div class="status-text">Inativo</div>
                                            <button onclick="toggleBot()" class="btn btn-sm btn-success">Iniciar</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">Controle do Servidor</div>
                        <div class="card-body">
                            <div class="server-controls">
                                <button id="startServerBtn" onclick="startServer()" class="btn-start">▶️ Iniciar Servidor</button>
                                <button id="stopServerBtn" onclick="stopServer()" class="btn-stop" disabled>⏹️ Parar Servidor</button>
                                <button id="restartServerBtn" onclick="restartServer()" class="btn-restart">🔄 Reiniciar Servidor</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">Log de Atividades</div>
                        <div class="card-body p-0">
                            <div id="logContainer" class="log-container p-2" style="height:200px; overflow-y:auto;"></div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4">
                    <div class="card mb-4">
                        <div class="card-header">QR Code WhatsApp</div>
                        <div class="card-body text-center">
                            <div id="qrContainer" class="qr-container" style="display:none">
                                <div id="qrCode" class="qr-code"></div>
                                <p class="mt-2">Escaneie com WhatsApp</p>
                                <button onclick="refreshQRCode()" class="btn btn-sm btn-outline-primary mt-2">Atualizar QR Code</button>
                            </div>
                            <div id="noQrMessage">
                                <p>Clique em "Conectar" para gerar QR Code</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mb-4">
                        <div class="card-header">Estatísticas</div>
                        <div class="card-body">
                            <div class="stat-item">
                                <span class="stat-label">Mensagens enviadas:</span>
                                <span id="stat-messages_sent" class="stat-value">0</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Faturas enviadas:</span>
                                <span id="stat-faturas_sent" class="stat-value">0</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Conversas ativas:</span>
                                <span id="stat-conversations" class="stat-value">0</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="progressContainer" class="progress-container" style="display:none">
                <div class="progress-overlay">
                    <div class="progress-content">
                        <div id="progressText">Processando...</div>
                        <div class="progress mt-2">
                            <div id="progressBar" class="progress-bar progress-bar-animated" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Logs tab
        const logs = document.createElement('div');
        logs.id = 'logs';
        logs.className = 'tab-content';
        logs.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="m-0">Logs do Sistema</h5>
                        <div>
                            <button onclick="loadLogs('all')" class="btn btn-sm btn-primary">Todos</button>
                            <button onclick="loadLogs('error')" class="btn btn-sm btn-danger">Erros</button>
                            <button onclick="loadLogs('info')" class="btn btn-sm btn-info">Info</button>
                        </div>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="logsContainer" class="logs-container"></div>
                </div>
            </div>
        `;
        
        // Métricas tab
        const metricas = document.createElement('div');
        metricas.id = 'metricas';
        metricas.className = 'tab-content';
        metricas.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="m-0">Métricas de Desempenho</h5>
                        <button onclick="loadMetrics()" class="btn btn-sm btn-primary">Atualizar</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-label">Total de Mensagens</div>
                            <div id="totalMessages" class="metric-value">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Mensagens Enviadas</div>
                            <div id="sentMessages" class="metric-value">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Mensagens com Falha</div>
                            <div id="failedMessages" class="metric-value">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Conversas Ativas</div>
                            <div id="activeConversations" class="metric-value">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Conversas Concluídas</div>
                            <div id="completedConversations" class="metric-value">0</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Faturas Enviadas</div>
                            <div id="invoicesSent" class="metric-value">0</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Mensagens tab
        const mensagens = document.createElement('div');
        mensagens.id = 'mensagens';
        mensagens.className = 'tab-content';
        mensagens.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="m-0">Histórico de Mensagens</h5>
                        <button onclick="loadMessageHistory()" class="btn btn-sm btn-primary">Atualizar</button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="messageHistoryContainer" class="message-history-container"></div>
                </div>
            </div>
        `;
        
        // Configurações tab
        const configuracoes = document.createElement('div');
        configuracoes.id = 'configuracoes';
        configuracoes.className = 'tab-content';
        configuracoes.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="m-0">Configurações do Sistema</h5>
                        <button onclick="loadConfiguration()" class="btn btn-sm btn-primary">Recarregar</button>
                    </div>
                </div>
                <div class="card-body">
                    <div id="configContainer" class="config-container"></div>
                </div>
            </div>
        `;
        
        // Adicionar elementos ao DOM
        main.appendChild(dashboard);
        main.appendChild(logs);
        main.appendChild(metricas);
        main.appendChild(mensagens);
        main.appendChild(configuracoes);
        
        appContainer.appendChild(header);
        appContainer.appendChild(nav);
        appContainer.appendChild(main);
        
        // Adicionar à página
        document.body.innerHTML = '';
        document.body.appendChild(appContainer);
        
        // Adicionar CSS básico para garantir que a interface funcione
        const style = document.createElement('style');
        style.textContent = `
            body, html { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            .container-fluid { width: 100%; padding: 15px; }
            .container { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 15px; }
            .row { display: flex; flex-wrap: wrap; margin: 0 -15px; }
            .col-md-4 { width: 33.333%; padding: 0 15px; box-sizing: border-box; }
            .col-md-8 { width: 66.666%; padding: 0 15px; box-sizing: border-box; }
            .card { border: 1px solid #dee2e6; border-radius: 5px; margin-bottom: 20px; background: white; }
            .card-header { padding: 10px 15px; background: #f8f9fa; border-bottom: 1px solid #dee2e6; }
            .card-body { padding: 15px; }
            .btn { display: inline-block; font-weight: 400; text-align: center; white-space: nowrap; vertical-align: middle; user-select: none; border: 1px solid transparent; padding: .375rem .75rem; font-size: 1rem; line-height: 1.5; border-radius: .25rem; cursor: pointer; }
            .btn-sm { padding: .25rem .5rem; font-size: .875rem; line-height: 1.5; border-radius: .2rem; }
            .btn-primary { color: #fff; background-color: #007bff; border-color: #007bff; }
            .btn-success { color: #fff; background-color: #28a745; border-color: #28a745; }
            .status-card { text-align: center; padding: 15px; border: 1px solid #dee2e6; border-radius: 5px; margin-bottom: 15px; }
            .status-icon { font-size: 2em; margin: 10px 0; }
            .online { color: #28a745; }
            .offline { color: #dc3545; }
            .nav-tabs { display: flex; border-bottom: 1px solid #dee2e6; }
            .nav-tab { background: none; border: none; padding: 10px 20px; cursor: pointer; border-bottom: 3px solid transparent; }
            .nav-tab.active { border-bottom-color: #007bff; color: #007bff; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            
            @media (max-width: 768px) {
                .row { flex-direction: column; }
                .col-md-4, .col-md-8 { width: 100%; }
            }
        `;
        document.head.appendChild(style);
        
        // Setup tab navigation
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all tabs
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab
                tab.classList.add('active');
                const tabId = tab.getAttribute('data-tab');
                document.getElementById(tabId).classList.add('active');
            });
        });
    }
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/status`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showNotification('WebSocket conectado', 'success');
                this.updateConnectionStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.scheduleReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showNotification('Erro de conexão WebSocket', 'error');
            };
            
        } catch (error) {
            console.error('Erro ao inicializar WebSocket:', error);
            this.scheduleReconnect();
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            
            setTimeout(() => {
                this.initWebSocket();
            }, delay);
            
            this.showNotification(`Tentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`, 'info');
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'status_update':
                this.updateSystemStatus(data.data);
                break;
            case 'stats_update':
                this.updateStats(data.data);
                break;
            case 'log_message':
                this.addLog(data.message, data.level);
                break;
            case 'qr_code':
                this.showQRCode(data.qr_data);
                break;
            default:
                console.log('Mensagem WebSocket não reconhecida:', data);
        }
    }
    
    setupEventListeners() {
        // File upload listeners
        document.getElementById('fpdFile')?.addEventListener('change', (e) => {
            this.handleFileUpload(e.target, '/api/upload/fpd', 'FPD');
        });
        
        document.getElementById('vendasFile')?.addEventListener('change', (e) => {
            this.handleFileUpload(e.target, '/api/upload/vendas', 'VENDAS');
        });
        
        // Drag and drop
        this.setupDragAndDrop();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.toggleBot();
            }
        });
        
        // Auto-refresh QR code
        setInterval(() => {
            if (!this.isWhatsAppConnected()) {
                this.refreshQRCode();
            }
        }, 30000); // Refresh every 30 seconds
    }
    
    setupDragAndDrop() {
        const uploadAreas = ['fpdUpload', 'vendasUpload'];
        
        uploadAreas.forEach(areaId => {
            const area = document.getElementById(areaId);
            if (!area) return;
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, this.preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.add('dragover'), false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
            });
            
            area.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const endpoint = areaId === 'fpdUpload' ? '/api/upload/fpd' : '/api/upload/vendas';
                    const type = areaId === 'fpdUpload' ? 'FPD' : 'VENDAS';
                    this.uploadFile(files[0], endpoint, type);
                }
            }, false);
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    setupNotifications() {
        if ('Notification' in window) {
            Notification.requestPermission();
        }
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        // Browser notification
        if (Notification.permission === 'granted') {
            new Notification('Blacktemplar Bolter', {
                body: message,
                icon: '/static/icon.png'
            });
        }
        
        // In-app notification
        this.addLog(message, type);
        
        // Toast notification
        this.showToast(message, type, duration);
    }
    
    showToast(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getIconForType(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }
    
    getIconForType(type) {
        const icons = {
            success: 'check-circle',
            error: 'times-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
    
    async handleFileUpload(input, endpoint, type) {
        const file = input.files[0];
        if (!file) return;
        
        this.showProgress(`Carregando ${type}...`, 0);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            this.updateProgress(50);
            
            const result = await response.json();
            
            this.updateProgress(100);
            
            if (result.success) {
                this.showNotification(`✅ ${type} carregado: ${result.message}`, 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification(`❌ Erro ao carregar ${type}: ${result.message}`, 'error');
            }
            
        } catch (error) {
            this.showNotification(`❌ Erro no upload: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async uploadFile(file, endpoint, type) {
        const formData = new FormData();
        formData.append('file', file);
        
        this.showProgress(`Processando ${file.name}...`, 0);
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`✅ ${file.name} processado com sucesso!`, 'success');
            } else {
                this.showNotification(`❌ Erro: ${result.message}`, 'error');
            }
            
        } catch (error) {
            this.showNotification(`❌ Erro no upload: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async connectWhatsApp() {
        this.showProgress('Conectando ao WhatsApp...');
        
        try {
            const response = await fetch('/api/whatsapp/connect', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success && result.qr_data) {
                this.showQRCode(result.qr_data);
                this.showNotification('QR Code gerado! Escaneie com seu WhatsApp.', 'info');
            } else {
                this.showNotification(`Erro: ${result.message}`, 'error');
            }
            
        } catch (error) {
            this.showNotification(`Erro de conexão: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    async toggleBot() {
        const isActive = this.isBotActive();
        const action = isActive ? 'stop' : 'start';
        
        this.showProgress(`${isActive ? 'Parando' : 'Iniciando'} bot...`);
        
        try {
            const response = await fetch(`/api/bot/${action}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`✅ Bot ${isActive ? 'parado' : 'iniciado'}!`, 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification(`❌ Erro: ${result.message}`, 'error');
            }
            
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        } finally {
            this.hideProgress();
        }
    }
    
    showQRCode(qrData) {
        const container = document.getElementById('qrContainer');
        const qrElement = document.getElementById('qrCode');
        
        if (container && qrElement) {
            qrElement.innerHTML = `<img src="${qrData}" class="img-fluid" alt="QR Code WhatsApp">`;
            container.style.display = 'block';
            
            // Auto-hide after 2 minutes
            setTimeout(() => {
                if (!this.isWhatsAppConnected()) {
                    this.refreshQRCode();
                }
            }, 120000);
        }
    }
    
    async refreshQRCode() {
        try {
            const response = await fetch('/api/whatsapp/qr');
            const result = await response.json();
            
            if (result.success && result.qr_data) {
                this.showQRCode(result.qr_data);
            }
        } catch (error) {
            console.error('Erro ao atualizar QR Code:', error);
        }
    }
    
    showProgress(text, progress = null) {
        const container = document.getElementById('progressContainer');
        const textElement = document.getElementById('progressText');
        const barElement = document.getElementById('progressBar');
        
        if (container && textElement) {
            textElement.textContent = text;
            container.style.display = 'block';
            
            if (progress !== null && barElement) {
                barElement.style.width = `${progress}%`;
            }
        }
    }
    
    updateProgress(progress) {
        const barElement = document.getElementById('progressBar');
        if (barElement) {
            barElement.style.width = `${progress}%`;
        }
    }
    
    hideProgress() {
        const container = document.getElementById('progressContainer');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    addLog(message, type = 'info') {
        const container = document.getElementById('logContainer');
        if (!container) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const colorClass = this.getLogColorClass(type);
        
        const logEntry = document.createElement('div');
        logEntry.className = colorClass;
        logEntry.innerHTML = `[${timestamp}] ${message}`;
        
        container.appendChild(logEntry);
        container.scrollTop = container.scrollHeight;
        
        // Keep only last 100 entries
        while (container.children.length > 100) {
            container.removeChild(container.firstChild);
        }
    }
    
    getLogColorClass(type) {
        const classes = {
            error: 'text-danger',
            success: 'text-success',
            warning: 'text-warning',
            info: 'text-info'
        };
        return classes[type] || 'text-info';
    }
    
    updateSystemStatus(status = null) {
        if (status) {
            // Update status cards based on received data
            this.updateStatusCard('whatsapp', status.whatsapp_connected);
            this.updateStatusCard('fpd', status.fpd_loaded);
            this.updateStatusCard('bot', status.bot_active);
            
            // Update stats
            if (status.stats) {
                this.updateStats(status.stats);
            }
        }
    }
    
    updateStatusCard(type, isOnline) {
        const card = document.querySelector(`[data-status="${type}"]`);
        if (card) {
            card.className = card.className.replace(/online|offline/g, '');
            card.classList.add(isOnline ? 'online' : 'offline');
        }
    }
    
    updateStats(stats) {
        Object.keys(stats).forEach(key => {
            const element = document.getElementById(`stat-${key}`);
            if (element) {
                element.textContent = stats[key];
            }
        });
        
        this.stats = { ...this.stats, ...stats };
    }
    
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('connectionIndicator');
        if (indicator) {
            indicator.className = connected ? 'status-online' : 'status-offline';
            indicator.title = connected ? 'WebSocket conectado' : 'WebSocket desconectado';
        }
    }
    
    startStatusUpdater() {
        // Update status every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                this.updateSystemStatus(status);
            } catch (error) {
                console.error('Erro ao atualizar status:', error);
            }
        }, 30000);
    }
    
    // Helper methods
    isWhatsAppConnected() {
        const card = document.querySelector('[data-status="whatsapp"]');
        return card && card.classList.contains('online');
    }
    
    isBotActive() {
        const card = document.querySelector('[data-status="bot"]');
        return card && card.classList.contains('online');
    }
    
    // 🚀 NOVAS FUNCIONALIDADES - CONTROLE AVANÇADO
    
    // Gerenciamento do Servidor
    async startServer() {
        try {
            this.showNotification('🚀 Iniciando servidor...', 'info');
            
            const response = await fetch('/api/server/start', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Servidor iniciado!', 'success');
                this.updateServerControls(true);
            } else {
                this.showNotification(`❌ Erro: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async stopServer() {
        try {
            this.showNotification('🛑 Parando servidor...', 'info');
            
            const response = await fetch('/api/server/stop', {
                method: 'POST'
            });
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Servidor parado!', 'success');
                this.updateServerControls(false);
            } else {
                this.showNotification(`❌ Erro: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async restartServer() {
        await this.stopServer();
        setTimeout(() => this.startServer(), 2000);
    }
    
    updateServerControls(isRunning) {
        const startBtn = document.getElementById('startServerBtn');
        const stopBtn = document.getElementById('stopServerBtn');
        const restartBtn = document.getElementById('restartServerBtn');
        
        if (startBtn) startBtn.disabled = isRunning;
        if (stopBtn) stopBtn.disabled = !isRunning;
        if (restartBtn) restartBtn.disabled = false;
    }
    
    // Sistema de Logs Avançado
    async loadLogs(type = 'all', limit = 100) {
        try {
            const response = await fetch(`/api/logs?type=${type}&limit=${limit}`);
            const logs = await response.json();
            
            this.displayLogs(logs);
        } catch (error) {
            this.showNotification(`❌ Erro ao carregar logs: ${error.message}`, 'error');
        }
    }
    
    displayLogs(logs) {
        const container = document.getElementById('logsContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        logs.forEach(log => {
            const logElement = document.createElement('div');
            logElement.className = `log-entry log-${log.level}`;
            logElement.innerHTML = `
                <span class="log-time">${new Date(log.timestamp).toLocaleString()}</span>
                <span class="log-level">[${log.level.toUpperCase()}]</span>
                <span class="log-message">${log.message}</span>
            `;
            container.appendChild(logElement);
        });
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
    }
    
    // Métricas e Estatísticas Avançadas
    async loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();
            
            this.displayMetrics(metrics);
        } catch (error) {
            this.showNotification(`❌ Erro ao carregar métricas: ${error.message}`, 'error');
        }
    }
    
    displayMetrics(metrics) {
        // Atualizar cards de métricas
        this.updateMetricCard('totalMessages', metrics.messages.total);
        this.updateMetricCard('sentMessages', metrics.messages.sent);
        this.updateMetricCard('failedMessages', metrics.messages.failed);
        this.updateMetricCard('activeConversations', metrics.conversations.active);
        this.updateMetricCard('completedConversations', metrics.conversations.completed);
        this.updateMetricCard('invoicesSent', metrics.invoices.sent);
        this.updateMetricCard('invoicesDownloaded', metrics.invoices.downloaded);
        
        // Gráficos se existirem
        this.updateCharts(metrics);
    }
    
    updateMetricCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = this.formatNumber(value);
        }
    }
    
    formatNumber(num) {
        return new Intl.NumberFormat('pt-BR').format(num);
    }
    
    updateCharts(metrics) {
        // Implementar gráficos se necessário
        if (window.Chart && metrics.charts) {
            // Código para gráficos aqui
        }
    }
    
    // Histórico de Mensagens
    async loadMessageHistory(phone = null, limit = 50) {
        try {
            const url = phone ? 
                `/api/messages/history?phone=${phone}&limit=${limit}` : 
                `/api/messages/history?limit=${limit}`;
                
            const response = await fetch(url);
            const history = await response.json();
            
            this.displayMessageHistory(history);
        } catch (error) {
            this.showNotification(`❌ Erro ao carregar histórico: ${error.message}`, 'error');
        }
    }
    
    displayMessageHistory(history) {
        const container = document.getElementById('messageHistoryContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        history.forEach(conversation => {
            const convElement = document.createElement('div');
            convElement.className = 'conversation-item';
            convElement.innerHTML = `
                <div class="conversation-header">
                    <strong>${conversation.phone}</strong>
                    <span class="conversation-time">${new Date(conversation.lastMessage).toLocaleString()}</span>
                </div>
                <div class="conversation-stats">
                    <span class="badge">📨 ${conversation.messageCount} mensagens</span>
                    <span class="badge ${conversation.status === 'completed' ? 'badge-success' : 'badge-warning'}">
                        ${conversation.status === 'completed' ? '✅ Resolvido' : '⏳ Em andamento'}
                    </span>
                </div>
                <div class="conversation-messages" id="messages-${conversation.phone}">
                    <!-- Mensagens serão carregadas aqui -->
                </div>
            `;
            
            convElement.addEventListener('click', () => {
                this.toggleConversationDetails(conversation.phone);
            });
            
            container.appendChild(convElement);
        });
    }
    
    async toggleConversationDetails(phone) {
        const messagesContainer = document.getElementById(`messages-${phone}`);
        if (!messagesContainer) return;
        
        if (messagesContainer.innerHTML === '') {
            // Carregar mensagens
            try {
                const response = await fetch(`/api/messages/conversation/${phone}`);
                const messages = await response.json();
                
                messagesContainer.innerHTML = messages.map(msg => `
                    <div class="message ${msg.direction}">
                        <div class="message-content">${msg.content}</div>
                        <div class="message-time">${new Date(msg.timestamp).toLocaleTimeString()}</div>
                    </div>
                `).join('');
                
                messagesContainer.style.display = 'block';
            } catch (error) {
                this.showNotification(`❌ Erro ao carregar mensagens: ${error.message}`, 'error');
            }
        } else {
            // Toggle visibilidade
            messagesContainer.style.display = 
                messagesContainer.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    // Configurações Avançadas
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            
            this.displayConfiguration(config);
        } catch (error) {
            this.showNotification(`❌ Erro ao carregar configurações: ${error.message}`, 'error');
        }
    }
    
    displayConfiguration(config) {
        const container = document.getElementById('configContainer');
        if (!container) return;
        
        container.innerHTML = `
            <div class="config-section">
                <h4>🤖 Bot</h4>
                <label>
                    <input type="checkbox" ${config.bot.autoStart ? 'checked' : ''} 
                           onchange="BlacktemplarBot.updateConfig('bot.autoStart', this.checked)">
                    Auto-iniciar bot
                </label>
                <label>
                    <input type="number" value="${config.bot.messageDelay || 1000}" 
                           onchange="BlacktemplarBot.updateConfig('bot.messageDelay', this.value)">
                    Delay entre mensagens (ms)
                </label>
            </div>
            
            <div class="config-section">
                <h4>📱 WhatsApp</h4>
                <label>
                    <input type="checkbox" ${config.whatsapp.stealthMode ? 'checked' : ''} 
                           onchange="BlacktemplarBot.updateConfig('whatsapp.stealthMode', this.checked)">
                    Modo Stealth
                </label>
                <label>
                    <input type="checkbox" ${config.whatsapp.autoReconnect ? 'checked' : ''} 
                           onchange="BlacktemplarBot.updateConfig('whatsapp.autoReconnect', this.checked)">
                    Auto-reconexão
                </label>
            </div>
            
            <div class="config-section">
                <h4>🗃️ Dados</h4>
                <label>
                    <input type="checkbox" ${config.data.autoBackup ? 'checked' : ''} 
                           onchange="BlacktemplarBot.updateConfig('data.autoBackup', this.checked)">
                    Backup automático
                </label>
            </div>
        `;
    }
    
    async updateConfig(key, value) {
        try {
            const response = await fetch('/api/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key, value })
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('✅ Configuração atualizada!', 'success');
            } else {
                this.showNotification(`❌ Erro: ${result.message}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    // Inicializar funcionalidades avançadas
    initAdvancedFeatures() {
        // Auto-refresh de métricas
        setInterval(() => this.loadMetrics(), 60000); // A cada minuto
        
        // Auto-refresh de logs
        setInterval(() => this.loadLogs('error', 10), 30000); // Erros a cada 30s
        
        // Carregar dados iniciais
        setTimeout(() => {
            this.loadMetrics();
            this.loadConfiguration();
            this.loadMessageHistory();
        }, 1000);
    }
    
    // Public methods for external use
    getStats() {
        return this.stats;
    }
    
    isWebSocketConnected() {
        return this.isConnected;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.BlacktemplarBot = new BlacktemplarBot();
    
    // Global functions for HTML onclick events
    window.connectWhatsApp = () => window.BlacktemplarBot.connectWhatsApp();
    window.toggleBot = () => window.BlacktemplarBot.toggleBot();
    window.refreshQRCode = () => window.BlacktemplarBot.refreshQRCode();
    
    // 🚀 NOVAS FUNÇÕES GLOBAIS - CONTROLE AVANÇADO
    window.startServer = () => window.BlacktemplarBot.startServer();
    window.stopServer = () => window.BlacktemplarBot.stopServer();
    window.restartServer = () => window.BlacktemplarBot.restartServer();
    window.loadLogs = (type = 'all', limit = 100) => window.BlacktemplarBot.loadLogs(type, limit);
    window.loadMetrics = () => window.BlacktemplarBot.loadMetrics();
    window.loadMessageHistory = (phone = null) => window.BlacktemplarBot.loadMessageHistory(phone);
    window.loadConfiguration = () => window.BlacktemplarBot.loadConfiguration();
    window.updateConfig = (key, value) => window.BlacktemplarBot.updateConfig(key, value);
});

// Service Worker for offline support
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js')
        .then(registration => {
            console.log('Service Worker registrado:', registration);
        })
        .catch(error => {
            console.log('Erro ao registrar Service Worker:', error);
        });
} 
 