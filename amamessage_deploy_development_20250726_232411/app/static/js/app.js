// AMA MESSAGE - Main JavaScript file

// Global variables
let alertTimeout;

// Utility functions
function showAlert(message, type = 'info', duration = 5000) {
    // Clear existing timeout
    if (alertTimeout) {
        clearTimeout(alertTimeout);
    }
    
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-floating');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-floating`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertDiv);
    
    // Auto-remove after duration
    if (duration > 0) {
        alertTimeout = setTimeout(() => {
            if (alertDiv && alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
}

// Phone number formatting
function formatPhoneNumber(phone) {
    // Remove all non-digit characters except +
    let cleaned = phone.replace(/[^\d+]/g, '');
    
    // If doesn't start with +, add +55 for Brazil
    if (!cleaned.startsWith('+')) {
        if (cleaned.length === 11 && (cleaned.startsWith('11') || cleaned.startsWith('21'))) {
            cleaned = '+55' + cleaned;
        } else if (cleaned.length === 10) {
            cleaned = '+55' + cleaned;
        }
    }
    
    return cleaned;
}

// Validate phone number
function validatePhoneNumber(phone) {
    const phoneRegex = /^\+\d{10,15}$/;
    return phoneRegex.test(phone);
}

// Format message for display
function formatMessage(message, maxLength = 50) {
    if (message.length <= maxLength) {
        return message;
    }
    return message.substring(0, maxLength) + '...';
}

// Format date/time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format relative time
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Agora mesmo';
    if (diffMins < 60) return `${diffMins} min atrás`;
    if (diffHours < 24) return `${diffHours}h atrás`;
    if (diffDays < 7) return `${diffDays} dias atrás`;
    
    return formatDateTime(dateString);
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Erro na requisição');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Loading states
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="loading-spinner me-2"></span>Carregando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

// Form validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Status badge helper
function getStatusBadge(status) {
    const statusMap = {
        'pending': { class: 'bg-warning', text: 'Pendente', icon: 'clock' },
        'sent': { class: 'bg-info', text: 'Enviado', icon: 'paper-plane' },
        'delivered': { class: 'bg-success', text: 'Entregue', icon: 'check-circle' },
        'failed': { class: 'bg-danger', text: 'Falhou', icon: 'exclamation-circle' },
        'received': { class: 'bg-primary', text: 'Recebido', icon: 'inbox' }
    };
    
    const config = statusMap[status] || { class: 'bg-secondary', text: status, icon: 'question' };
    
    return `<span class="badge ${config.class}">
        <i class="fas fa-${config.icon} me-1"></i>
        ${config.text}
    </span>`;
}

// Direction icon helper
function getDirectionIcon(direction) {
    if (direction === 'inbound') {
        return '<i class="fas fa-arrow-down text-success" title="Recebido"></i>';
    } else {
        return '<i class="fas fa-arrow-up text-primary" title="Enviado"></i>';
    }
}

// Auto-refresh functionality
class AutoRefresh {
    constructor(callback, interval = 30000) {
        this.callback = callback;
        this.interval = interval;
        this.timeoutId = null;
        this.isActive = false;
    }
    
    start() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.scheduleNext();
    }
    
    stop() {
        this.isActive = false;
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
    }
    
    scheduleNext() {
        if (!this.isActive) return;
        
        this.timeoutId = setTimeout(() => {
            if (this.isActive) {
                this.callback();
                this.scheduleNext();
            }
        }, this.interval);
    }
}

// Clipboard helper
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copiado para a área de transferência!', 'success', 2000);
        }).catch(() => {
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('Copiado para a área de transferência!', 'success', 2000);
    } catch (err) {
        showAlert('Erro ao copiar texto', 'danger');
    }
    
    document.body.removeChild(textArea);
}

// Initialize tooltips and popovers
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Page visibility API for pausing refresh when tab is not visible
function handleVisibilityChange(autoRefresh) {
    if (document.hidden) {
        autoRefresh.stop();
    } else {
        autoRefresh.start();
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initializeTooltips();
    
    // Initialize auto-refresh for pages that need it
    if (window.pageAutoRefresh && typeof window.pageAutoRefresh === 'function') {
        const autoRefresh = new AutoRefresh(window.pageAutoRefresh, 30000);
        autoRefresh.start();
        
        // Pause refresh when page is not visible
        document.addEventListener('visibilitychange', () => {
            handleVisibilityChange(autoRefresh);
        });
    }
    
    // Handle form submissions with loading states
    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                setButtonLoading(submitBtn, true);
            }
        });
    });
    
    // Auto-format phone inputs
    document.querySelectorAll('input[type="tel"], input[data-phone]').forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = formatPhoneNumber(this.value);
            }
        });
    });
});

// Export functions for global use
window.AmaMessage = {
    showAlert,
    formatPhoneNumber,
    validatePhoneNumber,
    formatMessage,
    formatDateTime,
    formatRelativeTime,
    apiRequest,
    setButtonLoading,
    validateForm,
    getStatusBadge,
    getDirectionIcon,
    AutoRefresh,
    copyToClipboard
};
