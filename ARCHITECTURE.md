# AMAMESSAGE - Arquitetura Monorepo

## 🏗️ Visão Geral da Arquitetura

Sistema AMAMESSAGE estruturado como **monorepo** com múltiplas interfaces de cliente e backend unificado.

### 📊 Diagrama da Arquitetura

```
AMAMESSAGE (Monorepo)
├── backend/              # Backend API unificado
│   ├── core/            # FastAPI + SQLAlchemy
│   ├── services/        # SMS, USSD, TWILIO
│   └── api/             # Endpoints REST
├── clients/             # Interfaces de cliente
│   ├── web-admin/       # Interface de Administração Principal
│   ├── web-enterprise/  # Cliente Web Empresarial
│   ├── web-individual/  # Cliente Web Individual
│   ├── mobile-android/  # App Android
│   └── mobile-ios/      # App iOS (futuro)
├── shared/              # Código compartilhado
│   ├── types/           # Tipos TypeScript
│   ├── constants/       # Constantes globais
│   └── utils/           # Utilitários comuns
└── deploy/              # Scripts de deployment
    ├── local/           # Deploy local para testes
    ├── web-test/        # Deploy web cliente (teste)
    ├── cloud-test/      # Deploy nuvem (teste)
    ├── cloud-prod/      # Deploy nuvem (produção)
    ├── mobile/          # Deploy mobile (Android/iOS)
    └── desktop/         # Deploy desktop Windows
```

## 🎯 Tipos de Cliente

### � **Interface de Administração** (Principal)
- **Web Admin**: Dashboard completo de administração do sistema
- **Features**: Gestão global, configurações, monitorização, logs, utilizadores
- **Acesso**: Apenas administradores do sistema

### �👔 **Cliente Empresarial**
- **Web Enterprise**: Interface completa para empresas
- **Mobile**: App móvel com funcionalidades empresariais
- **Features**: Gestão de equipes, relatórios avançados, integração API

### 👤 **Cliente Individual**
- **Web Individual**: Interface simplificada
- **Mobile**: Mesmas funcionalidades da web empresarial
- **Features**: Automação USSD, templates, envios básicos

## 🚀 Linhas de Deploy

### 1. **Deploy Local** (Desenvolvimento/Testes)
```bash
npm run deploy:local:backend
npm run deploy:local:web
npm run deploy:local:full
```

### 2. **Deploy Web Cliente** (Testes)
```bash
npm run deploy:web-test:admin
npm run deploy:web-test:enterprise
npm run deploy:web-test:individual
```

### 3. **Deploy Nuvem** (Testes)
```bash
npm run deploy:cloud-test:backend
npm run deploy:cloud-test:clients
```

### 4. **Deploy Nuvem** (Produção)
```bash
npm run deploy:cloud-prod:backend
npm run deploy:cloud-prod:clients
```

### 5. **Deploy Mobile** (Android/iOS)
```bash
npm run deploy:mobile:android
npm run deploy:mobile:ios
```

### 6. **Deploy Desktop** (Windows com Modem Físico)
```bash
npm run deploy:desktop:windows
```

## 🔧 Configuração por Ambiente

### **Backend Unificado**
- FastAPI como API central
- SQLAlchemy para persistência
- Suporte a múltiplos clientes via JWT/Auth
- WebSocket para tempo real

### **Frontend Diferenciado**
- **Web Enterprise**: React/Vue.js com Bootstrap
- **Web Individual**: Interface simplificada
- **Mobile**: React Native ou Flutter
- **Desktop**: Electron ou PWA

## 📱 Funcionalidades por Cliente

