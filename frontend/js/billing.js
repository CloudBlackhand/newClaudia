// Billing module

class BillingModule {
    constructor() {
        this.currentBatch = null;
        this.progressInterval = null;
        this.uploadedFiles = [];
    }

    init() {
        this.setupEventListeners();
        this.loadTemplates();
        this.loadUploadedFiles();
    }

    setupEventListeners() {
        // Upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFileUpload();
            });
        }

        // Billing form
        const billingForm = document.getElementById('billingForm');
        if (billingForm) {
            billingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleBillingSubmit();
            });
        }

        // File input change
        const fileInput = document.getElementById('clientsFile');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.validateFileInput(e.target.files[0]);
            });
        }
    }

    validateFileInput(file) {
        const uploadResult = document.getElementById('uploadResult');
        
        if (!file) {
            uploadResult.innerHTML = '';
            return;
        }

        const validation = Utils.validateFile(file);
        
        if (!validation.valid) {
            uploadResult.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Arquivo inválido:</strong>
                    <ul class="mb-0">
                        ${validation.errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            `;
            return;
        }

        uploadResult.innerHTML = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle"></i>
                <strong>Arquivo selecionado:</strong> ${file.name} (${Utils.formatFileSize(file.size)})
            </div>
        `;
    }

    async handleFileUpload() {
        const fileInput = document.getElementById('clientsFile');
        const file = fileInput.files[0];
        
        if (!file) {
            Notifications.error('Selecione um arquivo para upload');
            return;
        }

        const validation = Utils.validateFile(file);
        if (!validation.valid) {
            Notifications.error('Arquivo inválido: ' + validation.errors.join(', '));
            return;
        }

        const submitBtn = document.querySelector('#uploadForm button[type="submit"]');
        const loaderId = Loading.show(submitBtn, 'Enviando...');
        
        try {
            const result = await API.uploadClientsFile(file);
            
            if (result.success) {
                Notifications.success('Arquivo enviado com sucesso!');
                
                // Add to uploaded files list
                this.uploadedFiles.push({
                    filename: result.data.filename,
                    path: result.data.path,
                    uploadedAt: new Date().toISOString()
                });
                
                this.updateUploadedFilesList();
                this.updateFileSelect();
                
                // Clear form
                fileInput.value = '';
                document.getElementById('uploadResult').innerHTML = '';
                
            } else {
                Notifications.error(result.error || 'Erro no upload');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'File upload');
        } finally {
            Loading.hide(submitBtn);
        }
    }

    updateUploadedFilesList() {
        // Update any UI list of uploaded files if exists
        const filesList = document.getElementById('uploadedFilesList');
        if (filesList) {
            filesList.innerHTML = this.uploadedFiles.map(file => `
                <div class="uploaded-file-item">
                    <i class="bi bi-file-earmark-text"></i>
                    <span>${file.filename}</span>
                    <small class="text-muted">${Utils.formatRelativeTime(file.uploadedAt)}</small>
                </div>
            `).join('');
        }
    }

    updateFileSelect() {
        const fileSelect = document.getElementById('selectedFile');
        if (fileSelect) {
            // Clear current options except the first
            fileSelect.innerHTML = '<option value="">Selecione um arquivo...</option>';
            
            // Add uploaded files
            this.uploadedFiles.forEach(file => {
                const option = document.createElement('option');
                option.value = file.path;
                option.textContent = file.filename;
                fileSelect.appendChild(option);
            });
            
            // Add default example file
            const exampleOption = document.createElement('option');
            exampleOption.value = 'data/clients.json';
            exampleOption.textContent = 'clients.json (exemplo)';
            fileSelect.appendChild(exampleOption);
        }
    }

    async loadTemplates() {
        try {
            const result = await API.getTemplates();
            
            if (result.success) {
                const templateSelect = document.getElementById('selectedTemplate');
                if (templateSelect) {
                    templateSelect.innerHTML = '<option value="">Selecione um template...</option>';
                    
                    Object.keys(result.data).forEach(templateName => {
                        const option = document.createElement('option');
                        option.value = templateName;
                        option.textContent = templateName.replace(/_/g, ' ').toUpperCase();
                        templateSelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            console.warn('Failed to load templates:', error);
        }
    }

    loadUploadedFiles() {
        // Load from localStorage for persistence
        const saved = localStorage.getItem('uploadedFiles');
        if (saved) {
            try {
                this.uploadedFiles = JSON.parse(saved);
                this.updateFileSelect();
                this.updateUploadedFilesList();
            } catch (error) {
                console.warn('Failed to load uploaded files from storage');
            }
        }
    }

    saveUploadedFiles() {
        // Save to localStorage
        localStorage.setItem('uploadedFiles', JSON.stringify(this.uploadedFiles));
    }

    async validateBilling() {
        const clientsFile = document.getElementById('selectedFile').value;
        const templateName = document.getElementById('selectedTemplate').value;
        
        if (!clientsFile || !templateName) {
            Notifications.warning('Selecione arquivo e template antes de validar');
            return;
        }

        const validateBtn = document.querySelector('button[onclick="validateBilling()"]');
        const loaderId = Loading.show(validateBtn, 'Validando...');
        
        try {
            const result = await API.validateBillingConfig(clientsFile, templateName);
            
            if (result.success) {
                if (result.data.valid) {
                    Notifications.success('Configuração válida! Pronto para envio.');
                    
                    // Show validation details
                    this.showValidationResults(result.data);
                } else {
                    Notifications.error('Configuração inválida: ' + result.data.issues.join(', '));
                    this.showValidationResults(result.data);
                }
            } else {
                Notifications.error(result.error || 'Erro na validação');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'Billing validation');
        } finally {
            Loading.hide(validateBtn);
        }
    }

    showValidationResults(validation) {
        const resultDiv = document.getElementById('billingResult');
        if (!resultDiv) return;

        let html = '<div class="mt-3">';
        
        if (validation.valid) {
            html += '<div class="alert alert-success"><i class="bi bi-check-circle"></i> Configuração válida</div>';
        } else {
            html += '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Configuração inválida</div>';
        }

        // Client stats
        if (validation.client_stats) {
            html += `
                <div class="card mt-2">
                    <div class="card-header"><small>Estatísticas do Arquivo</small></div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Tamanho:</strong> ${validation.client_stats.file_size_mb?.toFixed(2)} MB
                            </div>
                            <div class="col-md-6">
                                <strong>Estimativa:</strong> ${validation.client_stats.estimated_count} clientes
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Waha status
        if (validation.waha_status) {
            const statusClass = validation.waha_status.success ? 'success' : 'danger';
            html += `
                <div class="card mt-2">
                    <div class="card-header"><small>Status WhatsApp</small></div>
                    <div class="card-body">
                        <span class="badge bg-${statusClass}">${validation.waha_status.status || 'Offline'}</span>
                    </div>
                </div>
            `;
        }

        // Issues and warnings
        if (validation.issues && validation.issues.length > 0) {
            html += `
                <div class="alert alert-danger mt-2">
                    <strong>Problemas encontrados:</strong>
                    <ul class="mb-0">${validation.issues.map(issue => `<li>${issue}</li>`).join('')}</ul>
                </div>
            `;
        }

        if (validation.warnings && validation.warnings.length > 0) {
            html += `
                <div class="alert alert-warning mt-2">
                    <strong>Avisos:</strong>
                    <ul class="mb-0">${validation.warnings.map(warning => `<li>${warning}</li>`).join('')}</ul>
                </div>
            `;
        }

        html += '</div>';
        resultDiv.innerHTML = html;
    }

    async handleBillingSubmit() {
        const clientsFile = document.getElementById('selectedFile').value;
        const templateName = document.getElementById('selectedTemplate').value;
        const delaySeconds = parseInt(document.getElementById('delaySeconds').value) || 2;
        
        if (!clientsFile || !templateName) {
            Notifications.error('Selecione arquivo e template');
            return;
        }

        const submitBtn = document.querySelector('#billingForm button[type="submit"]');
        const loaderId = Loading.show(submitBtn, 'Iniciando envio...');
        
        try {
            const result = await API.sendBillingBatch(clientsFile, templateName, {}, delaySeconds);
            
            if (result.success) {
                Notifications.success('Lote de cobrança iniciado!');
                this.currentBatch = result.data;
                this.showBatchProgress();
                this.startProgressMonitoring();
            } else {
                Notifications.error(result.error || 'Erro ao enviar lote');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'Billing batch send');
        } finally {
            Loading.hide(submitBtn);
        }
    }

    showBatchProgress() {
        const progressDiv = document.getElementById('batchProgress');
        if (progressDiv) {
            progressDiv.style.display = 'block';
            this.updateProgressDisplay();
        }
    }

    hideBatchProgress() {
        const progressDiv = document.getElementById('batchProgress');
        if (progressDiv) {
            progressDiv.style.display = 'none';
        }
    }

    updateProgressDisplay() {
        if (!this.currentBatch) return;

        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const totalClients = document.getElementById('totalClients');
        const processedClients = document.getElementById('processedClients');
        const successfulClients = document.getElementById('successfulClients');
        const failedClients = document.getElementById('failedClients');

        const progress = this.currentBatch.progress_percentage || 0;
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress.toFixed(1)}%`;
        }

        if (progressText) {
            if (this.currentBatch.is_running) {
                progressText.textContent = `Processando... ${this.currentBatch.processed}/${this.currentBatch.total_clients}`;
            } else {
                progressText.textContent = 'Lote concluído!';
            }
        }

        if (totalClients) totalClients.textContent = this.currentBatch.total_clients || 0;
        if (processedClients) processedClients.textContent = this.currentBatch.processed || 0;
        if (successfulClients) successfulClients.textContent = this.currentBatch.successful || 0;
        if (failedClients) failedClients.textContent = this.currentBatch.failed || 0;
    }

    startProgressMonitoring() {
        this.progressInterval = setInterval(async () => {
            await this.checkBatchStatus();
        }, CONFIG.UI.BATCH_PROGRESS_INTERVAL);
    }

    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
    }

    async checkBatchStatus() {
        try {
            const result = await API.getBatchStatus();
            
            if (result.success) {
                this.currentBatch = result.data;
                this.updateProgressDisplay();
                
                // Stop monitoring if batch is complete
                if (!this.currentBatch.is_running) {
                    this.stopProgressMonitoring();
                    Notifications.success('Lote de cobrança concluído!');
                    
                    // Update dashboard stats if available
                    if (window.Dashboard) {
                        Dashboard.updateStat('totalMessages', this.currentBatch.successful);
                        const successRate = Math.round((this.currentBatch.successful / this.currentBatch.total_clients) * 100);
                        Dashboard.updateStat('successRate', successRate);
                    }
                }
            } else {
                // No active batch
                this.currentBatch = null;
                this.stopProgressMonitoring();
                this.hideBatchProgress();
            }
        } catch (error) {
            console.warn('Batch status check failed:', error);
        }
    }

    refresh() {
        this.loadTemplates();
        this.checkBatchStatus();
    }

    // Get current batch info
    getCurrentBatch() {
        return this.currentBatch;
    }

    // Cancel current batch (if API supports it)
    async cancelBatch() {
        if (!this.currentBatch) return;

        try {
            // Implementation would depend on API support
            Notifications.warning('Cancelamento de lote não implementado');
        } catch (error) {
            ErrorHandler.handle(error, 'Batch cancellation');
        }
    }
}

// Global function for validation button
function validateBilling() {
    if (window.Billing) {
        window.Billing.validateBilling();
    }
}

// Export for global access
window.BillingModule = BillingModule;

