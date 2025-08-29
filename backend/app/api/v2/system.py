"""
Endpoints de Sistema - API v2
Monitorização, saúde do sistema e status dos modems
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import psutil
import platform

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import SystemHealthResponse, ModemStatusResponse
from shared.constants import SYSTEM_VERSION, API_VERSION

# Imports locais
from ...db.database import get_db
from ...db.models import User, SMS, USSDSession
from ...services.gsm_service import GSMModem
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

def get_gsm_service() -> GSMModem:
    """Factory para obter instância do serviço GSM."""
    return GSMModem()

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db),
    gsm_service: GSMModem = Depends(get_gsm_service)
):
    """
    Verifica saúde geral do sistema.
    
    Retorna status de todos os componentes críticos.
    """
    try:
        # Verificar base de dados
        try:
            db.execute("SELECT 1")
            database_status = "healthy"
        except Exception:
            database_status = "unhealthy"
        
        # Verificar modems GSM
        try:
            modems = await gsm_service.get_available_modems()
            connected_modems = [m for m in modems if m.get('is_connected', False)]
            
            if len(connected_modems) > 0:
                modem_status = "healthy"
            elif len(modems) > 0:
                modem_status = "degraded"  # Modems detectados mas não conectados
            else:
                modem_status = "unhealthy"  # Nenhum modem detectado
        except Exception:
            modem_status = "unhealthy"
        
        # Verificar fila de mensagens
        try:
            pending_messages = db.query(Message).filter(
                Message.status == "pending"
            ).count()
            message_queue_size = pending_messages
        except Exception:
            message_queue_size = -1
        
        # Determinar status geral
        if database_status == "unhealthy" or modem_status == "unhealthy":
            overall_status = "unhealthy"
        elif database_status == "degraded" or modem_status == "degraded":
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Calcular uptime (simplificado)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = int((datetime.now() - boot_time).total_seconds())
        
        return SystemHealthResponse(
            status=overall_status,
            version=SYSTEM_VERSION,
            uptime=uptime_seconds,
            database_status=database_status,
            modem_status=modem_status,
            message_queue_size=message_queue_size,
            last_check=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do sistema: {str(e)}")
        return SystemHealthResponse(
            status="unhealthy",
            version=SYSTEM_VERSION,
            uptime=0,
            database_status="unknown",
            modem_status="unknown",
            message_queue_size=-1,
            last_check=datetime.utcnow()
        )

@router.get("/modem-status", response_model=List[ModemStatusResponse])
async def get_modem_status(
    current_user: User = Depends(get_current_user),
    gsm_service: GSMModem = Depends(get_gsm_service)
):
    """
    Obtém status detalhado de todos os modems GSM.
    
    Requer autenticação de usuário.
    """
    try:
        modems = await gsm_service.get_available_modems()
        
        modem_responses = []
        for modem in modems:
            modem_responses.append(ModemStatusResponse(
                id=modem.get('id', 'unknown'),
                port=modem.get('port', 'unknown'),
                manufacturer=modem.get('manufacturer'),
                model=modem.get('model'),
                firmware_version=modem.get('firmware_version'),
                is_connected=modem.get('is_connected', False),
                network_registered=modem.get('network_registered', False),
                signal_strength=modem.get('signal_strength'),
                operator_name=modem.get('operator_name'),
                sim_status=modem.get('sim_status'),
                phone_number=modem.get('phone_number'),
                last_seen=datetime.fromisoformat(modem['last_seen']) if modem.get('last_seen') else None
            ))
        
        return modem_responses
        
    except Exception as e:
        logger.error(f"Erro ao obter status dos modems: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém estatísticas gerais do sistema para dashboard.
    
    Inclui métricas de uso e performance.
    """
    try:
        # Estatísticas de mensagens (últimas 24h)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        total_messages_24h = db.query(Message).filter(
            Message.created_at >= yesterday
        ).count()
        
        sent_messages_24h = db.query(Message).filter(
            Message.created_at >= yesterday,
            Message.status.in_(["sent", "delivered"])
        ).count()
        
        failed_messages_24h = db.query(Message).filter(
            Message.created_at >= yesterday,
            Message.status == "failed"
        ).count()
        
        # Estatísticas de usuários
        total_users = db.query(User).count()
        active_users_7d = db.query(User).filter(
            User.last_login >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Estatísticas de USSD (últimas 24h)
        ussd_sessions_24h = db.query(USSDSession).filter(
            USSDSession.created_at >= yesterday
        ).count()
        
        completed_ussd_24h = db.query(USSDSession).filter(
            USSDSession.created_at >= yesterday,
            USSDSession.status == "completed"
        ).count()
        
        # Estatísticas de sistema
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Top operadores (baseado nos números de telefone)
        operator_stats = db.query(
            db.func.substr(Message.phone_number, 1, 7).label('prefix'),
            db.func.count(Message.id).label('count')
        ).filter(
            Message.created_at >= yesterday
        ).group_by('prefix').order_by(db.text('count DESC')).limit(5).all()
        
        # Mapear prefixos para operadores (exemplo para Moçambique)
        operator_map = {
            '+25882': 'mCel',
            '+25883': 'mCel', 
            '+25884': 'Vodacom',
            '+25885': 'Vodacom',
            '+25886': 'Movitel',
            '+25887': 'Movitel'
        }
        
        operator_distribution = {}
        for prefix, count in operator_stats:
            operator = operator_map.get(prefix, 'Outros')
            operator_distribution[operator] = operator_distribution.get(operator, 0) + count
        
        return {
            "system_info": {
                "version": SYSTEM_VERSION,
                "api_version": API_VERSION,
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds())
            },
            "performance": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory_info.percent,
                "memory_available_gb": round(memory_info.available / (1024**3), 2),
                "disk_usage_percent": disk_info.percent,
                "disk_free_gb": round(disk_info.free / (1024**3), 2)
            },
            "messages_24h": {
                "total": total_messages_24h,
                "sent": sent_messages_24h,
                "failed": failed_messages_24h,
                "success_rate": round((sent_messages_24h / total_messages_24h * 100), 2) if total_messages_24h > 0 else 0
            },
            "ussd_24h": {
                "total_sessions": ussd_sessions_24h,
                "completed": completed_ussd_24h,
                "success_rate": round((completed_ussd_24h / ussd_sessions_24h * 100), 2) if ussd_sessions_24h > 0 else 0
            },
            "users": {
                "total": total_users,
                "active_7d": active_users_7d,
                "activity_rate": round((active_users_7d / total_users * 100), 2) if total_users > 0 else 0
            },
            "operator_distribution": operator_distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do sistema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/logs")
