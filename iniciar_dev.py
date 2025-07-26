#!/usr/bin/env python3
"""
Script para desenvolvimento - inicializa serviços após o servidor
"""
import uvicorn
import asyncio
import threading
import time

def delayed_modem_init():
    """Inicializar modem após alguns segundos com diagnóstico detalhado"""
    time.sleep(3)  # Aguardar servidor inicializar
    try:
        print("\n" + "="*20 + " DIAGNÓSTICO DO MODEM " + "="*20)
        
        from app.services.modem_detector import ModemDetector
        from app.services.sms_service import SMSService
        
        # 1. Listar portas disponíveis
        print("PASSO 1: Listando todas as portas seriais disponíveis...")
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        if not ports:
            print("❌ ERRO: Nenhuma porta serial encontrada. Verifique a conexão USB do modem.")
            print("="*62)
            return

        print(f"✅ Encontradas {len(ports)} portas:")
        for port in ports:
            desc = port.get('description', 'N/A')
            print(f"   - {port.get('port', 'N/A')}: {desc}")

        # 2. Tentar inicializar o SMSService (que aciona a detecção)
        print("\nPASSO 2: Inicializando serviço de SMS e tentando detectar o modem...")
        sms_service = SMSService()
        
        # 3. Verificar o resultado
        print("\nPASSO 3: Verificando o status da conexão.")
        if sms_service.gsm_modem and sms_service.gsm_modem.is_connected:
            print(f"🎉 SUCESSO! Modem GSM conectado na porta: {sms_service.gsm_modem.port}")
        else:
            print("❌ FALHA: O modem não foi conectado automaticamente.")
            print("\n💡 Possíveis Causas e Soluções:")
            print("   1. Drivers do Modem: Verifique se os drivers do seu modem USB estão instalados corretamente no Windows.")
            print("   2. Porta Ocupada: Outro programa pode estar usando a porta do modem. Feche outros aplicativos que possam acessá-lo.")
            print("   3. Problema Físico: Tente uma porta USB diferente ou reinicie o computador com o modem conectado.")
        
        print("="*62 + "\n")
            
    except Exception as e:
        print(f"💥 ERRO CRÍTICO durante a inicialização do modem: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando AMA MESSAGE (Modo Desenvolvimento)...")
    print("📱 Sistema de SMS com Modem GSM")
    print("🌐 Acesse: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("=" * 50)
    
    # Iniciar thread para inicializar modem após servidor
    modem_thread = threading.Thread(target=delayed_modem_init, daemon=True)
    modem_thread.start()
    
    # Iniciar servidor
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
