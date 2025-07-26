#!/usr/bin/env python3
"""
Detecção rápida de modem (sem teste AT)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def quick_detect():
    print("⚡ DETECÇÃO RÁPIDA DE MODEM")
    print("=" * 40)
    
    try:
        import serial.tools.list_ports
        
        # Listar portas
        ports = list(serial.tools.list_ports.comports())
        print(f"📋 {len(ports)} portas encontradas:")
        
        modem_found = False
        for i, port in enumerate(ports, 1):
            desc = port.description
            print(f"   {i}. {port.device}: {desc}")
            
            # Identificar modem por descrição (sem testar comunicação)
            desc_lower = desc.lower()
            modem_keywords = ['modem', 'qualcomm', 'gsm', 'cellular', 'mobile', 'huawei', 'zte']
            
            if any(keyword in desc_lower for keyword in modem_keywords):
                print(f"      🎯 MODEM DETECTADO!")
                modem_found = True
                
                # Se é COM3 e tem Qualcomm, provavelmente é o modem
                if port.device == 'COM3' and 'qualcomm' in desc_lower:
                    print(f"      ⭐ MODEM GSM PRINCIPAL (COM3 + Qualcomm)")
        
        print(f"\n🎯 RESULTADO:")
        if modem_found:
            print("   ✅ Modem(s) identificado(s) por descrição")
            print("   📝 Recomendação: Usar COM3 (Qualcomm USB Modem)")
        else:
            print("   ❌ Nenhum modem identificado na descrição")
            print("   💡 Pode ser necessário testar comunicação AT")
        
        # Testar configuração atual
        print(f"\n🔧 CONFIGURAÇÃO ATUAL:")
        from app.core.config import settings
        print(f"   GSM_PORT: {settings.GSM_PORT}")
        
        if settings.GSM_PORT == "AUTO":
            print("   ✅ Configurado para detecção automática")
        else:
            print(f"   📍 Configurado para porta fixa: {settings.GSM_PORT}")
        
        return modem_found
        
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    success = quick_detect()
    
    print("=" * 40)
    if success:
        print("✅ Detecção concluída!")
        print("\n🚀 Para testar:")
        print("   python start_server.py")
    else:
        print("⚠️ Nenhum modem detectado")
        print("\n💡 Verificar:")
        print("   - Modem conectado via USB")
        print("   - Drivers instalados")
