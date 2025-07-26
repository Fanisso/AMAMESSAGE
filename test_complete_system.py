#!/usr/bin/env python3
"""
Teste completo do sistema de SMS - individual e em massa
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_sms_system():
    print("=== Teste Completo do Sistema SMS ===")
    
    # 1. Verificar status do modem
    print("\n1️⃣ Verificando status do modem...")
    try:
        response = requests.get(f"{BASE_URL}/modem/api/status", timeout=10)
        status_data = response.json()
        
        if status_data.get('success'):
            modem_data = status_data['data']
            print(f"✅ Modem: {modem_data.get('status', 'N/A')}")
            print(f"   📍 Porta: {modem_data.get('port', 'N/A')}")
            print(f"   📱 Operadora: {modem_data.get('operator', 'N/A')}")
            print(f"   📶 Sinal: {modem_data.get('signal_strength', 0)}%")
        else:
            print(f"❌ Erro no modem: {status_data.get('message', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar modem: {e}")
        return False
    
    # 2. Testar SMS individual
    print("\n2️⃣ Testando SMS individual...")
    numero_teste = input("Digite o número para teste (Enter para pular): ").strip()
    
    if numero_teste:
        try:
            sms_data = {
                "phone_to": numero_teste,
                "message": "Teste SMS individual - AMA MESSAGE"
            }
            
            response = requests.post(f"{BASE_URL}/api/sms/send", json=sms_data, timeout=15)
            result = response.json()
            
            if result.get('id'):
                print(f"✅ SMS individual enviado - ID: {result['id']}")
                
                # Aguardar e verificar status
                time.sleep(3)
                status_response = requests.get(f"{BASE_URL}/api/sms/status/{result['id']}")
                status_result = status_response.json()
                print(f"   📊 Status final: {status_result.get('status', 'N/A')}")
            else:
                print(f"❌ Falha no SMS individual: {result}")
                
        except Exception as e:
            print(f"❌ Erro no SMS individual: {e}")
    else:
        print("⏭️ Teste de SMS individual pulado")
    
    # 3. Testar SMS em massa
    print("\n3️⃣ Testando SMS em massa...")
    
    # Números de teste (você pode mudar estes)
    numeros_teste = [
        "+258841111111",
        "+258842222222", 
        "+258843333333"
    ]
    
    confirmar = input(f"Enviar SMS em massa para {len(numeros_teste)} números? (y/N): ").strip().lower()
    
    if confirmar == 'y':
        try:
            bulk_data = {
                "phones": numeros_teste,
                "message": "Teste SMS em massa - AMA MESSAGE",
                "priority": 1
            }
            
            response = requests.post(f"{BASE_URL}/api/sms/send-bulk", json=bulk_data, timeout=10)
            result = response.json()
            
            if result.get('success'):
                print(f"✅ SMS em massa adicionado à fila: {result['message']}")
            else:
                print(f"❌ Falha no SMS em massa: {result}")
                
        except Exception as e:
            print(f"❌ Erro no SMS em massa: {e}")
    else:
        print("⏭️ Teste de SMS em massa pulado")
    
    # 4. Verificar status da fila
    print("\n4️⃣ Verificando status da fila de SMS...")
    try:
        response = requests.get(f"{BASE_URL}/api/sms/queue/status", timeout=5)
        queue_data = response.json()
        
        print(f"📋 Status da fila:")
        print(f"   ⏳ Pendentes: {queue_data.get('total_pending', 0)}")
        print(f"   ✅ Processados: {queue_data.get('total_processed', 0)}")
        print(f"   🔄 Processador ativo: {queue_data.get('processor_running', False)}")
        
        if queue_data.get('next_scheduled'):
            print(f"   📅 Próximo agendado: {queue_data['next_scheduled']}")
            
    except Exception as e:
        print(f"❌ Erro ao verificar fila: {e}")
    
    # 5. Listar últimos SMS
    print("\n5️⃣ Verificando últimos SMS...")
    try:
        response = requests.get(f"{BASE_URL}/api/sms/list?limit=10", timeout=5)
        sms_data = response.json()
        
        if sms_data.get('success') and sms_data.get('data'):
            print(f"📥 Últimos {len(sms_data['data'])} SMS:")
            
            for sms in sms_data['data'][:5]:  # Mostrar apenas os 5 mais recentes
                direction = "📤" if sms['direction'] == 'outbound' else "📥"
                status_icon = {
                    'pending': '⏳',
                    'sent': '✅', 
                    'delivered': '📬',
                    'failed': '❌',
                    'received': '📥'
                }.get(sms['status'], '❓')
                
                print(f"   {direction} {status_icon} ID:{sms['id']} - {sms['phone_from']} → {sms['phone_to']}")
                print(f"      📝 {sms['message'][:50]}{'...' if len(sms['message']) > 50 else ''}")
        else:
            print("📭 Nenhum SMS encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao listar SMS: {e}")
    
    # 6. Estatísticas gerais
    print("\n6️⃣ Estatísticas do sistema...")
    try:
        response = requests.get(f"{BASE_URL}/api/sms/stats", timeout=5)
        stats = response.json()
        
        print(f"📊 Estatísticas:")
        print(f"   📤 Total enviados: {stats.get('total_sent', 0)}")
        print(f"   📥 Total recebidos: {stats.get('total_received', 0)}")
        print(f"   ⏳ Pendentes: {stats.get('total_pending', 0)}")
        print(f"   ❌ Falhas: {stats.get('total_failed', 0)}")
        
        if stats.get('total_sent', 0) > 0:
            success_rate = (stats.get('total_sent', 0) / (stats.get('total_sent', 0) + stats.get('total_failed', 0))) * 100
            print(f"   📈 Taxa de sucesso: {success_rate:.1f}%")
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
    
    print("\n✅ Teste completo finalizado!")
    print("\n💡 Dicas:")
    print("- Acesse http://127.0.0.1:8000 para o dashboard web")
    print("- Acesse http://127.0.0.1:8000/admin/sms para ver todos os SMS")
    print("- Use http://127.0.0.1:8000/modem/ussd para códigos USSD")
    
    return True

if __name__ == "__main__":
    try:
        test_sms_system()
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
