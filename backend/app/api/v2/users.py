"""
Endpoints de Utilizadores - API v2
Gestão de utilizadores, perfis e preferências
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from pydantic import BaseModel
from shared.schemas import (
    UserRegistration, UserUpdate, UserProfile, 
    LoginRequest, LoginResponse
)
from shared.models import UserType

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserStatsResponse(BaseModel):
    total_messages: int
    messages_30d: int
    messages_7d: int
    total_ussd_sessions: int
    ussd_sessions_30d: int
    ussd_sessions_7d: int
    success_rate: float
    status_distribution: dict
    daily_activity: list
    last_message_at: str = None

class UserResponse(BaseModel):
    id: int
    username: str = None
    email: str
    full_name: str = None
    is_active: bool
    created_at: str = None

class PaginatedUsersResponse(BaseModel):
    users: list
    page: int
    size: int
    total_count: int
    total_pages: int

class UserCreateRequest(BaseModel):
    email: str
    password: str
    full_name: str = None
    username: str = None

class UserUpdateRequest(BaseModel):
    email: str = None
    full_name: str = None
    username: str = None

# Imports locais
from ...db.database import get_db
from ...db.models import User, SMS, SMSStatus, USSDSession
from .auth import get_current_user, hash_password

logger = logging.getLogger(__name__)
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Obtém perfil do utilizador atual.
    
    Retorna dados completos do utilizador autenticado.
    """
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        user_type=UserType.INDIVIDUAL,  # Valor padrão por enquanto
        is_active=current_user.is_active
    )

