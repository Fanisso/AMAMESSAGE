# AMA MESSAGE - Guia de Ficheiros para Deploy

Este documento lista todos os ficheiros necessários para deploy do sistema AMA MESSAGE em diferentes ambientes.

## 📋 Ficheiros OBRIGATÓRIOS para Deploy

### 🔧 **Configuração Principal**
```
backend/main.py             # Entrada principal da aplicação
backend/requirements.txt    # Dependências Python
.env.example               # Exemplo de configuração
backend/alembic.ini         # Configuração de migrações
deploy.ini                 # Configurações por ambiente
```

### 🏗️ **Aplicação Core**
```
app/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── config.py          # Configurações centrais
├── db/
│   ├── __init__.py
│   ├── database.py        # Conexão BD
│   └── models.py          # Modelos SQLAlchemy
└── utils/
    └── hex_utils.py       # Utilitários
```

### 🌐 **API REST**
```
app/api/
├── __init__.py
├── admin.py               # Rotas administrativas
├── auth.py                # Autenticação
├── contacts.py            # Gestão de contactos
├── forwarding.py          # Regras de reencaminhamento
├── modem.py               # Status do modem
├── sms.py                 # Envio/recepção SMS
├── ussd.py                # Códigos USSD
├── ussd_session.py        # Sessões USSD
├── schemas_ussd_session.py # Schemas Pydantic
└── v2/                    # API v2 (NOVA - moderna)
    ├── __init__.py        # Router principal v2
    ├── auth.py            # Autenticação JWT
    ├── sms.py             # SMS com componentes partilhados
    ├── ussd.py            # USSD automação avançada
    ├── contacts.py        # Gestão completa de contactos
    ├── forwarding_rules.py # Regras com regex
    ├── system.py          # Monitorização e saúde
    └── users.py           # Gestão de utilizadores
```

### 🔄 **Serviços de Negócio**
```
app/services/
├── __init__.py
├── alert_log.py           # Logs de alertas
├── alert_service.py       # Sistema de alertas
├── command_service.py     # Comandos automáticos
├── forwarding_service.py  # Processamento de regras
├── gsm_service.py         # Comunicação GSM
├── modem_detector.py      # Detecção de modem
├── queue_processor.py     # Processamento de filas
├── sms_service.py         # Gestão de SMS
├── ussd_service.py        # Serviços USSD
└── ussd_simple.py         # USSD simplificado
```

### 🎨 **Interface Web**
```
app/templates/
├── base.html              # Template base
├── dashboard.html         # Dashboard principal
└── admin/
    ├── contacts.html      # Gestão de contactos
    ├── forwarding_rules.html # Regras de reencaminhamento
    ├── modem_status.html  # Status do modem
    ├── sms_list.html      # Lista de SMS
    └── ussd.html          # Interface USSD

app/static/
├── css/
│   └── style.css          # Estilos CSS
└── js/
    ├── app.js             # JavaScript principal
    └── forwarding_rules.js # JS das regras

clients/                   # NOVA ESTRUTURA - Clientes React
├── web-admin/            # Interface Administração Principal
│   ├── src/
│   │   ├── pages/        # 8 páginas administrativas
│   │   ├── components/   # Componentes admin
│   │   └── contexts/     # Contextos React
│   ├── package.json      # Dependências admin
│   └── README.md         # Documentação admin
├── web-enterprise/       # Cliente Web Empresarial
│   ├── src/             # Código React TypeScript
│   ├── package.json     # Dependências enterprise
│   └── README.md        # Documentação enterprise
└── web-individual/       # Cliente Web Individual (futuro)
    ├── src/             # Interface simplificada
    └── package.json     # Dependências individual
```

### 🗄️ **Base de Dados e Migrações**
```
migrations/
└── create_forwarding_tables.py # Migração das regras

alembic/
├── env.py                 # Configuração Alembic
└── script.py.mako        # Template de migração

init_db.py                 # Inicialização da BD
run_migration.py           # Executar migrações
```

