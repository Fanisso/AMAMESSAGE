#!/usr/bin/env python3
"""
Teste rápido de detecção de porta
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def quick_test():
    print("⚡ TESTE RÁPIDO DE PORTA")
    print("=" * 40)
    
    try:
        from app.services.modem_detector import ModemDetector
        
        detector = ModemDetector()
        
        # Listar portas
        print("📋 Portas encontradas:")
        ports = detector.list_available_ports()
        
        for port in ports:
            print(f"   {port['port']}: {port['description']}")
            
            # Destacar portas que podem ser modem
            desc = port['description'].lower()
            if any(word in desc for word in ['modem', 'qualcomm', 'gsm', 'cellular']):
                print(f"   >>> 📱 POSSÍVEL MODEM GSM!")
        
        print(f"\n🎯 RECOMENDAÇÃO:")
        print(f"   - COM3 parece ser o modem GSM (Qualcomm USB Modem)")
        print(f"   - COM1 é uma porta de comunicação padrão")
        print(f"\n💡 PARA CORRIGIR:")
        print(f"   1. Sistema agora usa detecção automática")
        print(f"   2. Configuração mudou de COM3 fixo para AUTO")
        print(f"   3. Se necessário, pode especificar porta manualmente no .env")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    quick_test()
