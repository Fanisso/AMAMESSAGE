from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SMSStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RECEIVED = "received"

class SMSDirectionEnum(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

# Schemas para SMS
class SMSCreate(BaseModel):
    phone_to: str = Field(..., description="Número de telefone destino", example="+258841234567")
    message: str = Field(..., description="Mensagem a ser enviada", example="Olá! Esta é uma mensagem de teste.")

class SMSBulkCreate(BaseModel):
    phones: List[str] = Field(..., description="Lista de números de telefone")
    message: str = Field(..., description="Mensagem a ser enviada para todos")
    priority: Optional[int] = Field(0, description="Prioridade (maior número = maior prioridade)")
    scheduled_for: Optional[datetime] = Field(None, description="Data/hora para agendamento")

class SMSResponse(BaseModel):
    id: int
    phone_from: str
    phone_to: str
    message: str
    status: SMSStatusEnum
    direction: SMSDirectionEnum
    created_at: datetime
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    external_id: Optional[str]
    error_message: Optional[str]
    retry_count: int

    class Config:
        from_attributes = True

class SMSStatusUpdate(BaseModel):
    status: SMSStatusEnum
    external_id: Optional[str] = None
    error_message: Optional[str] = None

# Schemas para Webhook (recebimento de SMS)
class WebhookSMS(BaseModel):
    From: str = Field(..., description="Número que enviou o SMS")
    To: str = Field(..., description="Número que recebeu o SMS")
    Body: str = Field(..., description="Conteúdo da mensagem")
    MessageSid: Optional[str] = Field(None, description="ID externo da mensagem")

# Schemas para Comandos
class SMSCommandCreate(BaseModel):
    keyword: str = Field(..., description="Palavra-chave do comando", example="HELP")
    description: Optional[str] = Field(None, description="Descrição do comando")
    response_message: str = Field(..., description="Mensagem de resposta", example="Comandos disponíveis: HELP, INFO, STOP")
    is_active: bool = Field(True, description="Se o comando está ativo")
    case_sensitive: bool = Field(False, description="Se o comando é sensível a maiúsculas/minúsculas")

class SMSCommandUpdate(BaseModel):
    keyword: Optional[str] = None
    description: Optional[str] = None
    response_message: Optional[str] = None
    is_active: Optional[bool] = None
    case_sensitive: Optional[bool] = None

class SMSCommandResponse(BaseModel):
    id: int
    keyword: str
    description: Optional[str]
    response_message: str
    is_active: bool
    case_sensitive: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Schemas para Filas
class QueueStatusResponse(BaseModel):
    total_pending: int
    total_processed: int
    next_scheduled: Optional[datetime]
    processor_running: Optional[bool] = False

# Schemas para Dashboard/Estatísticas
class DashboardStats(BaseModel):
    total_sms_sent: int
    total_sms_received: int
    total_sms_pending: int
    total_sms_failed: int
    success_rate: float
    commands_active: int

# Schemas para resposta padrão da API
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None

# Schemas para USSD
class USSDRequest(BaseModel):
    ussd_code: str = Field(..., description="Código USSD", example="*144#")
    timeout: Optional[int] = Field(30, description="Timeout em segundos", ge=5, le=120)

class USSDResponse(BaseModel):
    success: bool
    response: str = ""
    error: Optional[str] = None
    status: Optional[str] = None
    raw_response: Optional[str] = None

class USSDHistoryResponse(BaseModel):
    id: int
    ussd_code: str
    response: str
    success: bool
    created_at: datetime
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class USSDCommonCodes(BaseModel):
    name: str
    code: str
    description: str


# Schemas para Contactos
class ContactCreate(BaseModel):
    name: str = Field(..., description="Nome do contacto", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição opcional")
    phone1: str = Field(..., description="Número de telefone principal", min_length=1, max_length=20)
    phone2: Optional[str] = Field(None, description="Segundo número de telefone", max_length=20)
    phone3: Optional[str] = Field(None, description="Terceiro número de telefone", max_length=20)
    is_favorite: Optional[bool] = Field(False, description="Marcar como favorito")

class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    phone1: Optional[str] = Field(None, min_length=1, max_length=20)
    phone2: Optional[str] = Field(None, max_length=20)
    phone3: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    is_favorite: Optional[bool] = None

class ContactResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    phone1: str
    phone2: Optional[str]
    phone3: Optional[str]
    is_active: bool
    is_favorite: bool
    created_at: datetime
    updated_at: Optional[datetime]
    phone_numbers: List[str] = []
    
    class Config:
        from_attributes = True

# Schemas para Grupos de Contactos
class ContactGroupCreate(BaseModel):
    name: str = Field(..., description="Nome do grupo", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Descrição do grupo")
    color: Optional[str] = Field("#007bff", description="Cor do grupo em hexadecimal", pattern="^#[0-9A-Fa-f]{6}$")

class ContactGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    is_active: Optional[bool] = None

class ContactGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    member_count: int = 0
    
    class Config:
        from_attributes = True

class ContactGroupWithMembers(ContactGroupResponse):
    members: List[ContactResponse] = []

# Schemas para Membros de Grupo
class ContactGroupMemberCreate(BaseModel):
    contact_id: int = Field(..., description="ID do contacto")
    group_id: int = Field(..., description="ID do grupo")

class ContactGroupMemberResponse(BaseModel):
    id: int
    contact_id: int
    group_id: int
    created_at: datetime
    contact: ContactResponse
    
    class Config:
        from_attributes = True

# Schema para envio de SMS usando contactos/grupos
class SMSContactCreate(BaseModel):
    contacts: Optional[List[int]] = Field(None, description="Lista de IDs de contactos")
    groups: Optional[List[int]] = Field(None, description="Lista de IDs de grupos")
    message: str = Field(..., description="Mensagem a ser enviada")
    priority: Optional[int] = Field(0, description="Prioridade")
    scheduled_for: Optional[datetime] = Field(None, description="Data/hora para agendamento")
