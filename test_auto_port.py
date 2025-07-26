#!/usr/bin/env python3
"""
Script para testar detecção automática de porta
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_port_detection():
    print("🔍 TESTE DE DETECÇÃO AUTOMÁTICA DE PORTA")
    print("=" * 60)
    
    try:
        # 1. Mostrar configuração atual
        from app.core.config import settings
        print(f"📋 Configuração atual:")
        print(f"   GSM_PORT: {settings.GSM_PORT}")
        print(f"   GSM_AUTO_DETECT: {settings.GSM_AUTO_DETECT}")
        print(f"   GSM_PREFERRED_PORTS: {settings.GSM_PREFERRED_PORTS}")
        
        # 2. Testar detector
        print(f"\n🔍 Testando detector de modem...")
        from app.services.modem_detector import ModemDetector
        
        detector = ModemDetector()
        
        # Listar todas as portas
        all_ports = detector.list_available_ports()
        print(f"   Portas disponíveis: {len(all_ports)}")
        for port in all_ports:
            print(f"     - {port['port']}: {port['description'][:60]}...")
        
        # Detectar modem GSM
        print(f"\n📱 Detectando modem GSM...")
        modem_info = detector.detect_gsm_modem()
        
        if modem_info:
            print(f"   ✅ Modem encontrado!")
            print(f"     Porta: {modem_info['port']}")
            print(f"     Descrição: {modem_info['description']}")
            print(f"     Fabricante: {modem_info.get('manufacturer', 'N/A')}")
        else:
            print(f"   ❌ Nenhum modem GSM encontrado")
        
        # 3. Testar GSMModem
        print(f"\n🔌 Testando GSMModem com configuração automática...")
        from app.services.gsm_service import GSMModem
        
        gsm = GSMModem()
        print(f"   Porta configurada: {gsm.port}")
        
        if gsm.port:
            print(f"   Tentando conectar...")
            if gsm.connect():
                print(f"   ✅ Conexão bem-sucedida!")
                print(f"   📊 Status: {gsm.is_connected}")
                
                # Obter informações do modem
                try:
                    info = gsm._get_command_response("AT+CGMI")  # Fabricante
                    print(f"   📱 Fabricante: {info}")
                except:
                    print(f"   ⚠️ Não foi possível obter informações do fabricante")
                
                gsm.disconnect()
                print(f"   🔌 Desconectado")
            else:
                print(f"   ❌ Falha na conexão")
        else:
            print(f"   ❌ Nenhuma porta disponível")
        
        # 4. Testar SMSService
        print(f"\n📱 Testando SMSService com nova configuração...")
        from app.services.sms_service import SMSService
        
        sms_service = SMSService()
        if sms_service.gsm_modem.is_connected:
            print(f"   ✅ SMSService conectado na porta: {sms_service.gsm_modem.port}")
        else:
            print(f"   ⚠️ SMSService não conectado (modo simulação)")
        
        print(f"\n🎯 CONCLUSÃO:")
        if modem_info:
            print(f"   ✅ Sistema configurado corretamente")
            print(f"   📱 Modem na porta: {modem_info['port']}")
            print(f"   🔧 Configuração: Detecção automática ativa")
        else:
            print(f"   ⚠️ Modem não detectado")
            print(f"   💡 Verifique:")
            print(f"     - Modem conectado via USB")
            print(f"     - Drivers instalados")
            print(f"     - SIM card inserido")
        
    except Exception as e:
        print(f"💥 Erro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 AMA MESSAGE - Teste de Configuração de Porta")
    success = test_port_detection()
    
    print("=" * 60)
    if success:
        print("🎉 Teste concluído!")
        print("\nPara usar o sistema:")
        print("1. python start_server.py")
        print("2. Acesse: http://127.0.0.1:8000/admin/modem")
    else:
        print("⚠️ Há problemas na configuração")
