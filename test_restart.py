import requests
import time

print("=== Reiniciando modem ===")
try:
    response = requests.post("http://127.0.0.1:8000/modem/api/restart", timeout=30)
    result = response.json()
    print(f"Resultado restart: {result}")
    
    # Aguardar um pouco para o modem reinicializar
    print("Aguardando 5 segundos...")
    time.sleep(5)
    
    # Verificar status após restart
    response = requests.get("http://127.0.0.1:8000/modem/api/status", timeout=10)
    status_data = response.json()
    print(f"Status após restart: {status_data}")
    
    # Tentar USSD novamente
    print("\n=== Enviando USSD *180# após restart ===")
    response = requests.post(
        "http://127.0.0.1:8000/modem/api/ussd/send",
        json={"ussd_code": "*180#"},
        timeout=30
    )
    ussd_data = response.json()
    print(f"Resultado USSD:")
    print(f"  Success: {ussd_data.get('success')}")
    print(f"  Response: {ussd_data.get('response', '')}")
    print(f"  Error: {ussd_data.get('error', '')}")
    
except Exception as e:
    print(f"Erro: {e}")
