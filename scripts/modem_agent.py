#!/usr/bin/env python3
"""
Agente de Modem para SaaS AMA MESSAGE
Conecta modem local do cliente ao servidor SaaS via API segura
"""

import os
import sys
import time
import json
import logging
import requests
import serial
from pathlib import Path
from datetime import datetime
import threading
import websocket
import ssl

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('modem_agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ModemAgent:
    """Agente que conecta modem local ao servidor SaaS"""
    
    def __init__(self, config_file="agent_config.json"):
        self.config = self.load_config(config_file)
        self.modem = None
        self.websocket = None
        self.running = False
        self.last_heartbeat = datetime.now()
        
    def load_config(self, config_file):
        """Carregar configuração do agente"""
        default_config = {
            "server_url": "https://seuservico.com",
            "api_key": "sua_api_key_aqui",
            "client_id": "cliente_001",
            "modem_port": "COM3",  # Windows: COM3, Linux: /dev/ttyUSB0
            "modem_baud": 115200,
            "reconnect_interval": 30,
            "heartbeat_interval": 60,
            "ssl_verify": True
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge com defaults
                default_config.update(config)
        else:
            # Criar ficheiro de configuração inicial
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Configuração criada: {config_file} - Configure antes de usar!")
            
        return default_config
    
    def connect_modem(self):
        """Conectar ao modem GSM local"""
        try:
            self.modem = serial.Serial(
                self.config['modem_port'],
                self.config['modem_baud'],
                timeout=10
            )
            
            # Testar comunicação
            self.modem.write(b'AT\r\n')
            response = self.modem.read(100).decode('utf-8', errors='ignore')
            
            if 'OK' in response:
                logger.info(f"✅ Modem conectado: {self.config['modem_port']}")
                return True
            else:
                logger.error(f"❌ Modem não responde: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar modem: {e}")
            return False
    
    def send_sms_via_modem(self, phone, message):
        """Enviar SMS via modem local"""
        try:
            if not self.modem:
                return {"success": False, "error": "Modem não conectado"}
            
            # Configurar modo texto
            self.modem.write(b'AT+CMGF=1\r\n')
            time.sleep(1)
            
            # Definir destinatário
            cmd = f'AT+CMGS="{phone}"\r\n'.encode()
            self.modem.write(cmd)
            time.sleep(1)
            
            # Enviar mensagem
            self.modem.write(f'{message}\x1A'.encode('utf-8'))
            time.sleep(3)
            
            # Ler resposta
            response = self.modem.read(200).decode('utf-8', errors='ignore')
            
            if '+CMGS:' in response:
                logger.info(f"✅ SMS enviado para {phone}")
                return {"success": True, "response": response}
            else:
                logger.error(f"❌ Falha no envio: {response}")
                return {"success": False, "error": response}
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def read_incoming_sms(self):
        """Ler SMS recebidos do modem"""
        try:
            if not self.modem:
                return []
            
            # Listar SMS recebidos
            self.modem.write(b'AT+CMGL="REC UNREAD"\r\n')
            time.sleep(2)
            
            response = self.modem.read(2000).decode('utf-8', errors='ignore')
            
            # Parse SMS (implementação simplificada)
            sms_list = []
            lines = response.split('\n')
            
            for i, line in enumerate(lines):
                if '+CMGL:' in line:
                    # Próxima linha contém a mensagem
                    if i + 1 < len(lines):
                        parts = line.split(',')
                        sender = parts[2].strip('"') if len(parts) > 2 else "Unknown"
                        message = lines[i + 1].strip()
                        
                        sms_list.append({
                            "sender": sender,
                            "message": message,
                            "timestamp": datetime.now().isoformat()
                        })
            
            return sms_list
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler SMS: {e}")
            return []
    
    def connect_to_server(self):
        """Conectar ao servidor SaaS via WebSocket"""
        try:
            ws_url = self.config['server_url'].replace('https://', 'wss://').replace('http://', 'ws://')
            ws_url += f"/ws/modem/{self.config['client_id']}?api_key={self.config['api_key']}"
            
            self.websocket = websocket.WebSocketApp(
                ws_url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Conectar com SSL se necessário
            if self.config['ssl_verify']:
                self.websocket.run_forever(sslopt={"cert_reqs": ssl.CERT_REQUIRED})
            else:
                self.websocket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                
        except Exception as e:
            logger.error(f"❌ Erro ao conectar servidor: {e}")
    
    def on_open(self, ws):
        """Callback quando WebSocket conecta"""
        logger.info("✅ Conectado ao servidor SaaS")
        self.send_status_update()
    
    def on_message(self, ws, message):
        """Processar comandos do servidor"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'send_sms':
                phone = data.get('phone')
                text = data.get('message')
                
                logger.info(f"📤 Enviando SMS para {phone}")
                result = self.send_sms_via_modem(phone, text)
                
                # Enviar resultado de volta
                response = {
                    "type": "sms_result",
                    "success": result['success'],
                    "phone": phone,
                    "error": result.get('error')
                }
                ws.send(json.dumps(response))
                
            elif command == 'get_status':
                self.send_status_update()
                
            elif command == 'heartbeat':
                self.last_heartbeat = datetime.now()
                ws.send(json.dumps({"type": "heartbeat_ack"}))
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar comando: {e}")
    
    def on_error(self, ws, error):
        """Callback para erros"""
        logger.error(f"❌ Erro WebSocket: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Callback quando desconecta"""
        logger.warning("⚠️ Desconectado do servidor")
    
    def send_status_update(self):
        """Enviar status do modem para servidor"""
        try:
            # Verificar status do modem
            modem_status = "connected" if self.modem and self.modem.is_open else "disconnected"
            
            status = {
                "type": "status_update",
                "client_id": self.config['client_id'],
                "modem_status": modem_status,
                "modem_port": self.config['modem_port'],
                "timestamp": datetime.now().isoformat(),
                "agent_version": "1.0.0"
            }
            
            if self.websocket:
                self.websocket.send(json.dumps(status))
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar status: {e}")
    
    def check_incoming_sms(self):
        """Thread para verificar SMS recebidos"""
        while self.running:
            try:
                sms_list = self.read_incoming_sms()
                
                for sms in sms_list:
                    # Enviar para servidor
                    data = {
                        "type": "incoming_sms",
                        "client_id": self.config['client_id'],
                        "sender": sms['sender'],
                        "message": sms['message'],
                        "timestamp": sms['timestamp']
                    }
                    
                    if self.websocket:
                        self.websocket.send(json.dumps(data))
                        logger.info(f"📥 SMS recebido enviado ao servidor: {sms['sender']}")
                
                time.sleep(10)  # Verificar a cada 10 segundos
                
            except Exception as e:
                logger.error(f"❌ Erro ao verificar SMS: {e}")
                time.sleep(30)
    
    def run(self):
        """Executar agente principal"""
        logger.info("🚀 Iniciando Agente de Modem SaaS...")
        
        # Conectar modem
        if not self.connect_modem():
            logger.error("❌ Não foi possível conectar ao modem. Verifique a configuração.")
            return
        
        self.running = True
        
        # Iniciar thread para verificar SMS
        sms_thread = threading.Thread(target=self.check_incoming_sms, daemon=True)
        sms_thread.start()
        
        # Loop principal com reconexão automática
        while self.running:
            try:
                logger.info("🔌 Conectando ao servidor SaaS...")
                self.connect_to_server()
                
                # Se chegou aqui, perdeu conexão
                logger.warning("⚠️ Conexão perdida. Reconectando em 30 segundos...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Parando agente...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                time.sleep(30)
        
        # Limpar recursos
        if self.modem:
            self.modem.close()
        
        logger.info("✅ Agente parado")


def create_windows_service():
    """Criar serviço Windows para o agente"""
    service_script = '''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import servicemanager
import win32serviceutil
import win32service
import win32event
from modem_agent import ModemAgent

class ModemAgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AMAMessageModemAgent"
    _svc_display_name_ = "AMA MESSAGE - Modem Agent"
    _svc_description_ = "Agente de conexão do modem GSM com servidor SaaS"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.agent = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.agent:
            self.agent.running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        self.agent = ModemAgent()
        self.agent.run()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(ModemAgentService)
'''
    
    with open('modem_service.py', 'w') as f:
        f.write(service_script)
    
    logger.info("✅ Script de serviço Windows criado: modem_service.py")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agente de Modem SaaS")
    parser.add_argument("--install-service", action="store_true", help="Instalar como serviço Windows")
    parser.add_argument("--config", default="agent_config.json", help="Ficheiro de configuração")
    
    args = parser.parse_args()
    
    if args.install_service:
        if os.name == 'nt':
            create_windows_service()
            print("\n📋 Para instalar o serviço Windows:")
            print("python modem_service.py install")
            print("python modem_service.py start")
        else:
            print("❌ Serviços Windows só funcionam no Windows")
        return
    
    # Executar agente
    agent = ModemAgent(args.config)
    agent.run()


if __name__ == "__main__":
    main()
