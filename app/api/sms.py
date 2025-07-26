from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import SMS, SMSStatus, SMSDirection, SMSQueue, SMSCommand, SMSResponse, Contact, ContactGroup, ContactGroupMember
from app.api.schemas import (
    SMSCreate, SMSBulkCreate, SMSResponse as SMSResponseSchema, 
    WebhookSMS, MessageResponse, DashboardStats, QueueStatusResponse,
    SMSStatusUpdate, SMSContactCreate
)
from app.services.sms_service import SMSService
from app.services.command_service import CommandService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Serviços serão inicializados dinamicamente
sms_service = None
command_service = None

def get_sms_service():
    """Obter instância do serviço SMS (lazy loading)"""
    global sms_service
    if sms_service is None:
        from app.services.sms_service import SMSService
        sms_service = SMSService()
    return sms_service

def get_command_service():
    """Obter instância do serviço de comandos (lazy loading)"""
    global command_service
    if command_service is None:
        from app.services.command_service import CommandService
        command_service = CommandService()
    return command_service

@router.post("/send", response_model=SMSResponseSchema)
async def send_sms(
    sms_data: SMSCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enviar um SMS individual"""
    try:
        # Criar registro na base de dados
        sms = SMS(
            phone_from="",  # Será preenchido pelo serviço
            phone_to=sms_data.phone_to,
            message=sms_data.message,
            status=SMSStatus.PENDING,
            direction=SMSDirection.OUTBOUND
        )
        db.add(sms)
        db.commit()
        db.refresh(sms)
        
        # Processar regras de reencaminhamento para SMS de saída
        from app.services.forwarding_service import ForwardingRuleService
        forwarding_service = ForwardingRuleService(db)
        forwarding_result = forwarding_service.process_sms(sms)
        
        # Se foi bloqueado ou deletado, não enviar
        if forwarding_result.get('blocked') or forwarding_result.get('deleted'):
            if forwarding_result.get('deleted'):
                db.delete(sms)
                db.commit()
                logger.info(f"SMS para {sms_data.phone_to} foi cancelado e deletado por regra")
            else:
                sms.status = SMSStatus.FAILED
                sms.error_message = "Bloqueado por regra de filtragem"
                db.commit()
                logger.info(f"SMS para {sms_data.phone_to} foi bloqueado por regra")
            
            return SMSResponseSchema.from_orm(sms)
        
        # Enviar SMS em background se não foi bloqueado
        service = get_sms_service()
        background_tasks.add_task(service.send_sms, sms.id, db)
        
        if forwarding_result.get('forwarded'):
            logger.info(f"SMS para {sms_data.phone_to} foi reencaminhado para {len(forwarding_result['forwarded'])} destinatário(s)")
        
        return SMSResponseSchema.from_orm(sms)
        
    except Exception as e:
        logger.error(f"Erro ao enviar SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao enviar SMS"
        )

@router.post("/send-bulk", response_model=MessageResponse)
async def send_bulk_sms(
    bulk_data: SMSBulkCreate,
    db: Session = Depends(get_db)
):
    """Enviar SMS em massa (adiciona à fila)"""
    try:
        total_added = 0
        
        for phone in bulk_data.phones:
            queue_item = SMSQueue(
                phone_to=phone,
                message=bulk_data.message,
                priority=bulk_data.priority or 0,
                scheduled_for=bulk_data.scheduled_for
            )
            db.add(queue_item)
            total_added += 1
        
        db.commit()
        
        return MessageResponse(
            message=f"{total_added} SMS adicionados à fila de envio",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Erro ao adicionar SMS à fila: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao adicionar SMS à fila"
        )

@router.post("/send-contacts", response_model=MessageResponse)
async def send_sms_to_contacts(
    contact_data: SMSContactCreate,
    db: Session = Depends(get_db)
):
    """Enviar SMS para contactos e/ou grupos específicos"""
    try:
        logger.info(f"Enviando SMS para contactos: {contact_data.contacts}, grupos: {contact_data.groups}, mensagem: {contact_data.message[:50]}...")
        
        phone_numbers = []
        
        # Obter números dos contactos
        if contact_data.contacts:
            contacts = db.query(Contact).filter(
                Contact.id.in_(contact_data.contacts),
                Contact.is_active == True
            ).all()
            
            logger.info(f"Contactos encontrados: {len(contacts)}")
            
            for contact in contacts:
                contact_phones = contact.phone_numbers
                logger.info(f"Contacto {contact.name}: números {contact_phones}")
                phone_numbers.extend(contact_phones)
        
        # Obter números dos grupos
        if contact_data.groups:
            group_contacts = db.query(Contact).join(ContactGroupMember).filter(
                ContactGroupMember.group_id.in_(contact_data.groups),
                Contact.is_active == True
            ).all()
            
            logger.info(f"Contactos de grupos encontrados: {len(group_contacts)}")
            
            for contact in group_contacts:
                contact_phones = contact.phone_numbers
                logger.info(f"Contacto do grupo {contact.name}: números {contact_phones}")
                phone_numbers.extend(contact_phones)
        
        # Remover duplicados
        phone_numbers = list(set(phone_numbers))
        logger.info(f"Números únicos para envio: {phone_numbers}")
        
        if not phone_numbers:
            logger.warning("Nenhum número de telefone encontrado")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum número de telefone encontrado nos contactos/grupos selecionados"
            )
        
        # Adicionar SMS à fila
        total_added = 0
        for phone in phone_numbers:
            logger.info(f"Adicionando SMS à fila para: {phone}")
            queue_item = SMSQueue(
                phone_to=phone,
                message=contact_data.message,
                priority=contact_data.priority or 0,
                scheduled_for=contact_data.scheduled_for
            )
            db.add(queue_item)
            total_added += 1
        
        db.commit()
        logger.info(f"Total de {total_added} SMS adicionados à fila")
        
        return MessageResponse(
            message=f"{total_added} SMS adicionados à fila de envio para contactos/grupos selecionados",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar SMS para contactos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar envio para contactos"
        )

@router.post("/webhook", response_model=MessageResponse)
async def receive_sms_webhook(
    webhook_data: WebhookSMS,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook para receber SMS do provedor (ex: Twilio)"""
    try:
        # Criar registro de SMS recebido
        sms = SMS(
            phone_from=webhook_data.From,
            phone_to=webhook_data.To,
            message=webhook_data.Body,
            status=SMSStatus.RECEIVED,
            direction=SMSDirection.INBOUND,
            external_id=webhook_data.MessageSid
        )
        db.add(sms)
        db.commit()
        db.refresh(sms)
        
        # Processar regras de reencaminhamento e filtragem
        from app.services.forwarding_service import ForwardingRuleService
        forwarding_service = ForwardingRuleService(db)
        forwarding_result = forwarding_service.process_sms(sms)
        
        # Se a mensagem foi bloqueada ou deletada, não processar comandos
        if not forwarding_result.get('blocked') and not forwarding_result.get('deleted'):
            # Processar comandos automáticos em background
            service = get_command_service()
            background_tasks.add_task(service.process_incoming_sms, sms.id, db)
        else:
            # Se foi bloqueada ou deletada, remover do banco de dados
            if forwarding_result.get('deleted'):
                db.delete(sms)
                db.commit()
                logger.info(f"SMS de {webhook_data.From} foi deletado por regra de filtragem")
            else:
                logger.info(f"SMS de {webhook_data.From} foi bloqueado por regra de filtragem")
        
        logger.info(f"SMS recebido de {webhook_data.From}: {webhook_data.Body[:50]}...")
        if forwarding_result.get('forwarded'):
            logger.info(f"SMS reencaminhado para {len(forwarding_result['forwarded'])} destinatário(s)")
        
        return MessageResponse(
            message="SMS recebido e processado com sucesso",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar SMS recebido"
        )

@router.get("/status/{sms_id}", response_model=SMSResponseSchema)
async def get_sms_status(sms_id: int, db: Session = Depends(get_db)):
    """Obter status de um SMS específico"""
    sms = db.query(SMS).filter(SMS.id == sms_id).first()
    if not sms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS não encontrado"
        )
    
    return SMSResponseSchema.from_orm(sms)

