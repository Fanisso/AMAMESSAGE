"""
Endpoints de Regras de Reencaminhamento - API v2
Gestão completa de regras automáticas para SMS
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import re

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import (
    ForwardingRuleCreate, ForwardingRuleUpdate, ForwardingRuleResponse,
    PaginationQuery
)
from shared.constants import MAX_FORWARDING_RULES_PER_USER
from shared.utils import validate_phone_number

# Imports locais
from ...db.database import get_db
from ...db.models import User, ForwardingRule
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def validate_regex_pattern(pattern: str) -> bool:
    """Valida se o pattern regex é válido."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

@router.post("/", response_model=ForwardingRuleResponse)
async def create_forwarding_rule(
    rule_data: ForwardingRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria nova regra de reencaminhamento.
    
    - **name**: Nome da regra (obrigatório)
    - **description**: Descrição da regra (opcional)
    - **condition_type**: Tipo de condição (contains, equals, starts_with, regex)
    - **condition_value**: Valor da condição
    - **source_numbers**: Números de origem (opcional, vazio = qualquer número)
    - **action_type**: Tipo de ação (forward, auto_reply, block, alert)
    - **action_value**: Valor da ação (número para forward, mensagem para auto_reply)
    - **priority**: Prioridade da regra (0-100, maior = mais prioritária)
    - **is_active**: Se a regra está ativa
    """
    try:
        # Verificar limite de regras
        rule_count = db.query(ForwardingRule).filter(ForwardingRule.user_id == current_user.id).count()
        if rule_count >= MAX_FORWARDING_RULES_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limite máximo de {MAX_FORWARDING_RULES_PER_USER} regras atingido"
            )
        
        # Validar pattern regex se necessário
        if rule_data.condition_type == "regex":
            if not validate_regex_pattern(rule_data.condition_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pattern regex inválido"
                )
        
        # Validar números de origem se fornecidos
        if rule_data.source_numbers:
            for phone in rule_data.source_numbers:
                if not validate_phone_number(phone):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Número de origem inválido: {phone}"
                    )
        
        # Validar action_value baseado no action_type
        if rule_data.action_type == "forward":
            if not validate_phone_number(rule_data.action_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Número de reencaminhamento inválido"
                )
        elif rule_data.action_type == "auto_reply":
            if not rule_data.action_value or len(rule_data.action_value.strip()) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mensagem de resposta automática é obrigatória"
                )
        
        # Verificar se já existe regra com mesmo nome
        existing_rule = db.query(ForwardingRule).filter(
            ForwardingRule.user_id == current_user.id,
            ForwardingRule.name == rule_data.name
        ).first()
        
        if existing_rule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma regra com este nome"
            )
        
        # Criar nova regra
        new_rule = ForwardingRule(
            user_id=current_user.id,
            name=rule_data.name,
            description=rule_data.description,
            condition_type=rule_data.condition_type,
            condition_value=rule_data.condition_value,
            source_numbers=rule_data.source_numbers,
            action_type=rule_data.action_type,
            action_value=rule_data.action_value,
            priority=rule_data.priority,
            is_active=rule_data.is_active,
            created_at=datetime.utcnow()
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        logger.info(f"Regra criada: {new_rule.id} - {new_rule.name}")
        
        return ForwardingRuleResponse(
            id=new_rule.id,
            name=new_rule.name,
            description=new_rule.description,
            condition_type=new_rule.condition_type,
            condition_value=new_rule.condition_value,
            source_numbers=new_rule.source_numbers,
            action_type=new_rule.action_type,
            action_value=new_rule.action_value,
            priority=new_rule.priority,
            is_active=new_rule.is_active,
            created_at=new_rule.created_at,
            updated_at=new_rule.updated_at,
            trigger_count=new_rule.trigger_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/", response_model=List[ForwardingRuleResponse])
async def list_forwarding_rules(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(50, ge=1, le=100, description="Items por página"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    action_type: Optional[str] = Query(None, description="Filtrar por tipo de ação"),
    search: Optional[str] = Query(None, description="Buscar por nome"),
    sort_by: Optional[str] = Query("priority", description="Campo para ordenação"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$", description="Ordem"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista regras de reencaminhamento do usuário.
    
    - **page**: Número da página (inicia em 1)
    - **per_page**: Items por página (1-100)
    - **is_active**: Filtrar por status ativo
    - **action_type**: Filtrar por tipo de ação
    - **search**: Buscar por nome da regra
    - **sort_by**: Campo para ordenação (priority, name, created_at, trigger_count)
    - **sort_order**: Ordem de classificação (asc/desc)
    """
    try:
        # Construir query base
        query = db.query(ForwardingRule).filter(ForwardingRule.user_id == current_user.id)
        
        # Aplicar filtros
        if is_active is not None:
            query = query.filter(ForwardingRule.is_active == is_active)
        
        if action_type:
            query = query.filter(ForwardingRule.action_type == action_type)
        
        if search:
            query = query.filter(ForwardingRule.name.contains(search))
        
        # Aplicar ordenação
        if sort_by == "priority":
            order_field = ForwardingRule.priority
        elif sort_by == "name":
            order_field = ForwardingRule.name
        elif sort_by == "created_at":
            order_field = ForwardingRule.created_at
        elif sort_by == "trigger_count":
            order_field = ForwardingRule.trigger_count
        else:
            order_field = ForwardingRule.priority
        
        if sort_order == "desc":
            order_field = order_field.desc()
        
        # Aplicar paginação
        rules = query.order_by(order_field)\
                    .offset((page - 1) * per_page)\
                    .limit(per_page)\
                    .all()
        
        # Preparar response
        rule_responses = []
        for rule in rules:
            rule_responses.append(ForwardingRuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                condition_type=rule.condition_type,
                condition_value=rule.condition_value,
                source_numbers=rule.source_numbers,
                action_type=rule.action_type,
                action_value=rule.action_value,
                priority=rule.priority,
                is_active=rule.is_active,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
                trigger_count=rule.trigger_count
            ))
        
        return rule_responses
        
    except Exception as e:
        logger.error(f"Erro ao listar regras: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{rule_id}", response_model=ForwardingRuleResponse)
