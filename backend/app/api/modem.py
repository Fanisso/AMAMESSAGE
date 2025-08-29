
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import io
import csv
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.api.schemas import MessageResponse
from backend.app.services.sms_service import SMSService
from backend.app.services.modem_detector import ModemDetector
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")

@router.get("/api/diagnostic/export")
async def export_modem_diagnostic():
    """Exportar diagnóstico robusto das portas em CSV"""
    try:
        detector = ModemDetector()
        result = detector.detect_gsm_modem_robust()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Porta", "Status", "AT", "ATI", "Erro"])
        for r in result['results']:
            writer.writerow([
                r['port'],
                r['status'],
                (r['response_at'] or '').replace('\n', ' ').replace('\r', ' '),
                (r['response_ati'] or '').replace('\n', ' ').replace('\r', ' '),
                r['error'] or ''
            ])
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=diagnostico_modem.csv"}
        )
    except Exception as e:
        logger.error(f"Erro ao exportar diagnóstico: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/alerts")
async def get_alert_log():
    """Obter log de alertas recentes (memória)"""
    try:
        from backend.app.services.alert_log import AlertLog
        return {"success": True, "alerts": AlertLog.get_all()}
    except Exception as e:
        logger.error(f"Erro ao obter log de alertas: {e}")
        return {"success": False, "error": str(e)}

@router.post("/api/alerts/clear")
async def clear_alert_log():
    """Limpar log de alertas"""
    try:
        from backend.app.services.alert_log import AlertLog
        AlertLog.clear()
        return {"success": True}
    except Exception as e:
        logger.error(f"Erro ao limpar log de alertas: {e}")
        return {"success": False, "error": str(e)}

@router.get("/api/diagnostic")
async def modem_diagnostic():
    """Diagnóstico robusto de todas as portas seriais para modem GSM."""
    try:
        detector = ModemDetector()
        result = detector.detect_gsm_modem_robust()
        return {
            "success": True,
            "found": result['found'],
            "results": result['results']
        }
    except Exception as e:
        logger.error(f"Erro no diagnóstico robusto do modem: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Instância global do serviço SMS (será inicializada na aplicação principal)
sms_service = None

def get_sms_service():
    """Obter instância do serviço SMS (lazy loading)"""
    global sms_service
    if sms_service is None:
        from backend.app.services.sms_service import SMSService
        sms_service = SMSService()
    return sms_service

@router.get("/")
async def modem_status_page(request: Request):
    """Página de status do modem GSM"""
    try:
        service = get_sms_service()
        modem_status = service.get_modem_status()
        
        return templates.TemplateResponse("admin/modem_status.html", {
            "request": request,
            "modem_status": modem_status
        })
    except Exception as e:
        logger.error(f"Erro ao obter status do modem: {str(e)}")
        return templates.TemplateResponse("admin/modem_status.html", {
            "request": request,
            "modem_status": {
                "connected": False,
                "signal_strength": 0,
                "operator": "Erro",
                "status": "Erro ao conectar"
            }
        })

@router.get("/api/status")
async def get_modem_status():
    """API para obter status do modem GSM"""
    try:
        service = get_sms_service()
        status_info = service.get_modem_status()
        
        return {
            "success": True,
            "connected": status_info.get("connected", False),
            "port": status_info.get("port", "N/A"),
            "manufacturer": status_info.get("manufacturer", "N/A"),
            "model": status_info.get("model", "N/A"),
            "signal_strength": status_info.get("signal_strength", 0),
            "operator": status_info.get("operator", "N/A"),
            "status": status_info.get("status", "Desconectado")
        }
    except Exception as e:
        logger.error(f"Erro ao obter status do modem: {str(e)}")
        return {
            "success": False,
            "connected": False,
            "port": "N/A",
            "manufacturer": "N/A", 
            "model": "N/A",
            "signal_strength": 0,
            "operator": "Erro",
            "status": "Erro ao conectar"
        }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter status do modem"
        )

@router.post("/api/restart", response_model=MessageResponse)
async def restart_modem():
    """Reiniciar conexão com modem GSM"""
    try:
        service = get_sms_service()
        
        if service.restart_modem():
            return MessageResponse(
                message="Modem GSM reiniciado com sucesso",
                success=True
            )
        else:
            return MessageResponse(
                message="Falha ao reiniciar modem GSM",
                success=False
            )
    except Exception as e:
        logger.error(f"Erro ao reiniciar modem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao reiniciar modem"
        )

