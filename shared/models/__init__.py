"""
Modelos de dados compartilhados - AMAMESSAGE
Definições que serão usadas em Python (backend), TypeScript (web) e Dart (mobile)
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import json

# Enums para tipos de dados
class MessageStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

class MessageType(Enum):
    SMS = "sms"
    USSD = "ussd"

class UserType(Enum):
    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class USSDSessionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class PlatformType(Enum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"

# Modelos de dados base
@dataclass
class BaseModel:
    """Classe base para todos os modelos."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        result = asdict(self)
        
        # Converte enums para strings
        for key, value in result.items():
            if isinstance(value, Enum):
                result[key] = value.value
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
        
        return result
    
    def to_json(self) -> str:
        """Converte para JSON."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Cria instância a partir de dicionário."""
        return cls(**data)

@dataclass
class User(BaseModel):
    """Modelo de usuário do sistema."""
    id: Optional[int] = None
    email: str = ""
    name: str = ""
    phone: Optional[str] = None
    user_type: UserType = UserType.INDIVIDUAL
    company_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Configurações específicas do usuário
    preferences: Optional[Dict[str, Any]] = None

@dataclass
class Contact(BaseModel):
    """Modelo de contacto."""
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    phone: str = ""
    email: Optional[str] = None
    group: Optional[str] = None
    notes: Optional[str] = None
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SMSMessage(BaseModel):
    """Modelo de mensagem SMS."""
    id: Optional[str] = None
    user_id: int = 0
    from_number: str = ""
    to_number: str = ""
    message: str = ""
    status: MessageStatus = MessageStatus.PENDING
    message_type: MessageType = MessageType.SMS
    
    # Timestamps
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Metadados
    cost: Optional[float] = None
    provider: Optional[str] = None
    error_message: Optional[str] = None
    
    # Para reencaminhamento
    forwarded_from: Optional[str] = None
    forwarding_rule_id: Optional[int] = None

@dataclass
class USSDSession(BaseModel):
    """Modelo de sessão USSD."""
    id: Optional[str] = None
    user_id: int = 0
    ussd_code: str = ""
    response: Optional[str] = None
    status: USSDSessionStatus = USSDSessionStatus.ACTIVE
    
    # Timestamps
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Sessão interativa
    session_steps: Optional[List[Dict[str, str]]] = None
    current_step: int = 0
    
    # Metadados
    cost: Optional[float] = None
    provider: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class ForwardingRule(BaseModel):
    """Modelo de regra de reencaminhamento."""
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    description: Optional[str] = None
    
    # Condições
    condition_type: str = "contains"  # contains, equals, starts_with, regex
    condition_value: str = ""
    source_numbers: Optional[List[str]] = None
    
    # Ações
    action_type: str = "forward"  # forward, auto_reply, block, alert
    action_value: str = ""
    
    # Configurações
    is_active: bool = True
    priority: int = 0
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    
    # Estatísticas
    trigger_count: int = 0

@dataclass
class ModemStatus(BaseModel):
    """Status do modem GSM."""
    id: Optional[str] = None
    port: str = ""
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    
    # Status de conectividade
    is_connected: bool = False
    network_registered: bool = False
    signal_strength: Optional[int] = None
    operator_name: Optional[str] = None
    
    # Informações do SIM
    sim_status: Optional[str] = None
    phone_number: Optional[str] = None
    sim_balance: Optional[float] = None
    
    # Timestamps
    last_seen: Optional[datetime] = None
    connected_since: Optional[datetime] = None
    
    # Configurações
    max_sms_storage: Optional[int] = None
    used_sms_storage: Optional[int] = None

@dataclass
class APIResponse(BaseModel):
    """Resposta padrão da API."""
    success: bool = True
    message: str = ""
    data: Optional[Any] = None
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class UserSession(BaseModel):
    """Sessão de usuário para autenticação."""
    user_id: int = 0
    session_token: str = ""
    platform: PlatformType = PlatformType.WEB
    device_info: Optional[Dict[str, str]] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Localização e preferências
    timezone: Optional[str] = None
    language: str = "pt"

@dataclass
class SystemAlert(BaseModel):
    """Alerta do sistema."""
    id: Optional[int] = None
    user_id: Optional[int] = None
    title: str = ""
    message: str = ""
    alert_type: str = "info"  # info, warning, error, success
    
    # Status
    is_read: bool = False
    is_dismissed: bool = False
    
    # Timestamps
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Metadados
    source: Optional[str] = None
    action_url: Optional[str] = None

# Export dos modelos principais
__all__ = [
    'MessageStatus', 'MessageType', 'UserType', 'USSDSessionStatus', 'PlatformType',
    'BaseModel', 'User', 'Contact', 'SMSMessage', 'USSDSession', 'ForwardingRule',
    'ModemStatus', 'APIResponse', 'UserSession', 'SystemAlert'
]
