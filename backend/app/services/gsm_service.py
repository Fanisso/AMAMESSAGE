import serial
import time
import re
import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from backend.app.core.config import settings
from backend.app.services.modem_detector import ModemDetector

logger = logging.getLogger(__name__)

class GSMModem:
    """Classe para comunicação com modem GSM via comandos AT"""
    
    def __init__(self, port=None):
        # Usar porta especificada ou detectar automaticamente
        if port:
            self.port = port
            logger.info(f"📍 Usando porta especificada: {self.port}")
        elif settings.GSM_PORT != "AUTO":
            self.port = settings.GSM_PORT
            logger.info(f"📍 Usando porta da configuração: {self.port}")
        else:
            # Detecção automática robusta
            detector = ModemDetector()
            result = detector.detect_gsm_modem_robust()
            modem_info = result['found']
            self.port = modem_info['port'] if modem_info else None
            if self.port:
                logger.info(f"🔍 [ROBUST] Modem detectado automaticamente: {self.port}")
            else:
                logger.warning("❌ [ROBUST] Nenhum modem encontrado - será tentada detecção na conexão")
                # ALERTA AUTOMÁTICO
                try:
                    from app.services.alert_service import AlertService
                    alert = AlertService()
                    alert.alert_modem_failure(str(result['results']))
                except Exception as e:
                    logger.error(f"Erro ao disparar alerta de falha de modem: {e}")
        
        self.baudrate = settings.GSM_BAUDRATE
        self.timeout = settings.GSM_TIMEOUT
        self.pin = settings.GSM_PIN
        self.connection = None
        self.is_connected = False
        self.phone_number = None
        self.smsc = settings.GSM_SMSC
        
    def connect(self) -> bool:
        """Conectar ao modem GSM com detecção automática"""
        try:
            # Se a porta não foi detectada, tentar detecção novamente
            if not self.port:
                logger.info("🔍 [ROBUST] Tentando detecção automática do modem...")
                detector = ModemDetector()
                result = detector.detect_gsm_modem_robust()
                modem_info = result['found']
                if modem_info:
                    self.port = modem_info['port']
                    logger.info(f"📱 [ROBUST] Modem detectado na porta: {self.port}")
                else:
                    logger.error("❌ [ROBUST] Nenhum modem GSM encontrado automaticamente")
                    return False
            
            logger.info(f"🔌 Conectando ao modem GSM na porta {self.port}...")
            
            # Verificar se a porta ainda existe
            import serial.tools.list_ports
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            
            if self.port not in available_ports:
                logger.warning(f"⚠️ Porta {self.port} não encontrada. Tentando nova detecção robusta...")
                # Tentar detectar novamente (robusto)
                detector = ModemDetector()
                result = detector.detect_gsm_modem_robust()
                modem_info = result['found']
                if modem_info:
                    self.port = modem_info['port']
                    logger.info(f"📱 [ROBUST] Modem redetectado na porta: {self.port}")
                else:
                    logger.error(f"❌ [ROBUST] Porta {self.port} não encontrada. Portas disponíveis: {available_ports}")
                    return False
            
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Aguardar um pouco para o modem inicializar
            time.sleep(2)
            
            # Testar comunicação básica
            if self._send_command("AT"):
                logger.info("Comunicação com modem estabelecida")
                
                # Configurar modem
                if self._initialize_modem():
                    self.is_connected = True
                    logger.info("Modem GSM conectado e configurado com sucesso")
                    return True
                else:
                    logger.error("Falha na configuração do modem")
                    return False
            else:
                logger.error("Falha na comunicação com modem")
                return False
                
        except serial.SerialException as e:
            logger.warning(f"Modem GSM não disponível na porta {self.port}: {str(e)}")
            return False
        except Exception as e:
            logger.warning(f"Erro ao conectar com modem GSM: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar do modem GSM"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.is_connected = False
            logger.info("Conexão com modem GSM encerrada")
    
    def _send_command(self, command: str, wait_for: str = "OK", timeout: int = None) -> bool:
        """Enviar comando AT para o modem"""
        if not self.connection or not self.connection.is_open:
            return False
        
        timeout = timeout or self.timeout
        
        try:
            # Limpar buffer de entrada
            self.connection.reset_input_buffer()
            
            # Enviar comando
            full_command = command + "\r\n"
            self.connection.write(full_command.encode())
            
            # Aguardar resposta
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < timeout:
                if self.connection.in_waiting > 0:
                    response += self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                    
                    if wait_for in response:
                        logger.debug(f"✅ Comando '{command}' executado com sucesso")
                        return True
                    elif "ERROR" in response:
                        # Extrair código de erro específico se possível
                        error_info = response.strip()
                        if "+CMS ERROR:" in error_info:
                            error_code = error_info.split("+CMS ERROR:")[-1].strip()
                            logger.warning(f"⚠️ Comando '{command}' retornou CMS ERROR {error_code}")
                        elif "+CME ERROR:" in error_info:
                            error_code = error_info.split("+CME ERROR:")[-1].strip()
                            logger.warning(f"⚠️ Comando '{command}' retornou CME ERROR {error_code}")
                        else:
                            logger.warning(f"⚠️ Comando '{command}' retornou erro: {error_info}")
                        return False
                
                time.sleep(0.1)
            
            logger.warning(f"Timeout no comando '{command}'. Resposta: {response}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao enviar comando '{command}': {str(e)}")
            return False
    
    def _get_command_response(self, command: str, timeout: int = None) -> str:
        """Enviar comando e retornar resposta completa"""
        if not self.connection or not self.connection.is_open:
            return ""
        
        timeout = timeout or self.timeout
        
        try:
            # Limpar buffer
            self.connection.reset_input_buffer()
            
            # Enviar comando
            full_command = command + "\r\n"
            self.connection.write(full_command.encode())
            
            # Coletar resposta
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < timeout:
                if self.connection.in_waiting > 0:
                    response += self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                
                if "OK" in response or "ERROR" in response:
                    break
                    
                time.sleep(0.1)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Erro ao obter resposta do comando '{command}': {str(e)}")
            return ""
    
    def reconnect_automatically(self) -> bool:
        """Tenta reconectar automaticamente detectando a nova porta do modem"""
        try:
            logger.info("🔄 Tentando reconexão automática do modem...")
            
            # Fechar conexão atual se existir
            if self.connection and self.connection.is_open:
                self.connection.close()
            
            self.is_connected = False
            
            # Detectar nova porta do modem (robusto)
            detector = ModemDetector()
            result = detector.detect_gsm_modem_robust()
            modem_info = result['found']
            if modem_info:
                old_port = self.port
                self.port = modem_info['port']
                logger.info(f"📱 [ROBUST] Modem redetectado: {old_port} → {self.port}")
                # Tentar conectar na nova porta
                if self.connect():
                    logger.info("✅ Reconexão automática bem-sucedida!")
                    return True
                else:
                    logger.error("❌ Falha na reconexão automática")
                    return False
            else:
                logger.error("❌ [ROBUST] Nenhum modem encontrado para reconexão")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante reconexão automática: {e}")
            return False
    
    def check_connection_health(self) -> bool:
        """Verifica se a conexão com o modem está saudável"""
        try:
            if not self.connection or not self.connection.is_open:
                return False
            
            # Enviar comando AT simples
            return self._send_command("AT", timeout=3)
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde da conexão: {e}")
            return False
    
    def _initialize_modem(self) -> bool:
        """Configurar modem para operação SMS com compatibilidade melhorada"""
        try:
            logger.info("🔧 Inicializando configurações do modem...")
            
            # Comandos básicos essenciais
            essential_commands = [
                ("ATE0", "Desabilitar eco"),
                ("AT+CMGF=1", "Modo texto para SMS"),
            ]
            
            # Comandos opcionais (podem falhar em alguns modems)
            optional_commands = [
                ("AT+CMEE=1", "Habilitar códigos de erro detalhados"),
                ("AT+CSCS=\"GSM\"", "Conjunto de caracteres GSM"),
                ("AT+CPMS=\"SM\",\"SM\",\"SM\"", "Armazenamento SMS no SIM"),
                ("AT+CNMI=2,1,0,1,0", "Notificação de SMS recebidos (modo 1)"),
                ("AT+CNMI=1,1,0,1,0", "Notificação de SMS recebidos (modo 2)"),
                ("AT+CNMI=2,2,0,1,0", "Notificação de SMS recebidos (modo 3)"),
            ]
            
            # Executar comandos essenciais
            for cmd, description in essential_commands:
                logger.debug(f"Executando comando essencial: {cmd} ({description})")
                if not self._send_command(cmd):
                    logger.error(f"❌ Falha no comando essencial: {cmd}")
                    return False
                time.sleep(0.5)
            
            # Executar comandos opcionais (continuar mesmo se falharem)
            for cmd, description in optional_commands:
                logger.debug(f"Executando comando opcional: {cmd} ({description})")
                if self._send_command(cmd):
                    logger.debug(f"✅ Comando opcional bem-sucedido: {cmd}")
                    # Se CNMI funcionou, parar de tentar outros modos
                    if "CNMI" in cmd:
                        logger.info(f"📨 Notificações SMS configuradas: {cmd}")
                        break
                else:
                    logger.warning(f"⚠️ Comando opcional falhou (ignorado): {cmd}")
                time.sleep(0.5)
            
            # Tentar configuração alternativa de notificações se nenhuma funcionou
            if not self._configure_sms_notifications():
                logger.warning("⚠️ Notificações SMS não puderam ser configuradas - modo polling será usado")
            
            # Verificar PIN se necessário
            if not self._check_pin():
                logger.warning("⚠️ Verificação de PIN falhou, mas continuando...")
            
            # Obter informações do modem
            self._get_modem_info()
            
            # Obter centro de mensagens se não configurado
            if not self.smsc:
                self._get_smsc()
            
            logger.info("✅ Modem GSM inicializado com sucesso (modo compatível)")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização do modem: {str(e)}")
            return False
    
    def _configure_sms_notifications(self) -> bool:
        """Configurar notificações SMS com múltiplas tentativas"""
        logger.info("📨 Tentando configurar notificações SMS...")
        
        # Lista de comandos CNMI alternativos para diferentes modems
        cnmi_variations = [
            "AT+CNMI=1,1,0,1,0",  # Modo básico
            "AT+CNMI=2,0,0,1,0",  # Sem indicação direta
            "AT+CNMI=1,0,0,1,0",  # Modo mínimo
            "AT+CNMI=0,0,0,0,0",  # Desabilitado (fallback)
        ]
        
        for cnmi_cmd in cnmi_variations:
            logger.debug(f"Tentando: {cnmi_cmd}")
            if self._send_command(cnmi_cmd):
                logger.info(f"✅ Notificações SMS configuradas com: {cnmi_cmd}")
                return True
            time.sleep(0.5)
        
        logger.warning("⚠️ Nenhuma configuração de notificação SMS funcionou")
        return False
    
    def _check_pin(self) -> bool:
        """Verificar e inserir PIN se necessário"""
        try:
            response = self._get_command_response("AT+CPIN?")
            
            if "READY" in response:
                logger.info("SIM card pronto")
                return True
            elif "SIM PIN" in response:
                if self.pin:
                    logger.info("Inserindo PIN do SIM...")
                    if self._send_command(f"AT+CPIN={self.pin}"):
                        time.sleep(3)  # Aguardar verificação do PIN
                        return self._check_pin()  # Verificar novamente
                    else:
                        logger.error("Falha ao inserir PIN")
                        return False
                else:
                    logger.error("SIM requer PIN mas não foi configurado")
                    return False
            else:
                logger.error(f"Problema com SIM card: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao verificar PIN: {str(e)}")
            return False
    
    def _get_modem_info(self):
        """Obter informações do modem"""
        try:
            # Fabricante
            manufacturer = self._get_command_response("AT+CGMI")
            # Modelo
            model = self._get_command_response("AT+CGMM")
            # Versão do firmware
            version = self._get_command_response("AT+CGMR")
            # IMEI
            imei = self._get_command_response("AT+CGSN")
            
            logger.info(f"Modem Info - Fabricante: {manufacturer}, Modelo: {model}, Versão: {version}, IMEI: {imei}")
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do modem: {str(e)}")
    
    def _get_smsc(self):
        """Obter centro de mensagens SMS"""
        try:
            response = self._get_command_response("AT+CSCA?")
            match = re.search(r'\+CSCA:\s*"([^"]+)"', response)
            if match:
                self.smsc = match.group(1)
                logger.info(f"Centro de mensagens SMS: {self.smsc}")
            else:
                logger.warning("Não foi possível obter o centro de mensagens SMS")
                
        except Exception as e:
            logger.error(f"Erro ao obter SMSC: {str(e)}")
    
    def send_sms(self, phone_number: str, message: str) -> Dict[str, any]:
        """Enviar SMS"""
        if not self.is_connected:
            return {"success": False, "error": "Modem não conectado"}
        
        try:
            logger.info(f"Enviando SMS para {phone_number}: {message[:50]}...")
            
            # Formatar número se necessário
            formatted_number = self._format_phone_number(phone_number)
            
            # Comando para iniciar envio de SMS
            if not self._send_command(f'AT+CMGS="{formatted_number}"', wait_for=">", timeout=10):
                return {"success": False, "error": "Falha ao iniciar envio de SMS"}
            
            # Enviar mensagem seguida de Ctrl+Z (ASCII 26)
            message_with_end = message + chr(26)
            self.connection.write(message_with_end.encode('utf-8', errors='ignore'))
            
            # Aguardar confirmação (pode demorar mais)
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < 30:  # 30 segundos para envio
                if self.connection.in_waiting > 0:
                    response += self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                
                if "+CMGS:" in response:
                    # Extrair ID da mensagem
                    match = re.search(r'\+CMGS:\s*(\d+)', response)
                    message_id = match.group(1) if match else None
                    
                    logger.info(f"SMS enviado com sucesso. ID: {message_id}")
                    return {
                        "success": True, 
                        "message_id": message_id,
                        "status": "sent"
                    }
                elif "ERROR" in response:
                    logger.error(f"Erro ao enviar SMS: {response}")
                    return {"success": False, "error": response}
                
                time.sleep(0.1)
            
            logger.error("Timeout ao enviar SMS")
            return {"success": False, "error": "Timeout no envio"}
            
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def read_sms(self, delete_after_read: bool = True) -> List[Dict[str, any]]:
        """Ler SMS recebidos"""
        if not self.is_connected:
            return []
        
        try:
            # Listar todas as mensagens
            response = self._get_command_response("AT+CMGL=\"ALL\"", timeout=15)
            
            sms_list = []
            messages = re.findall(r'\+CMGL:\s*(\d+),"([^"]+)","([^"]+)",[^,]*,"([^"]+)"\r?\n([^\r\n]+)', response)
            
            for match in messages:
                index, status, sender, timestamp, content = match
                
                sms_data = {
                    "index": int(index),
                    "status": status,
                    "sender": sender,
                    "timestamp": timestamp,
                    "content": content.strip(),
                    "received_at": datetime.now()
                }
                
                sms_list.append(sms_data)
                
                # Deletar mensagem após leitura se solicitado
                if delete_after_read:
                    self._send_command(f"AT+CMGD={index}")
            
            if sms_list:
                logger.info(f"Lidas {len(sms_list)} mensagens SMS")
            
            return sms_list
            
        except Exception as e:
            logger.error(f"Erro ao ler SMS: {str(e)}")
            return []
    
    def _format_phone_number(self, phone: str) -> str:
        """Formatar número de telefone para envio"""
        # Remove caracteres especiais
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        # Se não tem código do país, adicionar +258 (Moçambique)
        if not clean_phone.startswith('+'):
            if len(clean_phone) == 9:  # Número local moçambicano
                clean_phone = '+258' + clean_phone
            elif len(clean_phone) == 11 and clean_phone.startswith(('84', '85', '86', '87')):
                clean_phone = '+258' + clean_phone
        
        return clean_phone
    
    def get_signal_strength(self) -> int:
        """Obter força do sinal"""
        try:
            response = self._get_command_response("AT+CSQ")
            match = re.search(r'\+CSQ:\s*(\d+),', response)
            if match:
                rssi = int(match.group(1))
                # Converter para porcentagem aproximada
                if rssi == 99:
                    return 0  # Sem sinal
                else:
                    return min(100, max(0, (rssi * 100) // 31))
            return 0
            
        except Exception as e:
            logger.error(f"Erro ao obter força do sinal: {str(e)}")
            return 0
    
    def get_network_info(self) -> Dict[str, str]:
        """Obter informações da rede"""
        try:
            # Operadora
            operator_response = self._get_command_response("AT+COPS?")
            operator_match = re.search(r'\+COPS:\s*\d+,\d+,"([^"]+)"', operator_response)
            operator = operator_match.group(1) if operator_match else "Desconhecido"
            
            # Tecnologia de rede
            tech_response = self._get_command_response("AT+COPS=3,2;+COPS?;+COPS=3,0")
            
            return {
                "operator": operator,
                "signal_strength": self.get_signal_strength(),
                "status": "Conectado" if self.is_connected else "Desconectado"
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da rede: {str(e)}")
            return {"operator": "Erro", "signal_strength": 0, "status": "Erro"}
    
    def send_ussd_command(self, ussd_code: str, timeout: int = 30) -> Dict[str, any]:
        def translate_modem_error(error_msg: str) -> str:
            if 'ClearCommError' in error_msg or 'handle is invalid' in error_msg:
                return (
                    'Erro de comunicação com o modem: a porta serial foi desconectada ou está em uso por outro programa.\n'
                    '- Feche outros programas que possam estar usando o modem (ex: app do fabricante, scripts de teste).\n'
                    '- Desconecte e reconecte o modem USB.\n'
                    '- Reinicie o sistema se necessário.\n'
                    '- Certifique-se de que apenas esta aplicação está usando o modem.'
                )
            if '+CME ERROR: 258' in error_msg:
                return (
                    'Erro USSD: Serviço não disponível ou operação não permitida.\n'
                    '- Verifique se o SIM está ativo e habilitado para USSD.\n'
                    '- Teste o código USSD em um telefone comum.\n'
                    '- Tente reiniciar o modem.'
                )
            if 'Timeout' in error_msg:
                return (
                    'Não houve resposta do modem em tempo hábil.\n'
                    '- Verifique o sinal da operadora.\n'
                    '- Tente novamente em alguns instantes.'
                )
            if 'Modem não conectado' in error_msg:
                return (
                    'O modem não está conectado.\n'
                    '- Verifique o cabo USB e a porta.\n'
                    '- Certifique-se de que o modem foi detectado corretamente.'
                )
            return error_msg
        """
        Enviar comando USSD e obter resposta
        
        Args:
            ussd_code: Código USSD (ex: *144#, *150#)
            timeout: Timeout em segundos
            
        Returns:
            Dict com success, response e error
        """
        if not self.is_connected:
            return {"success": False, "error": translate_modem_error("Modem não conectado"), "response": ""}
        
        try:
            logger.info(f"📞 Enviando código USSD: {ussd_code}")
            
            # Limpar buffer antes de enviar
            self.connection.reset_input_buffer()
            
            # Primeiro, tentar cancelar qualquer sessão USSD ativa
            self._send_command("AT+CUSD=2", timeout=2)
            time.sleep(0.5)
            
            # Limpar buffer novamente
            self.connection.reset_input_buffer()
            
            # Enviar comando USSD com diferentes codificações
            def to_ucs2_hex(s: str) -> str:
                return ''.join(f'{ord(c):04X}' for c in s)

            ussd_commands = [
                f'AT+CUSD=1,"{ussd_code}",15',  # GSM 7-bit padrão
                f'AT+CUSD=1,"{ussd_code}",72',  # UCS2 (texto normal)
                f'AT+CUSD=1,"{ussd_code}"',     # Sem codificação especificada
                f'AT+CUSD=1,"{to_ucs2_hex(ussd_code)}",72',  # UCS2 real (hexadecimal)
            ]
            
            for attempt, ussd_command in enumerate(ussd_commands, 1):
                logger.info(f"🔄 Tentativa {attempt}: {ussd_command}")
                
                # Enviar comando
                full_command = ussd_command + "\r\n"
                self.connection.write(full_command.encode())
                
                # Aguardar resposta inicial (OK)
                initial_response = ""
                initial_start = time.time()
                
                while time.time() - initial_start < 5:
                    if self.connection.in_waiting > 0:
                        data = self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                        initial_response += data
                        
                        if "OK" in initial_response:
                            logger.info("✅ Comando USSD aceito pelo modem")
                            break
                        elif "ERROR" in initial_response:
                            logger.warning(f"⚠️ Erro no comando: {initial_response}")
                            if attempt < len(ussd_commands):
                                time.sleep(1)
                                continue
                            else:
                                return {
                                    "success": False,
                                    "error": translate_modem_error(f"Comando USSD rejeitado: {initial_response.strip()}"),
                                    "response": ""
                                }
                    time.sleep(0.1)
                
                # Aguardar resposta USSD
                start_time = time.time()
                response = ""
                ussd_response = ""
                
                while time.time() - start_time < timeout:
                    if self.connection.in_waiting > 0:
                        data = self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                        response += data
                        
                        # Procurar por resposta USSD com diferentes formatos
                        ussd_patterns = [
                            r'\+CUSD:\s*(\d+),"([^"]*)"(?:,(\d+))?',  # Formato padrão
                            r'\+CUSD:\s*(\d+),([^,\r\n]+)(?:,(\d+))?',  # Sem aspas
                            r'\+CUSD:\s*(\d+)',  # Apenas status
                        ]
                        
                        for pattern in ussd_patterns:
                            cusd_match = re.search(pattern, response)
                            if cusd_match:
                                status = cusd_match.group(1)
                                
                                # Tentar extrair mensagem se disponível
                                if len(cusd_match.groups()) >= 2 and cusd_match.group(2):
                                    ussd_response = cusd_match.group(2)
                                    
                                    # Limpar caracteres de controle e decodificar
                                    ussd_response = ussd_response.strip('\r\n\x00')
                                    
                                    # Tentar diferentes decodificações
                                    try:
                                        # Tentar UTF-8 primeiro
                                        ussd_response = ussd_response.encode('latin1').decode('utf-8', errors='ignore')
                                    except:
                                        try:
                                            # Tentar GSM 7-bit
                                            ussd_response = ussd_response.encode('utf-8').decode('gsm0338', errors='ignore')
                                        except:
                                            # Manter original se falhar
                                            pass
                                else:
                                    ussd_response = "Resposta recebida sem conteúdo"
                                
                                logger.info(f"✅ Resposta USSD recebida (Status {status}): {ussd_response}")
                                return {
                                    "success": True,
                                    "response": ussd_response,
                                    "status": status,
                                    "raw_response": response.strip()
                                }
                        
                        # Verificar erro
                        if "ERROR" in response or "COMMAND NOT SUPPORT" in response:
                            logger.error(f"❌ Erro USSD: {response}")
                            if attempt < len(ussd_commands):
                                time.sleep(1)
                                break
                            else:
                                return {
                                    "success": False,
                                    "error": translate_modem_error(f"Erro USSD: {response.strip()}"),
                                    "response": ""
                                }
                    
                    time.sleep(0.1)
                
                # Se chegou aqui com sucesso, sair do loop de tentativas
                if ussd_response:
                    break
            
            # Timeout ou sem resposta
            if not ussd_response:
                logger.warning(f"⏰ Timeout na resposta USSD para {ussd_code}")
                return {
                    "success": False,
                    "error": translate_modem_error(f"Timeout - sem resposta em {timeout}s"),
                    "response": response.strip() if response else "Nenhuma resposta recebida"
                }
            
        except Exception as e:
            logger.error(f"Erro ao enviar USSD {ussd_code}: {str(e)}")
            return {
                "success": False,
                "error": translate_modem_error(f"Erro interno: {str(e)}"),
                "response": ""
            }
    
    def send_ussd(self, ussd_code: str, timeout: int = 30) -> Dict[str, any]:
        """
        Alias para send_ussd_command para compatibilidade
        """
        return self.send_ussd_command(ussd_code, timeout)
    
    def cancel_ussd_session(self) -> bool:
        """Cancelar sessão USSD ativa"""
        try:
            logger.info("🚫 Cancelando sessão USSD...")
            return self._send_command("AT+CUSD=2")
        except Exception as e:
            logger.error(f"Erro ao cancelar USSD: {str(e)}")
            return False
    
    def get_ussd_status(self) -> Dict[str, any]:
        """Obter status da sessão USSD"""
        try:
            response = self._get_command_response("AT+CUSD=?")
            return {
                "supported": "+CUSD:" in response,
                "status": "Suportado" if "+CUSD:" in response else "Não suportado"
            }
        except Exception as e:
            logger.error(f"Erro ao verificar status USSD: {str(e)}")
            return {"supported": False, "status": "Erro"}
