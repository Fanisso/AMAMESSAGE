from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.database import get_db
from backend.app.db.models import SMSCommand, SMS, SMSQueue
from backend.app.api.schemas import (
    SMSCommandCreate, SMSCommandUpdate, SMSCommandResponse,
    MessageResponse
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

# Rotas da interface web
@router.get("/")
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard principal de administração"""
    # Estatísticas básicas
    total_sms = db.query(SMS).count()
    total_commands = db.query(SMSCommand).count()
    total_queue = db.query(SMSQueue).filter(SMSQueue.processed == False).count()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "total_sms": total_sms,
        "total_commands": total_commands,
        "total_queue": total_queue
    })

@router.get("/sms")
async def admin_sms_list(request: Request, db: Session = Depends(get_db)):
    """Página de listagem de SMS"""
    recent_sms = db.query(SMS).order_by(SMS.created_at.desc()).limit(20).all()
    
    return templates.TemplateResponse("admin/sms_list.html", {
        "request": request,
        "sms_list": recent_sms
    })

@router.get("/commands")
async def admin_commands(request: Request, db: Session = Depends(get_db)):
    """Página de gerenciamento de comandos"""
    commands = db.query(SMSCommand).order_by(SMSCommand.keyword).all()
    
    return templates.TemplateResponse("admin/commands.html", {
        "request": request,
        "commands": commands
    })

@router.get("/forwarding")
async def admin_forwarding_rules(request: Request, db: Session = Depends(get_db)):
    """Página de gerenciamento de regras de reencaminhamento"""
    from backend.app.db.models import ForwardingRule
    
    # Estatísticas básicas
    total_rules = db.query(ForwardingRule).count()
    active_rules = db.query(ForwardingRule).filter(ForwardingRule.is_active == True).count()
    
    return templates.TemplateResponse("admin/forwarding_rules.html", {
        "request": request,
        "total_rules": total_rules,
        "active_rules": active_rules
    })

@router.get("/contacts")
async def admin_contacts(request: Request, db: Session = Depends(get_db)):
    """Página de gestão de contactos"""
    return templates.TemplateResponse("admin/contacts.html", {
        "request": request
    })

@router.get("/queue")
async def admin_queue(request: Request, db: Session = Depends(get_db)):
    """Página de gerenciamento da fila"""
    pending_queue = db.query(SMSQueue).filter(
        SMSQueue.processed == False
    ).order_by(SMSQueue.priority.desc(), SMSQueue.created_at.asc()).limit(50).all()
    
    return templates.TemplateResponse("admin/queue.html", {
        "request": request,
        "queue_items": pending_queue
    })

# API para comandos automáticos
@router.post("/api/commands", response_model=SMSCommandResponse)
async def create_command(command_data: SMSCommandCreate, db: Session = Depends(get_db)):
    """Criar novo comando automático"""
    # Verificar se o comando já existe
    existing = db.query(SMSCommand).filter(SMSCommand.keyword == command_data.keyword.upper()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comando já existe"
        )
    
    command = SMSCommand(
        keyword=command_data.keyword.upper(),
        description=command_data.description,
        response_message=command_data.response_message,
        is_active=command_data.is_active,
        case_sensitive=command_data.case_sensitive
    )
    
    db.add(command)
    db.commit()
    db.refresh(command)
    
    logger.info(f"Comando criado: {command.keyword}")
    
    return SMSCommandResponse.from_orm(command)

@router.get("/api/commands", response_model=List[SMSCommandResponse])
async def list_commands(db: Session = Depends(get_db)):
    """Listar todos os comandos"""
    commands = db.query(SMSCommand).order_by(SMSCommand.keyword).all()
    return [SMSCommandResponse.from_orm(cmd) for cmd in commands]

@router.get("/api/commands/{command_id}", response_model=SMSCommandResponse)
async def get_command(command_id: int, db: Session = Depends(get_db)):
    """Obter comando específico"""
    command = db.query(SMSCommand).filter(SMSCommand.id == command_id).first()
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comando não encontrado"
        )
    
    return SMSCommandResponse.from_orm(command)

@router.put("/api/commands/{command_id}", response_model=SMSCommandResponse)
async def update_command(
    command_id: int,
    command_data: SMSCommandUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar comando existente"""
    command = db.query(SMSCommand).filter(SMSCommand.id == command_id).first()
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comando não encontrado"
        )
    
    # Atualizar campos fornecidos
    if command_data.keyword is not None:
        # Verificar se não conflita com outro comando
        existing = db.query(SMSCommand).filter(
            SMSCommand.keyword == command_data.keyword.upper(),
            SMSCommand.id != command_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comando já existe"
            )
        command.keyword = command_data.keyword.upper()
    
    if command_data.description is not None:
        command.description = command_data.description
    
    if command_data.response_message is not None:
        command.response_message = command_data.response_message
    
    if command_data.is_active is not None:
        command.is_active = command_data.is_active
    
    if command_data.case_sensitive is not None:
        command.case_sensitive = command_data.case_sensitive
    
    db.commit()
    db.refresh(command)
    
    logger.info(f"Comando atualizado: {command.keyword}")
    
    return SMSCommandResponse.from_orm(command)

@router.delete("/api/commands/{command_id}", response_model=MessageResponse)
async def delete_command(command_id: int, db: Session = Depends(get_db)):
    """Deletar comando"""
    command = db.query(SMSCommand).filter(SMSCommand.id == command_id).first()
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comando não encontrado"
        )
    
    keyword = command.keyword
    db.delete(command)
    db.commit()
    
    logger.info(f"Comando deletado: {keyword}")
    
    return MessageResponse(
        message=f"Comando '{keyword}' deletado com sucesso",
        success=True
    )

@router.post("/api/commands/{command_id}/toggle", response_model=MessageResponse)
async def toggle_command(command_id: int, db: Session = Depends(get_db)):
    """Ativar/desativar comando"""
    command = db.query(SMSCommand).filter(SMSCommand.id == command_id).first()
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comando não encontrado"
        )
    
    command.is_active = not command.is_active
    db.commit()
    
    status_text = "ativado" if command.is_active else "desativado"
    logger.info(f"Comando {command.keyword} {status_text}")
    
    return MessageResponse(
        message=f"Comando '{command.keyword}' {status_text} com sucesso",
        success=True
    )
