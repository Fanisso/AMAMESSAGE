#!/usr/bin/env python3
"""
Script para testar a inicialização melhorada do modem GSM
"""
import sys
import os
import logging

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gsm_service import GSMModem

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_modem_initialization():
    """Testar inicialização melhorada do modem"""
    print("🧪 TESTE DE INICIALIZAÇÃO MELHORADA DO MODEM GSM")
    print("=" * 60)
    
    try:
        # Criar instância do modem
        gsm_modem = GSMModem()
        print(f"📍 Porta detectada: {gsm_modem.port}")
        
        # Tentar conectar
        print("\n🔌 Tentando conectar ao modem...")
        if gsm_modem.connect():
            print("✅ Conexão estabelecida com sucesso!")
            
            # Verificar se está conectado
            if gsm_modem.is_connected:
                print("📡 Modem operacional!")
                
                # Testar alguns comandos básicos
                print("\n🧪 Testando comandos básicos...")
                
                # Teste 1: AT básico
                if gsm_modem._send_command("AT"):
                    print("   ✅ Comando AT: OK")
                else:
                    print("   ❌ Comando AT: FALHOU")
                
                # Teste 2: Informações do modem
                manufacturer = gsm_modem._get_command_response("AT+CGMI")
                if manufacturer:
                    print(f"   📱 Fabricante: {manufacturer.strip()}")
                
                model = gsm_modem._get_command_response("AT+CGMM")
                if model:
                    print(f"   📱 Modelo: {model.strip()}")
                
                # Teste 3: Status do SIM
                sim_status = gsm_modem._get_command_response("AT+CPIN?")
                if sim_status:
                    print(f"   📱 Status SIM: {sim_status.strip()}")
                
                # Teste 4: Modo SMS
                if gsm_modem._send_command("AT+CMGF=1"):
                    print("   ✅ Modo SMS texto: OK")
                else:
                    print("   ❌ Modo SMS texto: FALHOU")
                
                print("\n📊 RESULTADO: Modem totalmente funcional!")
                
            else:
                print("⚠️ Modem conectado mas não operacional")
            
            # Desconectar
            gsm_modem.disconnect()
            print("🔌 Modem desconectado")
            
        else:
            print("❌ Falha na conexão com o modem")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_modem_initialization()
