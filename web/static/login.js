// 🔐 Sistema de Login com Aprovação Manual - JavaScript Puro
// Blacktemplar Bolter - Login System

class LoginSystem {
    constructor() {
        this.isLoggedIn = false;
        this.sessionToken = null;
        this.pendingRequests = new Map();
        this.checkInterval = null;
        this.init();
    }

    init() {
        // Verificar se já está logado ao carregar
        this.checkExistingSession();
        
        // Se não logado, mostrar tela de login
        if (!this.isLoggedIn) {
            this.showLoginScreen();
        }
    }

    checkExistingSession() {
        const token = localStorage.getItem('blacktemplar_session');
        if (token) {
            this.validateSession(token);
        }
    }

    async validateSession(token) {
        try {
            const response = await fetch('/api/auth/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.valid) {
                    this.sessionToken = token;
                    this.isLoggedIn = true;
                    this.showMainApp();
                    return;
                }
            }
        } catch (error) {
            console.log('Erro validando sessão:', error);
        }

        // Se chegou aqui, sessão inválida
        localStorage.removeItem('blacktemplar_session');
        this.showLoginScreen();
    }

    showLoginScreen() {
        // Limpar conteúdo atual
        document.body.innerHTML = '';

        // Criar tela de login
        const loginContainer = document.createElement('div');
        loginContainer.className = 'login-container';
        loginContainer.innerHTML = `
            <div class="login-box">
                <div class="login-header">
                    <img src="/static/icon.png" alt="Logo" class="login-logo">
                    <h1>Blacktemplar Bolter</h1>
                    <p>Sistema de Autenticação Segura</p>
                </div>

                <div class="login-form">
                    <div class="input-group">
                        <label for="loginEmail">👤 Email/Usuário:</label>
                        <input type="text" id="loginEmail" placeholder="seu@email.com" autocomplete="username">
                    </div>

                    <div class="input-group">
                        <label for="loginPassword">🔑 Senha:</label>
                        <input type="password" id="loginPassword" placeholder="Sua senha" autocomplete="current-password">
                    </div>

                    <div class="input-group">
                        <label for="loginReason">📝 Motivo do Acesso (opcional):</label>
                        <input type="text" id="loginReason" placeholder="Ex: Verificar faturas, configurar bot...">
                    </div>

                    <button id="loginBtn" class="login-btn" onclick="loginSystem.requestLogin()">
                        🚀 Solicitar Acesso
                    </button>

                    <div id="loginStatus" class="login-status"></div>
                </div>

                <div class="login-footer">
                    <p>🛡️ <strong>Sistema com Aprovação Manual</strong></p>
                    <p>Sua solicitação será avaliada pelo administrador</p>
                    <p><small>Aguarde a aprovação no terminal Railway</small></p>
                </div>
            </div>

            <div class="login-background">
                <div class="bg-animation"></div>
            </div>
        `;

        document.body.appendChild(loginContainer);
        this.setupLoginEvents();
    }

    setupLoginEvents() {
        // Enter para submeter
        ['loginEmail', 'loginPassword', 'loginReason'].forEach(id => {
            document.getElementById(id)?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.requestLogin();
                }
            });
        });

        // Focus no primeiro campo
        document.getElementById('loginEmail')?.focus();
    }

    async requestLogin() {
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const reason = document.getElementById('loginReason').value.trim();

        if (!email || !password) {
            this.showLoginMessage('❌ Preencha email e senha', 'error');
            return;
        }

        const loginBtn = document.getElementById('loginBtn');
        const originalText = loginBtn.innerHTML;
        
        try {
            loginBtn.innerHTML = '⏳ Enviando solicitação...';
            loginBtn.disabled = true;

            const response = await fetch('/api/auth/request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    reason,
                    timestamp: new Date().toISOString(),
                    user_agent: navigator.userAgent,
                    ip: await this.getClientIP()
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.startPollingForApproval(data.request_id);
                this.showLoginMessage(
                    '✅ Solicitação enviada! Aguardando aprovação do administrador...', 
                    'success'
                );
            } else {
                this.showLoginMessage(`❌ ${data.error || 'Erro na solicitação'}`, 'error');
            }

        } catch (error) {
            console.error('Erro no login:', error);
            this.showLoginMessage('❌ Erro de conexão. Tente novamente.', 'error');
        } finally {
            loginBtn.innerHTML = originalText;
            loginBtn.disabled = false;
        }
    }

    async getClientIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch {
            return 'Unknown';
        }
    }

    startPollingForApproval(requestId) {
        this.showLoginMessage('⏳ Aguardando aprovação... (pode levar alguns minutos)', 'waiting');
        
        this.checkInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/auth/check/${requestId}`);
                const data = await response.json();

                if (data.status === 'approved') {
                    clearInterval(this.checkInterval);
                    this.sessionToken = data.token;
                    localStorage.setItem('blacktemplar_session', data.token);
                    this.isLoggedIn = true;
                    this.showLoginMessage('✅ Acesso aprovado! Carregando sistema...', 'success');
                    
                    setTimeout(() => {
                        this.showMainApp();
                    }, 2000);

                } else if (data.status === 'denied') {
                    clearInterval(this.checkInterval);
                    this.showLoginMessage('❌ Acesso negado pelo administrador', 'error');

                } else if (data.status === 'expired') {
                    clearInterval(this.checkInterval);
                    this.showLoginMessage('⏰ Solicitação expirou. Tente novamente.', 'error');
                }

            } catch (error) {
                console.error('Erro verificando status:', error);
            }
        }, 3000); // Verificar a cada 3 segundos
    }

    showLoginMessage(message, type) {
        const statusDiv = document.getElementById('loginStatus');
        if (statusDiv) {
            statusDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
            
            // Auto-limpar mensagens de erro após 10s
            if (type === 'error') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 10000);
            }
        }
    }

    showMainApp() {
        // Limpar polling se existir
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }

        // Recarregar a página para carregar o app principal
        // ou inserir dinamicamente o conteúdo principal
        document.body.innerHTML = '';
        
        // Recriar o app principal
        const appDiv = document.createElement('div');
        appDiv.id = 'main-app';
        document.body.appendChild(appDiv);

        // Recarregar scripts do app principal
        window.location.reload();
    }

    async logout() {
        try {
            if (this.sessionToken) {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.sessionToken}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Erro no logout:', error);
        }

        // Limpar dados locais
        localStorage.removeItem('blacktemplar_session');
        this.sessionToken = null;
        this.isLoggedIn = false;

        // Voltar para tela de login
        this.showLoginScreen();
    }

    // Método para verificar se está logado (usado pelos outros scripts)
    isAuthenticated() {
        return this.isLoggedIn;
    }

    getAuthHeaders() {
        if (this.sessionToken) {
            return {
                'Authorization': `Bearer ${this.sessionToken}`
            };
        }
        return {};
    }
}

// Inicializar sistema de login quando DOM carregar
document.addEventListener('DOMContentLoaded', () => {
    window.loginSystem = new LoginSystem();
});

// Exportar para uso global
window.LoginSystem = LoginSystem;