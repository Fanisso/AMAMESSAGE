import requests
import time

print("=== Teste de SMS - Envio e Recepção ===")

# 1. Verificar status do modem
print("\n1. Verificando status do modem...")
try:
    response = requests.get("http://127.0.0.1:8000/modem/api/status", timeout=10)
    status_data = response.json()
    print(f"✅ Modem: {status_data['data']['status']} - {status_data['data']['operator']}")
    print(f"   Sinal: {status_data['data']['signal_strength']}%")
except Exception as e:
    print(f"❌ Erro ao verificar status: {e}")
    exit(1)

# 2. Testar envio de SMS
print("\n2. Testando envio de SMS...")
numero_teste = input("Digite o número para teste (ex: +258123456789): ").strip()
if not numero_teste:
    numero_teste = "+258847000000"  # Número de teste padrão

mensagem_teste = "Teste de SMS do sistema AMA MESSAGE"

try:
    response = requests.post(
        "http://127.0.0.1:8000/api/sms/send",
        json={
            "phone_to": numero_teste,
            "message": mensagem_teste
        },
        timeout=30
    )
    sms_data = response.json()
    print(f"📤 Envio SMS:")
    print(f"   Success: {sms_data.get('success')}")
    print(f"   Message: {sms_data.get('message', '')}")
    if sms_data.get('success'):
        sms_id = sms_data.get('data', {}).get('id')
        print(f"   SMS ID: {sms_id}")
        
        # Aguardar alguns segundos e verificar status
        if sms_id:
            print(f"\n   Aguardando envio (5s)...")
            time.sleep(5)
            
            response = requests.get(f"http://127.0.0.1:8000/api/sms/status/{sms_id}")
            status_sms = response.json()
            print(f"   Status final: {status_sms.get('status', 'N/A')}")
            
except Exception as e:
    print(f"❌ Erro no envio: {e}")

# 3. Verificar SMS recebidos (últimos 10)
print("\n3. Verificando SMS recebidos...")
try:
    response = requests.get("http://127.0.0.1:8000/api/sms/list?limit=10", timeout=10)
    sms_list = response.json()
    
    if sms_list.get('success') and sms_list.get('data'):
        print(f"📥 Últimos SMS (total: {len(sms_list['data'])}):")
        for sms in sms_list['data'][:5]:  # Mostrar apenas os 5 mais recentes
            direction = "📤 Enviado" if sms['direction'] == 'outbound' else "📥 Recebido"
            print(f"   {direction} - {sms['phone_from']} → {sms['phone_to']}")
            print(f"     Status: {sms['status']} | {sms['message'][:50]}...")
    else:
        print("   Nenhum SMS encontrado")
        
except Exception as e:
    print(f"❌ Erro ao listar SMS: {e}")

# 4. Estatísticas do dashboard
print("\n4. Estatísticas gerais...")
try:
    response = requests.get("http://127.0.0.1:8000/api/sms/dashboard/stats", timeout=10)
    stats = response.json()
    
    if stats.get('success'):
        data = stats['data']
        print(f"📊 Estatísticas:")
        print(f"   Total SMS: {data.get('total_sms', 0)}")
        print(f"   Enviados: {data.get('sent_sms', 0)}")
        print(f"   Recebidos: {data.get('received_sms', 0)}")
        print(f"   Pendentes: {data.get('pending_sms', 0)}")
        print(f"   Falharam: {data.get('failed_sms', 0)}")
        
except Exception as e:
    print(f"❌ Erro nas estatísticas: {e}")

print("\n=== Teste concluído ===")
print("💡 Dicas:")
print("- Para testar recepção, envie um SMS para o número do SIM no modem")
print("- Acesse http://127.0.0.1:8000/admin/sms para ver a interface web")
print("- Use http://127.0.0.1:8000/api/sms/list para monitorar SMS")
