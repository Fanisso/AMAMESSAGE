# Sistema de SMS - AMA MESSAGE

Sistema completo de envio e recepção de SMS com:
- Base de dados SQLite/PostgreSQL
- API REST para integração externa
- Interface web de administração
- Processamento automático de comandos SMS
- **Comunicação direta com modem GSM/USB** (sem dependência de terceiros)
- Sistema de filas para envio em massa

## Tecnologias Utilizadas

- **Backend**: Python 3.12 + FastAPI
- **Base de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: HTML/CSS/JavaScript + Bootstrap
- **Comunicação GSM**: PySerial + Comandos AT
- **Filas**: Celery + Redis (opcional)
- **Modem GSM**: Qualquer modem USB GSM compatível

## Configuração

### Pré-requisitos

1. **Modem GSM USB**: Qualquer modem GSM compatível com comandos AT
2. **Cartão SIM**: Com plano de dados/SMS ativo
3. **Python 3.12+**
4. **Drivers do modem** instalados no sistema

### Instalação

1. Instalar dependências:
```bash
pip install -r requirements.txt
```

2. Conectar o modem GSM USB e identificar a porta:
   - **Windows**: Verificar no Gerenciador de Dispositivos (ex: COM3, COM4)
   - **Linux**: Verificar em `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.

3. Configurar variáveis de ambiente no arquivo `.env`:
```bash
# Configurar a porta do modem
GSM_PORT=COM3
GSM_BAUDRATE=115200
GSM_PIN=1234  # PIN do SIM (se necessário)
```

4. Executar migrações da base de dados:
```bash
alembic upgrade head
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
