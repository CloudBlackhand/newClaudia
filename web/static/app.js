// Claudia Cobranças - Frontend WAHA
class ClaudiaCobrancas {
    constructor() {
        this.wahaStatus = { connected: false, instance: null, phone: null };
        this.messages = [];
        this.webhookEvents = [];
        this.init();
    }
    
    init() {
        this.createInterface();
        this.setupEventListeners();
        this.startStatusPolling();
        console.log('🚀 Claudia Cobranças - Frontend WAHA iniciado!');
    }
    
    createInterface() {
        const app = document.createElement('div');
        app.id = 'claudia-app';
        app.innerHTML = `
            <!-- Header -->
            <header class="app-header">
                <div class="header-content">
                    <div class="logo">
                        <span class="logo-icon">🧠</span>
                        <h1>Claudia Cobranças</h1>
                        <span class="version">v2.2 - WAHA Integration</span>
                    </div>
                    <div class="header-actions">
                        <div class="status-indicator" id="connectionStatus">
                            <span class="status-dot offline"></span>
                            <span class="status-text">Offline</span>
                        </div>
                        <button class="btn-refresh" onclick="claudia.refreshStatus()">🔄</button>
                    </div>
                </div>
            </header>

            <!-- Navigation -->
            <nav class="main-nav">
                <div class="nav-container">
                    <button class="nav-btn active" data-tab="dashboard">📊 Dashboard</button>
                    <button class="nav-btn" data-tab="waha">📱 WAHA</button>
                    <button class="nav-btn" data-tab="messages">💬 Mensagens</button>
                    <button class="nav-btn" data-tab="webhooks">🔗 Webhooks</button>
                </div>
            </nav>

            <!-- Main Content -->
            <main class="main-content">
                <!-- Dashboard -->
                <div class="tab-content active" id="dashboard">
                    <div class="dashboard-grid">
                        <div class="status-card waha-card">
                            <div class="card-header">
                                <h3>📱 WhatsApp WAHA</h3>
                                <div class="card-actions">
                                    <button class="btn-test" onclick="claudia.testWaha()">Testar</button>
                                    <button class="btn-connect" onclick="claudia.showWahaModal()">Conectar</button>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="status-info">
                                    <div class="status-item">
                                        <span class="label">Status:</span>
                                        <span class="value" id="wahaStatus">Desconectado</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="label">Telefone:</span>
                                        <span class="value" id="wahaPhone">-</span>
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
                                        <span class="stat-number" id="messagesSent">0</span>
                                        <span class="stat-label">Mensagens</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="stat-number" id="webhooksReceived">0</span>
                                        <span class="stat-label">Webhooks</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- WAHA Tab -->
                <div class="tab-content" id="waha">
                    <div class="waha-container">
                        <div class="waha-config">
                            <h2>⚙️ Configuração WAHA</h2>
                            <div class="config-form">
                                <div class="form-group">
                                    <label>URL do WAHA:</label>
                                    <input type="text" id="wahaUrl" value="http://localhost:8000/waha" readonly>
                                    <small>WAHA embutido - URL automática</small>
                                </div>
                                <div class="form-group">
                                    <label>Número do WhatsApp:</label>
                                    <input type="text" id="phoneNumber" placeholder="5511999999999">
                                </div>
                                <div class="form-group">
                                    <label>Código de Verificação:</label>
                                    <div class="code-input-group">
                                        <input type="text" id="verificationCode" value="123456" maxlength="6">
                                        <button class="btn-send-code" onclick="claudia.sendCode()">Enviar</button>
                                    </div>
                                    <small class="code-info">Código fixo: <strong>123456</strong></small>
                                </div>
                                <div class="form-actions">
                                    <button class="btn-primary" onclick="claudia.connectWaha()">Conectar WhatsApp</button>
                                    <button class="btn-secondary" onclick="claudia.disconnectWaha()">Desconectar</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Messages Tab -->
                <div class="tab-content" id="messages">
                    <div class="messages-container">
                        <div class="messages-header">
                            <h2>💬 Mensagens</h2>
                            <div class="messages-actions">
                                <button class="btn-refresh" onclick="claudia.refreshMessages()">🔄</button>
                                <button class="btn-clear" onclick="claudia.clearMessages()">🗑️</button>
                            </div>
                        </div>
                        
                        <div class="messages-list" id="messagesList">
                            <!-- Messages will be populated here -->
                        </div>
                        
                        <div class="message-input">
                            <div class="input-group">
                                <input type="text" id="messageInput" placeholder="Digite uma mensagem...">
                                <input type="text" id="phoneInput" placeholder="Número (opcional)">
                                <button onclick="claudia.sendMessage()">📤</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Webhooks Tab -->
                <div class="tab-content" id="webhooks">
                    <div class="webhooks-container">
                        <div class="webhooks-header">
                            <h2>🔗 Webhooks</h2>
                            <div class="webhook-status">
                                <span class="status-dot" id="webhookStatus"></span>
                                <span id="webhookStatusText">Aguardando...</span>
                            </div>
                        </div>
                        
                        <div class="webhooks-list" id="webhooksList">
                            <!-- Webhook events will be populated here -->
                        </div>
                    </div>
                </div>
            </main>

            <!-- WAHA Modal -->
            <div class="modal" id="wahaModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>📱 Conectar WAHA</h3>
                        <button class="modal-close" onclick="claudia.hideWahaModal()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="modal-form">
                            <div class="form-group">
                                <label>Número do WhatsApp:</label>
                                <input type="text" id="modalPhone" placeholder="5511999999999">
                            </div>
                            <div class="form-group">
                                <label>Código de Verificação:</label>
                                <input type="text" id="modalCode" value="123456" maxlength="6">
                                <small>Use o código: <strong>123456</strong></small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="claudia.hideWahaModal()">Cancelar</button>
                        <button class="btn-primary" onclick="claudia.connectWahaFromModal()">Conectar</button>
                    </div>
                </div>
            </div>

            <!-- Notifications -->
            <div class="notifications" id="notifications"></div>
        `;
        
        document.body.appendChild(app);
        this.applyStyles();
    }
    