### 📚 **Documentação**
```
README.md                  # Documentação principal
LICENSE                    # Licença
docs/
└── FORWARDING_RULES.md   # Documentação das regras
.github/
└── copilot-instructions.md # Instruções para Copilot
```

### 🚀 **Scripts de Deploy**
```
deploy.py                  # Central de deploy
scripts/
├── README.md             # Documentação dos scripts
├── install.bat           # Instalação Windows
├── install.sh            # Instalação Linux/Mac
├── deploy.py             # Deploy produção Linux
├── deploy_docker.py      # Deploy Docker
├── check_system.bat      # Verificação Windows
├── check_system.sh       # Verificação Linux/Mac
├── test_deploy.py        # Testes de deploy
└── update.py             # Atualizador
```

---

## 📦 **Por Tipo de Deploy**

### 🖥️ **Deploy Local (Desenvolvimento)**

**Ficheiros mínimos:**
```
# Core obrigatório
backend/main.py
backend/requirements.txt
.env.example → .env (configurar)

# Aplicação
app/ (toda a estrutura)
migrations/
alembic/
backend/alembic.ini
init_db.py
run_migration.py

# Scripts úteis
deploy.py
scripts/install.bat ou scripts/install.sh
scripts/check_system.*
```

**Comando:**
```bash
python deploy.py install
```

### 🏭 **Deploy Produção Linux**

**Ficheiros necessários:**
```
# Todos os ficheiros obrigatórios acima +
deploy.ini                 # Configurações de ambiente
scripts/deploy.py          # Script de deploy produção
iniciar_producao.py        # Modo produção
verificar_sistema.py       # Verificação do sistema
```

**Não copiar (excluir):**
```
# Ficheiros de desenvolvimento/teste
test_*.py
debug_*.py
quick_*.py
diagnose_*.py
fix_*.py
configure_*.py
check_*.py
diag_*.py
iniciar_dev.py
iniciar.bat
amamessage.db (será criado automaticamente)
.env (configurar no servidor)
__pycache__/
.git/
.vscode/
logs/
```

**Comando:**
```bash
sudo python deploy.py production
```

### 🐳 **Deploy Docker**

**Ficheiros necessários:**
```
# Todos os ficheiros obrigatórios +
Dockerfile (será criado)
docker-compose.yml (será criado)
nginx.conf (será criado)
.dockerignore (será criado)
.env.docker → .env (configurar)
```

**Comando:**
```bash
python deploy.py docker
python deploy.py docker-build
python deploy.py docker-start
```

---

## 🔧 **Configurações por Ambiente**

### **Desenvolvimento (.env)**
```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///amamessage.db
HOST=127.0.0.1
PORT=8000
```

### **Produção (.env)**
```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/amamessage.db
HOST=0.0.0.0
PORT=8000
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_number
```

### **Docker (.env)**
```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///app/data/amamessage.db
HOST=0.0.0.0
PORT=8000
REDIS_URL=redis://redis:6379/0
```

---

## 📊 **Tamanhos e Estrutura**

### **Aplicação Core (~2.5MB)**
- `app/` - ~1.8MB (código Python)
- `templates/` - ~200KB (HTML)
- `static/` - ~150KB (CSS/JS)
- `scripts/` - ~300KB (deploy)

### **Configuração (~50KB)**
- `backend/main.py`, `backend/requirements.txt`, configs

### **Documentação (~100KB)**
- `README.md`, `docs/`, `LICENSE`

### **Total para deploy:** ~3MB (sem dependências Python)

---

## 🧪 **Estrutura de Testes por Linha de Deploy**

