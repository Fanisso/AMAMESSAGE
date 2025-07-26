#!/usr/bin/env python3
"""
Diagnóstico completo de detecção de modem
"""
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def diagnose_modem():
    print("🔧 DIAGNÓSTICO DE DETECÇÃO DE MODEM")
    print("=" * 50)
    
    try:
        # 1. Verificar importações
        print("1️⃣ Testando importações...")
        from app.services.modem_detector import ModemDetector
        from app.services.gsm_service import GSMModem
        from app.core.config import settings
        print("   ✅ Importações OK")
        
        # 2. Mostrar configurações
        print(f"\n2️⃣ Configurações atuais:")
        print(f"   GSM_PORT: {settings.GSM_PORT}")
        print(f"   GSM_BAUDRATE: {settings.GSM_BAUDRATE}")
        print(f"   GSM_TIMEOUT: {settings.GSM_TIMEOUT}")
        print(f"   GSM_AUTO_DETECT: {settings.GSM_AUTO_DETECT}")
        print(f"   GSM_PREFERRED_PORTS: {settings.GSM_PREFERRED_PORTS}")
        
        # 3. Listar portas seriais
        print(f"\n3️⃣ Portas seriais disponíveis:")
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        if not ports:
            print("   ❌ NENHUMA porta serial encontrada!")
            print("   💡 Possíveis causas:")
            print("      - Modem não está conectado")
            print("      - Drivers não instalados")
            print("      - Porta USB com problema")
            return False
        
        print(f"   📋 Encontradas {len(ports)} portas:")
        modem_candidates = []
        
        for i, port in enumerate(ports, 1):
            desc = port['description']
            print(f"   {i}. {port['port']}: {desc}")
            
            # Identificar possíveis modems
            desc_lower = desc.lower()
            modem_keywords = ['modem', 'gsm', 'qualcomm', 'huawei', 'zte', 'sierra', 'cellular', 'mobile']
            
            if any(keyword in desc_lower for keyword in modem_keywords):
                modem_candidates.append(port)
                print(f"      >>> 📱 POSSÍVEL MODEM GSM!")
        
        # 4. Testar detecção automática
        print(f"\n4️⃣ Testando detecção automática...")
        try:
            modem_info = detector.detect_gsm_modem()
            if modem_info:
                print(f"   ✅ Modem detectado automaticamente!")
                print(f"      Porta: {modem_info['port']}")
                print(f"      Descrição: {modem_info['description']}")
            else:
                print(f"   ❌ Detecção automática falhou")
        except Exception as e:
            print(f"   💥 Erro na detecção: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Testar manualmente cada candidato
        print(f"\n5️⃣ Testando candidatos manualmente...")
        if modem_candidates:
            for candidate in modem_candidates:
                port = candidate['port']
                print(f"   🧪 Testando {port}...")
                
                try:
                    # Teste básico de comunicação
                    gsm = GSMModem(port)
                    if gsm.connect():
                        print(f"      ✅ Conectado com sucesso!")
                        
                        # Testar comando AT
                        try:
                            response = gsm._send_command("AT")
                            if response:
                                print(f"      📞 Responde a comandos AT: OK")
                                
                                # Tentar obter informações
                                try:
                                    info = gsm._get_command_response("AT+CGMI")
                                    print(f"      📱 Fabricante: {info}")
                                except:
                                    print(f"      ⚠️ Não conseguiu obter fabricante")
                            else:
                                print(f"      ❌ Não responde a comandos AT")
                        except Exception as e:
                            print(f"      💥 Erro AT: {e}")
                        
                        gsm.disconnect()
                    else:
                        print(f"      ❌ Falha na conexão")
                        
                except Exception as e:
                    print(f"      💥 Erro: {e}")
                
                time.sleep(1)  # Aguardar entre testes
        else:
            print("   ⚠️ Nenhum candidato a modem identificado")
        
        # 6. Recomendações
        print(f"\n6️⃣ RECOMENDAÇÕES:")
        if modem_candidates:
            print("   📱 Modems candidatos encontrados:")
            for candidate in modem_candidates:
                print(f"      - {candidate['port']}: {candidate['description']}")
            
            print(f"\n   🔧 Para forçar uma porta específica:")
            print(f"      1. Editar arquivo .env")
            print(f"      2. Mudar GSM_PORT=AUTO para GSM_PORT={modem_candidates[0]['port']}")
            print(f"      3. Reiniciar o sistema")
        else:
            print("   ❌ Nenhum modem detectado")
            print("   💡 Soluções:")
            print("      1. Verificar conexão USB do modem")
            print("      2. Instalar drivers do fabricante")
            print("      3. Tentar portas USB diferentes")
            print("      4. Verificar se modem funciona em outros programas")
        
        return len(modem_candidates) > 0
        
    except Exception as e:
        print(f"💥 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 AMA MESSAGE - Diagnóstico de Modem")
    success = diagnose_modem()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Diagnóstico concluído - Modem(s) encontrado(s)!")
    else:
        print("❌ Nenhum modem encontrado - Verifique as recomendações acima")
    
    print("\nPara mais ajuda, acesse: http://127.0.0.1:8000/admin/modem")
