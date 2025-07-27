from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum
from datetime import datetime

class SMSStatus(enum.Enum):
    PENDING = "pending"        # Aguardando envio
    SENT = "sent"             # Enviado
    DELIVERED = "delivered"    # Entregue
    FAILED = "failed"         # Falhou
    RECEIVED = "received"     # Recebido

class SMSDirection(enum.Enum):
    INBOUND = "inbound"       # SMS recebido
    OUTBOUND = "outbound"     # SMS enviado

class SMS(Base):
    """Tabela principal para armazenar todas as mensagens SMS"""
    __tablename__ = "sms"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    phone_from = Column(String(20), nullable=False, index=True)
    phone_to = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Status e direção
    status = Column(Enum(SMSStatus), default=SMSStatus.PENDING, index=True)
    direction = Column(Enum(SMSDirection), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # IDs externos (do provedor de SMS)
    external_id = Column(String(100), nullable=True, unique=True)
    
    # Informações adicionais
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relacionamentos
    responses = relationship("SMSResponse", back_populates="original_sms", foreign_keys="SMSResponse.original_sms_id")
    response_to = relationship("SMSResponse", back_populates="response_sms", foreign_keys="SMSResponse.response_sms_id")
    
    def __repr__(self):
        return f"<SMS(id={self.id}, from={self.phone_from}, to={self.phone_to}, status={self.status})>"

class SMSQueue(Base):
    """Fila de SMS para envio em massa"""
    __tablename__ = "sms_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações da mensagem
    phone_to = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Controle da fila
    priority = Column(Integer, default=0)  # Maior número = maior prioridade
    scheduled_for = Column(DateTime(timezone=True), nullable=True)  # Agendamento
    
    # Status
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamento com SMS enviado
    sms_id = Column(Integer, ForeignKey("sms.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SMSQueue(id={self.id}, to={self.phone_to}, processed={self.processed})>"

class SMSCommand(Base):
    """Comandos automáticos para resposta a SMS"""
    __tablename__ = "sms_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Comando
    keyword = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)
    
    # Resposta
    response_message = Column(Text, nullable=False)
    
    # Configurações
    is_active = Column(Boolean, default=True, index=True)
    case_sensitive = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    responses = relationship("SMSResponse", back_populates="command")
    
    def __repr__(self):
        return f"<SMSCommand(id={self.id}, keyword='{self.keyword}', active={self.is_active})>"

class SMSResponse(Base):
    """Registro de respostas automáticas enviadas"""
    __tablename__ = "sms_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # SMS original que disparou a resposta
    original_sms_id = Column(Integer, ForeignKey("sms.id"), nullable=False)
    
    # Comando usado
    command_id = Column(Integer, ForeignKey("sms_commands.id"), nullable=False)
    
    # SMS de resposta enviado
    response_sms_id = Column(Integer, ForeignKey("sms.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    original_sms = relationship("SMS", back_populates="responses", foreign_keys=[original_sms_id])
    response_sms = relationship("SMS", back_populates="response_to", foreign_keys=[response_sms_id])
    command = relationship("SMSCommand", back_populates="responses")
    
    def __repr__(self):
        return f"<SMSResponse(id={self.id}, original_sms_id={self.original_sms_id}, command_id={self.command_id})>"

class User(Base):
    """Usuários do sistema de administração"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do usuário
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    
    # Autenticação
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', active={self.is_active})>"

class USSDHistory(Base):
    """Tabela para armazenar histórico de códigos USSD"""
    __tablename__ = "ussd_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Código USSD enviado
    ussd_code = Column(String(50), nullable=False, index=True)
    
    # Resposta recebida
    response = Column(Text, nullable=True)
    raw_response = Column(Text, nullable=True)  # Resposta completa/raw
    
    # Status da operação
    success = Column(Boolean, default=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Informações adicionais
    timeout_seconds = Column(Integer, default=30)
    response_time_ms = Column(Integer, nullable=True)  # Tempo de resposta em ms
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<USSDHistory(id={self.id}, code='{self.ussd_code}', success={self.success})>"


class Contact(Base):
    """Tabela para armazenar contactos"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)  # Descrição opcional
    
    # Números de telefone (até 3)
    phone1 = Column(String(20), nullable=False, index=True)
    phone2 = Column(String(20), nullable=True, index=True)
    phone3 = Column(String(20), nullable=True, index=True)
    
    # Configurações
    is_active = Column(Boolean, default=True, index=True)
    is_favorite = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    group_memberships = relationship("ContactGroupMember", back_populates="contact")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    @property
    def phone_numbers(self):
        """Retornar lista de números de telefone não vazios"""
        phones = []
        if self.phone1:
            phones.append(self.phone1)
        if self.phone2:
            phones.append(self.phone2)
        if self.phone3:
            phones.append(self.phone3)
        return phones


class ContactGroup(Base):
    """Tabela para grupos de contactos"""
    __tablename__ = "contact_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do grupo
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#007bff")  # Cor em hexadecimal
    
    # Configurações
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    members = relationship("ContactGroupMember", back_populates="group")
    forwarding_rules = relationship("ForwardingRule", back_populates="forward_to_group")
    
    def __repr__(self):
        return f"<ContactGroup(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    @property
    def member_count(self):
        """Retornar número de membros ativos no grupo"""
        return len([m for m in self.members if m.contact.is_active])


class ContactGroupMember(Base):
    """Tabela de associação entre contactos e grupos"""
    __tablename__ = "contact_group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Chaves estrangeiras
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("contact_groups.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    contact = relationship("Contact", back_populates="group_memberships")
    group = relationship("ContactGroup", back_populates="members")
    
    def __repr__(self):
        return f"<ContactGroupMember(contact_id={self.contact_id}, group_id={self.group_id})>"


class ForwardingRuleType(enum.Enum):
    """Tipos de regras de reencaminhamento"""
    SENDER_BASED = "sender_based"           # Baseado no remetente
    KEYWORD_BASED = "keyword_based"         # Baseado em palavras-chave
    RECIPIENT_BASED = "recipient_based"     # Baseado no destinatário
    BLOCK_SENDER = "block_sender"           # Bloquear remetente
    BLOCK_KEYWORD = "block_keyword"         # Bloquear palavras-chave


class ForwardingRuleAction(enum.Enum):
    """Ações das regras"""
    FORWARD = "forward"                     # Reencaminhar
    BLOCK = "block"                         # Bloquear/eliminar
    DELETE = "delete"                       # Deletar automaticamente


class ForwardingRule(Base):
    """Regras de reencaminhamento e filtragem de SMS"""
    __tablename__ = "forwarding_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações básicas da regra
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Tipo e ação da regra
    rule_type = Column(Enum(ForwardingRuleType), nullable=False, index=True)
    action = Column(Enum(ForwardingRuleAction), nullable=False)
    
    # Critérios de correspondência
    sender_pattern = Column(String(20), nullable=True, index=True)  # Para regras baseadas em remetente
    recipient_pattern = Column(String(20), nullable=True, index=True)  # Para regras baseadas em destinatário
    keyword_pattern = Column(Text, nullable=True)  # Palavras-chave ou frases (separadas por vírgula)
    
    # Configurações de reencaminhamento
    forward_to_numbers = Column(Text, nullable=True)  # Números para reencaminhar (JSON array)
    forward_to_group_id = Column(Integer, ForeignKey("contact_groups.id"), nullable=True)  # Grupo de contatos
    
    # Configurações adicionais
    case_sensitive = Column(Boolean, default=False)  # Para busca de palavras-chave
    whole_word_only = Column(Boolean, default=False)  # Apenas palavras completas
    priority = Column(Integer, default=0)  # Prioridade da regra (maior = executada primeiro)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Estatísticas
    match_count = Column(Integer, default=0)  # Quantas vezes a regra foi aplicada
    last_match_at = Column(DateTime(timezone=True), nullable=True)  # Última aplicação
    
    # Relacionamentos
    forward_to_group = relationship("ContactGroup", back_populates="forwarding_rules")
    rule_logs = relationship("ForwardingRuleLog", back_populates="rule")
    
    def __repr__(self):
        return f"<ForwardingRule(id={self.id}, name='{self.name}', type={self.rule_type.value})>"


class ForwardingRuleLog(Base):
    """Log de aplicação das regras de reencaminhamento"""
    __tablename__ = "forwarding_rule_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamentos
    rule_id = Column(Integer, ForeignKey("forwarding_rules.id"), nullable=False, index=True)
    original_sms_id = Column(Integer, ForeignKey("sms.id"), nullable=False, index=True)
    forwarded_sms_id = Column(Integer, ForeignKey("sms.id"), nullable=True, index=True)  # SMS reencaminhado (se aplicável)
    
    # Informações da aplicação
    action_taken = Column(Enum(ForwardingRuleAction), nullable=False)
    matched_criteria = Column(Text, nullable=True)  # O que foi correspondido
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    rule = relationship("ForwardingRule", back_populates="rule_logs")
    original_sms = relationship("SMS", foreign_keys=[original_sms_id])
    forwarded_sms = relationship("SMS", foreign_keys=[forwarded_sms_id])
    
    def __repr__(self):
        return f"<ForwardingRuleLog(id={self.id}, rule_id={self.rule_id}, action={self.action_taken.value})>"
