from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import ForwardingRule, ForwardingRuleLog
from app.api.schemas_forwarding import (
    ForwardingRuleCreate, ForwardingRuleUpdate, ForwardingRuleResponse,
    ForwardingRuleLogResponse, ForwardingRuleStats, MessageResponse
)
from app.services.forwarding_service import ForwardingRuleService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_forwarding_service(db: Session = Depends(get_db)) -> ForwardingRuleService:
    """Obter instância do serviço de regras"""
    return ForwardingRuleService(db)


@router.post("/forwarding/rules", response_model=ForwardingRuleResponse)
async def create_forwarding_rule(
    rule_data: ForwardingRuleCreate,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Criar nova regra de reencaminhamento"""
    try:
        rule = service.create_rule(rule_data)
        return rule
    except Exception as e:
        logger.error(f"Erro ao criar regra: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forwarding/rules", response_model=List[ForwardingRuleResponse])
async def get_forwarding_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Obter lista de regras de reencaminhamento"""
    try:
        rules = service.get_rules(skip=skip, limit=limit, active_only=active_only)
        return rules
    except Exception as e:
        logger.error(f"Erro ao obter regras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forwarding/rules/{rule_id}", response_model=ForwardingRuleResponse)
async def get_forwarding_rule(
    rule_id: int,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Obter regra específica por ID"""
    try:
        rule = service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter regra {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/forwarding/rules/{rule_id}", response_model=ForwardingRuleResponse)
async def update_forwarding_rule(
    rule_id: int,
    rule_data: ForwardingRuleUpdate,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Atualizar regra de reencaminhamento"""
    try:
        rule = service.update_rule(rule_id, rule_data)
        if not rule:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar regra {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/forwarding/rules/{rule_id}", response_model=MessageResponse)
async def delete_forwarding_rule(
    rule_id: int,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Deletar regra de reencaminhamento"""
    try:
        success = service.delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        return MessageResponse(
            success=True,
            message=f"Regra {rule_id} deletada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar regra {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forwarding/rules/{rule_id}/toggle", response_model=ForwardingRuleResponse)
async def toggle_forwarding_rule(
    rule_id: int,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Alternar estado ativo/inativo da regra"""
    try:
        rule = service.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        # Alternar estado
        update_data = ForwardingRuleUpdate(is_active=not rule.is_active)
        rule = service.update_rule(rule_id, update_data)
        
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alternar regra {rule_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forwarding/logs", response_model=List[ForwardingRuleLogResponse])
async def get_forwarding_logs(
    rule_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Obter logs de aplicação das regras"""
    try:
        logs = service.get_rule_logs(rule_id=rule_id, limit=limit)
        
        # Enriquecer dados dos logs
        enriched_logs = []
        for log in logs:
            log_data = {
                'id': log.id,
                'rule_id': log.rule_id,
                'original_sms_id': log.original_sms_id,
                'forwarded_sms_id': log.forwarded_sms_id,
                'action_taken': log.action_taken,
                'matched_criteria': log.matched_criteria,
                'applied_at': log.applied_at,
                'rule_name': log.rule.name if log.rule else None,
                'original_message': log.original_sms.message if log.original_sms else None,
                'original_sender': log.original_sms.phone_from if log.original_sms else None
            }
            enriched_logs.append(ForwardingRuleLogResponse(**log_data))
        
        return enriched_logs
    except Exception as e:
        logger.error(f"Erro ao obter logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forwarding/stats", response_model=ForwardingRuleStats)
async def get_forwarding_stats(
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """Obter estatísticas das regras de reencaminhamento"""
    try:
        stats = service.get_stats()
        return ForwardingRuleStats(**stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forwarding/test", response_model=MessageResponse)
async def test_forwarding_rules(
    test_message: str,
    test_sender: str,
    test_recipient: str,
    service: ForwardingRuleService = Depends(get_forwarding_service)
):
    """
    Testar regras contra uma mensagem simulada
    (Não envia SMS, apenas verifica quais regras seriam aplicadas)
    """
    try:
        from app.db.models import SMS, SMSDirection, SMSStatus
        
        # Criar SMS temporário para teste (não salvar no DB)
        test_sms = SMS(
            phone_from=test_sender,
            phone_to=test_recipient,
            message=test_message,
            direction=SMSDirection.INBOUND,
            status=SMSStatus.RECEIVED
        )
        
        # Obter regras ativas
        rules = service.get_rules(active_only=True, limit=1000)
        
        matched_rules = []
        for rule in rules:
            if service._matches_rule(test_sms, rule):
                matched_rules.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'rule_type': rule.rule_type.value,
                    'action': rule.action.value,
                    'priority': rule.priority
                })
        
        return MessageResponse(
            success=True,
            message=f"Teste concluído. {len(matched_rules)} regra(s) correspondem.",
            data={
                'matched_rules': matched_rules,
                'test_message': test_message,
                'test_sender': test_sender,
                'test_recipient': test_recipient
            }
        )
    except Exception as e:
        logger.error(f"Erro no teste de regras: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
