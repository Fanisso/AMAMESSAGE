from app.services.gsm_service import GSMModem
from app.core.config import settings
from app.db.models import SMS, SMSStatus
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import asyncio
import threading
import time

logger = logging.getLogger(__name__)

# Singleton pattern para garantir uma única instância
_sms_service_instance = None

class SMSService:
    """Serviço para envio e gerenciamento de SMS via modem GSM"""
    
    def __new__(cls):
        global _sms_service_instance
        if _sms_service_instance is None:
            _sms_service_instance = super(SMSService, cls).__new__(cls)
            _sms_service_instance._initialized = False
        return _sms_service_instance
        
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.gsm_modem = GSMModem()
        self.is_monitoring = False
        self.monitoring_thread = None
        self._initialize_modem()
        self._initialized = True
    
    def _initialize_modem(self):
        """Inicializar modem GSM com detecção automática de porta"""
        try:
            logger.info("Tentando conectar ao modem GSM...")
            
            # Se a porta estiver configurada como "AUTO", detectar automaticamente
            if settings.GSM_PORT == "AUTO":
                from app.services.modem_detector import ModemDetector
                detector = ModemDetector()
                modem_info = detector.detect_gsm_modem()
                
                if modem_info:
                    logger.info(f"🔍 Modem detectado automaticamente: {modem_info['port']}")
                    self.gsm_modem.port = modem_info['port']
                else:
                    logger.warning("❌ Nenhum modem GSM encontrado automaticamente")
                    return False
            else:
                # Usar porta específica das configurações
                logger.info(f"📍 Usando porta específica: {settings.GSM_PORT}")
                self.gsm_modem.port = settings.GSM_PORT
            
            if self.gsm_modem.connect():
                logger.info(f"✅ Modem GSM conectado na porta: {self.gsm_modem.port}")
                self._start_monitoring()
                return True
            else:
                logger.warning(f"⚠️ Falha ao conectar na porta: {self.gsm_modem.port}")
                return False
                
        except Exception as e:
            logger.warning(f"Modem GSM não disponível - funcionando em modo simulação: {str(e)}")
            return False
    
    def _start_monitoring(self):
        """Iniciar monitoramento de SMS recebidos"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_incoming_sms, daemon=True)
            self.monitoring_thread.start()
            logger.info("Monitoramento de SMS iniciado")
    
    def _monitor_incoming_sms(self):
        """Monitorar SMS recebidos em background com reconexão automática"""
        connection_check_interval = 30  # Verificar conexão a cada 30 segundos
        last_connection_check = 0
        
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # Verificar saúde da conexão periodicamente
                if current_time - last_connection_check > connection_check_interval:
                    if not self.gsm_modem.check_connection_health():
                        logger.warning("🔄 Conexão com modem perdida, tentando reconectar...")
                        if self.gsm_modem.reconnect_automatically():
                            logger.info("✅ Reconexão bem-sucedida!")
                        else:
                            logger.error("❌ Falha na reconexão - tentando novamente em 30s")
                    last_connection_check = current_time
                
                if self.gsm_modem.is_connected:
                    # Ler SMS recebidos
                    incoming_sms = self.gsm_modem.read_sms(delete_after_read=True)
                    
                    if incoming_sms:
                        logger.info(f"Recebidos {len(incoming_sms)} SMS")
                        
                        # Processar cada SMS (isso será feito via callback para a aplicação principal)
                        for sms_data in incoming_sms:
                            self._process_incoming_sms(sms_data)
                
                # Aguardar antes da próxima verificação
                time.sleep(settings.SMS_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento de SMS: {str(e)}")
                time.sleep(10)  # Aguardar mais tempo em caso de erro
    
    def _process_incoming_sms(self, sms_data: dict):
        """Processar SMS recebido (será chamado via callback)"""
        # Esta função será sobrescrita ou chamará um callback da aplicação principal
        logger.info(f"SMS recebido de {sms_data['sender']}: {sms_data['content'][:50]}...")
    
    async def send_sms(self, sms_id: int, db: Session):
        """Enviar SMS usando modem GSM"""
        try:
            # Buscar SMS na base de dados
            sms = db.query(SMS).filter(SMS.id == sms_id).first()
            if not sms:
                logger.error(f"SMS {sms_id} não encontrado")
                return False
            
            # Verificar se modem está conectado
            if not self.gsm_modem.is_connected:
                logger.error("Modem GSM não está conectado")
                sms.status = SMSStatus.FAILED
                sms.error_message = "Modem GSM não conectado"
                db.commit()
                return False
            
            # Enviar SMS via modem GSM
            result = self.gsm_modem.send_sms(sms.phone_to, sms.message)
            
            if result["success"]:
                # Atualizar SMS na base de dados
                sms.external_id = result.get("message_id")
                sms.phone_from = self.gsm_modem.phone_number or "Modem GSM"
                sms.status = SMSStatus.SENT
                sms.sent_at = datetime.utcnow()
                
                db.commit()
                
                logger.info(f"SMS {sms_id} enviado com sucesso. ID: {result.get('message_id')}")
                return True
            else:
                # Atualizar status como falhou
                sms.status = SMSStatus.FAILED
                sms.error_message = result.get("error", "Erro desconhecido")
                sms.retry_count += 1
                db.commit()
                
                logger.error(f"Falha ao enviar SMS {sms_id}: {result.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS {sms_id}: {str(e)}")
            
            # Atualizar status como falhou
            sms = db.query(SMS).filter(SMS.id == sms_id).first()
            if sms:
                sms.status = SMSStatus.FAILED
                sms.error_message = str(e)
                sms.retry_count += 1
                db.commit()
            
            return False
    
    async def send_sms_direct(self, phone_to: str, message: str) -> dict:
        """Enviar SMS diretamente (para respostas automáticas)"""
        try:
            if not self.gsm_modem.is_connected:
                return {
                    "success": False,
                    "error": "Modem GSM não conectado"
                }
            
            # Enviar SMS
            result = self.gsm_modem.send_sms(phone_to, message)
            
            if result["success"]:
                return {
                    "success": True,
                    "external_id": result.get("message_id"),
                    "status": result.get("status", "sent")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Erro no envio")
                }
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS direto para {phone_to}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validar formato do número de telefone"""
        # Remove espaços e caracteres especiais
        clean_phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
        
        # Verificar se tem pelo menos 8 dígitos (número local)
        if len(clean_phone) < 8:
            return False
        
        # Verificar se não tem mais de 15 dígitos (padrão internacional)
        if len(clean_phone) > 15:
            return False
        
        return True
    
    def format_phone_number(self, phone: str) -> str:
        """Formatar número de telefone para padrão local/internacional"""
        # Remove caracteres especiais
        clean_phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
        
        # Se número moçambicano (9 dígitos) e não tem código do país
        if len(clean_phone) == 9 and clean_phone.startswith(('84', '85', '86', '87')):
            return f"+258{clean_phone}"
        
        # Se já tem código do país
        if len(clean_phone) >= 10:
            return f"+{clean_phone}"
        
        # Retorna como está se não conseguir determinar
        return phone
    
    def get_modem_status(self) -> dict:
        """Obter status do modem GSM"""
        if not self.gsm_modem.is_connected:
            return {
                "connected": False,
                "signal_strength": 0,
                "operator": "Desconectado",
                "status": "Offline"
            }
        
        try:
            network_info = self.gsm_modem.get_network_info()
            return {
                "connected": True,
                "signal_strength": network_info.get("signal_strength", 0),
                "operator": network_info.get("operator", "Desconhecido"),
                "status": "Online"
            }
        except Exception as e:
            logger.error(f"Erro ao obter status do modem: {str(e)}")
            return {
                "connected": False,
                "signal_strength": 0,
                "operator": "Erro",
                "status": "Erro"
            }
    
    def restart_modem(self) -> bool:
        """Reiniciar conexão com modem"""
        try:
            logger.info("Reiniciando conexão com modem GSM...")
            
            # Parar monitoramento
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            # Desconectar
            self.gsm_modem.disconnect()
            
            # Reconectar
            if self.gsm_modem.connect():
                self._start_monitoring()
                logger.info("Modem GSM reiniciado com sucesso")
                return True
            else:
                logger.error("Falha ao reiniciar modem GSM")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao reiniciar modem: {str(e)}")
            return False
    
    def stop_service(self):
        """Parar serviço de SMS"""
        logger.info("Parando serviço de SMS...")
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.gsm_modem.disconnect()
        logger.info("Serviço de SMS parado")
    
    def set_incoming_sms_callback(self, callback_func):
        """Definir função callback para SMS recebidos"""
        self._incoming_sms_callback = callback_func
    
    def _process_incoming_sms(self, sms_data: dict):
        """Processar SMS recebido"""
        try:
            # Chamar callback se definido
            if hasattr(self, '_incoming_sms_callback') and self._incoming_sms_callback:
                self._incoming_sms_callback(sms_data)
            else:
                logger.info(f"SMS recebido de {sms_data['sender']}: {sms_data['content'][:50]}...")
                
        except Exception as e:
            logger.error(f"Erro ao processar SMS recebido: {str(e)}")
