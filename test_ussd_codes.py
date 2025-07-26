#!/usr/bin/env python3
"""
Script para testar códigos USSD especificamente
"""
import sys
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.services.gsm_service import GSMModem
from app.services.modem_detector import ModemDetector

def test_ussd_codes():
    """Testar códigos USSD com diferentes operadores"""
    print("🧪 TESTE DE CÓDIGOS USSD")
    print("=" * 50)
    
    # Detectar modem
    print("🔍 Detectando modem GSM...")
    detector = ModemDetector()
    modem_info = detector.detect_gsm_modem()
    
    if not modem_info:
        print("❌ Nenhum modem GSM encontrado!")
        print("   Certifique-se de que:")
        print("   - O modem está conectado via USB")
        print("   - Os drivers estão instalados")
        print("   - O SIM card está inserido")
        return False
    
    print(f"✅ Modem encontrado: {modem_info['port']}")
    print(f"   Descrição: {modem_info['description']}")
    
    # Conectar ao modem
    print("\n🔌 Conectando ao modem...")
    gsm = GSMModem(modem_info['port'])
    
    if not gsm.connect():
        print("❌ Falha ao conectar com o modem!")
        return False
    
    print("✅ Conectado com sucesso!")
    
    # Códigos USSD para testar (Moçambique)
    ussd_codes = [
        {"code": "*124#", "name": "Vodacom - Saldo", "operator": "Vodacom"},
        {"code": "*444#", "name": "Tmcel - Menu Principal", "operator": "Tmcel"},
        {"code": "*222#", "name": "Movitel - Menu Principal", "operator": "Movitel"},
        {"code": "*150#", "name": "Código genérico - Saldo", "operator": "Genérico"},
        {"code": "*144#", "name": "Código genérico - Menu", "operator": "Genérico"},
    ]
    
    print(f"\n📞 Testando {len(ussd_codes)} códigos USSD...")
    print("-" * 50)
    
    successful_tests = 0
    
    for i, ussd_info in enumerate(ussd_codes, 1):
        code = ussd_info["code"]
        name = ussd_info["name"]
        operator = ussd_info["operator"]
        
        print(f"\n{i}. Testando {name} ({code})")
        print(f"   Operador: {operator}")
        
        try:
            # Enviar código USSD
            result = gsm.send_ussd(code, timeout=20)
            
            if result["success"]:
                print(f"   ✅ Sucesso!")
                print(f"   📱 Resposta: {result['response'][:100]}...")
                if len(result['response']) > 100:
                    print(f"      (resposta truncada - {len(result['response'])} caracteres total)")
                successful_tests += 1
                
                # Salvar resposta completa em arquivo
                with open(f"ussd_response_{i}_{operator.lower()}.txt", "w", encoding="utf-8") as f:
                    f.write(f"Código USSD: {code}\n")
                    f.write(f"Operador: {operator}\n")
                    f.write(f"Nome: {name}\n")
                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Resposta completa:\n{result['response']}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Resposta raw:\n{result.get('raw_response', 'N/A')}\n")
                
                print(f"   💾 Resposta salva em: ussd_response_{i}_{operator.lower()}.txt")
                
            else:
                print(f"   ❌ Falhou: {result['error']}")
                if result.get('response'):
                    print(f"   📝 Resposta parcial: {result['response']}")
            
            # Aguardar um pouco entre testes
            if i < len(ussd_codes):
                print("   ⏳ Aguardando 3 segundos...")
                time.sleep(3)
                
        except Exception as e:
            print(f"   💥 Erro inesperado: {str(e)}")
        
        print("   " + "-" * 40)
    
    # Desconectar
    gsm.disconnect()
    
    # Resultado final
    print(f"\n📊 RESULTADO DOS TESTES:")
    print(f"   ✅ Sucessos: {successful_tests}")
    print(f"   ❌ Falhas: {len(ussd_codes) - successful_tests}")
    print(f"   📈 Taxa de sucesso: {(successful_tests/len(ussd_codes)*100):.1f}%")
    
    if successful_tests > 0:
        print(f"\n🎉 Códigos USSD estão funcionando!")
        print(f"   {successful_tests} de {len(ussd_codes)} testes foram bem-sucedidos")
    else:
        print(f"\n😞 Nenhum código USSD funcionou")
        print("   Possíveis causas:")
        print("   - SIM card não está ativo")
        print("   - Sem sinal da operadora")
        print("   - Modem não suporta USSD")
        print("   - Códigos não válidos para a operadora")
    
    return successful_tests > 0

def test_modem_ussd_support():
    """Testar se o modem suporta USSD"""
    print("\n🔧 TESTE DE SUPORTE USSD")
    print("=" * 30)
    
    # Detectar modem
    detector = ModemDetector()
    modem_info = detector.detect_gsm_modem()
    
    if not modem_info:
        print("❌ Nenhum modem encontrado!")
        return False
    
    # Conectar
    gsm = GSMModem(modem_info['port'])
    if not gsm.connect():
        print("❌ Falha ao conectar!")
        return False
    
    # Testar comandos USSD
    print("🧪 Testando comandos AT para USSD...")
    
    # Verificar suporte USSD
    support_result = gsm.get_ussd_status()
    print(f"   USSD Support: {support_result}")
    
    # Testar comando básico
    test_command = 'AT+CUSD=?'
    try:
        response = gsm._get_command_response(test_command)
        print(f"   Resposta para {test_command}: {response}")
    except Exception as e:
        print(f"   Erro ao testar {test_command}: {e}")
    
    gsm.disconnect()
    return True

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO DE USSD - AMA MESSAGE")
    print("=" * 60)
    
    # Teste de suporte
    test_modem_ussd_support()
    
    # Teste de códigos
    test_result = test_ussd_codes()
    
    print("\n" + "=" * 60)
    if test_result:
        print("🎉 Testes concluídos com sucesso!")
    else:
        print("⚠️  Alguns testes falharam - verifique a configuração")
    
    print("\nPara usar USSD na interface web:")
    print("🌐 http://127.0.0.1:8000/modem/ussd")
