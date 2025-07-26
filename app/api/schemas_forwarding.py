from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ForwardingRuleTypeEnum(str, Enum):
    """Tipos de regras de reencaminhamento"""
    SENDER_BASED = "sender_based"
    KEYWORD_BASED = "keyword_based"
    RECIPIENT_BASED = "recipient_based"
    BLOCK_SENDER = "block_sender"
    BLOCK_KEYWORD = "block_keyword"


class ForwardingRuleActionEnum(str, Enum):
    """Ações das regras"""
    FORWARD = "forward"
    BLOCK = "block"
    DELETE = "delete"


class ForwardingRuleBase(BaseModel):
    """Schema base para regras de reencaminhamento"""
    name: str = Field(..., min_length=1, max_length=100, description="Nome da regra")
    description: Optional[str] = Field(None, description="Descrição da regra")
    is_active: bool = Field(True, description="Se a regra está ativa")
    rule_type: ForwardingRuleTypeEnum = Field(..., description="Tipo da regra")
    action: ForwardingRuleActionEnum = Field(..., description="Ação a ser executada")
    
    # Critérios de correspondência
    sender_pattern: Optional[str] = Field(None, max_length=20, description="Padrão do remetente")
    recipient_pattern: Optional[str] = Field(None, max_length=20, description="Padrão do destinatário")
    keyword_pattern: Optional[str] = Field(None, description="Palavras-chave (separadas por vírgula)")
    
    # Configurações de reencaminhamento
    forward_to_numbers: Optional[List[str]] = Field(None, description="Números para reencaminhamento")
    forward_to_group_id: Optional[int] = Field(None, description="ID do grupo de contatos")
    
    # Configurações adicionais
    case_sensitive: bool = Field(False, description="Busca sensível a maiúsculas/minúsculas")
    whole_word_only: bool = Field(False, description="Apenas palavras completas")
    priority: int = Field(0, description="Prioridade da regra")


class ForwardingRuleCreate(ForwardingRuleBase):
    """Schema para criação de regra"""
    pass


class ForwardingRuleUpdate(BaseModel):
    """Schema para atualização de regra"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rule_type: Optional[ForwardingRuleTypeEnum] = None
    action: Optional[ForwardingRuleActionEnum] = None
    
    sender_pattern: Optional[str] = Field(None, max_length=20)
    recipient_pattern: Optional[str] = Field(None, max_length=20)
    keyword_pattern: Optional[str] = None
    
    forward_to_numbers: Optional[List[str]] = None
    forward_to_group_id: Optional[int] = None
    
    case_sensitive: Optional[bool] = None
    whole_word_only: Optional[bool] = None
    priority: Optional[int] = None


class ForwardingRuleResponse(ForwardingRuleBase):
    """Schema de resposta para regra"""
    id: int
    match_count: int
    last_match_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ForwardingRuleLogResponse(BaseModel):
    """Schema de resposta para log de regra"""
    id: int
    rule_id: int
    original_sms_id: int
    forwarded_sms_id: Optional[int]
    action_taken: ForwardingRuleActionEnum
    matched_criteria: Optional[str]
    applied_at: datetime
    
    # Informações detalhadas
    rule_name: Optional[str] = None
    original_message: Optional[str] = None
    original_sender: Optional[str] = None
    
    class Config:
        from_attributes = True


class ForwardingRuleStats(BaseModel):
    """Estatísticas das regras"""
    total_rules: int
    active_rules: int
    total_matches: int
    blocked_messages: int
    forwarded_messages: int
    deleted_messages: int


class MessageResponse(BaseModel):
    """Resposta padrão para operações"""
    success: bool
    message: str
    data: Optional[dict] = None
