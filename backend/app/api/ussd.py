from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.api.schemas import USSDRequest, USSDResponse, USSDHistoryResponse, MessageResponse
from backend.app.services.ussd_service import USSDService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

# Serviço USSD será inicializado dinamicamente
ussd_service = None

def get_ussd_service():
    """Obter instância do serviço USSD (lazy loading)"""
    global ussd_service
    if ussd_service is None:
        ussd_service = USSDService()
    return ussd_service

@router.get("/")
async def ussd_page(request: Request):
    """Página principal do USSD"""
    try:
        service = get_ussd_service()
        common_codes = service.get_common_codes()
        
        # Organizar códigos por categoria
        codes_by_category = {
            "Consultas Básicas": {
                "saldo": {"code": "*125#", "description": "Consultar saldo"},
                "bonus": {"code": "*126#", "description": "Consultar bônus"},
                "mb": {"code": "*127#", "description": "Consultar MB"},
                "planos": {"code": "*129#", "description": "Ver planos disponíveis"},
            },
            "Serviços": {
                "servicos": {"code": "*144#", "description": "Menu de serviços"},
                "info": {"code": "*100#", "description": "Informações da conta"},
                "status": {"code": "*131#", "description": "Status da linha"},
            },
            "Recarga": {
                "recarregar": {"code": "*150*", "description": "Recarregar (+ código)"},
            }
        }
        
        return templates.TemplateResponse("ussd/index.html", {
            "request": request,
            "codes_by_category": codes_by_category,
            "page_title": "Códigos USSD"
        })
    except Exception as e:
        logger.error(f"Erro ao carregar página USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/api/send-simple", response_model=USSDResponse)
async def send_ussd_simple(
    ussd_request: USSDRequest,
    db: Session = Depends(get_db)
):
    """Enviar código USSD usando método simplificado (baseado no teste funcional)"""
    try:
        service = get_ussd_service()
        
        logger.info(f"Enviando USSD (método simples): {ussd_request.ussd_code}")
        
        # Usar diretamente o método simples
        ussd_simple = service.get_ussd_simple()
        result = ussd_simple.send_ussd(ussd_request.ussd_code)
        
        # Salvar no histórico
        service._save_ussd_history(ussd_request.ussd_code, result, db)
        
        return USSDResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro ao enviar USSD simples {ussd_request.ussd_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

@router.post("/api/send", response_model=USSDResponse)
async def send_ussd(
    ussd_request: USSDRequest,
    db: Session = Depends(get_db)
):
    """Enviar código USSD"""
    try:
        service = get_ussd_service()
        
        logger.info(f"Enviando USSD: {ussd_request.ussd_code}")
        
        result = service.send_ussd(
            ussd_code=ussd_request.ussd_code,
            timeout=ussd_request.timeout,
            db=db
        )
        
        return USSDResponse(**result)
        
    except Exception as e:
        logger.error(f"Erro ao enviar USSD {ussd_request.ussd_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao enviar USSD"
        )

@router.post("/api/cancel", response_model=MessageResponse)
async def cancel_ussd():
    """Cancelar sessão USSD ativa"""
    try:
        service = get_ussd_service()
        result = service.cancel_ussd()
        
        return MessageResponse(
            message=result.get("message", "Operação realizada"),
            success=result.get("success", False)
        )
        
    except Exception as e:
        logger.error(f"Erro ao cancelar USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao cancelar USSD"
        )

@router.get("/api/history")
async def get_ussd_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Obter histórico de códigos USSD"""
    try:
        service = get_ussd_service()
        history = service.get_ussd_history(db, limit)
        
        return {
            "success": True,
            "data": history,
            "total": len(history)
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter histórico USSD"
        )

@router.get("/api/common-codes")
async def get_common_codes():
    """Obter códigos USSD comuns"""
    try:
        service = get_ussd_service()
        codes = service.get_common_codes()
        
        # Transformar em formato mais amigável
        formatted_codes = []
        for name, code in codes.items():
            formatted_codes.append({
                "name": name,
                "code": code,
                "description": f"Código {name.replace('_', ' ').title()}"
            })
        
        return {
            "success": True,
            "data": formatted_codes
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter códigos comuns: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter códigos USSD"
        )

@router.get("/history")
async def ussd_history_page(request: Request, db: Session = Depends(get_db)):
    """Página de histórico USSD"""
    try:
        service = get_ussd_service()
        history = service.get_ussd_history(db, limit=100)
        
        return templates.TemplateResponse("ussd/history.html", {
            "request": request,
            "history": history,
            "page_title": "Histórico USSD"
        })
        
    except Exception as e:
        logger.error(f"Erro ao carregar histórico USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
