from app.services.ussd_service import USSDService
import logging

logging.basicConfig(level=logging.INFO)

print("=== Teste USSD *180# ===")
ussd = USSDService()
result = ussd.send_ussd('*180#')
print('Resultado USSD *180#:')
print(f'Success: {result["success"]}')
print(f'Response: {result.get("response", "")}')
print(f'Error: {result.get("error", "")}')
