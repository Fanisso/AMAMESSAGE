from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import User
from backend.app.api.schemas import MessageResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuração de hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verificar senha"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Gerar hash da senha"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Criar token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/create-admin", response_model=MessageResponse)
async def create_admin_user(db: Session = Depends(get_db)):
    """Criar usuário administrador padrão (apenas se não existir)"""
    # Verificar se já existe um admin
    existing_admin = db.query(User).filter(User.is_admin == True).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário administrador já existe"
        )
    
    # Criar admin padrão
    admin_user = User(
        username="admin",
        email="admin@amamessage.com",
        full_name="Administrador do Sistema",
        hashed_password=get_password_hash("admin123"),  # Senha padrão
        is_active=True,
        is_admin=True
    )
    
    db.add(admin_user)
    db.commit()
    
    logger.info("Usuário administrador criado com sucesso")
    
    return MessageResponse(
        message="Usuário administrador criado. Username: admin, Senha: admin123 (ALTERE IMEDIATAMENTE!)",
        success=True
    )

# Função para obter usuário atual (será usada posteriormente)
async def get_current_user(token: str = Depends(lambda: ""), db: Session = Depends(get_db)):
    """Obter usuário atual a partir do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user
