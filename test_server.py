import requests
import json

print("=== Teste de acesso ao servidor ===")

# Primeiro, testar se o servidor está rodando
try:
    response = requests.get("http://127.0.0.1:8000/", timeout=5)
    print(f"Servidor acessível: {response.status_code}")
except Exception as e:
    print(f"Servidor não acessível: {e}")
    exit(1)

# Testar status do modem
try:
    response = requests.get("http://127.0.0.1:8000/modem/api/status", timeout=10)
    status_data = response.json()
    print(f"Status do modem: {status_data}")
except Exception as e:
    print(f"Erro ao obter status: {e}")

# Testar USSD *180#
try:
    print("\n=== Enviando USSD *180# ===")
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
    print(f"Erro ao enviar USSD: {e}")
