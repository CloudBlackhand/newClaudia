// Templates module

class TemplatesModule {
    constructor() {
        this.templates = {};
        this.currentTemplate = null;
    }

    init() {
        this.setupEventListeners();
        this.loadTemplates();
    }

    setupEventListeners() {
        // Template form
        const templateForm = document.getElementById('templateForm');
        if (templateForm) {
            templateForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleTemplateSubmit();
            });
        }

        // Template content textarea
        const templateContent = document.getElementById('templateContent');
        if (templateContent) {
            templateContent.addEventListener('input', (e) => {
                this.validateTemplate(e.target.value);
            });
        }

        // Template name input
        const templateName = document.getElementById('templateName');
        if (templateName) {
            templateName.addEventListener('input', (e) => {
                this.validateTemplateName(e.target.value);
            });
        }
    }

    async loadTemplates() {
        try {
            const result = await API.getTemplates();
            
            if (result.success) {
                this.templates = result.data;
                this.renderTemplatesList();
            } else {
                Notifications.error('Erro ao carregar templates');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'Template loading');
            this.loadDefaultTemplates();
        }
    }

    loadDefaultTemplates() {
        // Default templates for offline/error scenarios
        this.templates = {
            "cobranca_simples": {
                content: "Olá {name}! 👋\n\nEste é um lembrete sobre seu pagamento:\n💰 Valor: {amount}\n📅 Vencimento: {due_date}\n\nPara facilitar, responda esta mensagem.\n\nObrigado! 🙏",
                length: 156,
                variables: ["name", "amount", "due_date"],
                valid: true,
                preview: "Olá {name}! 👋\n\nEste é um lembrete sobre seu pagamento..."
            },
            "cobranca_urgente": {
                content: "⚠️ {name}, PAGAMENTO EM ATRASO ⚠️\n\nO pagamento de {amount} venceu em {due_date}.\n\n🔔 Regularize hoje mesmo!\n\nResponda para negociar.",
                length: 142,
                variables: ["name", "amount", "due_date"],
                valid: true,
                preview: "⚠️ {name}, PAGAMENTO EM ATRASO ⚠️..."
            }
        };
        this.renderTemplatesList();
    }

    renderTemplatesList() {
        const templatesList = document.getElementById('templatesList');
        if (!templatesList) return;

        if (Object.keys(this.templates).length === 0) {
            templatesList.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-file-text" style="font-size: 2rem;"></i>
                    <div class="mt-2">Nenhum template criado</div>
                </div>
            `;
            return;
        }

        templatesList.innerHTML = Object.entries(this.templates).map(([name, template]) => {
            const statusIcon = template.valid ? 'bi-check-circle text-success' : 'bi-exclamation-triangle text-warning';
            
            return `
                <div class="template-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="template-name">
                                <i class="bi ${statusIcon} me-2"></i>
                                ${this.formatTemplateName(name)}
                            </div>
                            <div class="template-preview">${Utils.escapeHtml(template.preview || template.content.substring(0, 100) + '...')}</div>
                            <small class="text-muted">
                                ${template.length} caracteres • 
                                Variáveis: ${template.variables ? template.variables.join(', ') : 'nenhuma'}
                            </small>
                        </div>
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu">
                                <li><a class="dropdown-item" href="#" onclick="Templates.editTemplate('${name}')">
                                    <i class="bi bi-pencil"></i> Editar
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="Templates.previewTemplate('${name}')">
                                    <i class="bi bi-eye"></i> Visualizar
                                </a></li>
                                <li><a class="dropdown-item" href="#" onclick="Templates.copyTemplate('${name}')">
                                    <i class="bi bi-copy"></i> Copiar
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item text-danger" href="#" onclick="Templates.deleteTemplate('${name}')">
                                    <i class="bi bi-trash"></i> Excluir
                                </a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    formatTemplateName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    validateTemplateName(name) {
        const nameInput = document.getElementById('templateName');
        const errors = [];

        if (!name || name.trim().length === 0) {
            errors.push('Nome é obrigatório');
        } else if (name.length > CONFIG.VALIDATION.MAX_TEMPLATE_NAME_LENGTH) {
            errors.push(`Nome muito longo (máximo ${CONFIG.VALIDATION.MAX_TEMPLATE_NAME_LENGTH} caracteres)`);
        } else if (!/^[a-zA-Z0-9_\-\s]+$/.test(name)) {
            errors.push('Nome pode conter apenas letras, números, espaços, hífens e sublinhados');
        } else if (this.templates[name.toLowerCase().replace(/\s/g, '_')] && !this.currentTemplate) {
            errors.push('Já existe um template com este nome');
        }

        this.showFieldValidation(nameInput, errors);
        return errors.length === 0;
    }

    validateTemplate(content) {
        const contentTextarea = document.getElementById('templateContent');
        const errors = [];

        if (!content || content.trim().length === 0) {
            errors.push('Conteúdo é obrigatório');
        } else if (content.length > CONFIG.VALIDATION.MAX_MESSAGE_LENGTH) {
            errors.push(`Mensagem muito longa (máximo ${CONFIG.VALIDATION.MAX_MESSAGE_LENGTH} caracteres)`);
        }

        // Check for required variables
        const requiredVars = ['name', 'amount'];
        const foundVars = (content.match(/\{(\w+)\}/g) || []).map(v => v.slice(1, -1));
        const missingVars = requiredVars.filter(v => !foundVars.includes(v));

        if (missingVars.length > 0) {
            errors.push(`Variáveis obrigatórias ausentes: ${missingVars.join(', ')}`);
        }

        this.showFieldValidation(contentTextarea, errors);
        this.updateTemplatePreview(content, foundVars);
        
        return errors.length === 0;
    }

    showFieldValidation(field, errors) {
        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        // Remove existing feedback
        const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }

        if (errors.length > 0) {
            field.classList.add('is-invalid');
            
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.innerHTML = errors.map(error => `<div>${error}</div>`).join('');
            field.parentNode.appendChild(feedback);
        } else if (field.value.trim()) {
            field.classList.add('is-valid');
        }
    }

    updateTemplatePreview(content, variables) {
        const previewDiv = document.getElementById('templatePreview');
        if (!previewDiv) return;

        if (!content.trim()) {
            previewDiv.innerHTML = '';
            return;
        }

        // Create preview with sample data
        const sampleData = {
            name: 'João Silva',
            amount: 'R$ 150,50',
            due_date: '15/01/2024',
            phone: '+55 11 98765-4321',
            description: 'Mensalidade janeiro',
            current_date: new Date().toLocaleDateString('pt-BR'),
            current_time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        };

        let preview = content;
        Object.entries(sampleData).forEach(([key, value]) => {
            preview = preview.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
        });

        previewDiv.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <small><i class="bi bi-eye"></i> Pré-visualização</small>
                </div>
                <div class="card-body">
                    <div class="message-preview">
                        ${Utils.escapeHtml(preview).replace(/\n/g, '<br>')}
                    </div>
                    <small class="text-muted mt-2 d-block">
                        ${content.length} caracteres • Variáveis: ${variables.length > 0 ? variables.join(', ') : 'nenhuma'}
                    </small>
                </div>
            </div>
        `;
    }

    async handleTemplateSubmit() {
        const nameInput = document.getElementById('templateName');
        const contentTextarea = document.getElementById('templateContent');
        
        const name = nameInput.value.trim();
        const content = contentTextarea.value.trim();

        // Validate inputs
        const nameValid = this.validateTemplateName(name);
        const contentValid = this.validateTemplate(content);

        if (!nameValid || !contentValid) {
            Notifications.error('Por favor, corrija os erros antes de salvar');
            return;
        }

        const submitBtn = document.querySelector('#templateForm button[type="submit"]');
        const loaderId = Loading.show(submitBtn, 'Salvando...');

        try {
            const templateKey = name.toLowerCase().replace(/\s/g, '_');
            const result = await API.addTemplate(templateKey, content);
            
            if (result.success) {
                Notifications.success('Template salvo com sucesso!');
                
                // Add to local templates
                this.templates[templateKey] = {
                    content: content,
                    length: content.length,
                    variables: (content.match(/\{(\w+)\}/g) || []).map(v => v.slice(1, -1)),
                    valid: true,
                    preview: content.substring(0, 100) + (content.length > 100 ? '...' : '')
                };
                
                this.renderTemplatesList();
                this.clearForm();
                
            } else {
                Notifications.error(result.error || 'Erro ao salvar template');
            }
        } catch (error) {
            ErrorHandler.handle(error, 'Template save');
        } finally {
            Loading.hide(submitBtn);
        }
    }

    clearForm() {
        document.getElementById('templateName').value = '';
        document.getElementById('templateContent').value = '';
        
        // Clear validation states
        ['templateName', 'templateContent'].forEach(id => {
            const field = document.getElementById(id);
            field.classList.remove('is-valid', 'is-invalid');
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback) feedback.remove();
        });

        // Clear preview
        const previewDiv = document.getElementById('templatePreview');
        if (previewDiv) previewDiv.innerHTML = '';

        this.currentTemplate = null;
    }

    editTemplate(templateName) {
        const template = this.templates[templateName];
        if (!template) return;

        this.currentTemplate = templateName;
        
        document.getElementById('templateName').value = this.formatTemplateName(templateName);
        document.getElementById('templateContent').value = template.content;
        
        // Update button text
        const submitBtn = document.querySelector('#templateForm button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="bi bi-save"></i> Atualizar Template';
        }

        // Validate and preview
        this.validateTemplateName(this.formatTemplateName(templateName));
        this.validateTemplate(template.content);
        
        Notifications.info(`Editando template: ${this.formatTemplateName(templateName)}`);
    }

    async deleteTemplate(templateName) {
        if (!confirm(`Tem certeza que deseja excluir o template "${this.formatTemplateName(templateName)}"?`)) {
            return;
        }

        try {
            // In a real implementation, you'd call API to delete
            // For now, just remove from local storage
            delete this.templates[templateName];
            this.renderTemplatesList();
            
            Notifications.success('Template excluído com sucesso');
        } catch (error) {
            ErrorHandler.handle(error, 'Template deletion');
        }
    }

    previewTemplate(templateName) {
        const template = this.templates[templateName];
        if (!template) return;

        // Create modal for preview
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Preview: ${this.formatTemplateName(templateName)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="message-preview mb-3">
                            ${Utils.escapeHtml(template.content).replace(/\n/g, '<br>')}
                        </div>
                        <hr>
                        <small class="text-muted">
                            <strong>Informações:</strong><br>
                            • Tamanho: ${template.length} caracteres<br>
                            • Variáveis: ${template.variables ? template.variables.join(', ') : 'nenhuma'}<br>
                            • Status: ${template.valid ? 'Válido' : 'Inválido'}
                        </small>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                        <button type="button" class="btn btn-primary" onclick="Templates.editTemplate('${templateName}')" data-bs-dismiss="modal">
                            <i class="bi bi-pencil"></i> Editar
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    async copyTemplate(templateName) {
        const template = this.templates[templateName];
        if (!template) return;

        const success = await Utils.copyToClipboard(template.content);
        if (success) {
            Notifications.success('Template copiado para a área de transferência');
        } else {
            Notifications.error('Erro ao copiar template');
        }
    }

    // Import templates from file
    async importTemplates(file) {
        try {
            const content = await file.text();
            const importedTemplates = JSON.parse(content);
            
            let importCount = 0;
            Object.entries(importedTemplates).forEach(([name, template]) => {
                if (typeof template === 'string') {
                    // Simple format: name -> content
                    this.templates[name] = {
                        content: template,
                        length: template.length,
                        variables: (template.match(/\{(\w+)\}/g) || []).map(v => v.slice(1, -1)),
                        valid: true,
                        preview: template.substring(0, 100) + (template.length > 100 ? '...' : '')
                    };
                    importCount++;
                } else if (template.content) {
                    // Full format with metadata
                    this.templates[name] = template;
                    importCount++;
                }
            });
            
            this.renderTemplatesList();
            Notifications.success(`${importCount} templates importados com sucesso`);
            
        } catch (error) {
            Notifications.error('Erro ao importar templates: arquivo inválido');
        }
    }

    // Export templates to file
    exportTemplates() {
        const exportData = {};
        Object.entries(this.templates).forEach(([name, template]) => {
            exportData[name] = template.content;
        });

        Utils.downloadJSON(exportData, `templates_${new Date().toISOString().split('T')[0]}.json`);
        Notifications.success('Templates exportados com sucesso');
    }

    refresh() {
        this.loadTemplates();
    }

    getTemplateNames() {
        return Object.keys(this.templates);
    }

    getTemplate(name) {
        return this.templates[name];
    }
}

// Global functions for template actions
function editTemplate(name) {
    if (window.Templates) {
        window.Templates.editTemplate(name);
    }
}

function deleteTemplate(name) {
    if (window.Templates) {
        window.Templates.deleteTemplate(name);
    }
}

function previewTemplate(name) {
    if (window.Templates) {
        window.Templates.previewTemplate(name);
    }
}

function copyTemplate(name) {
    if (window.Templates) {
        window.Templates.copyTemplate(name);
    }
}

// Export for global access
window.TemplatesModule = TemplatesModule;

