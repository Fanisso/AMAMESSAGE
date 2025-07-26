from app.services.gsm_service import GSMModem
from app.services.ussd_simple import USSDSimple
from app.core.config import settings
from app.db.models import USSDHistory
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class USSDService:
    @staticmethod
    def decode_hex_if_needed(text: str) -> str:
        """Detecta e decodifica string hexadecimal se aplicável usando utilitário dedicado."""
        from app.utils.hex_utils import decode_hex_message
        if not text or not isinstance(text, str):
            return text
        decoded = decode_hex_message(text)
        # Se não for hex válido, retorna o texto original
        if decoded.startswith('[Mensagem não é hexadecimal válida]') or decoded.startswith('[Erro na decodificação:'):
            return text
        return decoded
    """Serviço para gerenciamento de códigos USSD"""
    
    def __init__(self):
        self.gsm_modem = None
        self.ussd_simple = None
        self.common_codes = {
            # Códigos comuns em Moçambique
            "saldo": "*125#",
            "bonus": "*126#", 
            "mb": "*127#",
            "planos": "*129#",
            "servicos": "*144#",
            "recarregar": "*150*",
            "status": "*131#",
            "info": "*100#",
            
            # Códigos Vodacom
            "saldo_vodacom": "*125#",
            "mb_vodacom": "*127#",
            "bonus_vodacom": "*126#",
            "planos_vodacom": "*129#",
            
            # Códigos Tmcel/Movitel
            "saldo_tmcel": "*111#",
            "mb_tmcel": "*148#",
            "bonus_tmcel": "*149#",
        }
    
    def get_gsm_modem(self) -> GSMModem:
        """Obter instância singleton do modem GSM do SMSService"""
        from app.services.sms_service import SMSService
        sms_service = SMSService()  # Sempre retorna a mesma instância singleton
        modem = sms_service.gsm_modem
        # Se não estiver conectado, tentar reconectar automaticamente
        if not modem.is_connected:
            logger.info("[USSD] Modem desconectado, tentando reconectar...")
            modem.connect()
        self.gsm_modem = modem
        return self.gsm_modem
    
    def get_ussd_simple(self) -> USSDSimple:
        """Obter instância do USSD Simple (método direto)"""
        if self.ussd_simple is None:
            self.ussd_simple = USSDSimple(
                port=getattr(settings, 'MODEM_PORT', 'COM3'),
                baudrate=getattr(settings, 'MODEM_BAUDRATE', 115200)
            )
        return self.ussd_simple
    
    def send_ussd(self, ussd_code: str, timeout: int = 30, db: Session = None) -> dict:
        """
        Enviar código USSD - tenta método GSM primeiro, depois método simples
        
        Args:
            ussd_code: Código USSD (ex: *144#)
            timeout: Timeout em segundos
            db: Sessão do banco de dados
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Validar código USSD
            if not self._validate_ussd_code(ussd_code):
                return {
                    "success": False,
                    "error": "Código USSD inválido. Use formato como *144# ou *150*123456789#",
                    "response": ""
                }
            
            logger.info(f"📞 [USSD] Iniciando envio: {ussd_code}")
            
            # Método 1: Tentar com GSMModem (método complexo)
            try:
                modem = self.get_gsm_modem()
                if modem and modem.is_connected:
                    logger.info(f"[USSD] Tentando método GSMModem...")
                    result = modem.send_ussd_command(ussd_code, timeout)
                    
                    # Se teve sucesso ou erro específico que não vale a pena tentar novamente
                    if result.get('success') or 'não conectado' not in result.get('error', '').lower():
                        # Salvar no histórico se banco disponível
                        if db:
                            self._save_ussd_history(ussd_code, result, db)
                        return result
                else:
                    logger.warning(f"[USSD] GSMModem não conectado, tentando método simples...")
            except Exception as e:
                logger.warning(f"[USSD] Erro no método GSMModem: {str(e)}, tentando método simples...")
            
            # Método 2: Usar implementação simples baseada no teste funcional
            logger.info(f"[USSD] Tentando método simplificado...")
            ussd_simple = self.get_ussd_simple()
            result = ussd_simple.send_ussd(ussd_code)
            
            # Salvar no histórico se banco disponível
            if db:
                self._save_ussd_history(ussd_code, result, db)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro geral ao enviar USSD {ussd_code}: {str(e)}")
            error_result = {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "response": ""
            }
            
            # Salvar erro no histórico se banco disponível
            if db:
                self._save_ussd_history(ussd_code, error_result, db)
            
            return error_result
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "response": ""
            }
    
    def get_common_codes(self) -> dict:
        """Obter códigos USSD comuns"""
        return self.common_codes
    
    def get_ussd_by_name(self, name: str) -> str:
        """Obter código USSD por nome"""
        return self.common_codes.get(name.lower(), "")
    
    def cancel_ussd(self) -> dict:
        """Cancelar sessão USSD ativa"""
        try:
            modem = self.get_gsm_modem()
            
            if not modem or not modem.is_connected:
                return {
                    "success": False,
                    "error": (
                        "Modem GSM não está conectado ou foi desconectado.\n"
                        "- Tente reiniciar o modem pelo menu de status.\n"
                        "- Verifique se o cabo USB está conectado e se não há outro programa usando o modem.\n"
                        "- Aguarde alguns segundos e tente novamente."
                    )
                }
            
            success = modem.cancel_ussd_session()
            
            return {
                "success": success,
                "message": "Sessão USSD cancelada" if success else "Falha ao cancelar USSD"
            }
            
        except Exception as e:
            logger.error(f"Erro ao cancelar USSD: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}"
            }
    
    def get_ussd_history(self, db: Session, limit: int = 50) -> list:
        """Obter histórico de códigos USSD"""
        try:
            history = db.query(USSDHistory)\
                       .order_by(USSDHistory.created_at.desc())\
                       .limit(limit)\
                       .all()

            return [
                {
                    "id": h.id,
                    "ussd_code": h.ussd_code,
                    "response": self.decode_hex_if_needed(h.response),
                    "success": h.success,
                    "created_at": h.created_at.isoformat()
                }
                for h in history
            ]

        except Exception as e:
            logger.error(f"Erro ao obter histórico USSD: {str(e)}")
            return []
    
    def _validate_ussd_code(self, ussd_code: str) -> bool:
        """Validar formato do código USSD"""
        # Padrões válidos: *123#, *123*456#, #123#, etc.
        pattern = r'^[*#]\d+([*#]\d+)*[#]?$'
        return bool(re.match(pattern, ussd_code))
    
    def _save_ussd_history(self, ussd_code: str, result: dict, db: Session):
        """Salvar histórico USSD no banco"""
        try:
            history = USSDHistory(
                ussd_code=ussd_code,
                response=result.get("response", ""),
                success=result.get("success", False),
                error_message=result.get("error", ""),
                raw_response=result.get("raw_response", ""),
                created_at=datetime.utcnow()
            )
            
            db.add(history)
            db.commit()
            
            logger.debug(f"Histórico USSD salvo: {ussd_code}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar histórico USSD: {str(e)}")
            db.rollback()