async def get_forwarding_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de uma regra específica.
    
    - **rule_id**: ID único da regra
    """
    try:
        rule = db.query(ForwardingRule).filter(
            ForwardingRule.id == rule_id,
            ForwardingRule.user_id == current_user.id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        
        return ForwardingRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            condition_type=rule.condition_type,
            condition_value=rule.condition_value,
            source_numbers=rule.source_numbers,
            action_type=rule.action_type,
            action_value=rule.action_value,
            priority=rule.priority,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            trigger_count=rule.trigger_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/{rule_id}", response_model=ForwardingRuleResponse)
async def update_forwarding_rule(
    rule_id: int,
    rule_update: ForwardingRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza regra de reencaminhamento existente.
    
    - **rule_id**: ID único da regra
    - Campos da regra para atualização (todos opcionais)
    """
    try:
        rule = db.query(ForwardingRule).filter(
            ForwardingRule.id == rule_id,
            ForwardingRule.user_id == current_user.id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        
        # Verificar se novo nome já existe (se foi alterado)
        if rule_update.name and rule_update.name != rule.name:
            existing_rule = db.query(ForwardingRule).filter(
                ForwardingRule.user_id == current_user.id,
                ForwardingRule.name == rule_update.name,
                ForwardingRule.id != rule_id
            ).first()
            
            if existing_rule:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma regra com este nome"
                )
        
        # Validar pattern regex se foi alterado
        if rule_update.condition_type == "regex" and rule_update.condition_value:
            if not validate_regex_pattern(rule_update.condition_value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Pattern regex inválido"
                )
        
        # Validar números de origem se foram alterados
        if rule_update.source_numbers is not None:
            for phone in rule_update.source_numbers:
                if not validate_phone_number(phone):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Número de origem inválido: {phone}"
                    )
        
        # Validar action_value baseado no action_type
        if rule_update.action_type and rule_update.action_value:
            if rule_update.action_type == "forward":
                if not validate_phone_number(rule_update.action_value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Número de reencaminhamento inválido"
                    )
        
        # Atualizar campos
        update_data = rule_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        rule.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Regra atualizada: {rule.id} - {rule.name}")
        
        return ForwardingRuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            condition_type=rule.condition_type,
            condition_value=rule.condition_value,
            source_numbers=rule.source_numbers,
            action_type=rule.action_type,
            action_value=rule.action_value,
            priority=rule.priority,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            trigger_count=rule.trigger_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/{rule_id}")
