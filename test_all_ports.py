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


def test_modem_detector_robust():
    print("================== TESTE ROBUSTO AUTOMÁTICO ==================")
    from app.services.modem_detector import ModemDetector
    detector = ModemDetector()
    result = detector.detect_gsm_modem_robust()
    found = result['found']
    all_results = result['results']
    for r in all_results:
        print(f"Porta: {r['port']} | Status: {r['status']} | AT: {r['response_at']} | ATI: {r['response_ati']} | Erro: {r['error']}")
    if found:
        print(f"\n🎯 Porta AT encontrada automaticamente: {found['port']} ({found['description']})")
    else:
        print("\n❌ Nenhuma porta AT funcional encontrada pelo método robusto.")

if __name__ == "__main__":
    test_modem_detector_robust()
    print("\n" + "=" * 50)
    print("Teste concluído.")
