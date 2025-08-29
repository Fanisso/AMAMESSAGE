"""
Endpoints de USSD - API v2
Automação completa de códigos USSD com sessões interativas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import (
    USSDSendRequest, USSDResponse, USSDSessionResponse,
    PaginationQuery
)
from shared.models import USSDSessionStatus, MessageType
from shared.constants import MAX_USSD_SESSION_DURATION
from shared.utils import validate_ussd_code

# Imports locais
from ...db.database import get_db
from ...db.models import User, USSDHistory, USSDSession, USSDSessionStatus, SMS
from ...services.ussd_service import USSDService
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_ussd_service() -> USSDService:
    """Factory para obter instância do serviço USSD."""
    return USSDService()

@router.post("/send", response_model=USSDResponse)
async def send_ussd(
    ussd_data: USSDSendRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ussd_service: USSDService = Depends(get_ussd_service)
):
    """
    Executa código USSD.
    
    - **code**: Código USSD (ex: *120#, *144#)
    
    Retorna uma nova sessão USSD com response inicial.
    """
    try:
        # Validar código USSD
        if not validate_ussd_code(ussd_data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código USSD inválido. Use formato *XXX# ou *XXX*YYY#"
            )
        
        # Verificar se usuário tem sessões ativas em excesso
        active_sessions = db.query(USSDSession).filter(
            USSDSession.user_id == current_user.id,
            USSDSession.status == USSDSessionStatus.ACTIVE.value
        ).count()
        
        if active_sessions >= 5:  # Limite de 5 sessões simultâneas
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas sessões USSD ativas. Aguarde conclusão de outras sessões"
            )
        
        # Criar nova sessão USSD
        session_id = str(uuid.uuid4())
        session = USSDSession(
            id=session_id,
            user_id=current_user.id,
            code=ussd_data.code,
            status=USSDSessionStatus.ACTIVE.value,
            created_at=datetime.utcnow(),
            session_steps=[{"step": 0, "sent": ussd_data.code, "timestamp": datetime.utcnow().isoformat()}]
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Executar USSD em background e obter response
        try:
            response_text = await ussd_service.execute_ussd_async(ussd_data.code)
            
            # Atualizar sessão com response
            session.response = response_text
            session.current_step = 1
            session.session_steps.append({
                "step": 1,
                "received": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Determinar se sessão foi completada
            if ussd_service.is_session_complete(response_text):
                session.status = USSDSessionStatus.COMPLETED.value
                session.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            logger.info(f"USSD executado: {session_id} - {ussd_data.code}")
            
        except Exception as e:
            # Marcar sessão como erro
            session.status = USSDSessionStatus.ERROR.value
            session.response = f"Erro na execução: {str(e)}"
            session.completed_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Erro na execução USSD {session_id}: {str(e)}")
        
        return USSDResponse(
            session_id=session.id,
            code=session.code,
            response=session.response,
            status=USSDSessionStatus(session.status),
            created_at=session.created_at,
            completed_at=session.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no envio USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/sessions/{session_id}/continue", response_model=USSDResponse)
async def continue_ussd_session(
    session_id: str,
    input_data: Dict[str, str],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ussd_service: USSDService = Depends(get_ussd_service)
):
    """
    Continua sessão USSD interativa enviando input.
    
    - **session_id**: ID da sessão USSD ativa
    - **input**: Input do usuário para continuar sessão
    """
    try:
        # Buscar sessão
        session = db.query(USSDSession).filter(
            USSDSession.id == session_id,
            USSDSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão USSD não encontrada"
            )
        
        if session.status != USSDSessionStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sessão USSD não está ativa"
            )
        
        # Verificar timeout de sessão
        if (datetime.utcnow() - session.created_at).total_seconds() > MAX_USSD_SESSION_DURATION:
            session.status = USSDSessionStatus.TIMEOUT.value
            session.completed_at = datetime.utcnow()
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="Sessão USSD expirou"
            )
        
        user_input = input_data.get("input", "")
        
        # Registrar input do usuário
        session.session_steps.append({
            "step": session.current_step + 1,
            "sent": user_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.current_step += 1
        
        # Continuar sessão USSD
        try:
            response_text = await ussd_service.continue_ussd_session_async(session_id, user_input)
            
            # Atualizar sessão com nova response
            session.response = response_text
            session.session_steps.append({
                "step": session.current_step + 1,
                "received": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            session.current_step += 1
            
            # Verificar se sessão foi completada
            if ussd_service.is_session_complete(response_text):
                session.status = USSDSessionStatus.COMPLETED.value
                session.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            logger.info(f"USSD continuado: {session_id} - input: {user_input}")
            
        except Exception as e:
            session.status = USSDSessionStatus.ERROR.value
            session.response = f"Erro na continuação: {str(e)}"
            session.completed_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Erro na continuação USSD {session_id}: {str(e)}")
        
        return USSDResponse(
            session_id=session.id,
            code=session.code,
            response=session.response,
            status=USSDSessionStatus(session.status),
            created_at=session.created_at,
            completed_at=session.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao continuar sessão USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/sessions", response_model=List[USSDSessionResponse])
async def list_ussd_sessions(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    status: Optional[USSDSessionStatus] = Query(None, description="Filtrar por status"),
    code: Optional[str] = Query(None, description="Filtrar por código USSD"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista sessões USSD do usuário com paginação e filtros.
    
    - **page**: Número da página (inicia em 1)
    - **per_page**: Items por página (1-100)
    - **status**: Filtrar por status (active, completed, timeout, error)
    - **code**: Filtrar por código USSD
    - **date_from**: Data inicial (ISO format)
    - **date_to**: Data final (ISO format)
    """
    try:
        # Construir query base
        query = db.query(USSDSession).filter(USSDSession.user_id == current_user.id)
        
        # Aplicar filtros
        if status:
            query = query.filter(USSDSession.status == status.value)
        
        if code:
            query = query.filter(USSDSession.code.contains(code))
        
        if date_from:
            query = query.filter(USSDSession.created_at >= date_from)
        
        if date_to:
            query = query.filter(USSDSession.created_at <= date_to)
        
        # Aplicar paginação e ordenação
        sessions = query.order_by(USSDSession.created_at.desc())\
                       .offset((page - 1) * per_page)\
                       .limit(per_page)\
                       .all()
        
        # Preparar response
        session_responses = []
        for session in sessions:
            session_responses.append(USSDSessionResponse(
                id=session.id,
                code=session.code,
                status=USSDSessionStatus(session.status),
                response=session.response,
                session_steps=session.session_steps or [],
                current_step=session.current_step,
                created_at=session.created_at,
                completed_at=session.completed_at
            ))
        
        return session_responses
        
    except Exception as e:
        logger.error(f"Erro ao listar sessões USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/sessions/{session_id}", response_model=USSDSessionResponse)
async def get_ussd_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes completos de uma sessão USSD.
    
    - **session_id**: ID único da sessão
    """
    try:
        session = db.query(USSDSession).filter(
            USSDSession.id == session_id,
            USSDSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão USSD não encontrada"
            )
        
        return USSDSessionResponse(
            id=session.id,
            code=session.code,
            status=USSDSessionStatus(session.status),
            response=session.response,
            session_steps=session.session_steps or [],
            current_step=session.current_step,
            created_at=session.created_at,
            completed_at=session.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter sessão USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/sessions/{session_id}/cancel")
async def cancel_ussd_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ussd_service: USSDService = Depends(get_ussd_service)
):
    """
    Cancela sessão USSD ativa.
    
    - **session_id**: ID único da sessão
    """
    try:
        session = db.query(USSDSession).filter(
            USSDSession.id == session_id,
            USSDSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sessão USSD não encontrada"
            )
        
        if session.status != USSDSessionStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas sessões ativas podem ser canceladas"
            )
        
        # Cancelar sessão no serviço USSD
        try:
            await ussd_service.cancel_ussd_session_async(session_id)
        except Exception as e:
            logger.warning(f"Erro ao cancelar sessão USSD no serviço: {str(e)}")
        
        # Atualizar status na base de dados
        session.status = USSDSessionStatus.CANCELLED.value
        session.completed_at = datetime.utcnow()
        session.session_steps.append({
            "step": session.current_step + 1,
            "action": "cancelled",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        db.commit()
        
        logger.info(f"Sessão USSD cancelada: {session_id}")
        
        return {
            "success": True,
            "message": "Sessão USSD cancelada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar sessão USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/codes/popular")
async def get_popular_ussd_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém códigos USSD mais utilizados pelo usuário.
    """
    try:
        # Query para códigos mais utilizados
        popular_codes = db.query(
            USSDSession.code,
            db.func.count(USSDSession.code).label('usage_count')
        ).filter(
            USSDSession.user_id == current_user.id
        ).group_by(USSDSession.code)\
         .order_by(db.func.count(USSDSession.code).desc())\
         .limit(10)\
         .all()
        
        # Códigos USSD comuns por país (exemplo para Moçambique)
        common_codes = [
            {"code": "*120#", "description": "Consultar saldo", "operator": "mCel"},
            {"code": "*144#", "description": "Menu principal", "operator": "Vodacom"},
            {"code": "*130#", "description": "Recarregar saldo", "operator": "mCel"},
            {"code": "*133#", "description": "Consultar dados", "operator": "Vodacom"},
            {"code": "*111#", "description": "Serviços gerais", "operator": "Movitel"},
            {"code": "*140#", "description": "Transferir crédito", "operator": "mCel"},
            {"code": "*142#", "description": "Histórico", "operator": "Vodacom"},
        ]
        
        return {
            "popular_codes": [
                {
                    "code": code,
                    "usage_count": count,
                    "description": "Código personalizado"
                }
                for code, count in popular_codes
            ],
            "common_codes": common_codes
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter códigos populares: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/stats/summary")
async def get_ussd_stats(
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas de USSD do usuário.
    
    - **date_from**: Data inicial para estatísticas
    - **date_to**: Data final para estatísticas
    """
    try:
        # Query base
        query = db.query(USSDSession).filter(USSDSession.user_id == current_user.id)
        
        # Aplicar filtros de data
        if date_from:
            query = query.filter(USSDSession.created_at >= date_from)
        if date_to:
            query = query.filter(USSDSession.created_at <= date_to)
        
        # Calcular estatísticas
        total_sessions = query.count()
        completed_sessions = query.filter(USSDSession.status == USSDSessionStatus.COMPLETED.value).count()
        active_sessions = query.filter(USSDSession.status == USSDSessionStatus.ACTIVE.value).count()
        error_sessions = query.filter(USSDSession.status == USSDSessionStatus.ERROR.value).count()
        timeout_sessions = query.filter(USSDSession.status == USSDSessionStatus.TIMEOUT.value).count()
        
        # Taxa de sucesso
        success_rate = 0
        if total_sessions > 0:
            success_rate = round((completed_sessions / total_sessions) * 100, 2)
        
        # Tempo médio de sessão (para sessões completadas)
        avg_duration = db.query(
            db.func.avg(
                db.func.extract('epoch', USSDSession.completed_at - USSDSession.created_at)
            )
        ).filter(
            USSDSession.user_id == current_user.id,
            USSDSession.status == USSDSessionStatus.COMPLETED.value,
            USSDSession.completed_at.isnot(None)
        ).scalar() or 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "active_sessions": active_sessions,
            "error_sessions": error_sessions,
            "timeout_sessions": timeout_sessions,
            "success_rate": success_rate,
            "average_duration_seconds": round(float(avg_duration), 2),
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
