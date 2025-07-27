# AMAMESSAGE - Plataforma de Automação SMS/USSD

Sistema completo de gestão e automação de SMS/USSD via GSM modem com arquitetura monorepo.

## 🏗️ Arquitetura Monorepo

### Componentes da Plataforma

- **Backend API**: FastAPI com suporte SMS/USSD
- **Cliente Web Enterprise**: Interface para empresas
- **Cliente Web Individual**: Interface simplificada para usuários individuais  
- **App Mobile Android**: Aplicativo nativo Android
- **App Mobile iOS**: Aplicativo nativo iOS
- **Componentes Compartilhados**: Modelos, utilitários e schemas reutilizáveis

### Linhas de Deployment

1. **Local**: Desenvolvimento e testes locais
2. **Web Client**: Deploy dos clientes web
3. **Cloud Test**: Ambiente de testes na nuvem
4. **Cloud Production**: Ambiente de produção
5. **Mobile**: Build e distribuição dos apps mobile
6. **Windows Modem**: Servidor dedicado para modems GSM

## 🚀 Características

### Core Features
- **SMS & USSD**: Envio, recebimento e automação completa
- **Multi-Modem**: Suporte a múltiplos modems GSM
- **Multi-Cliente**: Suporte para empresas e usuários individuais
- **Cross-Platform**: Web, Android, iOS e Windows

### Funcionalidades Avançadas
- **Gestão de Contactos**: Importação/exportação, grupos, blacklist
- **Regras de Reencaminhamento**: Condições flexíveis com regex
- **Agendamento**: Envio programado de mensagens
- **Templates**: Sistema de templates personalizáveis
- **Dashboard**: Monitorização e estatísticas em tempo real
- **API REST**: Endpoints completos para integração

## 🛠️ Tecnologias

### Backend
- **Python 3.8+**: FastAPI, SQLAlchemy, Pydantic
- **Base de Dados**: SQLite (dev), PostgreSQL (prod)
- **Comunicação**: PySerial para modems GSM
- **Cache**: Redis para sessions e cache

### Frontend Web
- **TypeScript**: Tipagem forte para maior robustez
- **React 18**: Framework moderno com hooks
- **Material-UI**: Componentes de interface consistentes
- **Vite**: Build tool rápido e moderno

### Mobile
- **Android**: Kotlin nativo com Jetpack Compose
- **iOS**: Swift nativo com SwiftUI
- **Arquitetura**: MVVM com Repository pattern

### DevOps
- **Docker**: Containerização completa
- **GitHub Actions**: CI/CD automatizado
- **Nginx**: Proxy reverso e load balancer

## 📁 Estrutura do Projeto

```
AMAMESSAGE/
├── backend/                    # API Backend (FastAPI)
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
│
├── clients/                    # Clientes Frontend
│   ├── web-enterprise/         # Cliente Web Empresarial
│   │   ├── src/
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── web-individual/         # Cliente Web Individual
│   │   ├── src/
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── mobile-android/         # App Android
│   │   ├── app/
│   │   └── build.gradle
│   └── mobile-ios/             # App iOS
│       ├── AMAMESSAGE/
│       └── AMAMESSAGE.xcodeproj
│
├── shared/                     # Componentes Compartilhados
│   ├── api/                    # Cliente API Python
│   ├── models/                 # Modelos de dados
│   ├── schemas/                # Schemas Pydantic
│   ├── types/                  # Tipos TypeScript
│   ├── utils/                  # Utilitários
│   └── constants/              # Constantes do sistema
│
├── tests/                      # Testes por Deployment Line
│   ├── local/                  # Testes locais
│   ├── web_client/             # Testes web
│   ├── mobile/                 # Testes mobile
│   ├── cloud_test/             # Testes cloud
│   ├── cloud_production/       # Testes produção
│   ├── windows_modem/          # Testes modem
│   ├── pytest.ini
│   └── run_tests.py
│
├── docs/                       # Documentação
│   ├── api/                    # Docs da API
│   ├── deployment/             # Guias de deployment
│   └── user_guides/            # Manuais do usuário
│
└── infrastructure/             # Configurações de Deploy
    ├── docker/
    ├── nginx/
    └── scripts/
```

5. Iniciar a aplicação:
```bash
uvicorn main:app --reload
```

6. Acessar a interface web em: http://localhost:8000

## Estrutura do Projeto

```
├── app/
│   ├── api/          # Endpoints da API REST
│   ├── core/         # Configurações centrais
│   ├── db/           # Conexão e modelos da BD
│   ├── services/     # Lógica de negócio
│   ├── templates/    # Templates HTML
│   └── static/       # CSS, JS, imagens
├── alembic/          # Migrações da BD
├── tests/            # Testes automatizados
└── docker/           # Configuração Docker
```

## Funcionalidades

## ✅ SISTEMA COMPLETO E FUNCIONANDO!

### ✅ Funcionalidades Implementadas

**Interface Web Completa:**
- Dashboard administrativo responsivo
- Envio de SMS individual e em massa
- Visualização de SMS recebidos e enviados  
- Gerenciamento de comandos automáticos
- Monitor do status do modem GSM

