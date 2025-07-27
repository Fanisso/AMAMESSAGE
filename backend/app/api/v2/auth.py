"""
Endpoints de Autenticação - API v2
Implementação moderna com JWT tokens
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
import logging

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import (
    LoginRequest, LoginResponse, UserRegistration, UserProfile, 
    RefreshTokenRequest, APIErrorResponse
)
from shared.models import UserType, PlatformType
from shared.constants import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

# Imports locais
from ...db.database import get_db
from ...db.models import User
from ...core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Utilitários JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT de acesso."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Cria token JWT de refresh (válido por 7 dias)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verifica e decodifica token JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def hash_password(password: str) -> str:
    """Hash da senha usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Dependência para obter usuário atual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obtém usuário atual a partir do token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )
    
    return user

# Endpoints de autenticação

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Realiza login do usuário.
    
    - **email**: Email do usuário
    - **password**: Senha do usuário
    - **platform**: Plataforma (web, android, ios)
    - **device_info**: Informações do dispositivo (opcional)
    """
    try:
        # Buscar usuário por email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Tentativa de login inválida para {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Conta desactivada"
            )
        
        # Criar tokens
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "platform": login_data.platform.value},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.id, "email": user.email}
        )
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        db.commit()
        
        # Log de login bem-sucedido
        client_ip = request.client.host
        logger.info(f"Login bem-sucedido: {user.email} de {client_ip} via {login_data.platform.value}")
        
        # Preparar response
        user_profile = UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            user_type=UserType(user.user_type),
            company_name=user.company_name,
            is_active=user.is_active,
            created_at=user.created_at,
            preferences=user.preferences or {}
        )
        
        return LoginResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_profile,
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/register", response_model=UserProfile)
async def register(
    registration_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Registra novo usuário.
    
    - **email**: Email único do usuário
    - **password**: Senha (mínimo 8 caracteres)
    - **name**: Nome completo
    - **phone**: Telefone (opcional)
    - **user_type**: Tipo de usuário (individual/enterprise)
    - **company_name**: Nome da empresa (para usuários enterprise)
    """
    try:
        # Verificar se email já existe
        existing_user = db.query(User).filter(User.email == registration_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        
        # Verificar se telefone já existe (se fornecido)
        if registration_data.phone:
            existing_phone = db.query(User).filter(User.phone == registration_data.phone).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telefone já está em uso"
                )
        
        # Criar novo usuário
        hashed_password = hash_password(registration_data.password)
        new_user = User(
            email=registration_data.email,
            password_hash=hashed_password,
            name=registration_data.name,
            phone=registration_data.phone,
            user_type=registration_data.user_type.value,
            company_name=registration_data.company_name,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Novo usuário registrado: {new_user.email}")
        
        return UserProfile(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            phone=new_user.phone,
            user_type=UserType(new_user.user_type),
            company_name=new_user.company_name,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            preferences={}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Renova token de acesso usando refresh token.
    
    - **refresh_token**: Token de refresh válido
    """
    try:
        # Verificar refresh token
        payload = verify_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresh inválido"
            )
        
        user_id: int = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado ou inativo"
            )
        
        # Criar novo access token
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Realiza logout do usuário.
    
    Nota: Em uma implementação completa, isso invalidaria o token
    no lado do servidor (blacklist de tokens).
    """
    logger.info(f"Logout: {current_user.email}")
    
    return {
        "success": True,
        "message": "Logout realizado com sucesso"
    }

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Obtém perfil do usuário atual.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        user_type=UserType(current_user.user_type),
        company_name=current_user.company_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        preferences=current_user.preferences or {}
    )

@router.put("/me", response_model=UserProfile)
async def update_current_user_profile(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil do usuário atual.
    
    - **name**: Nome completo (opcional)
    - **phone**: Telefone (opcional)
    - **company_name**: Nome da empresa (opcional)
    - **preferences**: Preferências do usuário (opcional)
    """
    try:
        # Atualizar campos permitidos
        if "name" in user_update and user_update["name"]:
            current_user.name = user_update["name"]
        
        if "phone" in user_update:
            # Verificar se telefone já está em uso por outro usuário
            if user_update["phone"]:
                existing_phone = db.query(User).filter(
                    User.phone == user_update["phone"],
                    User.id != current_user.id
                ).first()
                if existing_phone:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Telefone já está em uso"
                    )
            current_user.phone = user_update["phone"]
        
        if "company_name" in user_update:
            current_user.company_name = user_update["company_name"]
        
        if "preferences" in user_update:
            current_user.preferences = user_update["preferences"]
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Perfil atualizado: {current_user.email}")
        
        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            phone=current_user.phone,
            user_type=UserType(current_user.user_type),
            company_name=current_user.company_name,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            preferences=current_user.preferences or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na atualização do perfil: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/change-password")
async def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera senha do usuário atual.
    
    - **current_password**: Senha atual
    - **new_password**: Nova senha
    """
    try:
        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual e nova senha são obrigatórias"
            )
        
        # Verificar senha atual
        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
        
        # Validar nova senha (básico)
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nova senha deve ter pelo menos 8 caracteres"
            )
        
        # Atualizar senha
        current_user.password_hash = hash_password(new_password)
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Senha alterada: {current_user.email}")
        
        return {
            "success": True,
            "message": "Senha alterada com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na alteração de senha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# Exportar dependências úteis
__all__ = ["router", "get_current_user", "verify_token"]