async def get_system_logs(
    level: str = "INFO",
    lines: int = 100,
    current_user: User = Depends(get_current_user)
):
    """
    Obtém logs recentes do sistema.
    
    - **level**: Nível de log (DEBUG, INFO, WARNING, ERROR)
    - **lines**: Número de linhas para retornar (máx. 1000)
    
    Requer usuário admin.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Limitar número de linhas
        lines = min(lines, 1000)
        
        # Ler logs (implementação simplificada)
        log_entries = []
        try:
            # Em produção, implementar leitura real dos arquivos de log
            log_entries = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "INFO",
                    "message": "Sistema funcionando normalmente",
                    "module": "system"
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "level": "INFO", 
                    "message": "Modem GSM conectado",
                    "module": "gsm_service"
                }
            ]
        except Exception:
            log_entries = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "WARNING",
                    "message": "Não foi possível ler arquivos de log",
                    "module": "system"
                }
            ]
        
        return {
            "logs": log_entries[-lines:],  # Últimas N linhas
            "total_lines": len(log_entries),
            "requested_level": level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/maintenance/restart-modems")
async def restart_modems(
    current_user: User = Depends(get_current_user),
    gsm_service: GSMModem = Depends(get_gsm_service)
):
    """
    Reinicia conexão com todos os modems GSM.
    
    Requer usuário admin.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Reiniciar modems
        result = await gsm_service.restart_all_modems()
        
        logger.info(f"Modems reiniciados por {current_user.email}")
        
        return {
            "success": True,
            "message": "Modems reiniciados com sucesso",
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reiniciar modems: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/maintenance/cleanup-old-data")
async def cleanup_old_data(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove dados antigos do sistema.
    
    - **days**: Remover dados com mais de N dias
    
    Requer usuário admin.
    """
    try:
        # Verificar se usuário é admin
        if current_user.user_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores"
            )
        
        # Validar parâmetro
        if days < 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível remover dados com menos de 7 dias"
            )
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Remover mensagens antigas
        old_messages = db.query(Message).filter(
            Message.created_at < cutoff_date,
            Message.status.in_(["delivered", "failed"])  # Manter pendentes
        )
        messages_count = old_messages.count()
        old_messages.delete()
        
        # Remover sessões USSD antigas
        old_ussd = db.query(USSDSession).filter(
            USSDSession.created_at < cutoff_date,
            USSDSession.status.in_(["completed", "error", "timeout"])  # Manter ativas
        )
        ussd_count = old_ussd.count()
        old_ussd.delete()
        
        db.commit()
        
        logger.info(f"Limpeza de dados executada por {current_user.email}: {messages_count} mensagens, {ussd_count} sessões USSD")
        
        return {
            "success": True,
            "message": "Limpeza executada com sucesso",
            "details": {
                "cutoff_date": cutoff_date.isoformat(),
                "messages_removed": messages_count,
                "ussd_sessions_removed": ussd_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na limpeza de dados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/info")
async def get_system_info():
    """
    Obtém informações básicas do sistema (público).
    
    Não requer autenticação.
    """
    try:
        return {
            "name": "AMAMESSAGE",
            "version": SYSTEM_VERSION,
            "api_version": API_VERSION,
            "description": "Sistema de automação SMS/USSD",
            "platform": platform.system(),
            "features": [
                "SMS Sending & Receiving",
                "USSD Automation", 
                "Contact Management",
                "Forwarding Rules",
                "Multi-Platform Support",
                "Real-time Monitoring"
            ],
            "endpoints": {
                "health": "/api/v2/system/health",
                "auth": "/api/v2/auth/login",
                "sms": "/api/v2/sms/send",
                "ussd": "/api/v2/ussd/send",
                "contacts": "/api/v2/contacts"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
