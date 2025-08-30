// Main application initialization and navigation

class App {
    constructor() {
        this.currentSection = 'home';
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        
        try {
            console.log('Initializing Billing System Frontend...');
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Setup navigation
            this.setupNavigation();
            
            // Check authentication
            await this.checkAuth();
            
            // Initialize modules
            await this.initializeModules();
            
            // Start periodic updates
            this.startPeriodicUpdates();
            
            this.initialized = true;
            console.log('Application initialized successfully');
            
        } catch (error) {
            ErrorHandler.handle(error, 'App initialization');
        }
    }

    setupEventListeners() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });

        // Window load
        window.addEventListener('load', () => {
            this.hideLoadingScreen();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Visibility change (tab focus/unfocus)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshData();
            }
        });
    }

    setupNavigation() {
        // Navigation links
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    this.navigateToSection(href.substring(1));
                }
            });
        });

        // Handle browser back/forward
        window.addEventListener('popstate', (e) => {
            const section = e.state?.section || 'home';
            this.showSection(section, false);
        });

        // Initial section from URL hash
        const hash = window.location.hash.substring(1);
        if (hash) {
            this.navigateToSection(hash);
        }
    }

    async checkAuth() {
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
            Auth.showLoginModal();
            return;
        }

        // Verify token with health check
        try {
            const result = await API.healthCheck();
            if (!result.success) {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.warn('Token verification failed:', error);
            Auth.showLoginModal();
        }
    }

    async initializeModules() {
        try {
            // Initialize authentication
            if (typeof AuthModule !== 'undefined') {
                window.Auth = new AuthModule();
                Auth.init();
            }

            // Initialize dashboard
            if (typeof DashboardModule !== 'undefined') {
                window.Dashboard = new DashboardModule();
                await Dashboard.init();
            }

            // Initialize billing module
            if (typeof BillingModule !== 'undefined') {
                window.Billing = new BillingModule();
                Billing.init();
            }

            // Initialize conversations module
            if (typeof ConversationsModule !== 'undefined') {
                window.Conversations = new ConversationsModule();
                Conversations.init();
            }

            // Initialize templates module
            if (typeof TemplatesModule !== 'undefined') {
                window.Templates = new TemplatesModule();
                Templates.init();
            }

        } catch (error) {
            console.error('Module initialization failed:', error);
        }
    }

    navigateToSection(sectionName) {
        this.showSection(sectionName, true);
    }

    showSection(sectionName, updateHistory = true) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionName;

            // Update navigation
            this.updateNavigation(sectionName);

            // Update browser history
            if (updateHistory) {
                history.pushState(
                    { section: sectionName }, 
                    '', 
                    `#${sectionName}`
                );
            }

            // Trigger section-specific actions
            this.onSectionChange(sectionName);
        }
    }

    updateNavigation(activeSection) {
        // Update nav links
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
            link.classList.remove('active');
            const href = link.getAttribute('href');
            if (href === `#${activeSection}`) {
                link.classList.add('active');
            }
        });
    }

    onSectionChange(sectionName) {
        // Trigger section-specific refresh/initialization
        switch (sectionName) {
            case 'dashboard':
                if (typeof Dashboard !== 'undefined') {
                    Dashboard.refresh();
                }
                break;
            case 'billing':
                if (typeof Billing !== 'undefined') {
                    Billing.refresh();
                }
                break;
            case 'conversations':
                if (typeof Conversations !== 'undefined') {
                    Conversations.refresh();
                }
                break;
            case 'templates':
                if (typeof Templates !== 'undefined') {
                    Templates.refresh();
                }
                break;
        }
    }

    startPeriodicUpdates() {
        // Update every 30 seconds
        setInterval(() => {
            if (!document.hidden) {
                this.refreshData();
            }
        }, CONFIG.UI.REFRESH_INTERVAL);
    }

    async refreshData() {
        try {
            // Only refresh current section data to avoid unnecessary requests
            switch (this.currentSection) {
                case 'dashboard':
                    if (typeof Dashboard !== 'undefined') {
                        await Dashboard.updateStats();
                    }
                    break;
                case 'billing':
                    if (typeof Billing !== 'undefined') {
                        await Billing.checkBatchStatus();
                    }
                    break;
                case 'conversations':
                    if (typeof Conversations !== 'undefined') {
                        await Conversations.updateStats();
                    }
                    break;
            }
        } catch (error) {
            console.warn('Periodic refresh failed:', error);
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + key combinations
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.navigateToSection('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.navigateToSection('billing');
                    break;
                case '3':
                    e.preventDefault();
                    this.navigateToSection('conversations');
                    break;
                case '4':
                    e.preventDefault();
                    this.navigateToSection('templates');
                    break;
            }
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
    }

    // Utility methods for other modules
    getCurrentSection() {
        return this.currentSection;
    }

    isInitialized() {
        return this.initialized;
    }
}

// Authentication module
class AuthModule {
    constructor() {
        this.loginModal = null;
    }

    init() {
        this.loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        this.setupLoginForm();
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
}

// Global logout function
function logout() {
    API.setToken(null);
    Notifications.info('Logout realizado com sucesso');
    
    // Reload page to reset state
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Initialize application
const app = new App();

// Start initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => app.init());
} else {
    app.init();
}

// Export for global access
window.app = app;