@router.put("/status/{sms_id}", response_model=MessageResponse)
async def update_sms_status(
    sms_id: int,
    status_update: SMSStatusUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar status de um SMS (usado por webhooks de status)"""
    sms = db.query(SMS).filter(SMS.id == sms_id).first()
    if not sms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SMS não encontrado"
        )
    
    sms.status = status_update.status
    if status_update.external_id:
        sms.external_id = status_update.external_id
    if status_update.error_message:
        sms.error_message = status_update.error_message
    
    db.commit()
    
    return MessageResponse(
        message="Status do SMS atualizado com sucesso",
        success=True
    )

@router.get("/list")
async def get_sms_list(
    limit: int = 50,
    offset: int = 0,
    direction: Optional[str] = None,
    status: Optional[str] = None,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
    message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obter lista de SMS com filtros"""
    try:
        query = db.query(SMS)
        
        # Aplicar filtros
        if direction:
            if direction == "inbound":
                query = query.filter(SMS.direction == SMSDirection.INBOUND)
            elif direction == "outbound":
                query = query.filter(SMS.direction == SMSDirection.OUTBOUND)
        
        if status:
            if status == "pending":
                query = query.filter(SMS.status == SMSStatus.PENDING)
            elif status == "sent":
                query = query.filter(SMS.status == SMSStatus.SENT)
            elif status == "delivered":
                query = query.filter(SMS.status == SMSStatus.DELIVERED)
            elif status == "failed":
                query = query.filter(SMS.status == SMSStatus.FAILED)
            elif status == "received":
                query = query.filter(SMS.status == SMSStatus.RECEIVED)
        
        if sender:
            query = query.filter(SMS.phone_from.contains(sender))
            
        if recipient:
            query = query.filter(SMS.phone_to.contains(recipient))
        
        if message:
            query = query.filter(SMS.message.contains(message))
        
        # Contar total antes da paginação
        total_count = query.count()
        
        # Ordenar por data mais recente e aplicar paginação
        sms_list = query.order_by(SMS.created_at.desc()).offset(offset).limit(limit).all()
        
        # Converter para dict para JSON
        sms_data = []
        for sms in sms_list:
            sms_data.append({
                'id': sms.id,
                'phone_from': sms.phone_from or '',
                'phone_to': sms.phone_to or '',
                'message': sms.message or '',
                'status': sms.status.value if sms.status else 'unknown',
                'direction': sms.direction.value if sms.direction else 'unknown',
                'created_at': sms.created_at.isoformat() if sms.created_at else '',
                'sent_at': sms.sent_at.isoformat() if sms.sent_at else '',
                'received_at': sms.created_at.isoformat() if sms.direction == SMSDirection.INBOUND and sms.created_at else '',
                'external_id': sms.external_id or '',
                'error_message': sms.error_message or ''
            })
        
        return {
            'success': True,
            'data': sms_data,
            'total': len(sms_data),
            'total_count': total_count,
            'message': f'{len(sms_data)} SMS encontrados de {total_count} total'
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar SMS: {str(e)}")
        return {
            'success': False,
            'data': [],
            'total': 0,
            'message': f'Erro ao carregar SMS: {str(e)}'
        }

@router.delete("/{sms_id}")
async def delete_sms(sms_id: int, db: Session = Depends(get_db)):
    """Excluir um SMS"""
    try:
        sms = db.query(SMS).filter(SMS.id == sms_id).first()
        if not sms:
            return {
                'success': False,
                'message': 'SMS não encontrado'
            }
        
        db.delete(sms)
        db.commit()
        
        return {
            'success': True,
            'message': f'SMS {sms_id} excluído com sucesso'
        }
    
    except Exception as e:
        logger.error(f"Erro ao excluir SMS {sms_id}: {str(e)}")
        return {
            'success': False,
            'message': f'Erro ao excluir SMS: {str(e)}'
        }

@router.get("/inbox", response_model=List[SMSResponseSchema])
async def get_inbox(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Obter SMS recebidos (inbox)"""
    sms_list = db.query(SMS).filter(
        SMS.direction == SMSDirection.INBOUND
    ).order_by(SMS.created_at.desc()).offset(offset).limit(limit).all()
    
    return [SMSResponseSchema.from_orm(sms) for sms in sms_list]

@router.get("/outbox", response_model=List[SMSResponseSchema])
async def get_outbox(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Obter SMS enviados (outbox)"""
    query = db.query(SMS).filter(SMS.direction == SMSDirection.OUTBOUND)
    
    if status_filter:
        query = query.filter(SMS.status == status_filter)
    
    sms_list = query.order_by(SMS.created_at.desc()).offset(offset).limit(limit).all()
    
    return [SMSResponseSchema.from_orm(sms) for sms in sms_list]

@router.get("/queue/status", response_model=QueueStatusResponse)
async def get_queue_status(db: Session = Depends(get_db)):
    """Obter status da fila de SMS"""
    try:
        from app.services.queue_processor import queue_processor
        
        # Status do processador
        processor_status = queue_processor.get_queue_status()
        
        # Status da base de dados
        total_pending = db.query(SMSQueue).filter(SMSQueue.processed == False).count()
        total_processed = db.query(SMSQueue).filter(SMSQueue.processed == True).count()
        
        next_scheduled = db.query(SMSQueue.scheduled_for).filter(
            SMSQueue.processed == False,
            SMSQueue.scheduled_for.isnot(None)
        ).order_by(SMSQueue.scheduled_for.asc()).first()
        
        return QueueStatusResponse(
            total_pending=total_pending,
            total_processed=total_processed,
            next_scheduled=next_scheduled[0] if next_scheduled else None,
            processor_running=processor_status.get("is_running", False)
        )
    
    except Exception as e:
        logger.error(f"Erro ao obter status da fila: {str(e)}")
        return QueueStatusResponse(
            total_pending=0,
            total_processed=0,
            next_scheduled=None,
            processor_running=False
        )

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obter estatísticas para o dashboard"""
    total_sent = db.query(SMS).filter(
        SMS.direction == SMSDirection.OUTBOUND,
        SMS.status.in_([SMSStatus.SENT, SMSStatus.DELIVERED])
    ).count()
    
    total_received = db.query(SMS).filter(
        SMS.direction == SMSDirection.INBOUND
    ).count()
    
    total_pending = db.query(SMS).filter(
        SMS.status == SMSStatus.PENDING
    ).count()
    
    total_failed = db.query(SMS).filter(
        SMS.status == SMSStatus.FAILED
    ).count()
    
    total_outbound = db.query(SMS).filter(
        SMS.direction == SMSDirection.OUTBOUND
    ).count()
    
    success_rate = (total_sent / total_outbound * 100) if total_outbound > 0 else 0
    
    commands_active = db.query(SMSCommand).filter(
        SMSCommand.is_active == True
    ).count()
    
    return DashboardStats(
        total_sms_sent=total_sent,
        total_sms_received=total_received,
        total_sms_pending=total_pending,
        total_sms_failed=total_failed,
        success_rate=round(success_rate, 2),
        commands_active=commands_active
    )
