<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AMA MESSAGE - Sistema de SMS

Este é um sistema completo de envio e recepção de SMS desenvolvido em Python com FastAPI.

## Estrutura do Projeto

- **Backend**: Python 3.12 + FastAPI + SQLAlchemy
- **Base de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend**: HTML/CSS/JavaScript com Bootstrap
- **SMS Provider**: Twilio
- **Processamento de Filas**: Celery + Redis (opcional)

## Funcionalidades Principais

1. **Envio de SMS**: Individual e em massa
2. **Recepção de SMS**: Via webhook do Twilio
3. **Comandos Automáticos**: Respostas automáticas baseadas em palavras-chave
4. **Interface Web**: Dashboard de administração
5. **API REST**: Para integração externa
6. **Fila de Processamento**: Para envios em massa e agendados

## Convenções de Código

- Use typing hints em todas as funções
- Siga PEP 8 para formatação
- Use docstrings para documentar funções e classes
- Prefira async/await quando apropriado
- Use SQLAlchemy ORM para interações com a base de dados
- Implemente tratamento de erros adequado
- Use logging para debug e monitoramento

## Arquitetura

```
app/
├── api/          # Routers FastAPI
├── core/         # Configurações
├── db/           # Modelos e conexão da BD
├── services/     # Lógica de negócio
├── templates/    # Templates HTML
└── static/       # CSS, JS, imagens
```

## Variáveis de Ambiente

Configure o arquivo `.env` com as credenciais necessárias antes de executar.

### Configuração de Alertas (Email/Webhook)

Para receber alertas automáticos de falha na detecção do modem, adicione as seguintes variáveis ao seu `.env`:

#### Email
```
ALERT_EMAIL_SMTP=smtp.seuprovedor.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=seuusuario@dominio.com
ALERT_EMAIL_PASSWORD=suasenha
ALERT_EMAIL_FROM=seuusuario@dominio.com
ALERT_EMAIL_TO=destinatario@dominio.com
```

#### Webhook (opcional)
```
ALERT_WEBHOOK_URL=https://seuservico.com/webhook
```

Se nenhuma dessas variáveis for definida, os alertas não serão enviados.

## Comandos Úteis

- Iniciar: `uvicorn main:app --reload`
- Migrações: `alembic upgrade head`
- Testes: `pytest`

## Próximas Fases

1. Fase 1: ✅ Estrutura básica e modelos
2. Fase 2: 🚧 Sistema de SMS completo
3. Fase 3: ⏳ Comandos inteligentes avançados
4. Fase 4: ⏳ Relatórios e analytics
