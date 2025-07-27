#!/usr/bin/env python3
"""
AMAMESSAGE Test Runner
Execute testes por linha de deploy específica

Uso:
    python run_tests.py --help
    python run_tests.py local
    python run_tests.py web_client --browser chrome
    python run_tests.py mobile --platform android
    python run_tests.py windows_modem --hardware
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Executa comando e retorna resultado."""
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0

def run_local_tests(args):
    """Executa testes locais de desenvolvimento."""
    cmd = ["pytest", "tests/local/", "-v"]
    
    if args.unit:
        cmd.append("-m unit")
    elif args.integration:
        cmd.append("-m integration")
    elif args.e2e:
        cmd.append("-m e2e")
    
    if args.coverage:
        cmd.extend(["--cov=backend", "--cov-report=html:reports/local_coverage"])
    
    return run_command(cmd)

def run_web_client_tests(args):
    """Executa testes do cliente web."""
    cmd = ["pytest", "tests/web_client/", "-v"]
    
    if args.ui:
        cmd.append("tests/web_client/ui/")
    elif args.api:
        cmd.append("tests/web_client/api/")
    
    if args.browser:
        cmd.extend(["--browser", args.browser])
    
    if args.headless:
        cmd.append("--headless")
    
    return run_command(cmd)

def run_cloud_tests(args):
    """Executa testes de nuvem."""
    if args.environment == "test":
        cmd = ["pytest", "tests/cloud_test/", "-v", "--cloud-env=test"]
    else:
        cmd = ["pytest", "tests/cloud_production/", "-v", "--cloud-env=prod"]
    
    if args.performance:
        cmd.append("-m performance")
    elif args.stress:
        cmd.append("-m stress")
    elif args.smoke:
        cmd.append("-m smoke")
    elif args.security:
        cmd.append("-m security")
    
    return run_command(cmd)

def run_mobile_tests(args):
    """Executa testes mobile."""
    cmd = ["pytest", "tests/mobile/", "-v", f"--platform={args.platform}"]
    
    if args.platform == "android":
        cmd.append("tests/mobile/android/")
    elif args.platform == "ios":
        cmd.append("tests/mobile/ios/")
    
    if args.device:
        cmd.extend(["--device", args.device])
    
    return run_command(cmd)

def run_windows_modem_tests(args):
    """Executa testes Windows com modem."""
    cmd = ["pytest", "tests/windows_modem/", "-v"]
    
    if args.hardware:
        cmd.append("--modem-test")
    
    if args.drivers:
        cmd.append("--driver-test")
    
    if args.stress:
        cmd.append("-m stress")
    
    # Adiciona warning para testes de hardware
    if args.hardware:
        print("⚠️  ATENÇÃO: Testes de hardware podem enviar SMS reais e gerar custos!")
        response = input("Tem certeza que deseja continuar? (s/N): ")
        if response.lower() != 's':
            print("Testes cancelados pelo usuário.")
            return False
    
    return run_command(cmd)

def run_shared_tests(args):
    """Executa testes compartilhados."""
    cmd = ["pytest", "tests/shared/", "-v"]
    return run_command(cmd)

def run_all_tests(args):
    """Executa todos os testes (cuidado!)."""
    print("🚨 Executando TODOS os testes - isso pode demorar muito!")
    response = input("Confirma? (s/N): ")
    if response.lower() != 's':
        print("Cancelado pelo usuário.")
        return False
    
    test_lines = [
        ("local", run_local_tests),
        ("web_client", run_web_client_tests),
        ("mobile", run_mobile_tests),
        ("shared", run_shared_tests)
    ]
    
    results = {}
    for line_name, test_func in test_lines:
        print(f"\n{'='*50}")
        print(f"Executando testes: {line_name}")
        print(f"{'='*50}")
        
        # Create mock args for each test type
        mock_args = type('Args', (), {})()
        results[line_name] = test_func(mock_args)
    
    # Summary
    print(f"\n{'='*50}")
    print("RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    for line_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{line_name}: {status}")
    
    return all(results.values())

