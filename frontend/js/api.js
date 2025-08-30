// API client for the billing system

class APIClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.token = localStorage.getItem('auth_token');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    // Get authentication headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            // Handle authentication errors
            if (response.status === 401) {
                this.setToken(null);
                Auth.showLoginModal();
                throw new Error('Sessão expirada. Faça login novamente.');
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return {
                success: true,
                data,
                status: response.status
            };
        } catch (error) {
            console.error('API Request failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // Upload file
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Add additional data
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': this.token ? `Bearer ${this.token}` : undefined
                },
                body: formData
            });
            
            if (response.status === 401) {
                this.setToken(null);
                Auth.showLoginModal();
                throw new Error('Sessão expirada. Faça login novamente.');
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return {
                success: true,
                data,
                status: response.status
            };
        } catch (error) {
            console.error('File upload failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // === Authentication APIs ===
    
    async login(username, password) {
        return this.post(CONFIG.ENDPOINTS.LOGIN, { username, password });
    }

    // === Billing APIs ===
    
    async sendBillingBatch(clientsFile, templateName, filters = {}, delaySeconds = 2) {
        return this.post(CONFIG.ENDPOINTS.BILLING_SEND_BATCH, {
            clients_file: clientsFile,
            template_name: templateName,
            filters,
            delay_seconds: delaySeconds
        });
    }
    
    async sendSingleMessage(clientData, templateName) {
        return this.post(CONFIG.ENDPOINTS.BILLING_SEND_SINGLE, {
            client: clientData,
            template_name: templateName
        });
    }
    
    async validateBillingConfig(clientsFile, templateName) {
        return this.post(CONFIG.ENDPOINTS.BILLING_VALIDATE, {
            clients_file: clientsFile,
            template_name: templateName
        });
    }
    
    async getBatchStatus() {
        return this.get(CONFIG.ENDPOINTS.BILLING_BATCH_STATUS);
    }
    
    async getTemplates() {
        return this.get(CONFIG.ENDPOINTS.BILLING_TEMPLATES);
    }
    
    async addTemplate(name, content) {
        return this.post(CONFIG.ENDPOINTS.BILLING_TEMPLATES, {
            name,
            content
        });
    }

    // === Chat APIs ===
    
    async processChatMessage(phone, message) {
        return this.post(CONFIG.ENDPOINTS.CHAT_PROCESS, {
            phone,
            message
        });
    }
    
    async getConversationHistory(phone, limit = null) {
        let endpoint = `${CONFIG.ENDPOINTS.CHAT_CONVERSATION}/${phone}`;
        if (limit) {
            endpoint += `?limit=${limit}`;
        }
        return this.get(endpoint);
    }
    
    async getConversationsStats() {
        return this.get(CONFIG.ENDPOINTS.CHAT_CONVERSATIONS_STATS);
    }

    // === Waha APIs ===
    
    async getWahaStatus() {
        return this.get(CONFIG.ENDPOINTS.WAHA_STATUS);
    }
    
    async startWahaSession() {
        return this.post(CONFIG.ENDPOINTS.WAHA_START, {});
    }
    
    async stopWahaSession() {
        return this.post(CONFIG.ENDPOINTS.WAHA_STOP, {});
    }
    
    async getQRCode() {
        return this.get(CONFIG.ENDPOINTS.WAHA_QR);
    }

    // === Upload APIs ===
    
    async uploadClientsFile(file) {
        return this.uploadFile(CONFIG.ENDPOINTS.UPLOAD_CLIENTS, file);
    }

    // === System APIs ===
    
    async healthCheck() {
        return this.get(CONFIG.ENDPOINTS.HEALTH);
    }
}

// Notification system
class NotificationManager {
    constructor() {
        this.container = document.querySelector('.toast-container');
        if (!this.container) {
            this.createContainer();
        }
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = CONFIG.UI.TOAST_DURATION) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToast(message, type) {
        const toastId = Utils.generateId();
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-triangle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        
        const colors = {
            success: 'text-success',
            error: 'text-danger',
            warning: 'text-warning',
            info: 'text-info'
        };

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.id = toastId;

        toast.innerHTML = `
            <div class="toast-header">
                <i class="bi ${icons[type]} ${colors[type]} me-2"></i>
                <strong class="me-auto">Sistema</strong>
                <small>${Utils.formatRelativeTime(new Date().toISOString())}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${Utils.escapeHtml(message)}
            </div>
        `;

        return toast;
    }

    success(message) {
        this.show(message, 'success');
    }

    error(message) {
        this.show(message, 'error');
    }

    warning(message) {
        this.show(message, 'warning');
    }

    info(message) {
        this.show(message, 'info');
    }
}

// Loading manager
class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
    }

    show(element, text = 'Carregando...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;

        const loaderId = Utils.generateId();
        this.activeLoaders.add(loaderId);

        // Store original content
        element.dataset.originalContent = element.innerHTML;
        element.dataset.loaderId = loaderId;
        
        // Show loading
        element.innerHTML = `
            <span class="loading me-2"></span>
            ${text}
        `;
        element.disabled = true;

        return loaderId;
    }

    hide(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;

        const loaderId = element.dataset.loaderId;
        if (loaderId) {
            this.activeLoaders.delete(loaderId);
        }

        // Restore original content
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
            delete element.dataset.loaderId;
        }
        
        element.disabled = false;
    }

    isLoading(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        return element && element.dataset.loaderId && this.activeLoaders.has(element.dataset.loaderId);
    }
}

// Error handler
class ErrorHandler {
    static handle(error, context = '') {
        console.error(`Error in ${context}:`, error);
        
        let message = 'Ocorreu um erro inesperado.';
        
        if (typeof error === 'string') {
            message = error;
        } else if (error.message) {
            message = error.message;
        }
        
        // Show user-friendly error
        Notifications.error(message);
        
        // Log for debugging in development
        if (CONFIG.DEBUG) {
            console.error('Full error details:', error);
        }
    }
}

// Initialize global instances
const API = new APIClient();
const Notifications = new NotificationManager();
const Loading = new LoadingManager();

// Export for other modules
window.API = API;
window.Notifications = Notifications;
window.Loading = Loading;
window.ErrorHandler = ErrorHandler;

