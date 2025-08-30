// Conversations module

class ConversationsModule {
    constructor() {
        this.conversations = [];
        this.currentConversation = null;
        this.updateInterval = null;
    }

    init() {
        this.setupEventListeners();
        this.loadConversations();
        this.startAutoUpdate();
    }

    setupEventListeners() {
        // Refresh button if exists
        const refreshBtn = document.getElementById('refreshConversations');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadConversations();
            });
        }
    }

    async loadConversations() {
        try {
            const result = await API.getConversationsStats();
            
            if (result.success) {
                // This is a basic implementation - in a real app, you'd have an API
                // to get the actual list of conversations with their details
                await this.loadMockConversations();
                this.renderConversationsList();
            }
        } catch (error) {
            console.warn('Failed to load conversations:', error);
            this.loadMockConversations();
            this.renderConversationsList();
        }
    }

    async loadMockConversations() {
        // Mock conversations for demonstration
        this.conversations = [
            {
                phone: "5511987654321",
                name: "João Silva",
                lastMessage: "Já fiz o pagamento via PIX",
                lastMessageTime: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
                status: "paid",
                unreadCount: 0,
                messages: [
                    {
                        role: "assistant",
                        content: "Olá João! Este é um lembrete sobre seu pagamento de R$ 150,50 com vencimento em 15/01/2024.",
                        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user", 
                        content: "Oi, posso pagar amanhã?",
                        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString()
                    },
                    {
                        role: "assistant",
                        content: "Claro! Sem problemas. Você pode pagar até amanhã. Quando efetuar o pagamento, me avise por favor.",
                        timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user",
                        content: "Já fiz o pagamento via PIX",
                        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString()
                    }
                ]
            },
            {
                phone: "5511976543210",
                name: "Maria Santos",
                lastMessage: "Quero parcelar em 3x",
                lastMessageTime: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
                status: "negotiating",
                unreadCount: 1,
                messages: [
                    {
                        role: "assistant",
                        content: "Olá Maria! Este é um lembrete sobre seu pagamento de R$ 225,00 com vencimento em 20/01/2024.",
                        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user",
                        content: "Oi, estou com dificuldades financeiras",
                        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "assistant",
                        content: "Entendo sua situação, Maria. Temos opções de parcelamento disponíveis! Para o valor de R$ 225,00, podemos parcelar em até 3x sem juros.",
                        timestamp: new Date(Date.now() - 55 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user",
                        content: "Quero parcelar em 3x",
                        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString()
                    }
                ]
            },
            {
                phone: "5511965432109",
                name: "Carlos Oliveira",
                lastMessage: "Não reconheço essa cobrança",
                lastMessageTime: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
                status: "disputed",
                unreadCount: 2,
                messages: [
                    {
                        role: "assistant",
                        content: "Olá Carlos! Este é um lembrete sobre seu pagamento de R$ 89,90 com vencimento em 10/01/2024.",
                        timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user",
                        content: "Não reconheço essa cobrança",
                        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString()
                    },
                    {
                        role: "assistant",
                        content: "Entendo sua preocupação. Vou transferir você para um atendente humano para resolvermos essa questão.",
                        timestamp: new Date(Date.now() - 40 * 60 * 1000).toISOString()
                    }
                ]
            },
            {
                phone: "5511954321098",
                name: "Ana Costa",
                lastMessage: "Como posso pagar?",
                lastMessageTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
                status: "pending",
                unreadCount: 0,
                messages: [
                    {
                        role: "assistant",
                        content: "Olá Ana! Este é um lembrete sobre seu pagamento de R$ 320,75 com vencimento em 25/01/2024.",
                        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "user",
                        content: "Como posso pagar?",
                        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
                    },
                    {
                        role: "assistant",
                        content: "Você pode pagar através de:\n\n🏦 Transferência bancária\n📱 PIX: empresa@exemplo.com\n💳 Boleto bancário\n\nQual forma prefere?",
                        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000 + 30000).toISOString()
                    }
                ]
            }
        ];
    }

    renderConversationsList() {
        const conversationsList = document.getElementById('conversationsList');
        if (!conversationsList) return;

        if (this.conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="bi bi-chat-dots" style="font-size: 2rem;"></i>
                    <div class="mt-2">Nenhuma conversa ativa</div>
                </div>
            `;
            return;
        }

        conversationsList.innerHTML = this.conversations.map(conversation => {
            const statusBadges = {
                pending: { class: 'secondary', text: 'Pendente' },
                negotiating: { class: 'warning', text: 'Negociando' },
                paid: { class: 'success', text: 'Pago' },
                disputed: { class: 'danger', text: 'Contestado' }
            };

            const badge = statusBadges[conversation.status] || statusBadges.pending;
            const isActive = this.currentConversation && this.currentConversation.phone === conversation.phone;

            return `
                <div class="conversation-item ${isActive ? 'active' : ''}" 
                     onclick="Conversations.selectConversation('${conversation.phone}')">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="conversation-phone">
                                <strong>${conversation.name || Utils.maskPhone(conversation.phone)}</strong>
                                ${conversation.unreadCount > 0 ? `<span class="badge bg-primary ms-2">${conversation.unreadCount}</span>` : ''}
                            </div>
                            <div class="conversation-preview">${Utils.escapeHtml(conversation.lastMessage)}</div>
                            <small class="text-muted">${Utils.formatRelativeTime(conversation.lastMessageTime)}</small>
                        </div>
                        <span class="badge bg-${badge.class}">${badge.text}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    selectConversation(phone) {
        const conversation = this.conversations.find(c => c.phone === phone);
        if (!conversation) return;

        this.currentConversation = conversation;
        
        // Mark as read
        conversation.unreadCount = 0;
        
        this.renderConversationsList();
        this.renderChatMessages();
        this.updateConversationTitle();
    }

    updateConversationTitle() {
        const titleElement = document.getElementById('currentConversationTitle');
        if (!titleElement) return;

        if (this.currentConversation) {
            titleElement.textContent = `${this.currentConversation.name || Utils.maskPhone(this.currentConversation.phone)}`;
        } else {
            titleElement.textContent = 'Selecione uma conversa';
        }
    }

    renderChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        if (!this.currentConversation) {
            chatMessages.innerHTML = `
                <div class="text-center text-muted">
                    Selecione uma conversa para ver o histórico
                </div>
            `;
            return;
        }

        chatMessages.innerHTML = this.currentConversation.messages.map(message => {
            const messageClass = message.role === 'user' ? 'user' : 'assistant';
            
            return `
                <div class="message ${messageClass}">
                    <div class="message-content">
                        ${Utils.escapeHtml(message.content).replace(/\n/g, '<br>')}
                        <div class="message-time">
                            ${Utils.formatDate(message.timestamp)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async updateStats() {
        try {
            const result = await API.getConversationsStats();
            
            if (result.success) {
                // Update any stats displays
                this.displayStats(result.data);
            }
        } catch (error) {
            console.warn('Failed to update conversation stats:', error);
        }
    }

    displayStats(stats) {
        // Update stats in UI if elements exist
        const elements = {
            totalConversations: stats.total_conversations,
            totalMessages: stats.total_messages,
            recentActivity: stats.recent_activity
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value || 0;
            }
        });

        // Update status breakdown
        const statusBreakdown = document.getElementById('conversationStatusBreakdown');
        if (statusBreakdown && stats.conversations_by_status) {
            statusBreakdown.innerHTML = Object.entries(stats.conversations_by_status).map(([status, count]) => {
                const statusLabels = {
                    pending: 'Pendentes',
                    negotiating: 'Negociando', 
                    paid: 'Pagos',
                    disputed: 'Contestados'
                };
                
                return `
                    <div class="d-flex justify-content-between">
                        <span>${statusLabels[status] || status}:</span>
                        <strong>${count}</strong>
                    </div>
                `;
            }).join('');
        }
    }

    startAutoUpdate() {
        // Update conversations every 30 seconds
        this.updateInterval = setInterval(async () => {
            if (!document.hidden && app.getCurrentSection() === 'conversations') {
                await this.loadConversations();
                await this.updateStats();
            }
        }, CONFIG.UI.REFRESH_INTERVAL);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    refresh() {
        this.loadConversations();
        this.updateStats();
    }

    // Filter conversations
    filterConversations(filterType) {
        let filteredConversations = [...this.conversations];

        switch (filterType) {
            case 'unread':
                filteredConversations = this.conversations.filter(c => c.unreadCount > 0);
                break;
            case 'pending':
                filteredConversations = this.conversations.filter(c => c.status === 'pending');
                break;
            case 'negotiating':
                filteredConversations = this.conversations.filter(c => c.status === 'negotiating');
                break;
            case 'disputed':
                filteredConversations = this.conversations.filter(c => c.status === 'disputed');
                break;
            case 'all':
            default:
                // No filter
                break;
        }

        // Temporarily replace conversations for rendering
        const originalConversations = this.conversations;
        this.conversations = filteredConversations;
        this.renderConversationsList();
        this.conversations = originalConversations;
    }

    // Search conversations
    searchConversations(query) {
        if (!query.trim()) {
            this.renderConversationsList();
            return;
        }

        const filteredConversations = this.conversations.filter(c => 
            (c.name && c.name.toLowerCase().includes(query.toLowerCase())) ||
            c.phone.includes(query) ||
            c.lastMessage.toLowerCase().includes(query.toLowerCase())
        );

        // Temporarily replace conversations for rendering
        const originalConversations = this.conversations;
        this.conversations = filteredConversations;
        this.renderConversationsList();
        this.conversations = originalConversations;
    }

    // Export conversation
    exportConversation(phone) {
        const conversation = this.conversations.find(c => c.phone === phone);
        if (!conversation) return;

        const exportData = {
            phone: conversation.phone,
            name: conversation.name,
            status: conversation.status,
            exportedAt: new Date().toISOString(),
            messages: conversation.messages
        };

        Utils.downloadJSON(exportData, `conversa_${conversation.phone}_${new Date().toISOString().split('T')[0]}.json`);
    }

    // Get conversation summary
    getConversationSummary(phone) {
        const conversation = this.conversations.find(c => c.phone === phone);
        if (!conversation) return null;

        return {
            phone: conversation.phone,
            name: conversation.name,
            status: conversation.status,
            totalMessages: conversation.messages.length,
            userMessages: conversation.messages.filter(m => m.role === 'user').length,
            botMessages: conversation.messages.filter(m => m.role === 'assistant').length,
            lastMessageTime: conversation.lastMessageTime,
            duration: this.calculateConversationDuration(conversation.messages)
        };
    }

    calculateConversationDuration(messages) {
        if (messages.length < 2) return 0;

        const firstMessage = new Date(messages[0].timestamp);
        const lastMessage = new Date(messages[messages.length - 1].timestamp);
        
        return Math.round((lastMessage - firstMessage) / 1000 / 60); // minutes
    }
}

// Global function for conversation selection
function selectConversation(phone) {
    if (window.Conversations) {
        window.Conversations.selectConversation(phone);
    }
}

// Export for global access
window.ConversationsModule = ConversationsModule;

