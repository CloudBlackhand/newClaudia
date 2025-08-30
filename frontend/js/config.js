// Configuration for the billing system frontend

const CONFIG = {
    // API Base URL - adjust for your environment
    API_BASE_URL: window.location.origin,
    
    // API Endpoints
    ENDPOINTS: {
        // Authentication
        LOGIN: '/auth/login',
        
        // Billing
        BILLING_SEND_BATCH: '/api/billing/send-batch',
        BILLING_SEND_SINGLE: '/api/billing/send-single',
        BILLING_VALIDATE: '/api/billing/validate',
        BILLING_BATCH_STATUS: '/api/billing/batch-status',
        BILLING_TEMPLATES: '/api/billing/templates',
        
        // Chat
        CHAT_PROCESS: '/api/chat/process',
        CHAT_CONVERSATION: '/api/chat/conversation',
        CHAT_CONVERSATIONS_STATS: '/api/chat/conversations/stats',
        
        // Waha
        WAHA_STATUS: '/api/waha/status',
        WAHA_START: '/api/waha/start',
        WAHA_STOP: '/api/waha/stop',
        WAHA_QR: '/api/waha/qr',
        
        // Upload
        UPLOAD_CLIENTS: '/api/upload/clients',
        
        // System
        HEALTH: '/health',
        WEBHOOK_WAHA: '/webhook/waha'
    },
    
    // UI Settings
    UI: {
        TOAST_DURATION: 5000,
        REFRESH_INTERVAL: 30000, // 30 seconds
        BATCH_PROGRESS_INTERVAL: 2000, // 2 seconds
        MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
        ALLOWED_FILE_TYPES: ['.json', '.txt', '.csv']
    },
    
    // Validation Rules
    VALIDATION: {
        MIN_PASSWORD_LENGTH: 6,
        MAX_MESSAGE_LENGTH: 4096,
        MAX_TEMPLATE_NAME_LENGTH: 50
    },
    
    // Status mappings
    STATUS: {
        WAHA: {
            WORKING: 'success',
            STARTING: 'warning',
            SCAN_QR_CODE: 'info',
            FAILED: 'danger',
            STOPPED: 'secondary'
        },
        BATCH: {
            RUNNING: 'info',
            COMPLETED: 'success',
            FAILED: 'danger',
            CANCELLED: 'warning'
        }
    },
    
    // Message types for activity feed
    MESSAGE_TYPES: {
        INFO: 'info',
        SUCCESS: 'success',
        WARNING: 'warning',
        ERROR: 'danger'
    }
};

// Utility functions
const Utils = {
    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(amount);
    },
    
    // Format date
    formatDate(dateString) {
        return new Intl.DateTimeFormat('pt-BR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(dateString));
    },
    
    // Format relative time
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInMs = now - date;
        const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
        const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
        const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
        
        if (diffInMinutes < 1) {
            return 'Agora';
        } else if (diffInMinutes < 60) {
            return `${diffInMinutes}m atrás`;
        } else if (diffInHours < 24) {
            return `${diffInHours}h atrás`;
        } else {
            return `${diffInDays}d atrás`;
        }
    },
    
    // Mask phone number
    maskPhone(phone) {
        if (!phone || phone.length < 4) return '****';
        return `${phone.slice(0, 2)}****${phone.slice(-2)}`;
    },
    
    // Generate random ID
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Validate file
    validateFile(file) {
        const errors = [];
        
        // Check file size
        if (file.size > CONFIG.UI.MAX_FILE_SIZE) {
            errors.push(`Arquivo muito grande. Máximo: ${CONFIG.UI.MAX_FILE_SIZE / (1024 * 1024)}MB`);
        }
        
        // Check file type
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!CONFIG.UI.ALLOWED_FILE_TYPES.includes(extension)) {
            errors.push(`Tipo de arquivo não permitido. Permitidos: ${CONFIG.UI.ALLOWED_FILE_TYPES.join(', ')}`);
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    },
    
    // Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    // Get status badge class
    getStatusBadgeClass(status, type = 'WAHA') {
        const statusMap = CONFIG.STATUS[type];
        return statusMap[status] || 'secondary';
    },
    
    // Format percentage
    formatPercentage(value, total) {
        if (total === 0) return '0%';
        return `${Math.round((value / total) * 100)}%`;
    },
    
    // Copy to clipboard
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy: ', err);
            return false;
        }
    },
    
    // Download data as JSON
    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },
    
    // Parse JSON safely
    parseJSON(jsonString) {
        try {
            return {
                success: true,
                data: JSON.parse(jsonString)
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    },
    
    // Validate phone number (Brazilian format)
    validatePhone(phone) {
        const cleanPhone = phone.replace(/\D/g, '');
        const phoneRegex = /^55\d{10,11}$/;
        return phoneRegex.test(cleanPhone);
    },
    
    // Format phone number for display
    formatPhone(phone) {
        const cleanPhone = phone.replace(/\D/g, '');
        if (cleanPhone.length === 13) { // +55XXXXXXXXXXX
            return `+${cleanPhone.slice(0, 2)} (${cleanPhone.slice(2, 4)}) ${cleanPhone.slice(4, 9)}-${cleanPhone.slice(9)}`;
        }
        return phone;
    },
    
    // Get file size in human readable format
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, Utils };
}

