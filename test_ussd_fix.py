#!/usr/bin/env python3
"""
Script para testar a funcionalidade USSD corrigida
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ussd_simple import USSDSimple
from app.services.ussd_service import USSDService
from app.core.config import settings

def test_ussd_simple():
    """Testar a implementação USSD simples"""
    print("=== TESTE USSD SIMPLES ===")
    
    ussd_simple = USSDSimple(
        port=getattr(settings, 'MODEM_PORT', 'COM3'),
        baudrate=getattr(settings, 'MODEM_BAUDRATE', 115200)
    )
    
    print(f"Testando USSD na porta: {ussd_simple.port}")
    
    # Testar códigos comuns
    test_codes = ['*155#', '*125#', '*144#']
    
    for code in test_codes:
        print(f"\n🔄 Testando código: {code}")
        result = ussd_simple.send_ussd(code)
        
        print(f"Sucesso: {result.get('success')}")
        print(f"Resposta: {result.get('response', 'N/A')}")
        if not result.get('success'):
            print(f"Erro: {result.get('error', 'N/A')}")
        print(f"Raw: {repr(result.get('raw_response', ''))}")
        print("-" * 50)

def test_ussd_service():
    """Testar o serviço USSD completo"""
    print("\n=== TESTE USSD SERVICE COMPLETO ===")
    
    service = USSDService()
    
    # Testar com o método híbrido (GSM + Simple fallback)
    test_codes = ['*155#']
    
    for code in test_codes:
        print(f"\n🔄 Testando código (método híbrido): {code}")
        result = service.send_ussd(code, timeout=10)
        
        print(f"Sucesso: {result.get('success')}")
        print(f"Resposta: {result.get('response', 'N/A')}")
        if not result.get('success'):
            print(f"Erro: {result.get('error', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        print("🚀 Iniciando testes USSD...")
        
        # Teste 1: Método simples direto
        test_ussd_simple()
        
        # Teste 2: Serviço completo
        test_ussd_service()
        
        print("\n✅ Testes concluídos!")
        
    except KeyboardInterrupt:
        print("\n❌ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro nos testes: {str(e)}")
        import traceback
        traceback.print_exc()
