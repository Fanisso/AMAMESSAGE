"""
Endpoints de SMS - API v2
Gestão completa de SMS com suporte a envio individual, bulk e agendamento
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import uuid

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import (
    SMSSendRequest, SMSBulkSendRequest, SMSResponse, SMSListResponse,
    PaginationQuery, SearchQuery
)
from shared.models import MessageStatus, MessageType
from shared.constants import MAX_SMS_LENGTH, MAX_BULK_RECIPIENTS
from shared.utils import validate_phone_number

# Imports locais
from ...db.database import get_db
from ...db.models import User, SMS, SMSStatus, SMSDirection
from ...services.sms_service import SMSService
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_sms_service() -> SMSService:
    """Factory para obter instância do serviço SMS."""
    return SMSService()

@router.post("/send", response_model=SMSResponse)
async def send_sms(
    sms_data: SMSSendRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sms_service: SMSService = Depends(get_sms_service)
):
    """
    Envia SMS individual.
    
    - **to**: Número de destino (formato internacional)
    - **message**: Texto da mensagem (máx. 1600 caracteres)
    - **schedule_at**: Data/hora para agendamento (opcional)
    """
    try:
        # Validações
        if not validate_phone_number(sms_data.to):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de telefone inválido"
            )
        
        if len(sms_data.message) > MAX_SMS_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mensagem muito longa. Máximo {MAX_SMS_LENGTH} caracteres"
            )
        
        # Verificar se é agendamento futuro
        is_scheduled = sms_data.schedule_at and sms_data.schedule_at > datetime.utcnow()
        
        # Criar registro na base de dados
        sms_record = SMS(
            phone_from="SYSTEM",  # O sistema está enviando
            phone_to=sms_data.to,
            message=sms_data.message,
            status=SMSStatus.PENDING,
            direction=SMSDirection.OUTBOUND
        )
        
        db.add(sms_record)
        db.commit()
        db.refresh(sms_record)
        
        # Enviar SMS imediatamente ou agendar
        if is_scheduled:
            # Agendar para envio posterior
            background_tasks.add_task(
                sms_service.schedule_sms,
                sms_record.id,
                sms_data.schedule_at
            )
            logger.info(f"SMS agendado: {sms_record.id} para {sms_data.schedule_at}")
        else:
            # Enviar imediatamente em background
            background_tasks.add_task(
                sms_service.send_sms_async,
                sms_record.id,
                sms_data.to,
                sms_data.message
            )
            logger.info(f"SMS enviado: {sms_record.id} para {sms_data.to}")
        
        return SMSResponse(
            id=sms_record.id,
            to=sms_record.phone_to,
            message=sms_record.message,
            status=sms_record.status.value,
            created_at=sms_record.created_at,
            cost=None  # Será calculado após envio
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no envio de SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/bulk-send", response_model=List[SMSResponse])
async def send_bulk_sms(
    bulk_data: SMSBulkSendRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sms_service: SMSService = Depends(get_sms_service)
):
    """
    Envia SMS em lote.
    
    - **recipients**: Lista de números de destino (máx. 100)
    - **message**: Texto da mensagem (máx. 1600 caracteres)
    - **schedule_at**: Data/hora para agendamento (opcional)
    """
    try:
        # Validações
        if len(bulk_data.recipients) > MAX_BULK_RECIPIENTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Máximo {MAX_BULK_RECIPIENTS} destinatários por envio"
            )
        
        if len(bulk_data.message) > MAX_SMS_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Mensagem muito longa. Máximo {MAX_SMS_LENGTH} caracteres"
            )
        
        # Validar todos os números
        invalid_numbers = []
        for phone in bulk_data.recipients:
            if not validate_phone_number(phone):
                invalid_numbers.append(phone)
        
        if invalid_numbers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Números inválidos: {', '.join(invalid_numbers)}"
            )
        
        # Remover duplicatas
        unique_recipients = list(set(bulk_data.recipients))
        
        # Verificar se é agendamento futuro
        is_scheduled = bulk_data.schedule_at and bulk_data.schedule_at > datetime.utcnow()
        
        # Criar registros na base de dados
        messages = []
        for phone in unique_recipients:
            message_id = str(uuid.uuid4())
            message = Message(
                id=message_id,
                user_id=current_user.id,
                phone_number=phone,
                message=bulk_data.message,
                message_type=MessageType.SMS.value,
                status=MessageStatus.PENDING.value if not is_scheduled else MessageStatus.SCHEDULED.value,
                scheduled_at=bulk_data.schedule_at,
                created_at=datetime.utcnow(),
                bulk_id=str(uuid.uuid4())  # ID para agrupar envio em lote
            )
            messages.append(message)
        
        db.add_all(messages)
        db.commit()
        
        # Processar envios
        if is_scheduled:
            # Agendar todos para envio posterior
            for message in messages:
                background_tasks.add_task(
                    sms_service.schedule_sms,
                    message.id,
                    bulk_data.schedule_at
                )
            logger.info(f"Bulk SMS agendado: {len(messages)} mensagens para {bulk_data.schedule_at}")
        else:
            # Processar envio em lote em background
            bulk_id = messages[0].bulk_id
            background_tasks.add_task(
                sms_service.send_bulk_sms_async,
                bulk_id,
                [(msg.id, msg.phone_number, msg.message) for msg in messages]
            )
            logger.info(f"Bulk SMS enviado: {len(messages)} mensagens")
        
        # Preparar response
        responses = []
        for message in messages:
            db.refresh(message)
            responses.append(SMSResponse(
                id=message.id,
                to=message.phone_number,
                message=message.message,
                status=MessageStatus(message.status),
                created_at=message.created_at,
                cost=None
            ))
        
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no envio bulk de SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/", response_model=SMSListResponse)
async def list_sms(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    status: Optional[MessageStatus] = Query(None, description="Filtrar por status"),
    phone_number: Optional[str] = Query(None, description="Filtrar por número"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    search: Optional[str] = Query(None, description="Buscar na mensagem"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista SMS do usuário com paginação e filtros.
    
    - **page**: Número da página (inicia em 1)
    - **per_page**: Items por página (1-100)
    - **status**: Filtrar por status (pending, sent, delivered, failed)
    - **phone_number**: Filtrar por número de telefone
    - **date_from**: Data inicial (ISO format)
    - **date_to**: Data final (ISO format)
    - **search**: Buscar texto na mensagem
    """
    try:
        # Construir query base
        query = db.query(Message).filter(
            Message.user_id == current_user.id,
            Message.message_type == MessageType.SMS.value
        )
        
        # Aplicar filtros
        if status:
            query = query.filter(Message.status == status.value)
        
        if phone_number:
            query = query.filter(Message.phone_number.contains(phone_number))
        
        if date_from:
            query = query.filter(Message.created_at >= date_from)
        
        if date_to:
            query = query.filter(Message.created_at <= date_to)
        
        if search:
            query = query.filter(Message.message.contains(search))
        
        # Contar total
        total = query.count()
        
        # Aplicar paginação e ordenação
        messages = query.order_by(Message.created_at.desc())\
                       .offset((page - 1) * per_page)\
                       .limit(per_page)\
                       .all()
        
        # Preparar response
        sms_responses = []
        for message in messages:
            sms_responses.append(SMSResponse(
                id=message.id,
                to=message.phone_number,
                message=message.message,
                status=MessageStatus(message.status),
                created_at=message.created_at,
                cost=message.cost
            ))
        
        return SMSListResponse(
            messages=sms_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=total > page * per_page
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{message_id}", response_model=SMSResponse)
async def get_sms_detail(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um SMS específico.
    
    - **message_id**: ID único da mensagem
    """
    try:
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == current_user.id,
            Message.message_type == MessageType.SMS.value
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem não encontrada"
            )
        
        return SMSResponse(
            id=message.id,
            to=message.phone_number,
            message=message.message,
            status=MessageStatus(message.status),
            created_at=message.created_at,
            cost=message.cost
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/{message_id}")
async def delete_sms(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove um SMS (apenas se ainda não foi enviado).
    
    - **message_id**: ID único da mensagem
    """
    try:
        message = db.query(Message).filter(
            Message.id == message_id,
            Message.user_id == current_user.id,
            Message.message_type == MessageType.SMS.value
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensagem não encontrada"
            )
        
        # Só permite remover se ainda não foi enviada
        if message.status not in [MessageStatus.PENDING.value, MessageStatus.SCHEDULED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover mensagem já processada"
            )
        
        db.delete(message)
        db.commit()
        
        logger.info(f"SMS removido: {message_id}")
        
        return {
            "success": True,
            "message": "SMS removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/stats/summary")
async def get_sms_stats(
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas de SMS do usuário.
    
    - **date_from**: Data inicial para estatísticas
    - **date_to**: Data final para estatísticas
    """
    try:
        # Query base
        query = db.query(Message).filter(
            Message.user_id == current_user.id,
            Message.message_type == MessageType.SMS.value
        )
        
        # Aplicar filtros de data
        if date_from:
            query = query.filter(Message.created_at >= date_from)
        if date_to:
            query = query.filter(Message.created_at <= date_to)
        
        # Calcular estatísticas
        total_messages = query.count()
        sent_messages = query.filter(Message.status == MessageStatus.SENT.value).count()
        delivered_messages = query.filter(Message.status == MessageStatus.DELIVERED.value).count()
        failed_messages = query.filter(Message.status == MessageStatus.FAILED.value).count()
        pending_messages = query.filter(Message.status == MessageStatus.PENDING.value).count()
        
        # Calcular custo total (se disponível)
        total_cost = db.query(db.func.sum(Message.cost)).filter(
            Message.user_id == current_user.id,
            Message.message_type == MessageType.SMS.value,
            Message.cost.isnot(None)
        ).scalar() or 0
        
        # Taxa de sucesso
        success_rate = 0
        if total_messages > 0:
            success_rate = round((delivered_messages / total_messages) * 100, 2)
        
        return {
            "total_messages": total_messages,
            "sent_messages": sent_messages,
            "delivered_messages": delivered_messages,
            "failed_messages": failed_messages,
            "pending_messages": pending_messages,
            "success_rate": success_rate,
            "total_cost": float(total_cost),
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
