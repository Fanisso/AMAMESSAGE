import serial.tools.list_ports
import serial
import time
import logging
from typing import List, Optional, Tuple, Dict

logger = logging.getLogger(__name__)

class ModemDetector:
    def detect_gsm_modem_robust(self, max_retries: int = 2, retry_delay: float = 1.0) -> dict:
        """
        Detecção robusta: testa todas as portas, faz logging detalhado e retorna o motivo de aceitação/rejeição de cada porta.
        Retorna um dicionário com:
            - 'found': info da porta encontrada ou None
            - 'results': lista de dicts com status de cada porta
        """
        logger.info("🔍 [ROBUST] Iniciando varredura total de portas seriais para modem GSM...")
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        all_results = []
        found = None
        for port in ports:
            for attempt in range(1, max_retries+1):
                logger.info(f"[ROBUST] Testando porta {port.device} (tentativa {attempt})...")
                try:
                    with serial.Serial(port.device, 115200, timeout=2) as ser:
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()
                        time.sleep(0.2)
                        ser.write(b'AT\r\n')
                        time.sleep(0.5)
                        response_at = ser.read_all().decode('utf-8', errors='ignore').strip()
                        ser.write(b'ATI\r\n')
                        time.sleep(0.5)
                        response_ati = ser.read_all().decode('utf-8', errors='ignore').strip()
                        logger.debug(f"[ROBUST] Porta {port.device} resposta AT: {repr(response_at)} | ATI: {repr(response_ati)}")
                        if "OK" in response_at or len(response_ati) > 5:
                            logger.info(f"[ROBUST] Porta {port.device} FUNCIONAL para comandos AT!")
                            result = {
                                'port': port.device,
                                'description': port.description,
                                'status': '✅ Funcional',
                                'response_at': repr(response_at),
                                'response_ati': repr(response_ati),
                                'error': ''
                            }
                            all_results.append(result)
                            if not found:
                                found = result
                            break
                        else:
                            result = {
                                'port': port.device,
                                'description': port.description,
                                'status': '⚠️ Sem Resposta AT',
                                'response_at': repr(response_at),
                                'response_ati': repr(response_ati),
                                'error': ''
                            }
                            all_results.append(result)
                    break
                except serial.SerialException as e:
                    logger.warning(f"[ROBUST] Porta {port.device} ocupada ou erro: {e}")
                    if attempt == max_retries:
                        all_results.append({
                            'port': port.device,
                            'description': port.description,
                            'status': '❌ Ocupada ou Erro',
                            'response_at': '',
                            'response_ati': '',
                            'error': str(e)
                        })
                    else:
                        time.sleep(retry_delay)
                except Exception as e:
                    logger.error(f"[ROBUST] Erro inesperado na porta {port.device}: {e}")
                    all_results.append({
                        'port': port.device,
                        'description': port.description,
                        'status': '💥 Erro Inesperado',
                        'response_at': '',
                        'response_ati': '',
                        'error': str(e)
                    })
                    break
        logger.info(f"[ROBUST] Varredura concluída. Porta encontrada: {found['port'] if found else None}")
        return {'found': found, 'results': all_results}
    """Classe para detectar automaticamente modems GSM conectados"""
    
    def detect_gsm_modem(self) -> Optional[Dict[str, str]]:
        """
        Detecta automaticamente um modem GSM conectado (versão otimizada)
        """
        logger.info("🔍 Procurando modems GSM...")
        
        from app.core.config import settings
        ports = serial.tools.list_ports.comports()
        
        # Primeiro, testar portas preferenciais na ordem
        preferred_ports = settings.GSM_PREFERRED_PORTS
        logger.info(f"📋 Testando portas preferenciais: {preferred_ports}")
        
        for preferred_port in preferred_ports:
            for port in ports:
                if port.device == preferred_port:
                    logger.info(f"🔍 Testando porta preferencial: {port.device}")
                    if self._test_modem_communication(port.device):
                        logger.info(f"✅ Modem GSM encontrado na porta preferencial: {port.device}")
                        return {
                            'port': port.device,
                            'description': port.description,
                            'hwid': getattr(port, 'hwid', 'N/A'),
                            'manufacturer': getattr(port, 'manufacturer', 'N/A')
                        }
        
        # Se não encontrou nas preferenciais, testar outras portas com descrições de modem
        logger.info("🔍 Testando outras portas com descrições de modem...")
        for port in ports:
            if port.device not in preferred_ports:
                desc = port.description.lower()
                if any(word in desc for word in ['modem', 'gsm', 'qualcomm', 'huawei', 'zte']):
                    logger.info(f"📱 Testando porta suspeita: {port.device} ({port.description})")
                    if self._test_modem_communication(port.device):
                        return {
                            'port': port.device,
                            'description': port.description,
                            'hwid': getattr(port, 'hwid', 'N/A'),
                            'manufacturer': getattr(port, 'manufacturer', 'N/A')
                        }
        
        logger.warning("❌ Nenhum modem GSM detectado")
        return None
    
    def _test_modem_communication(self, port: str, baudrate: int = 115200, timeout: int = 2) -> bool:
        """
        Testa rapidamente se há um modem na porta (melhorado para Qualcomm)
        """
        try:
            logger.debug(f"Testando comunicação na porta {port}")
            
            # Para modems Qualcomm, 115200 é geralmente o padrão.
            # Testar múltiplos baudrates pode ser lento e desnecessário.
            with serial.Serial(port, baudrate, timeout=timeout) as ser:
                # Limpar buffers
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(0.2)
                
                # Enviar comando AT e verificar resposta
                ser.write(b'AT\r\n')
                time.sleep(0.5) # Dar tempo para o modem responder
                
                response = ser.read_all().decode('utf-8', errors='ignore').strip()
                
                logger.debug(f"Resposta de 'AT' na porta {port}: {repr(response)}")
                
                if "OK" in response:
                    logger.info(f"✅ Modem respondeu 'OK' na porta {port}")
                    return True
                
                # Se 'OK' não veio, tentar um comando de identificação
                ser.write(b'ATI\r\n')
                time.sleep(0.5)
                response_ati = ser.read_all().decode('utf-8', errors='ignore').strip()
                logger.debug(f"Resposta de 'ATI' na porta {port}: {repr(response_ati)}")

                if "Manufacturer" in response_ati or "Model" in response_ati or len(response_ati) > 5:
                     logger.info(f"✅ Modem identificado com 'ATI' na porta {port}")
                     return True

        except serial.SerialException as e:
            logger.warning(f"⚠️ Porta {port} está ocupada ou inacessível: {e}")
        except Exception as e:
            logger.error(f"💥 Erro inesperado ao testar a porta {port}: {e}")
            
        logger.debug(f"❌ Nenhuma resposta de modem na porta {port}")
        return False
    
    def list_available_ports(self) -> List[Dict[str, str]]:
        """
        Lista todas as portas seriais disponíveis
        Retorna lista de dicionários com informações das portas
        """
        ports = serial.tools.list_ports.comports()
        return [
            {
                'port': port.device,
                'description': port.description,
                'hwid': getattr(port, 'hwid', 'N/A'),
                'manufacturer': getattr(port, 'manufacturer', 'N/A')
            }
            for port in ports
        ]
    
    @staticmethod
    def get_modem_info(port: str, baudrate: int = 115200) -> Optional[Dict[str, str]]:
        """
        Obtém informações detalhadas do modem na porta especificada
        """
        try:
            with serial.Serial(port, baudrate, timeout=3) as ser:
                info = {}
                
                # Limpar buffer
                ser.flushInput()
                ser.flushOutput()
                time.sleep(0.5)
                
                # Comandos AT para obter informações
                commands = {
                    'manufacturer': 'AT+CGMI',
                    'model': 'AT+CGMM',
                    'revision': 'AT+CGMR',
                    'imei': 'AT+CGSN',
                    'sim_status': 'AT+CPIN?'
                }
                
                for key, command in commands.items():
                    try:
                        ser.write(f'{command}\r\n'.encode())
                        time.sleep(0.5)
                        response = ser.read(200).decode('utf-8', errors='ignore').strip()
                        
                        # Processar resposta
                        lines = response.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('AT') and 'OK' not in line and 'ERROR' not in line:
                                info[key] = line
                                break
                    except Exception as e:
                        logger.debug(f"Erro ao obter {key}: {e}")
                        info[key] = "N/A"
                
                return info
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do modem na porta {port}: {e}")
            return None
