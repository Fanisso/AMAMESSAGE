#!/usr/bin/env python3
"""
Script para testar a detecção automática de modems GSM
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.modem_detector import ModemDetector
from app.services.gsm_service import GSMModem
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🔍 TESTE DE DETECÇÃO AUTOMÁTICA DE MODEMS GSM")
    print("=" * 60)
    
    # 1. Listar todas as portas disponíveis
    print("\n📋 1. LISTANDO TODAS AS PORTAS SERIAIS DISPONÍVEIS:")
    print("-" * 50)
    ports = ModemDetector.list_available_ports()
    
    if not ports:
        print("   ❌ Nenhuma porta serial encontrada")
    else:
        for port, description in ports:
            print(f"   📌 {port}: {description}")
    
    # 2. Detectar modems GSM automaticamente
    print("\n🎯 2. DETECÇÃO AUTOMÁTICA DE MODEMS GSM:")
    print("-" * 50)
    detected_port = ModemDetector.detect_gsm_modem()
    
    if detected_port:
        print(f"   ✅ Modem GSM detectado na porta: {detected_port}")
        
        # 3. Obter informações detalhadas do modem
        print(f"\n📱 3. INFORMAÇÕES DO MODEM NA PORTA {detected_port}:")
        print("-" * 50)
        modem_info = ModemDetector.get_modem_info(detected_port)
        
        if modem_info:
            for key, value in modem_info.items():
                print(f"   📊 {key.capitalize()}: {value}")
        else:
            print("   ⚠️ Não foi possível obter informações detalhadas do modem")
        
        # 4. Testar inicialização do GSMModem
        print(f"\n🔧 4. TESTANDO INICIALIZAÇÃO DA CLASSE GSMModem:")
        print("-" * 50)
        try:
            gsm_modem = GSMModem()
            print(f"   📍 Porta configurada automaticamente: {gsm_modem.port}")
            
            if gsm_modem.connect():
                print("   ✅ Conexão com modem estabelecida com sucesso!")
                
                if gsm_modem.is_connected:
                    print("   📡 Modem conectado e operacional")
                else:
                    print("   ⚠️ Modem conectado mas não está totalmente operacional")
                    
                gsm_modem.disconnect()
                print("   🔌 Modem desconectado com segurança")
            else:
                print("   ❌ Falha ao conectar com o modem")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar GSMModem: {e}")
            
    else:
        print("   ❌ Nenhum modem GSM detectado automaticamente")
        print("\n💡 DICAS PARA RESOLUÇÃO:")
        print("   • Certifique-se de que o modem GSM está conectado")
        print("   • Verifique se os drivers do modem estão instalados")  
        print("   • Tente diferentes portas USB")
        print("   • Verifique se outro software não está usando o modem")
        print("   • Alguns modems precisam de alguns segundos para inicializar")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO!")
    print("=" * 60)

def test_specific_port(port: str):
    """Testar uma porta específica"""
    print(f"🔧 TESTANDO PORTA ESPECÍFICA: {port}")
    print("=" * 50)
    
    if ModemDetector._test_modem_communication(port):
        print(f"✅ Modem GSM detectado na porta {port}")
        
        info = ModemDetector.get_modem_info(port)
        if info:
            print("📱 Informações do modem:")
            for key, value in info.items():
                print(f"   {key}: {value}")
    else:
        print(f"❌ Nenhum modem GSM encontrado na porta {port}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Testar porta específica
        port = sys.argv[1].upper()
        test_specific_port(port)
    else:
        # Executar teste completo
        main()
    
    print(f"\n💡 Para testar uma porta específica, use: python {sys.argv[0]} COM3")
