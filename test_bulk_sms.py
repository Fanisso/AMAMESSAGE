#!/usr/bin/env python3
"""
Teste do sistema de SMS em massa
"""
import asyncio
import requests
import json
import time

# Configuração de teste
BASE_URL = "http://127.0.0.1:8000"
TEST_PHONES = [
    "+258841111111",
    "+258841111112", 
    "+258841111113"
]
TEST_MESSAGE = "Teste SMS em massa - AMA MESSAGE"

def test_bulk_sms():
    """Testar envio de SMS em massa"""
    print("🧪 Testando sistema de SMS em massa...")
    
    # 1. Enviar SMS em massa
    print("\n📤 1. Enviando SMS em massa...")
    
    bulk_data = {
        "phones": TEST_PHONES,
        "message": TEST_MESSAGE,
        "priority": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sms/send-bulk",
            json=bulk_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Resposta do servidor: {result['message']}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar requisição: {str(e)}")
        return False
    
    # 2. Verificar status da fila
    print("\n📋 2. Verificando status da fila...")
    
    for i in range(10):  # Verificar por 20 segundos
        try:
            response = requests.get(f"{BASE_URL}/api/sms/queue/status", timeout=5)
            
            if response.status_code == 200:
                status = response.json()
                print(f"   Pendentes: {status['total_pending']}, Processados: {status['total_processed']}, Processador: {'Ativo' if status.get('processor_running') else 'Inativo'}")
                
                if status['total_pending'] == 0 and status['total_processed'] >= len(TEST_PHONES):
                    print("✅ Todos os SMS foram processados!")
                    break
            else:
                print(f"   ⚠️ Erro ao obter status: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar status: {str(e)}")
        
        time.sleep(2)
    else:
        print("⏰ Tempo limite atingido - alguns SMS podem ainda estar a ser processados")
    
    # 3. Verificar SMS na base de dados
    print("\n📱 3. Verificando SMS enviados...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/sms/list?limit=10", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                sms_list = result.get('data', [])
                recent_sms = [sms for sms in sms_list if sms['message'] == TEST_MESSAGE]
                
                print(f"   📊 Encontrados {len(recent_sms)} SMS de teste na base de dados")
                
                for sms in recent_sms[:3]:  # Mostrar apenas os primeiros 3
                    print(f"   📱 SMS #{sms['id']}: {sms['phone_to']} - Status: {sms['status']}")
            else:
                print(f"   ❌ Erro na resposta: {result.get('message')}")
        else:
            print(f"   ❌ Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar SMS: {str(e)}")
    
    print("\n✅ Teste concluído!")
    return True

def test_server_status():
    """Verificar se o servidor está a funcionar"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🔧 Sistema de Teste - SMS em Massa")
    print("=" * 50)
    
    # Verificar se servidor está ativo
    if not test_server_status():
        print("❌ Servidor não está a responder!")
        print("   Execute: uvicorn main:app --reload")
        exit(1)
    
    print("✅ Servidor está ativo!")
    
    # Executar teste
    success = test_bulk_sms()
    
    if success:
        print("\n🎉 Teste completado com sucesso!")
    else:
        print("\n❌ Teste falhou!")
