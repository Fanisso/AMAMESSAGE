#!/usr/bin/env python3
"""
Teste de diagnóstico definitivo para todas as portas seriais.
Analisa cada porta e mostra a resposta exata dos comandos AT.
"""
import sys
import time
import serial
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def run_port_test(port_name: str, baudrate: int = 115200, timeout: int = 2) -> dict:
    """Testa uma única porta e retorna um dicionário com os resultados."""
    results = {
        'port': port_name,
        'status': '❌ Falhou',
        'response_at': '',
        'response_ati': '',
        'error': ''
    }
    try:
        with serial.Serial(port_name, baudrate, timeout=timeout) as ser:
            results['status'] = '🤔 Testando...'
            
            # Limpar buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.2)
            
            # Testar comando AT
            ser.write(b'AT\r\n')
            time.sleep(0.5)
            response_at = ser.read_all().decode('utf-8', errors='ignore').strip()
            results['response_at'] = repr(response_at)
            
            # Testar comando ATI
            ser.write(b'ATI\r\n')
            time.sleep(0.5)
            response_ati = ser.read_all().decode('utf-8', errors='ignore').strip()
            results['response_ati'] = repr(response_ati)
            
            if "OK" in response_at or len(response_ati) > 5:
                results['status'] = '✅ Funcional'
            else:
                results['status'] = '⚠️ Sem Resposta AT'

    except serial.SerialException as e:
        results['status'] = '❌ Ocupada ou Erro'
        results['error'] = str(e)
    except Exception as e:
        results['status'] = '💥 Erro Inesperado'
        results['error'] = str(e)
        
    return results

def test_all_ports_deep_dive():
    print("� DIAGNÓSTICO PROFUNDO DE PORTAS SERIAIS")
    print("=" * 50)
    
    try:
        from app.services.modem_detector import ModemDetector
        
        detector = ModemDetector()
        ports = detector.list_available_ports()
        
        if not ports:
            print("❌ Nenhuma porta serial encontrada. Conecte o modem.")
            return

        print(f"📋 Encontradas {len(ports)} portas. Testando todas...")
        
        all_results = []
        at_command_port = None

        for port_info in ports:
            port_name = port_info['port']
            print(f"\n--- Testando Porta: {port_name} ({port_info['description']}) ---")
            
            result = run_port_test(port_name)
            all_results.append(result)
            
            print(f"   Status: {result['status']}")
            print(f"   Resposta 'AT': {result['response_at']}")
            print(f"   Resposta 'ATI': {result['response_ati']}")
            if result['error']:
                print(f"   Erro: {result['error']}")

            if result['status'] == '✅ Funcional' and not at_command_port:
                at_command_port = result
        
        print("\n" + "="*20 + " RESULTADO FINAL " + "="*20)
        if at_command_port:
            print(f"🎉 SUCESSO! A porta de comandos AT é muito provavelmente: {at_command_port['port']}")
            print("   Esta porta respondeu corretamente aos comandos do modem.")
        else:
            print("❌ FALHA! Nenhuma porta respondeu corretamente aos comandos AT.")
            print("\n💡 Possíveis Causas:")
            print("   1. Drivers do Modem: Certifique-se de que os drivers corretos estão instalados.")
            print("   2. Porta Ocupada: Outro programa pode estar usando a porta. Reinicie o computador.")
            print("   3. Problema Físico: Tente uma porta USB diferente.")
            print("   4. Modo do Modem: O modem pode estar em um modo que não responde a comandos AT.")

    except Exception as e:
        print(f"💥 Erro Crítico no script de teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_ports_deep_dive()
    print("\n" + "=" * 50)
    print("Teste concluído.")
