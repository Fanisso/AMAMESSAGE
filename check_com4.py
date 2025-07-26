#!/usr/bin/env python3
"""
Script para verificar e liberar COM4
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def check_com4_usage():
    print("🔍 VERIFICANDO USO DA COM4")
    print("=" * 40)
    
    try:
        import serial
        import time
        
        print("🧪 Tentando abrir COM4...")
        
        # Primeira tentativa
        try:
            with serial.Serial('COM4', 115200, timeout=2) as ser:
                print("✅ COM4 está livre!")
                
                # Teste AT
                ser.flushInput()
                ser.flushOutput()
                time.sleep(0.5)
                
                ser.write(b'AT\r\n')
                time.sleep(1)
                
                response = ser.read_all().decode('utf-8', errors='ignore')
                print(f"📤 Comando: AT")
                print(f"📥 Resposta: '{response.strip()}'")
                
                if 'OK' in response:
                    print("🎉 MODEM FUNCIONANDO NA COM4!")
                    return True
                else:
                    print("⚠️ Modem não responde adequadamente")
                    
        except Exception as e:
            if "in use" in str(e).lower():
                print("❌ COM4 está sendo usada por outro programa")
                print("\n💡 SOLUÇÕES:")
                print("1. Feche o Device Manager se estiver aberto")
                print("2. Feche qualquer programa de modem")
                print("3. Feche aplicações que possam usar COM4")
                print("4. Reinicie o modem USB")
                print("\n🔧 COMANDOS PARA VERIFICAR:")
                print("   - Abra o Task Manager")
                print("   - Procure por processos relacionados a modem")
                print("   - Ou reinicie o computador")
                return False
            else:
                print(f"❌ Erro inesperado: {e}")
                return False
                
    except Exception as e:
        print(f"Erro geral: {e}")
        return False

def test_alternative_ports():
    print("\n🔄 TESTANDO PORTAS ALTERNATIVAS")
    print("=" * 40)
    
    ports_to_test = ['COM3', 'COM5', 'COM6']
    
    for port in ports_to_test:
        print(f"\n🧪 Testando {port}...")
        try:
            import serial
            import time
            
            with serial.Serial(port, 115200, timeout=2) as ser:
                print(f"   ✅ {port} aberta")
                
                ser.flushInput()
                ser.flushOutput()
                time.sleep(0.5)
                
                ser.write(b'AT\r\n')
                time.sleep(1)
                
                response = ser.read_all().decode('utf-8', errors='ignore')
                print(f"   📤 AT → 📥 '{response.strip()}'")
                
                if 'OK' in response:
                    print(f"   🎉 {port} RESPONDE A COMANDOS AT!")
                    return port
                    
        except Exception as e:
            print(f"   ❌ {port}: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO PORTA QUALCOMM")
    
    # Tentar COM4 primeiro
    if check_com4_usage():
        print("\n🎯 USAR COM4 - CONFIGURAÇÃO CORRETA")
    else:
        # Testar alternativas
        working_port = test_alternative_ports()
        if working_port:
            print(f"\n🔄 USAR {working_port} COMO ALTERNATIVA")
            print(f"   Atualize o .env: GSM_PORT={working_port}")
        else:
            print("\n😞 NENHUMA PORTA RESPONDE")
            print("   Verifique drivers e conexão do modem")
    
    print("\n" + "=" * 40)
