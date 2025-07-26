from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import sms, admin, auth, modem, ussd, ussd_session
from app.db.database import engine, SessionLocal
from app.db import models
from app.services.command_service import CommandService
from app.services.sms_service import SMSService
from app.db.models import SMS, SMSStatus, SMSDirection
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas da base de dados
models.Base.metadata.create_all(bind=engine)

# Instância global do serviço SMS
sms_service_instance = None

def create_default_data():
    """Criar tabelas e dados padrão"""
    from app.db.models import Base
    from app.db.database import engine
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas/verificadas no banco de dados")
    
    db = SessionLocal()
    try:
        command_service = CommandService()
        command_service.create_default_commands(db)
        logger.info("Dados padrão criados")
    except Exception as e:
        logger.error(f"Erro ao criar dados padrão: {e}")
    finally:
        db.close()

def handle_incoming_sms(sms_data: dict):
    """Callback para processar SMS recebidos do modem"""
    db = SessionLocal()
    try:
        # Criar registro de SMS recebido
        sms = SMS(
            phone_from=sms_data['sender'],
            phone_to="Modem GSM",  # Nosso número (será obtido do modem posteriormente)
            message=sms_data['content'],
            status=SMSStatus.RECEIVED,
            direction=SMSDirection.INBOUND,
            external_id=str(sms_data.get('index', ''))
        )
        db.add(sms)
        db.commit()
        db.refresh(sms)
        
        # Processar comandos automáticos
        command_service = CommandService()
        import asyncio
        asyncio.create_task(command_service.process_incoming_sms(sms.id, db))
        
        logger.info(f"SMS recebido processado: ID {sms.id}")
        
    except Exception as e:
        logger.error(f"Erro ao processar SMS recebido: {str(e)}")
    finally:
        db.close()

# Inicializar FastAPI
app = FastAPI(
    title="AMA MESSAGE - Sistema de SMS",
    description="Sistema completo de envio e recepção de SMS",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Incluir routers da API
app.include_router(sms.router, prefix="/api/sms", tags=["SMS"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(modem.router, prefix="/modem", tags=["Modem GSM"])
app.include_router(ussd.router, prefix="/ussd", tags=["USSD"])

# Importar e incluir API de contactos
from app.api import contacts
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contactos"])

# Importar e incluir API de sessão USSD contínua
app.include_router(ussd_session.router, tags=["USSD Sessão"])

# Importar e incluir API de regras de reencaminhamento
from app.api import forwarding
app.include_router(forwarding.router, prefix="/api", tags=["Reencaminhamento"])

@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização"""
    global sms_service_instance
    
    logger.info("Iniciando AMA MESSAGE...")
    create_default_data()
    
    # Inicializar serviço SMS
    try:
        sms_service_instance = SMSService()
        sms_service_instance.set_incoming_sms_callback(handle_incoming_sms)
        
        # Configurar instância global no módulo modem
        import app.api.modem as modem_module
        modem_module.sms_service = sms_service_instance
        
        logger.info("Serviço SMS inicializado")
    except Exception as e:
        logger.error(f"Erro ao inicializar serviço SMS: {str(e)}")
    
    # Inicializar processador de fila SMS
    try:
        from app.services.queue_processor import queue_processor
        queue_processor.start_processing()
        logger.info("Processador de fila SMS iniciado")
    except Exception as e:
        logger.error(f"Erro ao inicializar processador de fila: {str(e)}")
    
    logger.info("AMA MESSAGE iniciado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos de encerramento"""
    global sms_service_instance
    
    logger.info("Encerrando AMA MESSAGE...")
    
    if sms_service_instance:
        sms_service_instance.stop_service()
        logger.info("Serviço SMS encerrado")
    
    # Parar processador de fila
    try:
        from app.services.queue_processor import queue_processor
        queue_processor.stop_processing()
        logger.info("Processador de fila SMS encerrado")
    except Exception as e:
        logger.error(f"Erro ao encerrar processador de fila: {str(e)}")
    
    logger.info("AMA MESSAGE encerrado")

@app.get("/")
async def root(request: Request):
    """Página principal - Dashboard de administração"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    """Endpoint para verificar se a aplicação está funcionando"""
    return {"status": "ok", "message": "AMA MESSAGE está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
