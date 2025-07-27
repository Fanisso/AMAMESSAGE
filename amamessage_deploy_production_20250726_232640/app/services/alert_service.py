import logging
import smtplib
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)

class AlertService:
    """Serviço para envio de alertas por email ou webhook."""
    def __init__(self, email_config: Optional[dict] = None, webhook_url: Optional[str] = None):
        if email_config is None or webhook_url is None:
            try:
                from app.core.config import Settings
                settings = Settings()
                if email_config is None and settings.ALERT_EMAIL_SMTP and settings.ALERT_EMAIL_TO:
                    self.email_config = {
                        'smtp': settings.ALERT_EMAIL_SMTP,
                        'port': settings.ALERT_EMAIL_PORT or 587,
                        'user': settings.ALERT_EMAIL_USER,
                        'password': settings.ALERT_EMAIL_PASSWORD,
                        'from': settings.ALERT_EMAIL_FROM,
                        'to': settings.ALERT_EMAIL_TO,
                    }
                else:
                    self.email_config = email_config
                if webhook_url is None and settings.ALERT_WEBHOOK_URL:
                    self.webhook_url = settings.ALERT_WEBHOOK_URL
                else:
                    self.webhook_url = webhook_url
            except Exception as e:
                logger.error(f"Erro ao carregar configurações de alerta: {e}")
                self.email_config = email_config
                self.webhook_url = webhook_url
        else:
            self.email_config = email_config
            self.webhook_url = webhook_url

    def send_email_alert(self, subject: str, message: str) -> bool:
        from app.services.alert_log import AlertLog
        if not self.email_config:
            logger.warning("Configuração de email não definida para alertas.")
            AlertLog.add("Alerta EMAIL não enviado", "Configuração ausente", False)
            return False
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            with smtplib.SMTP(self.email_config['smtp'], self.email_config.get('port', 587)) as server:
                server.starttls()
                server.login(self.email_config['user'], self.email_config['password'])
                server.sendmail(self.email_config['from'], [self.email_config['to']], msg.as_string())
            logger.info(f"Alerta de email enviado para {self.email_config['to']}")
            AlertLog.add("Alerta EMAIL enviado", f"Para: {self.email_config['to']}", True)
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de email: {e}")
            AlertLog.add("Falha ao enviar alerta EMAIL", str(e), False)
            return False

    def send_webhook_alert(self, message: str) -> bool:
        from app.services.alert_log import AlertLog
        if not self.webhook_url:
            logger.warning("Webhook URL não definida para alertas.")
            AlertLog.add("Alerta WEBHOOK não enviado", "Webhook URL ausente", False)
            return False
        try:
            import requests
            response = requests.post(self.webhook_url, json={"text": message})
            if response.status_code == 200:
                logger.info("Alerta enviado via webhook.")
                AlertLog.add("Alerta WEBHOOK enviado", f"URL: {self.webhook_url}", True)
                return True
            else:
                logger.error(f"Falha ao enviar alerta via webhook: {response.status_code}")
                AlertLog.add("Falha ao enviar alerta WEBHOOK", f"Status: {response.status_code}", False)
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar alerta via webhook: {e}")
            AlertLog.add("Erro ao enviar alerta WEBHOOK", str(e), False)
            return False

    def alert_modem_failure(self, details: str):
        subject = "[ALERTA] Falha na detecção do modem GSM"
        message = f"Falha crítica na detecção do modem. Detalhes:\n{details}"
        self.send_email_alert(subject, message)
        self.send_webhook_alert(message)
