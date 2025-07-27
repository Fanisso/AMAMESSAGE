"""
Implementação simplificada do USSD baseada no teste funcional
"""
import serial
import time
import logging
import re
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class USSDSimple:
    """Classe simplificada para USSD baseada no teste que funciona"""
    
    def __init__(self, port: str = None, baudrate: int = 115200, timeout: int = 10):
        self.port = port or getattr(settings, 'MODEM_PORT', 'COM3')
        self.baudrate = baudrate
        self.timeout = timeout
    
    def send_ussd(self, ussd_code: str) -> Dict[str, any]:
        """
        Enviar comando USSD usando a abordagem do teste funcional
        
        Args:
            ussd_code: Código USSD (ex: *155#)
            
        Returns:
            Dict com success, response e error
        """
        try:
            logger.info(f"📞 [SIMPLE] Enviando USSD: {ussd_code} na porta {self.port}")
            
            with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as modem:
                # Passo 1: Teste de comunicação (igual ao teste funcional)
                modem.write(b'AT\r')
                time.sleep(1)
                at_response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
                logger.info(f"[SIMPLE] AT Response: {at_response.strip()}")
                
                # Verificar se respondeu OK
                if 'OK' not in at_response.upper():
                    return {
                        "success": False,
                        "error": f"Modem não respondeu ao comando AT: {at_response}",
                        "response": ""
                    }
                
                # Passo 2: Habilitar USSD (igual ao teste funcional)
                modem.write(b'AT+CUSD=1\r')
                time.sleep(1)
                cusd_response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
                logger.info(f"[SIMPLE] CUSD Enable Response: {cusd_response.strip()}")
                
                # Passo 3: Enviar comando USSD (exatamente igual ao teste funcional)
                ussd_cmd = f'AT+CUSD=1,"{ussd_code}",15\r'
                logger.info(f"[SIMPLE] Enviando comando: {ussd_cmd.strip()}")
                modem.write(ussd_cmd.encode())
                
                # Passo 4: Aguardar resposta (igual ao teste funcional)
                time.sleep(5)  # Exatamente como no teste funcional
                
                # Passo 5: Ler resposta (igual ao teste funcional)
                raw_response = modem.read(modem.in_waiting).decode('utf-8', errors='ignore')
                logger.info(f"[SIMPLE] Raw Response: {repr(raw_response)}")
                
                if not raw_response.strip():
                    return {
                        "success": False,
                        "error": "Nenhuma resposta recebida do modem",
                        "response": ""
                    }
                
                # Processar a resposta
                return self._process_ussd_response(raw_response, ussd_code)
                
        except serial.SerialException as e:
            logger.error(f"[SIMPLE] Erro de conexão serial: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao conectar com o modem: {str(e)}",
                "response": ""
            }
        except Exception as e:
            logger.error(f"[SIMPLE] Erro geral: {str(e)}")
            return {
                "success": False,
                "error": f"Erro interno: {str(e)}",
                "response": ""
            }
    
    def _process_ussd_response(self, raw_response: str, ussd_code: str) -> Dict[str, any]:
        """Processar a resposta USSD, incluindo decodificação de hexadecimal se necessário"""
        from app.utils.hex_utils import decode_hex_message

        # Verificar se houve erro
        if "ERROR" in raw_response.upper() or "COMMAND NOT SUPPORT" in raw_response.upper():
            logger.error(f"[SIMPLE] Erro na resposta: {raw_response}")
            return {
                "success": False,
                "error": f"Erro USSD: {raw_response.strip()}",
                "response": ""
            }

        # Procurar padrões de resposta USSD
        ussd_patterns = [
            r'\+CUSD:\s*(\d+),"([^"]*)"(?:,(\d+))?',
            r'\+CUSD:\s*(\d+),([^,\r\n]+)(?:,(\d+))?',
            r'\+CUSD:\s*(\d+)',
        ]

        for pattern in ussd_patterns:
            match = re.search(pattern, raw_response, re.MULTILINE | re.DOTALL)
            if match:
                status = match.group(1)
                if len(match.groups()) >= 2 and match.group(2):
                    ussd_text = match.group(2).strip()
                    # Tenta decodificar como HEX
                    ussd_text_decoded = decode_hex_message(ussd_text)
                    # Se não for hex válido, mantém original
                    if ussd_text_decoded.startswith('[Mensagem não é hexadecimal válida]') or ussd_text_decoded.startswith('[Erro na decodificação:'):
                        ussd_text_decoded = ussd_text
                    # Limpar caracteres de controle
                    ussd_text_decoded = re.sub(r'[\r\n\x00-\x1f]+', ' ', ussd_text_decoded).strip()
                    ussd_text_decoded = re.sub(r'\s+', ' ', ussd_text_decoded)
                    if ussd_text_decoded:
                        logger.info(f"[SIMPLE] ✅ USSD extraído: {ussd_text_decoded}")
                        return {
                            "success": True,
                            "response": ussd_text_decoded,
                            "status": status,
                            "raw_response": raw_response.strip()
                        }
                else:
                    logger.info(f"[SIMPLE] USSD sem conteúdo, status: {status}")
                    return {
                        "success": True,
                        "response": f"Comando USSD {ussd_code} executado (sem resposta de texto)",
                        "status": status,
                        "raw_response": raw_response.strip()
                    }

        # Se não encontrou padrão CUSD específico, tentar extrair qualquer texto
        clean_response = raw_response.strip()
        lines = clean_response.split('\n')
        useful_lines = []
        for line in lines:
            line = line.strip()
            if line and not any(skip in line.upper() for skip in ['OK', 'AT+CUSD', 'AT\r']):
                # Tenta decodificar como HEX
                line_decoded = decode_hex_message(line)
                if line_decoded.startswith('[Mensagem não é hexadecimal válida]') or line_decoded.startswith('[Erro na decodificação:'):
                    useful_lines.append(line)
                else:
                    useful_lines.append(line_decoded)
        if useful_lines:
            response_text = ' '.join(useful_lines)
            response_text = re.sub(r'[\r\n\x00-\x1f]+', ' ', response_text).strip()
            response_text = re.sub(r'\s+', ' ', response_text)
            if len(response_text) > 3:
                logger.info(f"[SIMPLE] ✅ Resposta extraída: {response_text}")
                return {
                    "success": True,
                    "response": response_text,
                    "status": "0",
                    "raw_response": raw_response.strip()
                }

        logger.warning(f"[SIMPLE] Resposta não interpretada: {repr(raw_response)}")
        return {
            "success": False,
            "error": "Resposta USSD recebida mas não interpretada",
            "response": raw_response.strip()
        }
