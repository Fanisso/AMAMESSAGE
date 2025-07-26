# Sistema de Regras de Reencaminhamento e Filtragem SMS

## Visão Geral

O sistema de regras de reencaminhamento permite configurar automatização avançada para processamento de SMS, incluindo:

- **Reencaminhamento automático** baseado em critérios específicos
- **Filtragem e bloqueio** de mensagens indesejadas  
- **Remoção automática** de spam e conteúdo ofensivo
- **Regras baseadas em remetente, destinatário ou conteúdo**

## Funcionalidades Principais

### 1. Tipos de Regras

#### 📤 **Por Remetente (`sender_based`)**
- Processa mensagens baseado no número do remetente
- Suporte a wildcards (`*` para qualquer sequência, `?` para um caractere)
- Exemplo: `+55 11 *` (qualquer número de São Paulo)

#### 📥 **Por Destinatário (`recipient_based`)**  
- Processa mensagens baseado no número do destinatário
- Útil para regras de saída (forward de mensagens enviadas)
- Mesmo sistema de wildcards

#### 🔑 **Por Palavra-chave (`keyword_based`)**
- Processa mensagens baseado no conteúdo
- Múltiplas palavras/frases separadas por vírgula
- Opções: sensível a maiúsculas, apenas palavras completas

#### 🚫 **Bloquear Remetente (`block_sender`)**
- Versão otimizada para bloqueio por remetente
- Ações disponíveis: bloquear ou deletar

#### 🚫 **Bloquear Palavra-chave (`block_keyword`)**
- Versão otimizada para bloqueio por conteúdo
- Ações disponíveis: bloquear ou deletar

### 2. Ações Disponíveis

#### ↗️ **Reencaminhar (`forward`)**
- Envia cópia da mensagem para números específicos
- Suporte para grupos de contatos
- Prefixo automático: `[Reencaminhado de {remetente}]`

#### 🛑 **Bloquear (`block`)**
- Impede processamento adicional da mensagem
- Mensagem permanece no banco com flag de bloqueada
- Útil para análise posterior

#### 🗑️ **Deletar (`delete`)**
- Remove completamente a mensagem do sistema
- **Ação irreversível** - use com cuidado
- Ideal para spam e conteúdo ofensivo

### 3. Sistema de Prioridades

- Regras são executadas por **ordem de prioridade** (maior primeiro)
- Prioridade padrão: `0`
- Regras de bloqueio/deleção interrompem processamento posterior
- Múltiplas regras de reencaminhamento podem ser aplicadas

## Exemplos de Uso

### Reencaminhamento por Remetente
```
Nome: "Mensagens do Chefe"
Tipo: Por Remetente
Critério: +55 11 99999-0001
Ação: Reencaminhar
Destinos: ["+55 11 88888-0001"]
Prioridade: 10
```

### Filtragem de Spam
```
Nome: "Bloquear Spam"
Tipo: Bloquear Palavra-chave  
Critério: "promoção, desconto, ganhe dinheiro"
Ação: Deletar
Prioridade: 20
```

### Mensagens Urgentes
```
Nome: "Alertas Urgentes"
Tipo: Por Palavra-chave
Critério: "urgente, emergência, importante"
Ação: Reencaminhar
Destinos: ["+55 11 77777-0001", "+55 11 77777-0002"]
Prioridade: 15
```

### Bloqueio por Número
```
Nome: "Bloquear Telemarketing"
Tipo: Bloquear Remetente
Critério: +55 11 3000-*
Ação: Bloquear
Prioridade: 25
```

## Interface de Administração

### Dashboard Principal
- **Estatísticas em tempo real**: total de regras, regras ativas, mensagens processadas
- **Filtros avançados**: por tipo, ação, status
- **Indicadores visuais**: regras ativas (verde), inativas (cinza)

### Criação/Edição de Regras
- **Formulário intuitivo** com validação em tempo real
- **Campos condicionais** baseados no tipo selecionado
- **Suporte a múltiplos destinos** de reencaminhamento
- **Integração com grupos** de contatos

