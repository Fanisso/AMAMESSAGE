import serial.tools.list_ports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

print("=== DEBUG BÁSICO ===")

try:
    # Listar portas
    ports = list(serial.tools.list_ports.comports())
    print(f"Portas encontradas: {len(ports)}")
    
    for port in ports:
        print(f"  {port.device}: {port.description}")
        
        # Identificar modem
        desc = port.description.lower()
        if any(word in desc for word in ['modem', 'qualcomm', 'gsm']):
            print(f"    >>> POSSÍVEL MODEM!")
    
    # Testar detector
    print("\n=== TESTANDO DETECTOR ===")
    from app.services.modem_detector import ModemDetector
    detector = ModemDetector()
    
    result = detector.detect_gsm_modem()
    if result:
        print(f"Modem detectado: {result['port']}")
    else:
        print("Nenhum modem detectado")
        
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()

print("=== FIM DEBUG ===")