    applyStyles() {
        const style = document.createElement('style');
        style.textContent = `
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }
            
            .app-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .logo-icon { font-size: 2rem; }
            .logo h1 { font-size: 1.5rem; font-weight: 600; }
            .version { font-size: 0.8rem; opacity: 0.8; }
            
            .header-actions {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: #ff4444;
            }
            
            .status-dot.online { background: #44ff44; }
            
            .btn-refresh {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                padding: 0.5rem;
                border-radius: 50%;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .btn-refresh:hover {
                background: rgba(255,255,255,0.3);
                transform: rotate(180deg);
            }
            
            .main-nav {
                background: white;
                border-bottom: 1px solid #eee;
                padding: 0.5rem 0;
            }
            
            .nav-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1rem;
                display: flex;
                gap: 0.5rem;
                overflow-x: auto;
            }
            
            .nav-btn {
                background: none;
                border: none;
                padding: 0.75rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transition: all 0.3s;
                white-space: nowrap;
            }
            
            .nav-btn:hover { background: #f0f0f0; }
            .nav-btn.active { background: #667eea; color: white; }
            
            .main-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem 1rem;
            }
            
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            
            .dashboard-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            
            .status-card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
                transition: all 0.3s;
            }
            
            .status-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
            
            .card-header {
                padding: 1rem;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .card-header h3 { font-size: 1.1rem; font-weight: 600; }
            
            .card-actions { display: flex; gap: 0.5rem; }
            
            .card-body { padding: 1rem; }
            
            .btn-primary, .btn-secondary, .btn-test, .btn-connect {
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.9rem;
                transition: all 0.3s;
            }
            
            .btn-primary { background: #667eea; color: white; }
            .btn-primary:hover { background: #5a6fd8; }
            .btn-secondary { background: #6c757d; color: white; }
            .btn-test { background: #17a2b8; color: white; }
            .btn-connect { background: #28a745; color: white; }
            
            .status-info {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .label { font-weight: 500; color: #666; }
            .value { font-weight: 600; }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }
            
            .stat-item { text-align: center; }
            
            .stat-number {
                display: block;
                font-size: 2rem;
                font-weight: 700;
                color: #667eea;
            }
            
            .stat-label {
                font-size: 0.8rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .waha-container {
                display: grid;
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            
            .waha-config {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .form-group {
                margin-bottom: 1rem;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }
            
            .form-group input {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 1rem;
            }
            
            .code-input-group {
                display: flex;
                gap: 0.5rem;
            }
            
            .code-input-group input { flex: 1; }
            
            .btn-send-code {
                padding: 0.75rem 1rem;
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            
            .code-info {
                display: block;
                margin-top: 0.25rem;
                font-size: 0.8rem;
                color: #28a745;
            }
            
            .form-actions {
                display: flex;
                gap: 1rem;
                margin-top: 1.5rem;
            }
            
            .messages-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .messages-header {
                padding: 1rem;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .messages-list {
                height: 400px;
                overflow-y: auto;
                padding: 1rem;
            }
            
            .message-item {
                margin-bottom: 1rem;
                padding: 0.75rem;
                border-radius: 8px;
                background: #f8f9fa;
            }
            
            .message-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                font-size: 0.8rem;
                color: #666;
            }
            
            .message-input {
                padding: 1rem;
                border-top: 1px solid #eee;
            }
            
            .input-group {
                display: flex;
                gap: 0.5rem;
            }
            
            .input-group input {
                flex: 1;
                padding: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            
            .input-group button {
                padding: 0.75rem 1rem;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
            }
            
            .webhooks-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 1.5rem;
            }
            
            .webhooks-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            
            .webhook-status {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .webhooks-list {
                max-height: 300px;
                overflow-y: auto;
                margin-bottom: 1rem;
            }
            
            .webhook-event {
                padding: 0.75rem;
                border: 1px solid #eee;
                border-radius: 6px;
                margin-bottom: 0.5rem;
                background: #f8f9fa;
            }
            
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 1000;
            }
            
            .modal.active {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .modal-content {
                background: white;
                border-radius: 12px;
                max-width: 500px;
                width: 90%;
                max-height: 90%;
                overflow-y: auto;
            }
            
            .modal-header {
                padding: 1rem;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: #666;
            }
            
            .modal-body { padding: 1rem; }
            
            .modal-footer {
                padding: 1rem;
                border-top: 1px solid #eee;
                display: flex;
                justify-content: flex-end;
                gap: 1rem;
            }
            
            .notifications {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1001;
            }
            
            .notification {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                padding: 1rem;
                margin-bottom: 0.5rem;
                min-width: 300px;
                animation: slideIn 0.3s ease;
            }
            
            .notification.success { border-left: 4px solid #28a745; }
            .notification.error { border-left: 4px solid #dc3545; }
            .notification.info { border-left: 4px solid #17a2b8; }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @media (max-width: 768px) {
                .dashboard-grid { grid-template-columns: 1fr; }
                .nav-text { display: none; }
                .header-content { flex-direction: column; gap: 1rem; }
                .form-actions { flex-direction: column; }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
    }
    
    switchTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        
        document.getElementById(tabName).classList.add('active');
        
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    }
    
    startStatusPolling() {
        setInterval(() => {
            this.updateStatus();
        }, 5000);
        
        this.updateStatus();
    }
    
    async updateStatus() {
        try {
            const response = await fetch('/api/waha/status');
            const status = await response.json();
            
            this.wahaStatus = status;
            this.updateUI();
            
        } catch (error) {
            console.error('Erro ao atualizar status:', error);
        }
    }
    
    updateUI() {
        const statusDot = document.querySelector('#connectionStatus .status-dot');
        const statusText = document.querySelector('#connectionStatus .status-text');
        
        if (this.wahaStatus.connected) {
            statusDot.classList.remove('offline');
            statusDot.classList.add('online');
            statusText.textContent = 'Online';
        } else {
            statusDot.classList.remove('online');
            statusDot.classList.add('offline');
            statusText.textContent = 'Offline';
        }
        
        document.getElementById('wahaStatus').textContent = 
            this.wahaStatus.connected ? 'Conectado' : 'Desconectado';
        document.getElementById('wahaPhone').textContent = 
            this.wahaStatus.phone || '-';
    }
    
    async testWaha() {
        try {
            const response = await fetch('/waha-test');
            const result = await response.json();
            
            if (result.waha === 'available') {
                this.showNotification('✅ WAHA funcionando!', 'success');
            } else {
                this.showNotification(`❌ WAHA não disponível: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro ao testar WAHA: ${error.message}`, 'error');
        }
    }
    
    showWahaModal() {
        document.getElementById('wahaModal').classList.add('active');
    }
    
    hideWahaModal() {
        document.getElementById('wahaModal').classList.remove('active');
    }
    
    async sendCode() {
        const phoneNumber = document.getElementById('phoneNumber').value;
        
        if (!phoneNumber) {
            this.showNotification('❌ Digite o número do WhatsApp', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/waha/send-code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_number: phoneNumber })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Código enviado! Use 123456', 'success');
            } else {
                this.showNotification(`❌ Erro: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async connectWaha() {
        const phoneNumber = document.getElementById('phoneNumber').value;
        const code = document.getElementById('verificationCode').value;
        
        if (!phoneNumber || !code) {
            this.showNotification('❌ Preencha todos os campos', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/waha/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    waha_url: 'http://localhost:8000/waha',
                    phone_number: phoneNumber,
                    code: code
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ WhatsApp conectado!', 'success');
                this.updateStatus();
            } else {
                this.showNotification(`❌ Erro: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async connectWahaFromModal() {
        const phoneNumber = document.getElementById('modalPhone').value;
        const code = document.getElementById('modalCode').value;
        
        if (!phoneNumber || !code) {
            this.showNotification('❌ Preencha todos os campos', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/waha/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    waha_url: 'http://localhost:8000/waha',
                    phone_number: phoneNumber,
                    code: code
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ WhatsApp conectado!', 'success');
                this.hideWahaModal();
                this.updateStatus();
            } else {
                this.showNotification(`❌ Erro: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async disconnectWaha() {
        try {
            const response = await fetch('/api/waha/disconnect', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ WhatsApp desconectado', 'success');
                this.updateStatus();
            } else {
                this.showNotification(`❌ Erro: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const phoneInput = document.getElementById('phoneInput');
        
        const message = messageInput.value;
        const phone = phoneInput.value;
        
        if (!message) {
            this.showNotification('❌ Digite uma mensagem', 'error');
            return;
        }
        
        try {
            const response = await fetch('/api/waha/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone_number: phone || this.wahaStatus.phone,
                    message: message
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Mensagem enviada!', 'success');
                messageInput.value = '';
                this.addMessage({
                    from: 'Você',
                    to: phone || this.wahaStatus.phone,
                    message: message,
                    timestamp: new Date().toISOString(),
                    type: 'sent'
                });
            } else {
                this.showNotification(`❌ Erro: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showNotification(`❌ Erro: ${error.message}`, 'error');
        }
    }
    
    addMessage(message) {
        this.messages.unshift(message);
        this.updateMessagesList();
        this.updateStats();
    }
    
    updateMessagesList() {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;
        
        messagesList.innerHTML = this.messages.map(msg => `
            <div class="message-item ${msg.type}">
                <div class="message-header">
                    <span>${msg.from} → ${msg.to}</span>
                    <span>${new Date(msg.timestamp).toLocaleString()}</span>
                </div>
                <div class="message-content">${msg.message}</div>
            </div>
        `).join('');
    }
    
    updateStats() {
        document.getElementById('messagesSent').textContent = this.messages.length;
        document.getElementById('webhooksReceived').textContent = this.webhookEvents.length;
    }
    
    showNotification(message, type = 'info') {
        const notifications = document.getElementById('notifications');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        notifications.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    refreshStatus() {
        this.updateStatus();
        this.showNotification('🔄 Status atualizado', 'info');
    }
    
    refreshMessages() {
        this.showNotification('🔄 Mensagens atualizadas', 'info');
    }
    
    clearMessages() {
        this.messages = [];
        this.updateMessagesList();
        this.showNotification('🗑️ Mensagens limpas', 'info');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.claudia = new ClaudiaCobrancas();
});