**Comunicação com Modem GSM:**
- Conexão direta via porta serial
- Envio de SMS via comandos AT
- Recepção automática de SMS
- Detecção automática de portas disponíveis
- Status do sinal e operadora

**API REST Completa:**
- Endpoints para envio/recepção de SMS
- Gerenciamento de comandos automáticos
- Estatísticas e relatórios
- Controle do modem GSM

**Comandos Automáticos:**
- Respostas automáticas baseadas em palavras-chave
- Comandos padrão: HELP, INFO, STATUS, STOP, START
- Gerenciamento via interface web

**Base de Dados:**
- Armazenamento de SMS enviados/recebidos
- Histórico completo e comandos configuráveis

## Como Usar o Sistema

### 1. Iniciar a Aplicação
```bash
# Opção 1: Script direto
python start_server.py

# Opção 2: Uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Acessar Interfaces
- **Dashboard Principal**: http://127.0.0.1:8000
- **Documentação API**: http://127.0.0.1:8000/docs  
- **Status do Modem**: http://127.0.0.1:8000/modem

### 3. Configurar Modem GSM (Automático!)
✨ **NOVA FUNCIONALIDADE: Detecção Automática!**

O sistema agora detecta automaticamente o modem GSM, mesmo quando a porta muda!

**Configuração Automática:**
1. Conecte o modem USB GSM ao computador
2. Reinicie a aplicação - ela detectará automaticamente
3. Acesse `/modem` para ver o status da detecção

**Configuração Manual (opcional):**
1. Se precisar forçar uma porta específica, edite `.env`:
   ```
   GSM_PORT=COM3  # Sua porta específica
   GSM_BAUDRATE=115200
   GSM_PIN=1234   # PIN do SIM (se necessário)
   ```
2. A detecção automática sempre será tentada primeiro

**Funcionalidades de Detecção:**
- ✅ **Detecção automática** de modems GSM em qualquer porta
- ✅ **Reconexão automática** quando o modem muda de porta  
- ✅ **Monitoramento contínuo** da conexão
- ✅ **Interface web** para gerenciar detecção
- ✅ **Teste manual** de portas disponíveis
- ✅ **Códigos USSD** para consultas de saldo e serviços

### 4. Testar Detecção Automática
Execute o script de teste:
```bash
python test_modem_detection.py
```

### 5. Funcionalidades Principais
- **Envio SMS**: Dashboard → "Enviar SMS" ou API `POST /api/sms/send`
- **SMS em Massa**: Dashboard → "SMS em Massa"
- **Códigos USSD**: Dashboard → "USSD" ou `/modem/ussd`
- **Comandos**: `/admin/commands` - configurar respostas automáticas
- **Monitoramento**: Status em tempo real do modem e estatísticas

### 6. Códigos USSD
- **Interface Web**: http://127.0.0.1:8000/modem/ussd
- **Consulta de Saldo**: *124# (padrão Moçambique)
- **Pacotes Internet**: *125# (Vodacom)
- **Códigos Personalizados**: Digite qualquer código
- **Teste via Script**: `python test_ussd.py`
- [ ] Relatórios de uso
- [ ] Logs detalhados
- [ ] Backup automático

## API Endpoints

- `POST /api/sms/send` - Enviar SMS individual
- `POST /api/sms/send-bulk` - Enviar SMS em massa
- `GET /api/sms/status/{id}` - Status do SMS
- `GET /api/sms/inbox` - SMS recebidas
- `GET /api/sms/outbox` - SMS enviadas
- `GET /api/sms/stats` - Estatísticas do sistema

### Modem GSM
- `GET /modem/api/status` - Status do modem
- `POST /modem/api/restart` - Reiniciar modem
- `POST /modem/api/test-connection` - Testar conexão
- `GET /modem/api/ports` - Listar portas seriais
- `POST /modem/api/send-test-sms` - Enviar SMS de teste

## Comandos Automáticos Padrão

O sistema vem com comandos pré-configurados:

- **HELP** - Lista de comandos disponíveis
- **INFO** - Informações do sistema
- **STATUS** - Status do serviço
- **STOP** - Parar de receber mensagens
- **START** - Reativar recebimento de mensagens

## Modems GSM Testados

- Huawei E3131, E3372
- ZTE MF823, MF831
- Qualcomm modems genéricos
- Simcom SIM800, SIM900

## Troubleshooting

### Modem não conecta
1. Verificar se a porta está correta
2. Verificar se o driver está instalado
3. Verificar se outro software não está usando a porta
4. Tentar diferentes baudrates (9600, 115200)

### SMS não são enviados
1. Verificar saldo/plano do cartão SIM
2. Verificar força do sinal
3. Verificar se o PIN está correto
4. Reiniciar o modem

### Performance
- Para alto volume, considere múltiplos modems
- Configure intervalos adequados para verificação
- Use Redis para filas em produção

## Licença

Projeto privado - AMA MESSAGE