@router.get("/api/detect")
async def detect_modems():
    """Detectar modems GSM disponíveis"""
    try:
        detector = ModemDetector()
        # Detectar modem automaticamente
        detected_port = detector.detect_gsm_modem()
        
        # Listar todas as portas disponíveis
        available_ports = detector.list_available_ports()
        
        return {
            "success": True,
            "data": {
                "detected_modem": detected_port,
                "available_ports": [
                    {"port": port, "description": desc} 
                    for port, desc in available_ports
                ]
            }
        }
    except Exception as e:
        logger.error(f"Erro ao detectar modems: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao detectar modems"
        )

@router.post("/api/reconnect", response_model=MessageResponse)
async def reconnect_modem():
    """Reconectar modem com detecção automática"""
    try:
        service = get_sms_service()
        
        if service.gsm_modem.reconnect_automatically():
            return MessageResponse(
                message="Modem reconectado automaticamente com sucesso",
                success=True
            )
        else:
            return MessageResponse(
                message="Falha na reconexão automática do modem",
                success=False
            )
    except Exception as e:
        logger.error(f"Erro ao reconectar modem: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao reconectar modem"
        )

@router.get("/ussd")
async def ussd_page(request: Request):
    """Página de códigos USSD"""
    try:
        return templates.TemplateResponse("admin/ussd.html", {
            "request": request,
            "page_title": "Códigos USSD"
        })
    except Exception as e:
        logger.error(f"Erro ao carregar página USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao carregar página USSD"
        )

@router.post("/api/ussd/send")
async def send_ussd_code(request: Request):
    """Enviar código USSD"""
    try:
        body = await request.json()
        ussd_code = body.get("ussd_code")
        
        if not ussd_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código USSD é obrigatório"
            )
        
        service = get_sms_service()
        result = service.gsm_modem.send_ussd(ussd_code)
        
        return {
            "success": result["success"],
            "response": result.get("response", ""),
            "error": result.get("error", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao enviar USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar código USSD"
        )

@router.post("/api/ussd/cancel", response_model=MessageResponse)
async def cancel_ussd_session():
    """Cancelar sessão USSD ativa"""
    try:
        service = get_sms_service()
        
        if service.gsm_modem.cancel_ussd_session():
            return MessageResponse(
                message="Sessão USSD cancelada com sucesso",
                success=True
            )
        else:
            return MessageResponse(
                message="Falha ao cancelar sessão USSD",
                success=False
            )
    except Exception as e:
        logger.error(f"Erro ao cancelar USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao cancelar sessão USSD"
        )

@router.get("/api/ussd/status")
async def get_ussd_status():
    """Obter status da funcionalidade USSD"""
    try:
        service = get_sms_service()
        status_info = service.gsm_modem.get_ussd_status()
        
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        logger.error(f"Erro ao obter status USSD: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter status USSD"
        )

@router.post("/api/test-connection", response_model=MessageResponse)
async def test_modem_connection():
    """Testar conexão com modem GSM"""
    try:
        service = get_sms_service()
        modem_status = service.get_modem_status()
        
        if modem_status["connected"]:
            signal_strength = modem_status["signal_strength"]
            operator = modem_status["operator"]
            
            message = f"Conexão OK - Operadora: {operator}, Sinal: {signal_strength}%"
            
            return MessageResponse(
                message=message,
                success=True
            )
        else:
            return MessageResponse(
                message="Modem GSM não conectado",
                success=False
            )
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao testar conexão com modem"
        )

@router.get("/api/ports")
async def list_available_ports():
    """Listar portas seriais disponíveis"""
    try:
        import serial.tools.list_ports
        
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "name": port.name,
                "description": port.description,
                "manufacturer": getattr(port, 'manufacturer', None)
            })
        
        return {
            "success": True,
            "ports": ports
        }
    except Exception as e:
        logger.error(f"Erro ao listar portas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar portas seriais"
        )

@router.post("/api/send-test-sms", response_model=MessageResponse)
async def send_test_sms(phone_number: str, message: str = "Teste do sistema AMA MESSAGE"):
    """Enviar SMS de teste"""
    try:
        service = get_sms_service()
        
        # Validar número
        if not service.validate_phone_number(phone_number):
            return MessageResponse(
                message="Número de telefone inválido",
                success=False
            )
        
        # Formatar número
        formatted_number = service.format_phone_number(phone_number)
        
        # Enviar SMS
        result = await service.send_sms_direct(formatted_number, message)
        
        if result["success"]:
            return MessageResponse(
                message=f"SMS de teste enviado com sucesso para {formatted_number}",
                success=True
            )
        else:
            return MessageResponse(
                message=f"Falha ao enviar SMS: {result.get('error')}",
                success=False
            )
    except Exception as e:
        logger.error(f"Erro ao enviar SMS de teste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar SMS de teste"
        )
