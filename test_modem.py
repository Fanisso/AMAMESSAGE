import logging
logging.basicConfig(level=logging.INFO)

from app.services.sms_service import SMSService
from app.services.ussd_service import USSDService

# Testar status do SMSService
sms_service = SMSService()
print(f'SMSService - Modem conectado: {sms_service.gsm_modem.is_connected}')
print(f'SMSService - Porta do modem: {sms_service.gsm_modem.port}')

# Testar USSDService
ussd_service = USSDService()
modem = ussd_service.get_gsm_modem()
print(f'USSDService - Modem conectado: {modem.is_connected}')
print(f'USSDService - Porta do modem: {modem.port}')
print(f'Mesma instância? {sms_service.gsm_modem is modem}')