@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil do utilizador atual.
    
    Permite alterar dados pessoais (exceto email e tipo de utilizador).
    """
    try:
        # Atualizar campos permitidos
        if user_update.full_name is not None:
            current_user.full_name = user_update.full_name
        if user_update.phone_number is not None:
            current_user.phone_number = user_update.phone_number
        if user_update.company is not None:
            current_user.company = user_update.company
        if user_update.timezone is not None:
            current_user.timezone = user_update.timezone
        if user_update.language is not None:
            current_user.language = user_update.language
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Perfil atualizado para utilizador {current_user.email}")
        
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            user_type=current_user.user_type,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            last_login=current_user.last_login,
            phone_number=current_user.phone_number,
            company=current_user.company,
            timezone=current_user.timezone,
            language=current_user.language
        )
        
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil do utilizador: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera password do utilizador atual.
    
    Requer password atual para validação.
    """
    try:
        # Verificar password atual
        if not pwd_context.verify(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password atual incorreta"
            )
        
        # Validar nova password
        if len(password_data.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nova password deve ter pelo menos 8 caracteres"
            )
        
        # Confirmar nova password
        if password_data.new_password != password_data.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmação de password não confere"
            )
        
        # Atualizar password
        current_user.hashed_password = hash_password(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Password alterada para utilizador {current_user.email}")
        
        return {"message": "Password alterada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas de uso do utilizador atual.
    
    Inclui métricas dos últimos 30 dias.
    """
    try:
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Estatísticas de mensagens (SMS)
        total_messages = db.query(SMS).count()  # Total de SMS no sistema
        messages_30d = db.query(SMS).filter(
            SMS.created_at >= thirty_days_ago
        ).count()
        messages_7d = db.query(SMS).filter(
            SMS.created_at >= seven_days_ago
        ).count()
        
        # Estatísticas de USSD
        total_ussd = db.query(USSDSession).filter(USSDSession.user_id == current_user.id).count()
        ussd_30d = db.query(USSDSession).filter(
            USSDSession.user_id == current_user.id,
            USSDSession.created_at >= thirty_days_ago
        ).count()
        ussd_7d = db.query(USSDSession).filter(
            USSDSession.user_id == current_user.id,
            USSDSession.created_at >= seven_days_ago
        ).count()
        
        # Taxa de sucesso (mensagens enviadas vs total)
        successful_messages = db.query(SMS).filter(
            SMS.status.in_([SMSStatus.SENT, SMSStatus.DELIVERED])
        ).count()
        
        success_rate = (successful_messages / total_messages * 100) if total_messages > 0 else 0
        
        # Distribuição por status
        status_distribution = {}
        status_counts = db.query(
            SMS.status,
            db.func.count(SMS.id).label('count')
        ).filter(
            SMS.created_at >= thirty_days_ago
        ).group_by(SMS.status).all()
        
        for status, count in status_counts:
            status_distribution[status.value] = count
        
        # Atividade diária (últimos 7 dias)
        daily_activity = []
        for i in range(7):
            day_start = datetime.utcnow().date() - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            day_messages = db.query(SMS).filter(
                SMS.created_at >= day_start,
                SMS.created_at < day_end
            ).count()
            
            daily_activity.append({
                "date": day_start.isoformat(),
                "messages": day_messages
            })
        
        return UserStatsResponse(
            total_messages=total_messages,
            messages_30d=messages_30d,
            messages_7d=messages_7d,
            total_ussd_sessions=total_ussd,
            ussd_sessions_30d=ussd_30d,
            ussd_sessions_7d=ussd_7d,
            success_rate=round(success_rate, 2),
            status_distribution=status_distribution,
            daily_activity=list(reversed(daily_activity)),  # Mais recente primeiro
            last_message_at=db.query(SMS.created_at).filter(
                SMS.id.isnot(None)  # Qualquer SMS
            ).order_by(SMS.created_at.desc()).first()[0] if total_messages > 0 else None
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do utilizador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Endpoints administrativos (apenas para admins)

@router.get("/", response_model=PaginatedUsersResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    user_type: Optional[UserType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista utilizadores do sistema (apenas admins).
    
    Suporta paginação, pesquisa e filtros.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Construir query base
        query = db.query(User)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                db.or_(
                    User.email.contains(search),
                    User.full_name.contains(search),
                    User.company.contains(search)
                )
            )
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Contar total
        total_count = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * per_page
        users = query.offset(offset).limit(per_page).all()
        
        # Converter para response models
        user_responses = [
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                user_type=user.user_type,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login,
                phone_number=user.phone_number,
                company=user.company,
                timezone=user.timezone,
                language=user.language
            )
            for user in users
        ]
        
        total_pages = (total_count + per_page - 1) // per_page
        
        return PaginatedUsersResponse(
            users=user_responses,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar utilizadores: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo utilizador (apenas admins).
    
    Permite especificar tipo de utilizador e dados completos.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Criar utilizador
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            user_type=user_data.user_type,
            phone_number=user_data.phone_number,
            company=user_data.company,
            timezone=user_data.timezone or "UTC",
            language=user_data.language or "pt",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Utilizador criado por admin {current_user.email}: {new_user.email}")
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            user_type=new_user.user_type,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login=new_user.last_login,
            phone_number=new_user.phone_number,
            company=new_user.company,
            timezone=new_user.timezone,
            language=new_user.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar utilizador: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém utilizador específico (apenas admins).
    
    Retorna dados completos do utilizador.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Buscar utilizador
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilizador não encontrado"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            phone_number=user.phone_number,
            company=user.company,
            timezone=user.timezone,
            language=user.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter utilizador: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza utilizador específico (apenas admins).
    
    Permite alterar todos os dados (exceto password).
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Buscar utilizador
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilizador não encontrado"
            )
        
        # Atualizar campos
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        if user_update.phone_number is not None:
            user.phone_number = user_update.phone_number
        if user_update.company is not None:
            user.company = user_update.company
        if user_update.timezone is not None:
            user.timezone = user_update.timezone
        if user_update.language is not None:
            user.language = user_update.language
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Utilizador {user.email} atualizado por admin {current_user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            user_type=user.user_type,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            phone_number=user.phone_number,
            company=user.company,
            timezone=user.timezone,
            language=user.language
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar utilizador: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ativa/desativa utilizador (apenas admins).
    
    Alterna entre ativo e inativo.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Buscar utilizador
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilizador não encontrado"
            )
        
        # Não permitir desativar próprio usuário
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível alterar status do próprio utilizador"
            )
        
        # Alterar status
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        action = "ativado" if user.is_active else "desativado"
        logger.info(f"Utilizador {user.email} {action} por admin {current_user.email}")
        
        return {
            "message": f"Utilizador {action} com sucesso",
            "is_active": user.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao alterar status do utilizador: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Redefine password do utilizador (apenas admins).
    
    Gera password temporária que deve ser alterada no primeiro login.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Buscar utilizador
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilizador não encontrado"
            )
        
        # Gerar password temporária (8 caracteres aleatórios)
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # Atualizar password
        user.hashed_password = hash_password(temp_password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Password redefinida para utilizador {user.email} por admin {current_user.email}")
        
        return {
            "message": "Password redefinida com sucesso",
            "temporary_password": temp_password,
            "note": "O utilizador deve alterar a password no primeiro login"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao redefinir password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
