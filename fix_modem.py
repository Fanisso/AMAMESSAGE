import requests
import time

print("=== Correção: Novo modem detectado ===")

# 1. Verificar detecção automática
print("\n1. Verificando detecção automática...")
try:
    response = requests.get("http://127.0.0.1:8000/modem/api/diagnostic", timeout=15)
    diagnostic = response.json()
    
    if diagnostic.get('success') and diagnostic.get('found'):
        modem_info = diagnostic['found']
        print(f"✅ Novo modem detectado:")
        print(f"   Porta: {modem_info['port']}")
        print(f"   Status: {modem_info['status']}")
        print(f"   Resposta AT: {modem_info.get('response_at', 'N/A')}")
    else:
        print("❌ Nenhum modem detectado automaticamente")
        if diagnostic.get('results'):
            print("   Portas testadas:")
            for result in diagnostic['results'][:3]:
                print(f"     {result['port']}: {result['status']}")
except Exception as e:
    print(f"❌ Erro na detecção: {e}")

# 2. Reiniciar conexão do modem
print("\n2. Reiniciando conexão do modem...")
try:
    response = requests.post("http://127.0.0.1:8000/modem/api/restart", timeout=30)
    restart_result = response.json()
    print(f"🔄 Reinício: {restart_result.get('message', 'N/A')}")
    
    if restart_result.get('success'):
        print("   Aguardando inicialização (8 segundos)...")
        time.sleep(8)
    else:
        print("❌ Falha no reinício")
        
except Exception as e:
    print(f"❌ Erro no reinício: {e}")

# 3. Verificar status após reinício
print("\n3. Verificando status após reinício...")
try:
    response = requests.get("http://127.0.0.1:8000/modem/api/status", timeout=10)
    status_data = response.json()
    
    if status_data.get('success'):
        data = status_data['data']
        print(f"📱 Status do modem:")
        print(f"   Conectado: {data.get('connected', False)}")
        print(f"   Operadora: {data.get('operator', 'N/A')}")
        print(f"   Sinal: {data.get('signal_strength', 0)}%")
        print(f"   Status: {data.get('status', 'N/A')}")
    else:
        print("❌ Erro ao obter status")
        
except Exception as e:
    print(f"❌ Erro no status: {e}")

# 4. Teste básico de comunicação
print("\n4. Teste básico de comunicação...")
try:
    response = requests.post("http://127.0.0.1:8000/modem/api/test-connection", timeout=15)
    test_result = response.json()
    print(f"🔧 Teste de comunicação: {test_result.get('message', 'N/A')}")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")

print("\n=== Correção concluída ===")
print("💡 Instruções:")
print("1. Recarregue a página web (F5)")
print("2. Acesse http://127.0.0.1:8000/modem/ para verificar")
print("3. Se ainda não funcionar, reinicie o servidor completamente")
