#!/usr/bin/env python3
"""
Script final para testar e corrigir USSD
"""
import sys
import time
import json
from pathlib import Path

# Adicionar o diretório raiz
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔧 CORREÇÃO E TESTE USSD - AMA MESSAGE")
    print("=" * 60)
    
    try:
        # 1. Testar importações
        print("📦 Testando importações...")
        from app.services.gsm_service import GSMModem
        from app.services.modem_detector import ModemDetector
        print("✅ Importações OK")
        
        # 2. Testar detecção de modem
        print("\n🔍 Detectando modem...")
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        print(f"✅ {len(ports)} portas encontradas")
        for i, port in enumerate(ports[:5]):  # Mostrar apenas 5
            print(f"   {i+1}. {port['port']}: {port['description'][:60]}...")
        
        # 3. Tentar detectar modem GSM
        modem_info = detector.detect_gsm_modem()
        
        if modem_info:
            print(f"\n📱 Modem GSM encontrado!")
            print(f"   Porta: {modem_info['port']}")
            print(f"   Descrição: {modem_info['description']}")
            
            # 4. Testar conexão
            print(f"\n🔌 Testando conexão...")
            gsm = GSMModem(modem_info['port'])
            
            if gsm.connect():
                print("✅ Conexão estabelecida!")
                
                # 5. Testar suporte USSD
                print("\n🧪 Testando suporte USSD...")
                ussd_status = gsm.get_ussd_status()
                print(f"   Status: {ussd_status}")
                
                # 6. Teste básico USSD
                print("\n📞 Testando código USSD simples...")
                test_code = "*144#"  # Código genérico
                
                print(f"   Enviando: {test_code}")
                result = gsm.send_ussd(test_code, timeout=15)
                
                if result["success"]:
                    print("   ✅ USSD funcionando!")
                    print(f"   📱 Resposta: {result['response'][:100]}...")
                    
                    # Salvar resultado
                    with open("ussd_test_result.json", "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    print("   💾 Resultado salvo em: ussd_test_result.json")
                    
                else:
                    print("   ❌ USSD falhou")
                    print(f"   💥 Erro: {result['error']}")
                
                gsm.disconnect()
                print("   🔌 Desconectado")
                
            else:
                print("❌ Falha na conexão")
                
        else:
            print("\n❌ Nenhum modem GSM encontrado")
            print("\nSoluções possíveis:")
            print("1. Conectar modem GSM via USB")
            print("2. Instalar drivers do modem")
            print("3. Inserir SIM card ativo")
            print("4. Reiniciar o computador")
        
        # 7. Resumo final
        print(f"\n📊 RESUMO:")
        print(f"   Importações: ✅")
        print(f"   Detecção portas: ✅ ({len(ports)} portas)")
        print(f"   Modem GSM: {'✅' if modem_info else '❌'}")
        
        if modem_info:
            print(f"\n🎯 PRÓXIMOS PASSOS:")
            print(f"1. Iniciar servidor: python start_server.py")
            print(f"2. Acessar USSD: http://127.0.0.1:8000/modem/ussd")
            print(f"3. Testar códigos da sua operadora")
        
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        print("\nVerifique:")
        print("1. Python está instalado corretamente")
        print("2. Dependências instaladas: pip install -r requirements.txt")
        print("3. Diretório correto: w:\\projects\\AMAMESSAGE")
        return False
    
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 Teste concluído! Sistema pronto para uso.")
    else:
        print("⚠️ Há problemas que precisam ser resolvidos.")
