#!/usr/bin/env python3
"""
Teste rápido da funcionalidade do sistema com o novo modem
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sms_service import SMSService
import asyncio

async def test_system():
    print("=== Teste do Sistema com Novo Modem ===")
    
    # Inicializar serviço SMS (que usa detecção automática)
    sms_service = SMSService()
    
    print("\n1. Testando conexão com modem...")
    try:
        if await sms_service.connect():
            print("✅ Conectado com sucesso ao modem")
            
            # Testar status
            status = await sms_service.get_status()
            print(f"📱 Status: {status}")
            
            # Testar informações do modem
            info = await sms_service.get_modem_info()
            print(f"📋 Info do modem: {info}")
            
            # Fechar conexão
            await sms_service.disconnect()
            print("✅ Desconectado com sucesso")
            
        else:
            print("❌ Falha ao conectar com o modem")
            
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_system())
