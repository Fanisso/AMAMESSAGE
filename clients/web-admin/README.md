# AMA MESSAGE - Web Admin Interface

Interface de **Administração Principal** para gestão completa do sistema AMA MESSAGE.

## 🎯 Objetivo

Interface dedicada para **super administradores** gerirem todo o sistema:
- Monitorização global
- Gestão de utilizadores de todos os tipos
- Configurações do sistema
- Logs e auditoria
- Controlo de modems
- Estatísticas globais

## 🚀 Características Especiais

### 🔐 **Acesso Restrito**
- Apenas `super_admin` e `admin`
- Autenticação multi-factor (futura)
- Sessões com timeout reduzido
- Logs de todas as ações

### 📊 **Dashboard Avançado**
- **Métricas em tempo real** via WebSocket
- **Gráficos interativos** com Recharts
- **Alertas críticos** do sistema
- **Visão global** de todos os clientes

### 🛠️ **Funcionalidades Exclusivas**

#### **Gestão Global de Utilizadores**
- Listar todos os utilizadores (enterprise + individual)
- Criar contas para qualquer tipo
- Alterar roles e permissões
- Suspender/reativar contas
- Estatísticas de uso por utilizador

#### **Configurações do Sistema**
- Configurar limites globais
- Definir preços e planos
- Configurar integrações (Twilio, etc.)
- Gerir templates globais
- Configurar regras de reencaminhamento master

#### **Monitorização Completa**
- Status de todos os modems
- Saúde do backend
- Performance das APIs
- Uso de recursos (CPU, RAM, disco)
- Filas de processamento

#### **Logs e Auditoria**
- Logs de sistema completos
- Auditoria de ações de utilizadores
- Rastreamento de SMS/USSD
- Logs de segurança
- Exportação de relatórios

#### **Gestão de Hardware**
- Configurar modems físicos
- Testar conexões GSM
- Reiniciar serviços
- Backup e restore
- Manutenção programada

## 🎨 Design Diferenciado

### **Tema Administrativo**
- **Cores**: Vermelho/laranja administrativo
- **Layout**: Focado em dados e métricas
- **Densidade**: Interface densa com muita informação
- **Modo escuro**: Por padrão para reduzir fadiga

### **Componentes Especiais**
- **Dashboard tiles** com métricas críticas
- **Tabelas avançadas** com filtros complexos
- **Gráficos em tempo real** com atualizações WebSocket
- **Modais de confirmação** para ações críticas
- **Breadcrumbs detalhados** para navegação

## 📋 Páginas da Interface

### 🏠 **Dashboard**
- Visão geral do sistema
- Métricas críticas em tempo real
- Alertas e notificações
- Ações rápidas

### 👥 **Gestão de Utilizadores**
- Lista completa de todos os utilizadores
- Filtros por tipo, status, empresa
- Criação e edição de contas
- Histórico de atividade

### ⚙️ **Configurações do Sistema**
- Configurações globais
- Limites e quotas
- Integrações externas
- Templates e regras master

### 📊 **Monitorização**
- Status dos serviços
- Performance em tempo real
- Uso de recursos
- Histórico de uptime

### 📋 **Logs e Auditoria**
- Logs do sistema
- Auditoria de utilizadores
- Rastreamento de transações
- Relatórios de segurança

### 🔧 **Gestão de Hardware**
- Status dos modems
- Configuração GSM
- Testes de conectividade
- Manutenção e backup

### 📈 **Relatórios Globais**
- Estatísticas de uso
- Relatórios financeiros
- Análise de performance
- Exportação de dados

### 🛡️ **Segurança**
- Gestão de permissões
- Logs de segurança
- Configurações de autenticação
- Políticas de acesso

## 🔄 Hierarquia de Acesso

```
Super Admin (Acesso Total)
├── Gestão completa do sistema
├── Criação de outros admins
├── Configurações críticas
└── Acesso a todos os dados

Admin (Acesso Limitado)
├── Monitorização do sistema
├── Gestão de utilizadores
├── Relatórios básicos
└── Sem configurações críticas

Enterprise User (Sem Acesso)
├── Apenas ao próprio cliente
└── Sem acesso à interface admin

Individual User (Sem Acesso)
├── Apenas ao próprio cliente
└── Sem acesso à interface admin
```

## 🚀 Instalação e Configuração

```bash
# Navegar para o diretório
cd clients/web-admin

# Instalar dependências
npm install

# Configurar variáveis (apenas super_admin)
cp .env.example .env

# Executar
npm start
```

### **Variáveis de Ambiente**
```env
REACT_APP_API_URL=http://localhost:8000/api/v2
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
REACT_APP_ADMIN_MODE=true
REACT_APP_LOG_LEVEL=debug
```

## 🔐 Segurança Adicional

### **Autenticação Reforçada**
- Token JWT com tempo de vida reduzido (30 min)
- Refresh automático
- Logout automático por inatividade
- Validação de IP (opcional)

### **Auditoria Completa**
- Log de todas as ações administrativas
- Rastreamento de alterações
- Backup automático antes de mudanças críticas
- Notificações por email para ações sensíveis

### **Acesso Controlado**
- Lista branca de IPs (produção)
- Horários de acesso permitido
- Confirmação dupla para ações críticas
- Histórico de login

## 📊 Métricas Especiais

### **Em Tempo Real**
- Utilizadores online
- SMS sendo processados
- Status dos modems
- Uso de CPU/RAM

### **Relatórios Automáticos**
- Relatório diário por email
- Alertas críticos instantâneos
- Backup status
- Performance summary

## 🎯 Diferenças dos Outros Clientes

| Característica | Web Admin | Web Enterprise | Web Individual |
|----------------|-----------|----------------|----------------|
| **Acesso** | Super Admin apenas | Utilizadores empresa | Utilizadores individuais |
| **Foco** | Gestão do sistema | Operação empresarial | Uso pessoal |
| **Interface** | Densa, técnica | Profissional | Simples, amigável |
| **Dados** | Todos os utilizadores | Dados da empresa | Dados próprios |
| **Configurações** | Sistema completo | Perfil empresa | Perfil pessoal |
| **Relatórios** | Globais | Empresariais | Pessoais |

## 🚧 Estado de Desenvolvimento

### ✅ **Planeamento**
- Arquitetura definida
- Funcionalidades mapeadas
- Design system especificado

### 🚧 **Em Desenvolvimento**
- Estrutura base da aplicação
- Sistema de autenticação admin
- Dashboard principal
- Gestão de utilizadores

### 📋 **Próximos Passos**
1. Dashboard com métricas em tempo real
2. Gestão completa de utilizadores
3. Interface de configurações do sistema
4. Monitorização e logs
5. Relatórios avançados
6. Gestão de hardware

---

**Prioridade:** 🔥 **MÁXIMA** - Interface principal do sistema
**Usuários:** Super Administradores apenas
**Complexidade:** Alta - Interface mais completa do sistema