| Funcionalidade | Web Admin | Web Enterprise | Web Individual | Mobile | Desktop |
|----------------|-----------|----------------|----------------|---------|---------|
| **ADMINISTRAÇÃO SISTEMA** |
| Gestão Geral Utilizadores | ✅ | ❌ | ❌ | ❌ | ❌ |
| Configurações Globais | ✅ | ❌ | ❌ | ❌ | ❌ |
| Monitorização Sistema | ✅ | ✅ | ❌ | ❌ | ✅ |
| Logs e Auditoria | ✅ | ✅ | ❌ | ❌ | ✅ |
| Gestão de Modems | ✅ | ✅ | ❌ | ❌ | ✅ |
| Estatísticas Globais | ✅ | ✅ | ❌ | ❌ | ✅ |
| **FUNCIONALIDADES SMS/USSD** |
| Envio SMS Individual | ✅ | ✅ | ✅ | ✅ | ✅ |
| Envio SMS Massa | ✅ | ✅ | ❌ | ✅ | ✅ |
| Automação USSD | ✅ | ✅ | ✅ | ✅ | ✅ |
| Templates | ✅ | ✅ | ✅ | ✅ | ✅ |
| Relatórios Avançados | ✅ | ✅ | ❌ | ✅ | ✅ |
| Gestão de Equipes | ✅ | ✅ | ❌ | ✅ | ❌ |
| API Integration | ✅ | ✅ | ❌ | ❌ | ✅ |
| **HARDWARE** |
| Modem Físico | ✅ | ❌ | ❌ | ❌ | ✅ |
| Modem Virtual | ✅ | ✅ | ✅ | ✅ | ❌ |

## 🎨 Design System

### **Cores por Cliente**
- **Admin**: Vermelho/laranja administrativo (#dc2626)
- **Enterprise**: Azul corporativo (#1e3a8a)
- **Individual**: Verde amigável (#059669)
- **Mobile**: Gradientes modernos
- **Desktop**: Tema escuro profissional

### **Componentes Compartilhados**
- Sistema de design unificado
- Componentes reutilizáveis
- Temas configuráveis
- Responsividade automática

## 🔐 Autenticação e Autorização

### **Sistema Unificado**
- JWT tokens para todas as interfaces
- Roles: `super_admin`, `admin`, `enterprise_user`, `individual_user`
- Permissions granulares por funcionalidade
- SSO opcional para empresas
- Hierarquia de acesso bem definida

### **Planos e Limitações**
- **Individual**: Limitações de SMS/mês
- **Enterprise**: Sem limitações, features avançadas
- **Premium**: Funcionalidades exclusivas

## 📈 Escalabilidade

### **Backend**
- Microserviços internos
- Cache Redis
- Queue Celery
- Load balancing

### **Frontend**
- CDN para assets
- Code splitting
- Lazy loading
- PWA capabilities

## 🔄 Fluxo de Desenvolvimento

1. **Desenvolvimento**: Local deploy para testes
2. **Staging**: Deploy web/cloud para testes
3. **QA**: Testes em ambiente de nuvem
4. **Produção**: Deploy coordenado de todas as interfaces
5. **Mobile**: Build e distribuição via stores

## 🛠️ Tecnologias por Camada

### **Backend**
- Python 3.12 + FastAPI
- SQLAlchemy + Alembic
- Redis + Celery
- WebSocket support

### **Web Clients**
- React 18 + TypeScript
- Tailwind CSS + Headless UI
- React Query + Zustand
- Vite build system

### **Mobile**
- React Native + TypeScript
- Native modules para SMS/USSD
- Expo managed workflow
- OTA updates

### **Desktop**
- Electron + React
- Node.js serial communication
- Auto-updater
- System tray integration

## 📋 Próximos Passos

1. ✅ **Definir arquitetura** - Completo
2. 🚧 **Implementar backend unificado** - Em progresso
3. ⏳ **Desenvolver interface web admin** - Prioritário
4. ⏳ **Desenvolver cliente web enterprise**
5. ⏳ **Desenvolver cliente web individual**
6. ⏳ **Desenvolver app mobile**
7. ⏳ **Configurar linhas de deploy**
8. ⏳ **Testes e otimização**

---

**Status**: 🚀 Pronto para início do desenvolvimento!
