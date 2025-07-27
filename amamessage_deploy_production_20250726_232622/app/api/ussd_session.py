from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.schemas_ussd_session import USSDSessionStartRequest, USSDSessionReplyRequest, USSDSessionResponse
from app.services.ussd_service import USSDService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Sessão USSD simples em memória (por usuário, para demo; produção: usar cache/db)
ussd_sessions = {}

def get_ussd_service():
    return USSDService()

@router.post("/ussd/api/session/start", response_model=USSDSessionResponse)
async def start_ussd_session(
    req: USSDSessionStartRequest,
    db: Session = Depends(get_db)
):
    """Iniciar sessão USSD multi-etapa (simples, não persistente)"""
    try:
        service = get_ussd_service()
        ussd_simple = service.get_ussd_simple()
        # Iniciar sessão (envia o código)
        result = ussd_simple.send_ussd(req.ussd_code)
        # Simular controle de sessão (em produção, usar ID de sessão/usuário)
        ussd_sessions['active'] = True
        ussd_sessions['step'] = 1
        ussd_sessions['last_code'] = req.ussd_code
        ussd_sessions['last_response'] = result.get('response', '')
        session_active = 'Mais' in result.get('response', '') or 'responder' in result.get('response', '').lower()
        ussd_sessions['session_active'] = session_active
        return USSDSessionResponse(
            success=result.get('success', False),
            response=result.get('response', ''),
            error=result.get('error'),
            session_active=session_active,
            step=1
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar sessão USSD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ussd/api/session/reply", response_model=USSDSessionResponse)
async def ussd_session_reply(
    req: USSDSessionReplyRequest,
    db: Session = Depends(get_db)
):
    """Enviar resposta para sessão USSD multi-etapa (simples, não persistente)"""
    try:
        service = get_ussd_service()
        ussd_simple = service.get_ussd_simple()
        # Enviar resposta (continuação da sessão)
        result = ussd_simple.send_ussd(req.reply)
        ussd_sessions['step'] = req.step or (ussd_sessions.get('step', 1) + 1)
        ussd_sessions['last_code'] = req.reply
        ussd_sessions['last_response'] = result.get('response', '')
        session_active = 'Mais' in result.get('response', '') or 'responder' in result.get('response', '').lower()
        ussd_sessions['session_active'] = session_active
        return USSDSessionResponse(
            success=result.get('success', False),
            response=result.get('response', ''),
            error=result.get('error'),
            session_active=session_active,
            step=ussd_sessions['step']
        )
    except Exception as e:
        logger.error(f"Erro ao responder sessão USSD: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
