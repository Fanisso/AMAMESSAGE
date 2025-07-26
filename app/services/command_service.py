from sqlalchemy.orm import Session
from app.db.models import SMS, SMSCommand, SMSResponse, SMSStatus, SMSDirection
from app.services.sms_service import SMSService
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class CommandService:
    """Serviço para processar comandos automáticos em SMS"""
    
    def __init__(self):
        self.sms_service = SMSService()
    
    async def process_incoming_sms(self, sms_id: int, db: Session):
        """Processar SMS recebido e verificar se contém comandos"""
        try:
            # Buscar SMS
            sms = db.query(SMS).filter(SMS.id == sms_id).first()
            if not sms:
                logger.error(f"SMS {sms_id} não encontrado")
                return
            
            logger.info(f"Processando SMS de {sms.phone_from}: {sms.message}")
            
            # Extrair comandos da mensagem
            commands_found = self._extract_commands(sms.message, db)
            
            if not commands_found:
                logger.info("Nenhum comando encontrado no SMS")
                return
            
            # Processar cada comando encontrado
            for command in commands_found:
                await self._execute_command(sms, command, db)
            
        except Exception as e:
            logger.error(f"Erro ao processar SMS {sms_id}: {str(e)}")
    
    def _extract_commands(self, message: str, db: Session) -> list:
        """Extrair comandos da mensagem SMS"""
        commands_found = []
        
        # Buscar todos os comandos ativos
        active_commands = db.query(SMSCommand).filter(
            SMSCommand.is_active == True
        ).all()
        
        for command in active_commands:
            keyword = command.keyword
            
            # Verificar se o comando está na mensagem
            if command.case_sensitive:
                # Busca exata (case sensitive)
                if keyword in message:
                    commands_found.append(command)
            else:
                # Busca case insensitive
                if keyword.lower() in message.lower():
                    commands_found.append(command)
        
        return commands_found
    
    async def _execute_command(self, original_sms: SMS, command: SMSCommand, db: Session):
        """Executar comando e enviar resposta"""
        try:
            logger.info(f"Executando comando '{command.keyword}' para {original_sms.phone_from}")
            
            # Processar variáveis na mensagem de resposta
            response_message = self._process_response_variables(
                command.response_message, 
                original_sms
            )
            
            # Enviar SMS de resposta
            result = await self.sms_service.send_sms_direct(
                phone_to=original_sms.phone_from,
                message=response_message
            )
            
            if result["success"]:
                # Criar registro do SMS de resposta na base de dados
                response_sms = SMS(
                    phone_from=original_sms.phone_to,  # Nosso número
                    phone_to=original_sms.phone_from,  # Número que enviou o comando
                    message=response_message,
                    status=SMSStatus.SENT,
                    direction=SMSDirection.OUTBOUND,
                    external_id=result.get("external_id"),
                    sent_at=datetime.utcnow()
                )
                db.add(response_sms)
                db.flush()  # Para obter o ID
                
                # Registrar a resposta automática
                sms_response = SMSResponse(
                    original_sms_id=original_sms.id,
                    command_id=command.id,
                    response_sms_id=response_sms.id
                )
                db.add(sms_response)
                db.commit()
                
                logger.info(f"Resposta enviada com sucesso para comando '{command.keyword}'")
            else:
                logger.error(f"Falha ao enviar resposta: {result.get('error')}")
                
                # Registrar tentativa de resposta (mesmo com falha)
                sms_response = SMSResponse(
                    original_sms_id=original_sms.id,
                    command_id=command.id,
                    response_sms_id=None  # Sem SMS de resposta pois falhou
                )
                db.add(sms_response)
                db.commit()
                
        except Exception as e:
            logger.error(f"Erro ao executar comando '{command.keyword}': {str(e)}")
    
    def _process_response_variables(self, response_template: str, original_sms: SMS) -> str:
        """Processar variáveis na mensagem de resposta"""
        try:
            # Variáveis disponíveis
            variables = {
                '{NOME}': self._extract_name_from_phone(original_sms.phone_from),
                '{TELEFONE}': original_sms.phone_from,
                '{MENSAGEM}': original_sms.message,
                '{DATA}': datetime.now().strftime('%d/%m/%Y'),
                '{HORA}': datetime.now().strftime('%H:%M'),
                '{DATETIME}': datetime.now().strftime('%d/%m/%Y %H:%M')
            }
            
            # Substituir variáveis
            response = response_template
            for var, value in variables.items():
                response = response.replace(var, value)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar variáveis: {str(e)}")
            return response_template
    
    def _extract_name_from_phone(self, phone: str) -> str:
        """Extrair nome do telefone (implementação básica)"""
        # Por enquanto, retorna "Cliente"
        # Posteriormente pode integrar com agenda ou base de dados de clientes
        return "Cliente"
    
    def create_default_commands(self, db: Session):
        """Criar comandos padrão do sistema"""
        default_commands = [
            {
                "keyword": "HELP",
                "description": "Comando de ajuda",
                "response_message": "📱 AMA MESSAGE - Comandos disponíveis:\n\nHELP - Esta mensagem\nINFO - Informações do sistema\nSTATUS - Status do serviço\nSTOP - Parar de receber mensagens\n\nPara mais informações, visite nosso site."
            },
            {
                "keyword": "INFO", 
                "description": "Informações do sistema",
                "response_message": "ℹ️ AMA MESSAGE\n\nSistema de mensagens SMS\nData: {DATA}\nHora: {HORA}\n\nSeu número: {TELEFONE}\n\nPara ajuda, envie HELP"
            },
            {
                "keyword": "STATUS",
                "description": "Status do serviço", 
                "response_message": "✅ Sistema AMA MESSAGE\n\nStatus: ONLINE\nÚltima atualização: {DATETIME}\n\nTodos os serviços funcionando normalmente."
            },
            {
                "keyword": "STOP",
                "description": "Parar mensagens",
                "response_message": "🛑 Você foi removido da nossa lista de mensagens.\n\nObrigado por usar nossos serviços!\n\nPara reativar, envie START."
            },
            {
                "keyword": "START", 
                "description": "Reativar mensagens",
                "response_message": "🎉 Bem-vindo de volta!\n\nVocê foi reativado em nossa lista.\n\nPara ver comandos disponíveis, envie HELP."
            }
        ]
        
        for cmd_data in default_commands:
            # Verificar se já existe
            existing = db.query(SMSCommand).filter(
                SMSCommand.keyword == cmd_data["keyword"]
            ).first()
            
            if not existing:
                command = SMSCommand(
                    keyword=cmd_data["keyword"],
                    description=cmd_data["description"],
                    response_message=cmd_data["response_message"],
                    is_active=True,
                    case_sensitive=False
                )
                db.add(command)
        
        db.commit()
        logger.info("Comandos padrão criados/verificados")
