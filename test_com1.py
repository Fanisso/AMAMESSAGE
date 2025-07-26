#!/usr/bin/env python3
"""
Teste específico para COM1
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_com1():
    print("🧪 TESTE ESPECÍFICO COM1")
    print("=" * 40)
    
    try:
        # Testar importações
        from app.services.modem_detector import ModemDetector
        from app.services.gsm_service import GSMModem
        
        print("✅ Imports OK")
        
        # 1. Listar portas
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        print(f"\n📋 Portas encontradas:")
        com1_found = False
        for port in ports:
            if port['port'] == 'COM1':
                com1_found = True
                print(f"   ✅ COM1: {port['description']}")
            else:
                print(f"   - {port['port']}: {port['description'][:50]}...")
        
        if not com1_found:
            print("   ❌ COM1 não encontrada!")
            return False
        
        # 2. Testar comunicação COM1 diretamente
        print(f"\n🔍 Testando comunicação COM1...")
        if detector._test_modem_communication('COM1'):
            print("   ✅ COM1 responde a comandos AT!")
        else:
            print("   ❌ COM1 não responde a comandos AT")
            return False
        
        # 3. Testar detecção automática
        print(f"\n🔍 Testando detecção automática...")
        modem_info = detector.detect_gsm_modem()
        
        if modem_info and modem_info['port'] == 'COM1':
            print(f"   ✅ Detecção automática encontrou COM1!")
            print(f"   📱 Descrição: {modem_info['description']}")
        else:
            print(f"   ❌ Detecção automática falhou")
            if modem_info:
                print(f"   ℹ️  Encontrou: {modem_info['port']}")
            return False
        
        # 4. Testar GSMModem
        print(f"\n🔌 Testando GSMModem...")
        gsm = GSMModem('COM1')  # Forçar COM1
        
        if gsm.connect():
            print(f"   ✅ GSMModem conectou na COM1!")
            
            # Teste básico
            try:
                response = gsm._get_command_response('AT')
                print(f"   📱 Resposta AT: {response}")
            except Exception as e:
                print(f"   ⚠️ Erro comando AT: {e}")
            
            gsm.disconnect()
        else:
            print(f"   ❌ GSMModem falhou ao conectar")
            return False
        
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"   Modem GSM está funcionando na COM1")
        return True
        
    except Exception as e:
        print(f"💥 Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_com1()
    print("=" * 40)
    if success:
        print("✅ COM1 está funcionando perfeitamente!")
        print("\nPróximos passos:")
        print("1. python iniciar_dev.py")
        print("2. Sistema deve detectar COM1 automaticamente")
    else:
        print("❌ Há problemas com COM1")
        print("\nVerifique:")
        print("- Modem está conectado")
        print("- Drivers instalados")
        print("- Porta não está sendo usada por outro programa")
