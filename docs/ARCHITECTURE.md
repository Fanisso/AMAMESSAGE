# Arquitetura do Sistema AMAMESSAGE

## Visão Geral

O AMAMESSAGE 2.0 é uma plataforma completa de automação SMS/USSD construída com arquitetura monorepo, oferecendo múltiplos clientes para diferentes tipos de usuários.

## Arquitetura Monorepo

### Componentes Principais

```
AMAMESSAGE/
├── backend/               # API FastAPI central
├── clients/               # Aplicações cliente
│   ├── web-enterprise/    # Interface empresarial
│   ├── web-individual/    # Interface individual
│   ├── mobile-android/    # App Android nativo
│   └── mobile-ios/        # App iOS nativo
├── shared/                # Código compartilhado
└── tests/                 # Testes por deployment line
```

### Benefícios da Arquitetura Monorepo

1. **Consistência**: Código compartilhado garante consistência entre plataformas
2. **Desenvolvimento Eficiente**: Mudanças simultâneas em múltiplos clientes
3. **Versionamento Unificado**: Releases coordenados entre componentes
4. **Reutilização**: Maximização de código reutilizável

## Backend - API Central

### Tecnologias
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para abstração de banco de dados
- **Pydantic**: Validação de dados e serialização
- **Celery**: Processamento assíncrono de tarefas
- **Redis**: Cache e broker de mensagens
- **PySerial**: Comunicação com modems GSM

### Estrutura

```
backend/
├── app/
│   ├── api/               # Endpoints da API
│   │   ├── v2/            # Versão atual da API
│   │   │   ├── auth.py    # Autenticação
│   │   │   ├── sms.py     # Gestão de SMS
│   │   │   ├── ussd.py    # Automação USSD
│   │   │   ├── contacts.py # Gestão de contactos
│   │   │   └── system.py   # Status do sistema
│   ├── core/              # Lógica de negócio
│   │   ├── modem.py       # Interface com modems
│   │   ├── sms_service.py # Serviços SMS
│   │   └── ussd_service.py # Serviços USSD
│   ├── models/            # Modelos SQLAlchemy
│   ├── schemas/           # Schemas Pydantic
│   └── database.py        # Configuração BD
├── requirements.txt
└── Dockerfile
```

### Funcionalidades Core

1. **Gestão de SMS**
   - Envio individual e em lote
   - Recepção e processamento
   - Agendamento de mensagens
   - Status de entrega

2. **Automação USSD**
   - Execução de códigos USSD
   - Sessões interativas
   - Histórico de comandos
   - Processamento de respostas

3. **Multi-Modem**
   - Detecção automática de modems
   - Balanceamento de carga
   - Failover automático
   - Monitorização de status

4. **Sistema de Filas**
   - Processamento assíncrono
   - Retry automático
   - Priorização de mensagens
   - Métricas de performance

## Clientes Frontend

### Web Enterprise
**Tecnologias**: React 18 + TypeScript + Material-UI

**Características**:
- Dashboard avançado com métricas detalhadas
- Gestão de equipes e permissões
- Integração com APIs externas
- Relatórios e análises
- Webhooks e automações

**Estrutura**:
```
web-enterprise/
├── src/
│   ├── components/        # Componentes React
│   ├── pages/             # Páginas da aplicação
│   ├── hooks/             # Custom React hooks
│   ├── services/          # Serviços API
│   ├── utils/             # Utilitários
│   └── types/             # Tipos TypeScript
├── package.json
└── vite.config.ts
```

### Web Individual
**Tecnologias**: React 18 + TypeScript + Material-UI

**Características**:
- Interface simplificada e intuitiva
- Funcionalidades essenciais
- Foco na facilidade de uso
- Templates personais

### Mobile Android
**Tecnologias**: Kotlin + Jetpack Compose

**Características**:
- Interface nativa Android
- Sincronização offline
- Notificações push
- Integração com contactos do dispositivo

**Estrutura**:
```
mobile-android/
├── app/
│   ├── src/main/java/
│   │   ├── ui/             # UI com Compose
│   │   ├── data/           # Repositórios e data sources
│   │   ├── domain/         # Casos de uso
│   │   └── di/             # Dependency injection
│   └── build.gradle
└── build.gradle
```

### Mobile iOS
**Tecnologias**: Swift + SwiftUI

**Características**:
- Interface nativa iOS
- Design seguindo Human Interface Guidelines
- Integração com iOS SDK
- Notificações nativas

## Componentes Compartilhados

### Shared Models
Definições de dados compartilhadas entre backend e clientes:
- Enums (UserType, MessageStatus, etc.)
- Data classes Python
- Interfaces TypeScript

### Shared Utils
Utilitários comuns:
- Validação de números de telefone
- Formatação de dados
- Geração de IDs
- Constantes do sistema

### Shared API Client
Cliente Python para interação com a API:
- Versões síncrona e assíncrona
- Tratamento de erros
- Retry automático
- Cache de autenticação

### Shared Schemas
Esquemas de validação Pydantic:
- Requests e responses da API
- Validação de dados
- Documentação automática

## Deployment e Infraestrutura

### Linhas de Deployment

1. **Local**: Desenvolvimento e testes locais
2. **Web Client**: Deploy estático dos clientes web
3. **Cloud Test**: Ambiente de testes completo
4. **Cloud Production**: Ambiente de produção
5. **Mobile**: Build e distribuição dos apps
6. **Windows Modem**: Servidor dedicado para modems

### Containerização

**Backend**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Web Clients**:
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

### CI/CD Pipeline

```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: python tests/run_tests.py --all
  
  build-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build and push Docker image
        run: |
          docker build -t amamessage/backend:${{ github.sha }} backend/
          docker push amamessage/backend:${{ github.sha }}
```

## Segurança

### Autenticação
- JWT tokens com refresh
- Autenticação por plataforma
- Expiração configurável
- Revogação de tokens

### Autorização
- RBAC (Role-Based Access Control)
- Permissões granulares
- Separação por tenant (empresas)
- Auditoria de ações

### Comunicação
- HTTPS obrigatório
- Criptografia de dados sensíveis
- Rate limiting
- CORS configurado

## Monitorização e Observabilidade

### Métricas
- Mensagens enviadas/recebidas
- Latência da API
- Status dos modems
- Uso por cliente

### Logs
- Estruturados em JSON
- Níveis configuráveis
- Agregação centralizada
- Rotação automática

### Health Checks
- Endpoints de saúde
- Verificação de dependências
- Alertas automáticos
- Status dashboard

## Performance e Escalabilidade

### Estratégias de Cache
- Redis para sessões
- Cache de consultas frequentes
- Cache de configurações
- Invalidação inteligente

### Otimizações
- Connection pooling
- Queries otimizadas
- Compressão de responses
- CDN para assets estáticos

### Escalabilidade Horizontal
- Load balancers
- Multiple backend instances
- Database read replicas
- Message queue clustering

## Futuras Extensões

### Integrações Planejadas
- WhatsApp Business API
- Telegram Bot API
- Email marketing
- CRM integrations

### Funcionalidades Futuras
- IA para classificação de mensagens
- Analytics avançados
- Multi-tenancy completo
- API marketplace

### Plataformas Adicionais
- Desktop apps (Electron)
- CLI tools
- Browser extensions
- Third-party plugins

## Conclusão

A arquitetura monorepo do AMAMESSAGE 2.0 oferece uma base sólida para crescimento futuro, mantendo consistência entre plataformas e facilitando o desenvolvimento colaborativo. A separação clara de responsabilidades, combinada com componentes compartilhados, garante eficiência no desenvolvimento e manutenção do sistema.
