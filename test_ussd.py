#!/usr/bin/env python3
"""
Script para testar funcionalidades USSD do modem GSM
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ussd_service import USSDService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_ussd_functionality():
    print("=== Teste USSD *180# ===")
    ussd = USSDService()
    result = ussd.send_ussd('*180#')
    print('Resultado USSD *180#:')
    print(f'Success: {result["success"]}')
    print(f'Response: {result.get("response", "")}')
    print(f'Error: {result.get("error", "")}')

if __name__ == "__main__":
    test_ussd_functionality()
    """Testar funcionalidades USSD do modem"""
    print("📞 TESTE DE FUNCIONALIDADES USSD")
    print("=" * 50)
    
    try:
        # Inicializar modem
        gsm_modem = GSMModem()
        print(f"📍 Porta detectada: {gsm_modem.port}")
        
        # Conectar modem
        if not gsm_modem.connect():
            print("❌ Falha ao conectar com o modem")
            return
        
        print("✅ Modem conectado com sucesso!")
        
        # Verificar suporte USSD
        print("\n🔍 Verificando suporte USSD...")
        ussd_status = gsm_modem.get_ussd_status()
        print(f"   Suporte USSD: {'✅ Sim' if ussd_status['supported'] else '❌ Não'}")
        print(f"   Status: {ussd_status['status']}")
        
        if not ussd_status['supported']:
            print("⚠️ Modem não suporta USSD ou comando não disponível")
            print("💡 Tentaremos enviar códigos USSD mesmo assim...")
        
        # Menu interativo
        while True:
            print("\n" + "="*50)
            print("📞 MENU USSD")
            print("1. Consultar Saldo (*124#)")
            print("2. Código USSD Personalizado")
            print("3. Cancelar Sessão USSD")
            print("4. Sair")
            print("="*50)
            
            choice = input("Escolha uma opção (1-4): ").strip()
            
            if choice == "1":
                print("\n💰 Consultando saldo...")
                result = gsm_modem.send_ussd("*124#")
                print_ussd_result(result)
                
            elif choice == "2":
                code = input("Digite o código USSD (ex: *125#): ").strip()
                if code:
                    print(f"\n📤 Enviando código: {code}")
                    result = gsm_modem.send_ussd(code)
                    print_ussd_result(result)
                else:
                    print("❌ Código inválido!")
                    
            elif choice == "3":
                print("\n🚫 Cancelando sessão USSD...")
                if gsm_modem.cancel_ussd_session():
                    print("✅ Sessão cancelada com sucesso")
                else:
                    print("❌ Falha ao cancelar sessão")
                    
            elif choice == "4":
                break
                
            else:
                print("❌ Opção inválida!")
        
        # Desconectar
        gsm_modem.disconnect()
        print("\n🔌 Modem desconectado")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

def print_ussd_result(result):
    """Imprimir resultado de comando USSD"""
    if result["success"]:
        print("✅ USSD enviado com sucesso!")
        if result["response"]:
            print("📥 Resposta:")
            print("-" * 30)
            print(result["response"])
            print("-" * 30)
        else:
            print("📋 Aguardando resposta...")
    else:
        print(f"❌ Erro ao enviar USSD: {result['error']}")

def quick_balance_check():
    """Verificação rápida de saldo"""
    print("💰 VERIFICAÇÃO RÁPIDA DE SALDO")
    print("=" * 40)
    
    try:
        gsm_modem = GSMModem()
        
        if gsm_modem.connect():
            print("📤 Consultando saldo (*124#)...")
            result = gsm_modem.send_ussd("*124#")
            print_ussd_result(result)
            gsm_modem.disconnect()
        else:
            print("❌ Falha ao conectar com o modem")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--balance":
        quick_balance_check()
    else:
        test_ussd_functionality()
    
    print(f"\n💡 Para verificação rápida de saldo: python {sys.argv[0]} --balance")
