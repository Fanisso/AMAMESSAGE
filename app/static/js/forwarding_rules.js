// Variáveis globais
let currentRules = [];
let contactGroups = [];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    loadForwardingRules();
    loadContactGroups();
    loadStats();
});

// Carregar regras de reencaminhamento
async function loadForwardingRules() {
    try {
        showLoading('rules-container');
        
        const response = await fetch('/api/forwarding/rules');
        const rules = await response.json();
        
        if (response.ok) {
            currentRules = rules;
            renderRules(rules);
        } else {
            showError('Erro ao carregar regras: ' + rules.message);
        }
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

// Renderizar lista de regras
function renderRules(rules) {
    const container = document.getElementById('rules-container');
    
    if (rules.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-route fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">Nenhuma regra configurada</h5>
                <p class="text-muted">Clique em "Nova Regra" para começar</p>
            </div>
        `;
        return;
    }
    
    const rulesHtml = rules.map(rule => `
        <div class="rule-card card mb-3 ${rule.is_active ? 'active' : 'inactive'}">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center mb-2">
                            <h6 class="mb-0 me-3">${rule.name}</h6>
                            <span class="badge bg-primary rule-type-badge me-2">${getRuleTypeLabel(rule.rule_type)}</span>
                            <span class="badge bg-${getActionColor(rule.action)} rule-type-badge me-2">${getActionLabel(rule.action)}</span>
                            <span class="badge bg-${rule.is_active ? 'success' : 'secondary'} rule-type-badge">
                                ${rule.is_active ? 'Ativa' : 'Inativa'}
                            </span>
                            ${rule.priority > 0 ? `<span class="badge bg-info rule-type-badge ms-2">P${rule.priority}</span>` : ''}
                        </div>
                        
                        ${rule.description ? `<p class="text-muted mb-2">${rule.description}</p>` : ''}
                        
                        <div class="small text-muted">
                            ${getRuleCriteria(rule)}
                            ${rule.match_count > 0 ? `• <strong>${rule.match_count}</strong> correspondências` : ''}
                            ${rule.last_match_at ? `• Última: ${formatDate(rule.last_match_at)}` : ''}
                        </div>
                    </div>
                    
                    <div class="col-md-4 text-end">
                        <div class="btn-group" role="group">
                            <button class="btn btn-sm btn-outline-primary" onclick="editRule(${rule.id})" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-${rule.is_active ? 'warning' : 'success'}" 
                                    onclick="toggleRule(${rule.id})" 
                                    title="${rule.is_active ? 'Desativar' : 'Ativar'}">
                                <i class="fas fa-${rule.is_active ? 'pause' : 'play'}"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="showRuleLogs(${rule.id})" title="Histórico">
                                <i class="fas fa-history"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteRule(${rule.id})" title="Deletar">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = rulesHtml;
}

// Obter critérios da regra para exibição
function getRuleCriteria(rule) {
    let criteria = [];
    
    if (rule.sender_pattern) {
        criteria.push(`Remetente: ${rule.sender_pattern}`);
    }
    if (rule.recipient_pattern) {
        criteria.push(`Destinatário: ${rule.recipient_pattern}`);
    }
    if (rule.keyword_pattern) {
        criteria.push(`Palavras: ${rule.keyword_pattern}`);
    }
    
    return criteria.join(' • ');
}

// Labels para tipos de regra
function getRuleTypeLabel(type) {
    const labels = {
        'sender_based': 'Por Remetente',
        'keyword_based': 'Por Palavra-chave',
        'recipient_based': 'Por Destinatário',
        'block_sender': 'Bloquear Remetente',
        'block_keyword': 'Bloquear Palavra-chave'
    };
    return labels[type] || type;
}

// Labels para ações
function getActionLabel(action) {
    const labels = {
        'forward': 'Reencaminhar',
        'block': 'Bloquear',
        'delete': 'Deletar'
    };
    return labels[action] || action;
}

// Cores para ações
function getActionColor(action) {
    const colors = {
        'forward': 'success',
        'block': 'warning',
        'delete': 'danger'
    };
    return colors[action] || 'secondary';
}

// Carregar grupos de contatos
async function loadContactGroups() {
    try {
        const response = await fetch('/api/contacts/groups');
        if (response.ok) {
            contactGroups = await response.json();
            updateGroupSelect();
        }
    } catch (error) {
        console.error('Erro ao carregar grupos:', error);
    }
}

// Atualizar select de grupos
function updateGroupSelect() {
    const select = document.getElementById('forward-group');
    const groupOptions = contactGroups.map(group => 
        `<option value="${group.id}">${group.name} (${group.member_count || 0} membros)</option>`
    ).join('');
    
    select.innerHTML = '<option value="">Selecione um grupo (opcional)</option>' + groupOptions;
}

// Carregar estatísticas
async function loadStats() {
    try {
        const response = await fetch('/api/forwarding/stats');
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('total-rules').textContent = stats.total_rules;
            document.getElementById('active-rules').textContent = stats.active_rules;
            document.getElementById('forwarded-count').textContent = stats.forwarded_messages;
            document.getElementById('blocked-count').textContent = stats.blocked_messages;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Atualizar campos do formulário baseado no tipo
function updateRuleFields() {
    const type = document.getElementById('rule-type').value;
    
    // Ocultar todos os campos
    document.getElementById('sender-field').style.display = 'none';
    document.getElementById('recipient-field').style.display = 'none';
    document.getElementById('keyword-field').style.display = 'none';
    
    // Mostrar campos relevantes
    if (type === 'sender_based' || type === 'block_sender') {
        document.getElementById('sender-field').style.display = 'block';
    } else if (type === 'recipient_based') {
        document.getElementById('recipient-field').style.display = 'block';
    } else if (type === 'keyword_based' || type === 'block_keyword') {
        document.getElementById('keyword-field').style.display = 'block';
    }
    
    // Atualizar ações disponíveis
    updateAvailableActions(type);
}

// Atualizar ações disponíveis baseado no tipo
function updateAvailableActions(type) {
    const actionSelect = document.getElementById('rule-action');
    let options = '';
    
    if (type.startsWith('block_')) {
        options = `
            <option value="">Selecione a ação</option>
            <option value="block">Bloquear</option>
            <option value="delete">Deletar</option>
        `;
    } else {
        options = `
            <option value="">Selecione a ação</option>
            <option value="forward">Reencaminhar</option>
            <option value="block">Bloquear</option>
            <option value="delete">Deletar</option>
        `;
    }
    
    actionSelect.innerHTML = options;
}

// Atualizar campos baseado na ação
function updateActionFields() {
    const action = document.getElementById('rule-action').value;
    const forwardFields = document.getElementById('forward-fields');
    
    if (action === 'forward') {
        forwardFields.style.display = 'block';
    } else {
        forwardFields.style.display = 'none';
    }
}

// Adicionar campo de número
function addForwardNumber() {
    const container = document.getElementById('forward-numbers');
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="text" class="form-control" placeholder="+55 11 99999-9999">
        <button class="btn btn-outline-danger" type="button" onclick="removeForwardNumber(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(div);
}

// Remover campo de número
function removeForwardNumber(button) {
    button.closest('.input-group').remove();
}

// Salvar regra
async function saveRule() {
    try {
        const ruleData = {
            name: document.getElementById('rule-name').value,
            description: document.getElementById('rule-description').value,
            rule_type: document.getElementById('rule-type').value,
            action: document.getElementById('rule-action').value,
            is_active: document.getElementById('rule-active').checked,
            priority: parseInt(document.getElementById('rule-priority').value) || 0,
            case_sensitive: document.getElementById('case-sensitive').checked,
            whole_word_only: document.getElementById('whole-word').checked
        };
        
        // Critérios
        const senderPattern = document.getElementById('sender-pattern').value;
        const recipientPattern = document.getElementById('recipient-pattern').value;
        const keywordPattern = document.getElementById('keyword-pattern').value;
        
        if (senderPattern) ruleData.sender_pattern = senderPattern;
        if (recipientPattern) ruleData.recipient_pattern = recipientPattern;
        if (keywordPattern) ruleData.keyword_pattern = keywordPattern;
        
        // Destinos de reencaminhamento
        if (ruleData.action === 'forward') {
            const numberInputs = document.querySelectorAll('#forward-numbers input');
            const numbers = Array.from(numberInputs)
                .map(input => input.value.trim())
                .filter(value => value);
            
            if (numbers.length > 0) {
                ruleData.forward_to_numbers = numbers;
            }
            
            const groupId = document.getElementById('forward-group').value;
            if (groupId) {
                ruleData.forward_to_group_id = parseInt(groupId);
            }
        }
        
        // Validação
        if (!ruleData.name || !ruleData.rule_type || !ruleData.action) {
            showError('Preencha todos os campos obrigatórios');
            return;
        }
        
        const ruleId = document.getElementById('rule-id').value;
        const url = ruleId ? `/api/forwarding/rules/${ruleId}` : '/api/forwarding/rules';
        const method = ruleId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(ruleData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(ruleId ? 'Regra atualizada com sucesso!' : 'Regra criada com sucesso!');
            bootstrap.Modal.getInstance(document.getElementById('ruleModal')).hide();
            loadForwardingRules();
            loadStats();
        } else {
            showError('Erro ao salvar regra: ' + result.detail);
        }
        
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

// Editar regra
function editRule(ruleId) {
    const rule = currentRules.find(r => r.id === ruleId);
    if (!rule) return;
    
    // Preencher formulário
    document.getElementById('rule-id').value = rule.id;
    document.getElementById('rule-name').value = rule.name;
    document.getElementById('rule-description').value = rule.description || '';
    document.getElementById('rule-type').value = rule.rule_type;
    document.getElementById('rule-action').value = rule.action;
    document.getElementById('rule-active').checked = rule.is_active;
    document.getElementById('rule-priority').value = rule.priority;
    document.getElementById('case-sensitive').checked = rule.case_sensitive;
    document.getElementById('whole-word').checked = rule.whole_word_only;
    
    // Preencher critérios
    if (rule.sender_pattern) {
        document.getElementById('sender-pattern').value = rule.sender_pattern;
    }
    if (rule.recipient_pattern) {
        document.getElementById('recipient-pattern').value = rule.recipient_pattern;
    }
    if (rule.keyword_pattern) {
        document.getElementById('keyword-pattern').value = rule.keyword_pattern;
    }
    
    // Preencher destinos de reencaminhamento
    if (rule.forward_to_numbers) {
        const numbers = JSON.parse(rule.forward_to_numbers);
        const container = document.getElementById('forward-numbers');
        container.innerHTML = '';
        
        numbers.forEach(number => {
            const div = document.createElement('div');
            div.className = 'input-group mb-2';
            div.innerHTML = `
                <input type="text" class="form-control" value="${number}">
                <button class="btn btn-outline-danger" type="button" onclick="removeForwardNumber(this)">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(div);
        });
    }
    
    if (rule.forward_to_group_id) {
        document.getElementById('forward-group').value = rule.forward_to_group_id;
    }
    
    // Atualizar campos
    updateRuleFields();
    updateActionFields();
    
    // Atualizar título do modal
    document.getElementById('modal-title').textContent = 'Editar Regra';
    
    // Mostrar modal
    new bootstrap.Modal(document.getElementById('ruleModal')).show();
}

// Alternar status da regra
async function toggleRule(ruleId) {
    try {
        const response = await fetch(`/api/forwarding/rules/${ruleId}/toggle`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showSuccess('Status da regra alterado com sucesso!');
            loadForwardingRules();
            loadStats();
        } else {
            const error = await response.json();
            showError('Erro ao alterar status: ' + error.detail);
        }
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

// Deletar regra
async function deleteRule(ruleId) {
    if (!confirm('Tem certeza que deseja deletar esta regra? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/forwarding/rules/${ruleId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showSuccess('Regra deletada com sucesso!');
            loadForwardingRules();
            loadStats();
        } else {
            const error = await response.json();
            showError('Erro ao deletar regra: ' + error.detail);
        }
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

// Mostrar logs da regra
async function showRuleLogs(ruleId) {
    try {
        const response = await fetch(`/api/forwarding/logs?rule_id=${ruleId}`);
        const logs = await response.json();
        
        if (response.ok) {
            renderLogs(logs);
            new bootstrap.Modal(document.getElementById('logsModal')).show();
        } else {
            showError('Erro ao carregar logs: ' + logs.message);
        }
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

// Renderizar logs
function renderLogs(logs) {
    const container = document.getElementById('logs-container');
    
    if (logs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-history fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">Nenhum log encontrado</h5>
                <p class="text-muted">Esta regra ainda não foi aplicada</p>
            </div>
        `;
        return;
    }
    
    const logsHtml = logs.map(log => `
        <div class="card mb-2">
            <div class="card-body py-2">
                <div class="row align-items-center">
                    <div class="col-md-2">
                        <span class="badge bg-${getActionColor(log.action_taken)}">${getActionLabel(log.action_taken)}</span>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">${formatDate(log.applied_at)}</small>
                    </div>
                    <div class="col-md-3">
                        <small>De: ${log.original_sender || 'N/A'}</small>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted">${log.matched_criteria || 'N/A'}</small>
                    </div>
                </div>
                ${log.original_message ? `
                    <div class="mt-2">
                        <small class="text-muted">Mensagem: ${log.original_message.substring(0, 100)}${log.original_message.length > 100 ? '...' : ''}</small>
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = logsHtml;
}

// Testar regras
function showTestPanel() {
    document.getElementById('test-panel').style.display = 'block';
    document.getElementById('test-sender').focus();
}

function hideTestPanel() {
    document.getElementById('test-panel').style.display = 'none';
    document.getElementById('test-results').style.display = 'none';
}

async function testRules() {
    const sender = document.getElementById('test-sender').value;
    const recipient = document.getElementById('test-recipient').value;
    const message = document.getElementById('test-message').value;
    
    if (!sender || !recipient || !message) {
        showError('Preencha todos os campos do teste');
        return;
    }
    
    try {
        const response = await fetch('/api/forwarding/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_sender: sender,
                test_recipient: recipient,
                test_message: message
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            renderTestResults(result);
        } else {
            showError('Erro no teste: ' + result.detail);
        }
    } catch (error) {
        showError('Erro de conexão: ' + error.message);
    }
}

function renderTestResults(result) {
    const container = document.getElementById('test-results');
    const data = result.data;
    
    let html = `
        <div class="alert alert-info">
            <h6><i class="fas fa-info-circle me-2"></i>${result.message}</h6>
        </div>
    `;
    
    if (data.matched_rules.length > 0) {
        html += `
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Regra</th>
                            <th>Tipo</th>
                            <th>Ação</th>
                            <th>Prioridade</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        data.matched_rules.forEach(rule => {
            html += `
                <tr>
                    <td>${rule.rule_name}</td>
                    <td><span class="badge bg-primary">${getRuleTypeLabel(rule.rule_type)}</span></td>
                    <td><span class="badge bg-${getActionColor(rule.action)}">${getActionLabel(rule.action)}</span></td>
                    <td>${rule.priority}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
    }
    
    container.innerHTML = html;
    container.style.display = 'block';
}

// Limpar filtros
function clearFilters() {
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-action').value = '';
    document.getElementById('filter-status').value = '';
    loadForwardingRules();
}

// Limpar formulário
function clearForm() {
    document.getElementById('rule-form').reset();
    document.getElementById('rule-id').value = '';
    document.getElementById('modal-title').textContent = 'Nova Regra';
    
    // Limpar números de reencaminhamento
    const container = document.getElementById('forward-numbers');
    container.innerHTML = `
        <div class="input-group mb-2">
            <input type="text" class="form-control" placeholder="+55 11 99999-9999">
            <button class="btn btn-outline-danger" type="button" onclick="removeForwardNumber(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Ocultar campos
    updateRuleFields();
    updateActionFields();
}

// Event listener para limpar formulário ao fechar modal
document.getElementById('ruleModal').addEventListener('hidden.bs.modal', clearForm);

// Funções auxiliares
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `;
}

function showError(message) {
    // Implementar toast ou alert
    alert('Erro: ' + message);
}

function showSuccess(message) {
    // Implementar toast ou alert
    alert('Sucesso: ' + message);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString('pt-BR');
}
