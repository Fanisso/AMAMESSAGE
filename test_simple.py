#!/usr/bin/env python3
"""
Script simples para testar USSD
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_ussd_simple():
    try:
        print("🧪 Teste simples USSD")
        
        # Testar importação
        from app.services.gsm_service import GSMModem
        print("✅ GSMModem importado")
        
        from app.services.modem_detector import ModemDetector
        print("✅ ModemDetector importado")
        
        # Detectar modem (sem conectar)
        detector = ModemDetector()
        print("✅ Detector criado")
        
        # Listar portas disponíveis
        ports = detector.list_available_ports()
        print(f"✅ Portas disponíveis: {len(ports)}")
        for port in ports[:3]:  # Mostrar apenas 3
            print(f"   - {port['port']}: {port['description'][:50]}...")
        
        print("\n🎉 Teste básico passou!")
        print("\nPara testar USSD com modem real:")
        print("1. Conecte o modem GSM via USB")
        print("2. Insira um SIM card ativo")
        print("3. Execute: python test_ussd_codes.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_ussd_simple()