def setup_test_environment():
    """Configura ambiente de testes."""
    print("Configurando ambiente de testes...")
    
    # Create necessary directories
    dirs = [
        "tests/logs",
        "tests/tmp", 
        "reports",
        "reports/coverage"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Copy test environment file
    env_test = Path(".env.test")
    if env_test.exists() and not Path(".env").exists():
        import shutil
        shutil.copy(env_test, ".env")
        print("Arquivo .env.test copiado para .env")
    
    print("✅ Ambiente configurado!")

def main():
    parser = argparse.ArgumentParser(
        description="AMAMESSAGE Test Runner - Execute testes por linha de deploy",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Linha de deploy para testar")
    
    # Local tests
    local_parser = subparsers.add_parser("local", help="Testes locais de desenvolvimento")
    local_parser.add_argument("--unit", action="store_true", help="Apenas testes unitários")
    local_parser.add_argument("--integration", action="store_true", help="Apenas testes de integração")
    local_parser.add_argument("--e2e", action="store_true", help="Apenas testes end-to-end")
    local_parser.add_argument("--coverage", action="store_true", help="Gerar relatório de cobertura")
    
    # Web client tests
    web_parser = subparsers.add_parser("web_client", help="Testes do cliente web")
    web_parser.add_argument("--ui", action="store_true", help="Apenas testes de UI")
    web_parser.add_argument("--api", action="store_true", help="Apenas testes de API")
    web_parser.add_argument("--browser", choices=["chrome", "firefox", "edge"], default="chrome", help="Browser para testes")
    web_parser.add_argument("--headless", action="store_true", help="Executar browser em modo headless")
    
    # Cloud tests
    cloud_parser = subparsers.add_parser("cloud", help="Testes de nuvem")
    cloud_parser.add_argument("environment", choices=["test", "production"], help="Ambiente de nuvem")
    cloud_parser.add_argument("--performance", action="store_true", help="Testes de performance")
    cloud_parser.add_argument("--stress", action="store_true", help="Testes de stress")
    cloud_parser.add_argument("--smoke", action="store_true", help="Testes smoke")
    cloud_parser.add_argument("--security", action="store_true", help="Testes de segurança")
    
    # Mobile tests
    mobile_parser = subparsers.add_parser("mobile", help="Testes mobile")
    mobile_parser.add_argument("--platform", choices=["android", "ios"], default="android", help="Plataforma mobile")
    mobile_parser.add_argument("--device", help="Nome do dispositivo específico")
    
    # Windows modem tests
    windows_parser = subparsers.add_parser("windows_modem", help="Testes Windows com modem")
    windows_parser.add_argument("--hardware", action="store_true", help="Executar testes de hardware (CUIDADO: pode gerar custos!)")
    windows_parser.add_argument("--drivers", action="store_true", help="Executar testes de drivers")
    windows_parser.add_argument("--stress", action="store_true", help="Testes de stress de hardware")
    
    # Shared tests
    subparsers.add_parser("shared", help="Testes compartilhados")
    
    # All tests
    subparsers.add_parser("all", help="Executar todos os testes (CUIDADO!)")
    
    # Setup command
    subparsers.add_parser("setup", help="Configurar ambiente de testes")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup environment if needed
    if args.command == "setup":
        setup_test_environment()
        return
    
    # Verify test environment
    if not Path("tests").exists():
        print("❌ Estrutura de testes não encontrada!")
        print("Execute: python run_tests.py setup")
        return
    
    # Route to appropriate test runner
    success = False
    
    if args.command == "local":
        success = run_local_tests(args)
    elif args.command == "web_client":
        success = run_web_client_tests(args)
    elif args.command == "cloud":
        success = run_cloud_tests(args)
    elif args.command == "mobile":
        success = run_mobile_tests(args)
    elif args.command == "windows_modem":
        success = run_windows_modem_tests(args)
    elif args.command == "shared":
        success = run_shared_tests(args)
    elif args.command == "all":
        success = run_all_tests(args)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
