"""
Schemas de validação - AMAMESSAGE
Definições Pydantic para validação de dados da API
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Import dos modelos compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import MessageStatus, MessageType, UserType, USSDSessionStatus, PlatformType
from utils import validate_phone_number, validate_ussd_code
from constants import MAX_SMS_LENGTH, MAX_CONTACTS_PER_USER

# Schemas de autenticação
class LoginRequest(BaseModel):
    """Schema para request de login."""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    platform: PlatformType = PlatformType.WEB
    device_info: Optional[Dict[str, str]] = None

class LoginResponse(BaseModel):
    """Schema para response de login."""
    success: bool
    access_token: str
    refresh_token: str
    user: 'UserProfile'
    expires_in: int

class RefreshTokenRequest(BaseModel):
    """Schema para refresh de token."""
    refresh_token: str

# Schemas de usuário
class UserProfile(BaseModel):
    """Schema para perfil de usuário."""
    id: int
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    user_type: UserType
    company_name: Optional[str] = Field(None, max_length=200)
    is_active: bool = True
    created_at: datetime
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v

class UserRegistration(BaseModel):
    """Schema para registro de usuário."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    user_type: UserType = UserType.INDIVIDUAL
    company_name: Optional[str] = Field(None, max_length=200)
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Validações básicas de senha
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v

class UserUpdate(BaseModel):
    """Schema para atualização de usuário."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = None
    company_name: Optional[str] = Field(None, max_length=200)
    preferences: Optional[Dict[str, Any]] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v

# Schemas de SMS
class SMSSendRequest(BaseModel):
    """Schema para envio de SMS."""
    to: str = Field(..., description="Número de destino")
    message: str = Field(..., min_length=1, max_length=MAX_SMS_LENGTH, description="Mensagem")
    schedule_at: Optional[datetime] = Field(None, description="Agendamento (opcional)")
    
    @validator('to')
    def validate_to(cls, v):
        if not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v

class SMSBulkSendRequest(BaseModel):
    """Schema para envio de SMS em lote."""
    recipients: List[str] = Field(..., min_items=1, max_items=100, description="Lista de destinatários")
    message: str = Field(..., min_length=1, max_length=MAX_SMS_LENGTH, description="Mensagem")
    schedule_at: Optional[datetime] = Field(None, description="Agendamento (opcional)")
    
    @validator('recipients')
    def validate_recipients(cls, v):
        for phone in v:
            if not validate_phone_number(phone):
                raise ValueError(f'Número de telefone inválido: {phone}')
        return list(set(v))  # Remove duplicatas

class SMSResponse(BaseModel):
    """Schema para response de SMS."""
    id: str
    to: str
    message: str
    status: MessageStatus
    created_at: datetime
    cost: Optional[float] = None

class SMSListResponse(BaseModel):
    """Schema para lista de SMS."""
    messages: List[SMSResponse]
    total: int
    page: int
    per_page: int
    has_next: bool

# Schemas de USSD
class USSDSendRequest(BaseModel):
    """Schema para envio de USSD."""
    code: str = Field(..., description="Código USSD")
    
    @validator('code')
    def validate_code(cls, v):
        if not validate_ussd_code(v):
            raise ValueError('Código USSD inválido')
        return v

class USSDResponse(BaseModel):
    """Schema para response de USSD."""
    session_id: str
    code: str
    response: Optional[str] = None
    status: USSDSessionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

class USSDSessionResponse(BaseModel):
    """Schema para sessão USSD."""
    id: str
    code: str
    status: USSDSessionStatus
    response: Optional[str] = None
    session_steps: Optional[List[Dict[str, str]]] = None
    current_step: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None

# Schemas de contactos
class ContactCreate(BaseModel):
    """Schema para criação de contacto."""
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., description="Número de telefone")
    email: Optional[EmailStr] = None
    group: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('phone')
    def validate_phone(cls, v):
        if not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v

class ContactUpdate(BaseModel):
    """Schema para atualização de contacto."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    group: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)
    is_blocked: Optional[bool] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not validate_phone_number(v):
            raise ValueError('Número de telefone inválido')
        return v

class ContactResponse(BaseModel):
    """Schema para response de contacto."""
    id: int
    name: str
    phone: str
    email: Optional[str] = None
    group: Optional[str] = None
    notes: Optional[str] = None
    is_blocked: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

