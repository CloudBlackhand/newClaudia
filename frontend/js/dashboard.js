// Dashboard module

class DashboardModule {
    constructor() {
        this.updateInterval = null;
        this.stats = {
            totalMessages: 0,
            successRate: 0,
            activeConversations: 0,
            wahaStatus: 'Offline'
        };
    }

    async init() {
        try {
            await this.updateStats();
            await this.loadActivityFeed();
            this.startAutoUpdate();
        } catch (error) {
            ErrorHandler.handle(error, 'Dashboard initialization');
        }
    }

    async updateStats() {
        try {
            // Update system status
            await this.updateSystemStatus();
            
            // Update conversation stats
            await this.updateConversationStats();
            
            // Update batch stats if available
            await this.updateBatchStats();
            
        } catch (error) {
            console.warn('Stats update failed:', error);
        }
    }

    async updateSystemStatus() {
        try {
            // Check Waha status
            const wahaResult = await API.getWahaStatus();
            
            const statusElement = document.getElementById('wahaStatus');
            const statusBadge = document.getElementById('wahaStatusBadge');
            
            if (wahaResult.success) {
                const status = wahaResult.data.status || 'Unknown';
                this.stats.wahaStatus = status;
                
                if (statusElement) {
                    statusElement.textContent = status;
                }
                
                if (statusBadge) {
                    const badgeClass = Utils.getStatusBadgeClass(status, 'WAHA');
                    statusBadge.className = `badge bg-${badgeClass}`;
                    statusBadge.textContent = status;
                }
            } else {
                this.stats.wahaStatus = 'Offline';
                if (statusElement) {
                    statusElement.textContent = 'Offline';
                }
                if (statusBadge) {
                    statusBadge.className = 'badge bg-danger';
                    statusBadge.textContent = 'Offline';
                }
            }
        } catch (error) {
            console.warn('Waha status update failed:', error);
        }
    }

    async updateConversationStats() {
        try {
            const result = await API.getConversationsStats();
            
            if (result.success) {
                const stats = result.data;
                this.stats.activeConversations = stats.total_conversations || 0;
                
                const activeConversationsElement = document.getElementById('activeConversations');
                if (activeConversationsElement) {
                    activeConversationsElement.textContent = this.stats.activeConversations;
                }
            }
        } catch (error) {
            console.warn('Conversation stats update failed:', error);
        }
    }

    async updateBatchStats() {
        try {
            const result = await API.getBatchStatus();
            
            if (result.success) {
                const batchData = result.data;
                
                // Update total messages (from current batch)
                this.stats.totalMessages = batchData.processed || 0;
                
                // Calculate success rate
                if (batchData.processed > 0) {
                    this.stats.successRate = Math.round(
                        (batchData.successful / batchData.processed) * 100
                    );
                }
                
                // Update UI elements
                const totalMessagesElement = document.getElementById('totalMessages');
                const successRateElement = document.getElementById('successRate');
                
                if (totalMessagesElement) {
                    totalMessagesElement.textContent = this.stats.totalMessages;
                }
                
                if (successRateElement) {
                    successRateElement.textContent = `${this.stats.successRate}%`;
                }
            }
        } catch (error) {
            // Batch status might not be available - this is normal
            console.debug('No active batch found');
        }
    }

    async loadActivityFeed() {
        const activityFeed = document.getElementById('activityFeed');
        if (!activityFeed) return;

        // Mock activity data - in real implementation, this would come from API
        const activities = [
            {
                icon: 'bi-envelope-check',
                iconClass: 'bg-success',
                title: 'Lote de cobrança enviado',
                description: '150 mensagens enviadas com sucesso',
                time: new Date(Date.now() - 5 * 60 * 1000).toISOString()
            },
            {
                icon: 'bi-chat-dots',
                iconClass: 'bg-info',
                title: 'Nova conversa iniciada',
                description: 'Cliente respondeu sobre pagamento',
                time: new Date(Date.now() - 15 * 60 * 1000).toISOString()
            },
            {
                icon: 'bi-check-circle',
                iconClass: 'bg-success',
                title: 'Pagamento confirmado',
                description: 'Cliente confirmou pagamento via bot',
                time: new Date(Date.now() - 30 * 60 * 1000).toISOString()
            },
            {
                icon: 'bi-upload',
                iconClass: 'bg-primary',
                title: 'Arquivo carregado',
                description: 'clients_20240115.json processado',
                time: new Date(Date.now() - 60 * 60 * 1000).toISOString()
            },
            {
                icon: 'bi-gear',
                iconClass: 'bg-warning',
                title: 'Template atualizado',
                description: 'Template "cobranca_urgente" modificado',
                time: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            }
        ];

        activityFeed.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.iconClass}">
                    <i class="bi ${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div><strong>${activity.title}</strong></div>
                    <div class="text-muted">${activity.description}</div>
                    <small class="activity-time">${Utils.formatRelativeTime(activity.time)}</small>
                </div>
            </div>
        `).join('');
    }

    startAutoUpdate() {
        // Update every 30 seconds
        this.updateInterval = setInterval(async () => {
            if (!document.hidden && app.getCurrentSection() === 'dashboard') {
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
        this.updateStats();
        this.loadActivityFeed();
    }

    // Add activity to feed (for real-time updates)
    addActivity(activity) {
        const activityFeed = document.getElementById('activityFeed');
        if (!activityFeed) return;

        const activityHtml = `
            <div class="activity-item fade-in">
                <div class="activity-icon ${activity.iconClass}">
                    <i class="bi ${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <div><strong>${activity.title}</strong></div>
                    <div class="text-muted">${activity.description}</div>
                    <small class="activity-time">Agora</small>
                </div>
            </div>
        `;

        activityFeed.insertAdjacentHTML('afterbegin', activityHtml);

        // Remove old activities (keep max 10)
        const activities = activityFeed.querySelectorAll('.activity-item');
        if (activities.length > 10) {
            activities[activities.length - 1].remove();
        }
    }

    // Update stats manually (for external calls)
    updateStat(statName, value) {
        if (statName in this.stats) {
            this.stats[statName] = value;
            
            const element = document.getElementById(statName);
            if (element) {
                if (statName === 'successRate') {
                    element.textContent = `${value}%`;
                } else {
                    element.textContent = value;
                }
            }
        }
    }

    getStats() {
        return { ...this.stats };
    }
}

// Export for global access
window.DashboardModule = DashboardModule;

