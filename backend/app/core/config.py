from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Alertas (Email/Webhook)
    ALERT_EMAIL_SMTP: Optional[str] = None
    ALERT_EMAIL_PORT: Optional[int] = 587
    ALERT_EMAIL_USER: Optional[str] = None
    ALERT_EMAIL_PASSWORD: Optional[str] = None
    ALERT_EMAIL_FROM: Optional[str] = None
    ALERT_EMAIL_TO: Optional[str] = None
    ALERT_WEBHOOK_URL: Optional[str] = None
    # Base de Dados
    DATABASE_URL: str = "sqlite:///./amamessage.db"
    
    # Configuração do Modem GSM
    GSM_PORT: str = "AUTO"  # Usar "AUTO" para detecção automática ou especificar uma porta (ex: "COM4")
    GSM_BAUDRATE: int = 115200  # Taxa de comunicação
    GSM_TIMEOUT: int = 10  # Timeout em segundos
    GSM_PIN: Optional[str] = None  # PIN do cartão SIM (se necessário)
    GSM_SMSC: Optional[str] = None  # Centro de mensagens SMS (será detectado automaticamente)
    
    # Configurações de Monitoramento
    GSM_CHECK_INTERVAL: int = 30  # Intervalo para verificar conexão (segundos)
    GSM_AUTO_DETECT: bool = True  # Detecção automática de porta
    GSM_PREFERRED_PORTS: list = ["COM4", "COM6", "COM5", "COM1", "COM3", "COM2"]  # Portas preferenciais (Qualcomm primeiro)
    
    # Redis (Filas)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Segurança
    SECRET_KEY: str = "sua_chave_secreta_muito_forte_aqui_mude_em_producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Servidor
    HOST: str = "127.0.0.1"
    PORT: int = 7000
    DEBUG: bool = True
    
    # Configurações de SMS
    SMS_CHECK_INTERVAL: int = 30  # Intervalo para verificar SMS recebidas (segundos)
    SMS_MAX_RETRIES: int = 3  # Máximo de tentativas para envio
    SMS_RETRY_DELAY: int = 60  # Delay entre tentativas (segundos)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