class ContactListResponse(BaseModel):
    """Schema para lista de contactos."""
    contacts: List[ContactResponse]
    total: int
    page: int
    per_page: int
    has_next: bool

# Schemas de regras de reencaminhamento
class ForwardingRuleCreate(BaseModel):
    """Schema para criação de regra de reencaminhamento."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    condition_type: str = Field(..., pattern="^(contains|equals|starts_with|regex)$")
    condition_value: str = Field(..., min_length=1, max_length=200)
    source_numbers: Optional[List[str]] = None
    action_type: str = Field(..., pattern="^(forward|auto_reply|block|alert)$")
    action_value: str = Field(..., min_length=1, max_length=200)
    priority: int = Field(0, ge=0, le=100)
    is_active: bool = True
    
    @validator('source_numbers')
    def validate_source_numbers(cls, v):
        if v:
            for phone in v:
                if not validate_phone_number(phone):
                    raise ValueError(f'Número de telefone inválido: {phone}')
        return v

class ForwardingRuleUpdate(BaseModel):
    """Schema para atualização de regra."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    condition_type: Optional[str] = Field(None, pattern="^(contains|equals|starts_with|regex)$")
    condition_value: Optional[str] = Field(None, min_length=1, max_length=200)
    source_numbers: Optional[List[str]] = None
    action_type: Optional[str] = Field(None, pattern="^(forward|auto_reply|block|alert)$")
    action_value: Optional[str] = Field(None, min_length=1, max_length=200)
    priority: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None

class ForwardingRuleResponse(BaseModel):
    """Schema para response de regra."""
    id: int
    name: str
    description: Optional[str] = None
    condition_type: str
    condition_value: str
    source_numbers: Optional[List[str]] = None
    action_type: str
    action_value: str
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    trigger_count: int = 0

# Schemas de sistema
class ModemStatusResponse(BaseModel):
    """Schema para status do modem."""
    id: str
    port: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    is_connected: bool
    network_registered: bool
    signal_strength: Optional[int] = None
    operator_name: Optional[str] = None
    sim_status: Optional[str] = None
    phone_number: Optional[str] = None
    last_seen: Optional[datetime] = None

class SystemHealthResponse(BaseModel):
    """Schema para saúde do sistema."""
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    version: str
    uptime: int
    database_status: str
    modem_status: str
    message_queue_size: int
    last_check: datetime

class APIErrorResponse(BaseModel):
    """Schema para resposta de erro."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class PaginationQuery(BaseModel):
    """Schema para parâmetros de paginação."""
    page: int = Field(1, ge=1, description="Número da página")
    per_page: int = Field(20, ge=1, le=100, description="Items por página")
    sort_by: Optional[str] = Field(None, description="Campo para ordenação")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Ordem de classificação")

class SearchQuery(BaseModel):
    """Schema para parâmetros de busca."""
    q: Optional[str] = Field(None, min_length=1, max_length=100, description="Termo de busca")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros adicionais")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

# Configuração para responses automáticos
UserProfile.update_forward_refs()
LoginResponse.update_forward_refs()

# Schemas de configuração para diferentes clientes
class WebClientConfig(BaseModel):
    """Configuração específica para cliente web."""
    theme: str = Field("light", pattern="^(light|dark|auto)$")
    language: str = Field("pt", pattern="^(pt|en|es)$")
    notifications_enabled: bool = True
    auto_refresh_interval: int = Field(30, ge=10, le=300)
    items_per_page: int = Field(20, ge=10, le=100)

class MobileClientConfig(BaseModel):
    """Configuração específica para cliente mobile."""
    push_notifications: bool = True
    sync_contacts: bool = False
    auto_backup: bool = True
    offline_mode: bool = True
    biometric_auth: bool = False

# Export dos schemas principais
__all__ = [
    'LoginRequest', 'LoginResponse', 'UserProfile', 'UserRegistration',
    'SMSSendRequest', 'SMSBulkSendRequest', 'SMSResponse', 'SMSListResponse',
    'USSDSendRequest', 'USSDResponse', 'USSDSessionResponse',
    'ContactCreate', 'ContactUpdate', 'ContactResponse', 'ContactListResponse',
    'ForwardingRuleCreate', 'ForwardingRuleUpdate', 'ForwardingRuleResponse',
    'ModemStatusResponse', 'SystemHealthResponse', 'APIErrorResponse',
    'PaginationQuery', 'SearchQuery', 'WebClientConfig', 'MobileClientConfig'
]