async def delete_forwarding_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove regra de reencaminhamento.
    
    - **rule_id**: ID único da regra
    """
    try:
        rule = db.query(ForwardingRule).filter(
            ForwardingRule.id == rule_id,
            ForwardingRule.user_id == current_user.id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        
        rule_name = rule.name
        db.delete(rule)
        db.commit()
        
        logger.info(f"Regra removida: {rule_id} - {rule_name}")
        
        return {
            "success": True,
            "message": "Regra removida com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/{rule_id}/toggle")
async def toggle_forwarding_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Alterna status ativo/inativo da regra.
    
    - **rule_id**: ID único da regra
    """
    try:
        rule = db.query(ForwardingRule).filter(
            ForwardingRule.id == rule_id,
            ForwardingRule.user_id == current_user.id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        
        # Alternar status
        rule.is_active = not rule.is_active
        rule.updated_at = datetime.utcnow()
        db.commit()
        
        status_text = "ativada" if rule.is_active else "desativada"
        logger.info(f"Regra {status_text}: {rule.id} - {rule.name}")
        
        return {
            "success": True,
            "is_active": rule.is_active,
            "message": f"Regra {status_text} com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alternar regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/{rule_id}/test")
async def test_forwarding_rule(
    rule_id: int,
    test_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Testa regra de reencaminhamento com mensagem exemplo.
    
    - **rule_id**: ID único da regra
    - **message**: Mensagem para testar
    - **source_number**: Número de origem (opcional)
    """
    try:
        rule = db.query(ForwardingRule).filter(
            ForwardingRule.id == rule_id,
            ForwardingRule.user_id == current_user.id
        ).first()
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Regra não encontrada"
            )
        
        test_message = test_data.get('message', '')
        test_source = test_data.get('source_number', '+258123456789')
        
        if not test_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mensagem de teste é obrigatória"
            )
        
        # Testar condição
        matches = False
        
        # Verificar número de origem (se especificado na regra)
        source_matches = True
        if rule.source_numbers:
            source_matches = test_source in rule.source_numbers
        
        # Verificar condição da mensagem
        if rule.condition_type == "contains":
            matches = rule.condition_value.lower() in test_message.lower()
        elif rule.condition_type == "equals":
            matches = rule.condition_value.lower() == test_message.lower()
        elif rule.condition_type == "starts_with":
            matches = test_message.lower().startswith(rule.condition_value.lower())
        elif rule.condition_type == "regex":
            try:
                matches = bool(re.search(rule.condition_value, test_message, re.IGNORECASE))
            except re.error:
                matches = False
        
        # Resultado final
        would_trigger = matches and source_matches and rule.is_active
        
        result = {
            "would_trigger": would_trigger,
            "rule_active": rule.is_active,
            "source_matches": source_matches,
            "condition_matches": matches,
            "test_details": {
                "message": test_message,
                "source_number": test_source,
                "condition_type": rule.condition_type,
                "condition_value": rule.condition_value,
                "action_type": rule.action_type,
                "action_value": rule.action_value
            }
        }
        
        if would_trigger:
            result["action_result"] = f"Ação '{rule.action_type}' seria executada com valor: {rule.action_value}"
        else:
            reasons = []
            if not rule.is_active:
                reasons.append("regra está inativa")
            if not source_matches:
                reasons.append("número de origem não coincide")
            if not matches:
                reasons.append("condição da mensagem não é atendida")
            
            result["no_action_reason"] = "Regra não seria acionada: " + ", ".join(reasons)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao testar regra: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/stats/summary")
async def get_forwarding_rules_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas das regras de reencaminhamento.
    """
    try:
        # Estatísticas gerais
        total_rules = db.query(ForwardingRule).filter(ForwardingRule.user_id == current_user.id).count()
        active_rules = db.query(ForwardingRule).filter(
            ForwardingRule.user_id == current_user.id,
            ForwardingRule.is_active == True
        ).count()
        
        # Estatísticas por tipo de ação
        action_stats = db.query(
            ForwardingRule.action_type,
            db.func.count(ForwardingRule.id).label('count')
        ).filter(
            ForwardingRule.user_id == current_user.id
        ).group_by(ForwardingRule.action_type).all()
        
        # Total de triggers
        total_triggers = db.query(
            db.func.sum(ForwardingRule.trigger_count)
        ).filter(ForwardingRule.user_id == current_user.id).scalar() or 0
        
        # Regras mais acionadas
        top_rules = db.query(ForwardingRule).filter(
            ForwardingRule.user_id == current_user.id,
            ForwardingRule.trigger_count > 0
        ).order_by(ForwardingRule.trigger_count.desc()).limit(5).all()
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "inactive_rules": total_rules - active_rules,
            "total_triggers": int(total_triggers),
            "action_type_distribution": {
                action_type: count for action_type, count in action_stats
            },
            "top_triggered_rules": [
                {
                    "id": rule.id,
                    "name": rule.name,
                    "trigger_count": rule.trigger_count,
                    "action_type": rule.action_type
                }
                for rule in top_rules
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de regras: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