### **Nova Organização de Testes**
```
tests/
├── shared/                     # Testes compartilhados
├── local/                      # Deploy Local (Desenvolvimento)
│   ├── unit/                   # Testes unitários
│   ├── integration/            # Testes de integração
│   └── e2e/                    # Testes end-to-end
├── web_client/                 # Deploy Web Cliente
│   ├── ui/                     # Testes de interface
│   └── api/                    # Testes de API cliente
├── cloud_test/                 # Deploy Nuvem (Testes)
│   ├── performance/            # Testes de performance
│   ├── stress/                 # Testes de stress
│   └── load/                   # Testes de carga
├── cloud_production/           # Deploy Nuvem (Produção)
│   ├── monitoring/             # Testes de monitoramento
│   ├── security/               # Testes de segurança
│   └── smoke/                  # Testes smoke
├── mobile/                     # Deploy Mobile
│   ├── android/                # Testes Android
│   └── ios/                    # Testes iOS
└── windows_modem/              # Deploy Windows com Modem
    ├── hardware/               # Testes de hardware
    └── drivers/                # Testes de drivers
```

### **Comandos de Teste por Linha**
```bash
# Testes locais
python run_tests.py local --unit --coverage

# Testes web cliente
python run_tests.py web_client --ui --browser chrome

# Testes mobile
python run_tests.py mobile --platform android

# Testes Windows com modem (CUIDADO: pode gerar custos!)
python run_tests.py windows_modem --hardware

# Testes de nuvem
python run_tests.py cloud test --performance
python run_tests.py cloud production --smoke

# Configurar ambiente de testes
python run_tests.py setup
```

### **Ficheiros de Configuração de Testes**
```
conftest.py                     # Configuração global
pytest.ini                     # Configurações pytest
.env.test                       # Variáveis de teste
run_tests.py                    # Script executador
tests/README.md                 # Documentação de testes
tests/local/conftest.py         # Config testes locais
tests/web_client/conftest.py    # Config testes web
tests/mobile/conftest.py        # Config testes mobile
tests/windows_modem/conftest.py # Config testes hardware
```

---

## ⚠️ **Ficheiros NUNCA incluir no deploy**

```
# Base de dados local
amamessage.db
*.db-journal
test_*.db

# Configuração sensível
.env (criar no servidor)
.env.test (apenas para desenvolvimento)

# Cache Python
__pycache__/
*.pyc
*.pyo

# Logs
*.log
logs/
tests/logs/

# Testes (organizados em pastas próprias)  
tests/
reports/
.pytest_cache/

# IDE
.vscode/
.idea/

# Git
.git/

# Testes e desenvolvimento antigos (migrados para tests/)
test_*.py (root level)
*_test.py (root level)
debug_*.py
quick_*.py
diagnose_*.py
fix_*.py
configure_*.py
check_*.py
diag_*.py

# Temporários
*.tmp
*.temp
Thumbs.db
.DS_Store
```

---

## 🚀 **Comando Rápido para Deploy**

### **Copiar ficheiros essenciais:**
```bash
# Criar estrutura mínima para deploy
mkdir amamessage_deploy
cd amamessage_deploy

# Copiar ficheiros obrigatórios
cp ../backend/main.py .
cp ../backend/requirements.txt .
cp ../deploy.py .
cp ../deploy.ini .
cp ../init_db.py .
cp ../run_migration.py .
cp ../.env.example .env
cp -r ../app/ .
cp -r ../migrations/ .
cp -r ../alembic/ .
cp ../backend/alembic.ini .
cp -r ../scripts/ .
cp -r ../docs/ .
cp ../README.md .

# Configurar e testar
python deploy.py test
```

### **Deploy automático:**
```bash
# Use os scripts incluídos
python deploy.py install      # Local
python deploy.py production   # Produção
python deploy.py docker      # Docker
```

---

**Total de ficheiros para deploy completo:** ~45 ficheiros essenciais  
**Tamanho aproximado:** 3-5MB (sem dependências Python)  
**Tempo de deploy:** 2-5 minutos (dependendo do ambiente)

**✅ Para começar:** Execute `python deploy.py help` para ver todas as opções!
