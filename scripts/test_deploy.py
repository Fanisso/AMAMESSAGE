#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Teste de Deploy Local
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocalTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def test_installation(self):
        """Testar instalação local"""
        logger.info("Testando instalação local...")
        
        # Verificar ambiente virtual
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            logger.error("Ambiente virtual não encontrado. Execute install.bat/.sh primeiro.")
            return False
            
        # Verificar .env
        env_path = self.project_root / ".env"
        if not env_path.exists():
            logger.error("Arquivo .env não encontrado.")
            return False
            
        # Verificar base de dados
        db_path = self.project_root / "amamessage.db"
        if not db_path.exists():
            logger.warning("Base de dados não encontrada. Será criada automaticamente.")
            
        logger.info("Instalação verificada com sucesso!")
        return True
        
    def test_dependencies(self):
        """Testar dependências"""
        logger.info("Testando dependências...")
        
        try:
            # Importar módulos principais
            sys.path.insert(0, str(self.project_root))
            
            import fastapi
            import sqlalchemy
            import uvicorn
            import serial
            import requests
            
            logger.info("Dependências principais encontradas!")
            return True
            
        except ImportError as e:
            logger.error(f"Dependência em falta: {e}")
            return False
            
    def test_database(self):
        """Testar conexão com base de dados"""
        logger.info("Testando base de dados...")
        
        try:
            from app.db.database import engine, get_db
            from sqlalchemy import text
            
            # Testar conexão
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Conexão com base de dados OK!")
                return True
                
        except Exception as e:
            logger.error(f"Erro na base de dados: {e}")
            return False
            
    def test_api_endpoints(self):
        """Testar endpoints da API"""
        logger.info("Testando endpoints da API...")
        
        try:
            # Importar router principal
            from main import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Testar endpoint de saúde
            response = client.get("/")
            if response.status_code == 200:
                logger.info("Endpoint principal OK!")
            else:
                logger.warning(f"Endpoint principal retornou: {response.status_code}")
                
            # Testar API SMS
            response = client.get("/api/sms/")
            logger.info(f"API SMS status: {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao testar API: {e}")
            return False
            
    def test_services(self):
        """Testar serviços"""
        logger.info("Testando serviços...")
        
        try:
            from app.services.sms_service import SMSService
            from app.services.forwarding_service import ForwardingRuleService
            
            # Testar SMSService
            sms_service = SMSService()
            logger.info("SMSService criado com sucesso!")
            
            # Testar ForwardingRuleService
            forwarding_service = ForwardingRuleService()
            logger.info("ForwardingRuleService criado com sucesso!")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao testar serviços: {e}")
            return False
            
    def test_modem_detection(self):
        """Testar detecção de modem (opcional)"""
        logger.info("Testando detecção de modem...")
        
        try:
            import serial.tools.list_ports
            
            ports = serial.tools.list_ports.comports()
            logger.info(f"Portas encontradas: {len(ports)}")
            
            for port in ports:
                logger.info(f"- {port.device}: {port.description}")
                
            if not ports:
                logger.warning("Nenhuma porta serial encontrada. Modem pode não estar conectado.")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na detecção de modem: {e}")
            return False
            
    def generate_report(self, results):
        """Gerar relatório de testes"""
        logger.info("Gerando relatório...")
        
        report = []
        report.append("=" * 50)
        report.append("  RELATÓRIO DE TESTE DE DEPLOY LOCAL")
        report.append("=" * 50)
        report.append("")
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r)
        
        report.append(f"Testes executados: {total_tests}")
        report.append(f"Testes aprovados: {passed_tests}")
        report.append(f"Taxa de sucesso: {passed_tests/total_tests*100:.1f}%")
        report.append("")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report.append(f"{status} {test_name}")
            
        report.append("")
        
        if passed_tests == total_tests:
            report.append("🎉 TODOS OS TESTES PASSARAM!")
            report.append("Sistema pronto para deploy em produção.")
        else:
            report.append("⚠️  ALGUNS TESTES FALHARAM!")
            report.append("Corrija os problemas antes do deploy em produção.")
            
        report.append("")
        report.append("Próximos passos:")
        report.append("1. Para desenvolvimento: python iniciar_dev.py")
        report.append("2. Para produção: python scripts/deploy.py")
        report.append("3. Para Docker: python scripts/deploy_docker.py")
        
        report_text = "\n".join(report)
        print(report_text)
        
        # Salvar relatório
        report_file = self.project_root / "test_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
            
        logger.info(f"Relatório salvo em: {report_file}")
        
    def run_tests(self):
        """Executar todos os testes"""
        logger.info("Iniciando testes de deploy local...")
        
        results = {}
        
        results["Instalação"] = self.test_installation()
        results["Dependências"] = self.test_dependencies()
        results["Base de Dados"] = self.test_database()
        results["API Endpoints"] = self.test_api_endpoints()
        results["Serviços"] = self.test_services()
        results["Detecção Modem"] = self.test_modem_detection()
        
        self.generate_report(results)
        
        # Retornar status geral
        return all(results.values())

if __name__ == "__main__":
    tester = LocalTester()
    success = tester.run_tests()
    
    sys.exit(0 if success else 1)
