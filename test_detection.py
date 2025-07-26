#!/usr/bin/env python3
"""
Teste da detecção automática do modem
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.modem_detector import ModemDetector
from app.core.config import Settings
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def main():
    print("=== Teste de Detecção Automática do Modem ===")
    
    # Verificar configurações
    settings = Settings()
    print(f"🔧 GSM_PORT: {settings.GSM_PORT}")
    print(f"🔧 GSM_AUTO_DETECT: {settings.GSM_AUTO_DETECT}")
    print(f"🔧 Portas preferenciais: {settings.GSM_PREFERRED_PORTS}")
    
    # Testar detecção
    detector = ModemDetector()
    
    print("\n📡 Testando detecção otimizada...")
    result = detector.detect_gsm_modem()
    
    if result:
        print(f"✅ Modem detectado automaticamente:")
        print(f"   📍 Porta: {result['port']}")
        print(f"   📋 Descrição: {result['description']}")
        print(f"   🏭 Fabricante: {result.get('manufacturer', 'N/A')}")
        print(f"   🆔 Hardware ID: {result.get('hwid', 'N/A')}")
    else:
        print("❌ Nenhum modem detectado na detecção otimizada")
        
        # Tentar detecção robusta
        print("\n🔍 Executando detecção robusta completa...")
        robust_result = detector.detect_gsm_modem_robust()
        
        if robust_result['found']:
            print(f"✅ Modem encontrado na detecção robusta:")
            found = robust_result['found']
            print(f"   📍 Porta: {found['port']}")
            print(f"   📋 Descrição: {found['description']}")
            print(f"   📊 Status: {found['status']}")
        else:
            print("❌ Nenhum modem encontrado mesmo na detecção robusta")
        
        print("\n📋 Detalhes de todas as portas testadas:")
        for result in robust_result['results']:
            print(f"   {result['port']}: {result['status']} ({result['description']})")
            if result['error']:
                print(f"      Erro: {result['error']}")

if __name__ == "__main__":
    main()