### Teste de Regras
- **Simulação em tempo real** sem envio de SMS
- **Preview das regras** que seriam aplicadas
- **Validação de critérios** antes da implementação

### Histórico e Logs
- **Log detalhado** de todas as aplicações de regras
- **Estatísticas por regra**: quantas vezes foi aplicada
- **Auditoria completa**: quando, onde e como cada regra foi executada

## API REST

### Endpoints Principais

```http
# Listar regras
GET /api/forwarding/rules

# Criar regra
POST /api/forwarding/rules

# Atualizar regra
PUT /api/forwarding/rules/{id}

# Deletar regra
DELETE /api/forwarding/rules/{id}

# Alternar status
POST /api/forwarding/rules/{id}/toggle

# Ver logs
GET /api/forwarding/logs?rule_id={id}

# Estatísticas
GET /api/forwarding/stats

# Testar regras
POST /api/forwarding/test
```

### Schema de Regra
```json
{
  "name": "Nome da Regra",
  "description": "Descrição opcional",
  "rule_type": "sender_based|keyword_based|recipient_based|block_sender|block_keyword", 
  "action": "forward|block|delete",
  "sender_pattern": "+55 11 *",
  "recipient_pattern": "+55 11 *", 
  "keyword_pattern": "palavra1, palavra2",
  "forward_to_numbers": ["+55 11 99999-0001"],
  "forward_to_group_id": 1,
  "case_sensitive": false,
  "whole_word_only": false,
  "priority": 10,
  "is_active": true
}
```

## Instalação e Configuração

### 1. Migração do Banco de Dados
```bash
python migrations/create_forwarding_tables.py
```

### 2. Verificação das Tabelas
- `forwarding_rules`: Armazena as regras configuradas
- `forwarding_rule_logs`: Histórico de aplicações

### 3. Interface Web
Acesse: `http://localhost:8000/admin/forwarding`

## Integração no Fluxo SMS

### SMS Recebidos (Webhook)
1. SMS é salvo no banco de dados
2. **Regras são processadas automaticamente**
3. Ações são executadas (forward/block/delete)
4. Comandos automáticos são processados (se não bloqueado)

### SMS Enviados
1. SMS é criado para envio
2. **Regras são processadas antes do envio**
3. Ações são executadas (forward/block/delete)
4. SMS é enviado (se não bloqueado)

## Considerações de Segurança

### Validação de Entrada
- Todos os padrões são validados antes da aplicação
- Expressões regulares são sanitizadas
- Números de telefone são validados

### Controle de Acesso
- Interface administrativa protegida
- Logs de auditoria completos
- Confirmação para ações destrutivas

### Performance
- Índices otimizados para busca rápida
- Processamento assíncrono para alto volume
- Cache de regras ativas em memória

## Monitoramento e Troubleshooting

### Logs do Sistema
```bash
# Verificar aplicação de regras
grep "ForwardingRuleService" app.log

# Verificar regras que falharam
grep "Erro ao aplicar regra" app.log
```

### Métricas Importantes
- **Taxa de correspondência**: quantas mensagens correspondem às regras
- **Performance**: tempo de processamento das regras
- **Erros**: regras que falharam na execução

### Debug de Regras
1. Use a funcionalidade de **teste** na interface
2. Verifique os **logs detalhados** de cada regra
3. Monitore as **estatísticas** em tempo real

## Casos de Uso Avançados

### 1. Sistema de Triagem
- Regras de alta prioridade para emergências
- Reencaminhamento automático para equipes específicas
- Escalation baseado em palavras-chave

### 2. Compliance e Auditoria
- Bloqueio automático de conteúdo sensível
- Log completo para auditoria regulatória
- Retenção configurável de mensagens

### 3. Automação de Processos
- Integração com sistemas externos via webhooks
- Processamento de comandos contextuais
- Workflows complexos baseados em conteúdo

---

## Suporte

Para dúvidas, problemas ou sugestões:
- Consulte os logs em tempo real na interface
- Use a funcionalidade de teste para debug
- Verifique as estatísticas para monitoramento
