from sqlalchemy.orm import Session
from app.db.models import (
    ForwardingRule, ForwardingRuleLog, SMS, Contact, ContactGroup, ContactGroupMember,
    ForwardingRuleType, ForwardingRuleAction, SMSDirection, SMSStatus
)
from app.api.schemas_forwarding import ForwardingRuleCreate, ForwardingRuleUpdate
from typing import List, Optional, Dict, Any
import json
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ForwardingRuleService:
    """Serviço para gerenciar regras de reencaminhamento e filtragem de SMS"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rule(self, rule_data: ForwardingRuleCreate) -> ForwardingRule:
        """Criar nova regra de reencaminhamento"""
        # Converter lista de números para JSON
        forward_to_numbers = None
        if rule_data.forward_to_numbers:
            forward_to_numbers = json.dumps(rule_data.forward_to_numbers)
        
        db_rule = ForwardingRule(
            name=rule_data.name,
            description=rule_data.description,
            is_active=rule_data.is_active,
            rule_type=rule_data.rule_type,
            action=rule_data.action,
            sender_pattern=rule_data.sender_pattern,
            recipient_pattern=rule_data.recipient_pattern,
            keyword_pattern=rule_data.keyword_pattern,
            forward_to_numbers=forward_to_numbers,
            forward_to_group_id=rule_data.forward_to_group_id,
            case_sensitive=rule_data.case_sensitive,
            whole_word_only=rule_data.whole_word_only,
            priority=rule_data.priority
        )
        
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        
        logger.info(f"Regra criada: {db_rule.name} (ID: {db_rule.id})")
        return db_rule
    
    def get_rule(self, rule_id: int) -> Optional[ForwardingRule]:
        """Obter regra por ID"""
        return self.db.query(ForwardingRule).filter(ForwardingRule.id == rule_id).first()
    
    def get_rules(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[ForwardingRule]:
        """Obter lista de regras"""
        query = self.db.query(ForwardingRule)
        
        if active_only:
            query = query.filter(ForwardingRule.is_active == True)
        
        return query.order_by(ForwardingRule.priority.desc(), ForwardingRule.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_rule(self, rule_id: int, rule_data: ForwardingRuleUpdate) -> Optional[ForwardingRule]:
        """Atualizar regra existente"""
        db_rule = self.get_rule(rule_id)
        if not db_rule:
            return None
        
        # Atualizar campos fornecidos
        update_data = rule_data.dict(exclude_unset=True)
        
        # Tratar lista de números
        if 'forward_to_numbers' in update_data:
            forward_to_numbers = update_data['forward_to_numbers']
            if forward_to_numbers:
                update_data['forward_to_numbers'] = json.dumps(forward_to_numbers)
            else:
                update_data['forward_to_numbers'] = None
        
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        self.db.commit()
        self.db.refresh(db_rule)
        
        logger.info(f"Regra atualizada: {db_rule.name} (ID: {db_rule.id})")
        return db_rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Deletar regra"""
        db_rule = self.get_rule(rule_id)
        if not db_rule:
            return False
        
        self.db.delete(db_rule)
        self.db.commit()
        
        logger.info(f"Regra deletada: {db_rule.name} (ID: {rule_id})")
        return True
    
    def process_sms(self, sms: SMS) -> Dict[str, Any]:
        """
        Processar SMS contra todas as regras ativas
        Retorna informações sobre ações tomadas
        """
        results = {
            'processed': False,
            'blocked': False,
            'deleted': False,
            'forwarded': [],
            'rules_applied': []
        }
        
        # Obter regras ativas ordenadas por prioridade
        rules = self.get_rules(active_only=True, limit=1000)
        
        for rule in rules:
            if self._matches_rule(sms, rule):
                action_result = self._apply_rule(sms, rule)
                results['rules_applied'].append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'action': rule.action.value,
                    'result': action_result
                })
                
                # Atualizar estatísticas da regra
                rule.match_count += 1
                rule.last_match_at = datetime.utcnow()
                
                # Processar ação
                if rule.action == ForwardingRuleAction.BLOCK:
                    results['blocked'] = True
                    results['processed'] = True
                    break  # Bloquear impede outras ações
                
                elif rule.action == ForwardingRuleAction.DELETE:
                    results['deleted'] = True
                    results['processed'] = True
                    break  # Deletar impede outras ações
                
                elif rule.action == ForwardingRuleAction.FORWARD:
                    results['forwarded'].extend(action_result.get('forwarded_to', []))
                    results['processed'] = True
        
        self.db.commit()
        return results
    
    def _matches_rule(self, sms: SMS, rule: ForwardingRule) -> bool:
        """Verificar se SMS corresponde à regra"""
        try:
            if rule.rule_type == ForwardingRuleType.SENDER_BASED:
                return self._matches_pattern(sms.phone_from, rule.sender_pattern)
            
            elif rule.rule_type == ForwardingRuleType.RECIPIENT_BASED:
                return self._matches_pattern(sms.phone_to, rule.recipient_pattern)
            
            elif rule.rule_type == ForwardingRuleType.KEYWORD_BASED:
                return self._matches_keywords(sms.message, rule.keyword_pattern, rule.case_sensitive, rule.whole_word_only)
            
            elif rule.rule_type == ForwardingRuleType.BLOCK_SENDER:
                return self._matches_pattern(sms.phone_from, rule.sender_pattern)
            
            elif rule.rule_type == ForwardingRuleType.BLOCK_KEYWORD:
                return self._matches_keywords(sms.message, rule.keyword_pattern, rule.case_sensitive, rule.whole_word_only)
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar regra {rule.id}: {str(e)}")
            return False
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Verificar se texto corresponde ao padrão"""
        if not text or not pattern:
            return False
        
        # Suporte a wildcards simples
        pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _matches_keywords(self, text: str, keywords: str, case_sensitive: bool, whole_word_only: bool) -> bool:
        """Verificar se texto contém palavras-chave"""
        if not text or not keywords:
            return False
        
        keyword_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for keyword in keyword_list:
            if whole_word_only:
                pattern = r'\b' + re.escape(keyword) + r'\b'
            else:
                pattern = re.escape(keyword)
            
            if re.search(pattern, text, flags):
                return True
        
        return False
    
    def _apply_rule(self, sms: SMS, rule: ForwardingRule) -> Dict[str, Any]:
        """Aplicar regra ao SMS"""
        result = {'success': False, 'forwarded_to': []}
        
        try:
            if rule.action == ForwardingRuleAction.FORWARD:
                result = self._forward_sms(sms, rule)
            
            # Registrar log da aplicação
            self._log_rule_application(sms, rule, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regra {rule.id} ao SMS {sms.id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _forward_sms(self, sms: SMS, rule: ForwardingRule) -> Dict[str, Any]:
        """Reencaminhar SMS"""
        forwarded_to = []
        
        # Coletar números de destino
        target_numbers = []
        
        # Números específicos
        if rule.forward_to_numbers:
            try:
                numbers = json.loads(rule.forward_to_numbers)
                target_numbers.extend(numbers)
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar números da regra {rule.id}")
        
        # Grupo de contatos
        if rule.forward_to_group_id:
            group_members = self.db.query(ContactGroupMember).join(Contact).filter(
                ContactGroupMember.group_id == rule.forward_to_group_id,
                Contact.is_active == True
            ).all()
            
            for member in group_members:
                target_numbers.append(member.contact.phone_number)
        
        # Criar SMS de reencaminhamento
        for number in target_numbers:
            if number != sms.phone_from and number != sms.phone_to:  # Evitar loops
                forward_message = f"[Reencaminhado de {sms.phone_from}] {sms.message}"
                
                forwarded_sms = SMS(
                    phone_from=sms.phone_to,  # Remetente é o destinatário original
                    phone_to=number,
                    message=forward_message,
                    status=SMSStatus.PENDING,
                    direction=SMSDirection.OUTBOUND
                )
                
                self.db.add(forwarded_sms)
                self.db.flush()  # Para obter o ID
                
                forwarded_to.append({
                    'number': number,
                    'sms_id': forwarded_sms.id
                })
        
        return {
            'success': True,
            'forwarded_to': forwarded_to,
            'count': len(forwarded_to)
        }
    
    def _log_rule_application(self, sms: SMS, rule: ForwardingRule, result: Dict[str, Any]):
        """Registrar aplicação da regra"""
        # Garantir que o SMS tem um ID válido
        if sms.id is None:
            self.db.flush()  # Força a criação do ID sem commit
        
        matched_criteria = self._get_matched_criteria(sms, rule)
        
        forwarded_sms_id = None
        if result.get('forwarded_to'):
            # Usar o primeiro SMS reencaminhado para o log
            forwarded_sms_id = result['forwarded_to'][0].get('sms_id')
        
        log_entry = ForwardingRuleLog(
            rule_id=rule.id,
            original_sms_id=sms.id,
            forwarded_sms_id=forwarded_sms_id,
            action_taken=rule.action,
            matched_criteria=matched_criteria
        )
        
        self.db.add(log_entry)
    
    def _get_matched_criteria(self, sms: SMS, rule: ForwardingRule) -> str:
        """Obter critério que foi correspondido"""
        if rule.rule_type in [ForwardingRuleType.SENDER_BASED, ForwardingRuleType.BLOCK_SENDER]:
            return f"Remetente: {sms.phone_from}"
        elif rule.rule_type == ForwardingRuleType.RECIPIENT_BASED:
            return f"Destinatário: {sms.phone_to}"
        elif rule.rule_type in [ForwardingRuleType.KEYWORD_BASED, ForwardingRuleType.BLOCK_KEYWORD]:
            return f"Palavras-chave: {rule.keyword_pattern}"
        return "Critério desconhecido"
    
    def get_rule_logs(self, rule_id: Optional[int] = None, limit: int = 100) -> List[ForwardingRuleLog]:
        """Obter logs de aplicação das regras"""
        query = self.db.query(ForwardingRuleLog)
        
        if rule_id:
            query = query.filter(ForwardingRuleLog.rule_id == rule_id)
        
        return query.order_by(ForwardingRuleLog.applied_at.desc()).limit(limit).all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas das regras"""
        total_rules = self.db.query(ForwardingRule).count()
        active_rules = self.db.query(ForwardingRule).filter(ForwardingRule.is_active == True).count()
        
        # Estatísticas de logs
        total_matches = self.db.query(ForwardingRuleLog).count()
        blocked_messages = self.db.query(ForwardingRuleLog).filter(
            ForwardingRuleLog.action_taken == ForwardingRuleAction.BLOCK
        ).count()
        forwarded_messages = self.db.query(ForwardingRuleLog).filter(
            ForwardingRuleLog.action_taken == ForwardingRuleAction.FORWARD
        ).count()
        deleted_messages = self.db.query(ForwardingRuleLog).filter(
            ForwardingRuleLog.action_taken == ForwardingRuleAction.DELETE
        ).count()
        
        return {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'total_matches': total_matches,
            'blocked_messages': blocked_messages,
            'forwarded_messages': forwarded_messages,
            'deleted_messages': deleted_messages
        }
