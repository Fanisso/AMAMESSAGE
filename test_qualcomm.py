#!/usr/bin/env python3
"""
Teste específico para portas Qualcomm
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_qualcomm_ports():
    print("📱 TESTE ESPECÍFICO PORTAS QUALCOMM")
    print("=" * 50)
    
    try:
        from app.services.modem_detector import ModemDetector
        
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        # Filtrar portas Qualcomm
        qualcomm_ports = []
        for port in ports:
            if 'qualcomm' in port['description'].lower():
                qualcomm_ports.append(port)
        
        print(f"🔍 Portas Qualcomm encontradas: {len(qualcomm_ports)}")
        
        # Mostrar informações detalhadas
        for port in qualcomm_ports:
            print(f"\n📋 {port['port']}: {port['description']}")
            
            # Identificar tipo de porta Qualcomm
            desc = port['description'].lower()
            if 'command' in desc or 'control' in desc:
                print(f"   🎯 PORTA DE COMANDOS AT - Esta deve ser usada!")
            elif 'voice' in desc:
                print(f"   🎤 Porta de voz")
            elif 'dm' in desc or 'diagnostic' in desc:
                print(f"   🔧 Porta de diagnóstico")
            else:
                print(f"   ❓ Tipo desconhecido")
        
        # Testar especificamente COM4 (Command Control)
        print(f"\n🧪 TESTE ESPECÍFICO COM4:")
        try:
            import serial
            import time
            
            with serial.Serial('COM4', 115200, timeout=2) as ser:
                print(f"   ✅ Conseguiu abrir COM4")
                
                # Limpar buffers
                ser.flushInput()
                ser.flushOutput()
                time.sleep(0.5)
                
                # Teste AT básico
                ser.write(b'AT\r\n')
                time.sleep(1)
                
                response = ser.read_all().decode('utf-8', errors='ignore')
                print(f"   📤 Enviado: AT")
                print(f"   📥 Resposta: '{response.strip()}'")
                
                if 'OK' in response:
                    print(f"   🎉 MODEM RESPONDEU! COM4 é a porta correta!")
                else:
                    print(f"   ⚠️ Resposta inesperada")
                    
        except Exception as e:
            print(f"   ❌ Erro ao testar COM4: {e}")
        
        # Sugestão final
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"   - Use COM4 (Qualcomm Command Control Port)")
        print(f"   - Esta é a porta padrão para comandos AT em modems Qualcomm")
        print(f"   - Configurar GSM_PORT=COM4 no .env")
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qualcomm_ports()
