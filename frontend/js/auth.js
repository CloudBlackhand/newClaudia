// Authentication module

class AuthModule {
    constructor() {
        this.loginModal = null;
        this.token = localStorage.getItem('auth_token');
    }

    init() {
        this.loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        this.setupLoginForm();
        this.checkAuthStatus();
    }

    setupLoginForm() {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleLogin();
            });
        }
    }

    async handleLogin() {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        if (!username || !password) {
            Notifications.error('Por favor, preencha todos os campos');
            return;
        }

        const submitBtn = document.querySelector('#loginForm button[type="submit"]');
        const loaderId = Loading.show(submitBtn, 'Entrando...');

        try {
            const result = await API.login(username, password);
            
            if (result.success) {
                API.setToken(result.data.access_token);
                this.token = result.data.access_token;
                
                // Update username in navbar
                const usernameSpan = document.getElementById('username');
                if (usernameSpan) {
                    usernameSpan.textContent = result.data.user;
                }
                
                this.hideLoginModal();
                Notifications.success('Login realizado com sucesso!');
                
                // Refresh current section
                if (typeof app !== 'undefined') {
                    app.refreshData();
                }
            } else {
                Notifications.error(result.error || 'Erro no login');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'Login');
        } finally {
            Loading.hide(submitBtn);
        }
    }

    showLoginModal() {
        if (this.loginModal) {
            this.loginModal.show();
        }
    }

    hideLoginModal() {
        if (this.loginModal) {
            this.loginModal.hide();
        }
    }

    checkAuthStatus() {
        if (!this.token) {
            this.showLoginModal();
        }
    }

    logout() {
        API.setToken(null);
        this.token = null;
        Notifications.info('Logout realizado com sucesso');
        
        // Clear user info
        const usernameSpan = document.getElementById('username');
        if (usernameSpan) {
            usernameSpan.textContent = 'Usuário';
        }
        
        // Reload page after delay
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    isAuthenticated() {
        return !!this.token;
    }
}

// Global logout function
function logout() {
    if (window.Auth) {
        window.Auth.logout();
    }
}

// Export for global access
window.AuthModule = AuthModule;

