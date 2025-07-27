# Teste de configuração inicial
import pytest
import os
import sys
from pathlib import Path

def test_project_structure():
    """Verifica se a estrutura do projeto está correta."""
    project_root = Path(__file__).parent.parent.parent
    
    required_dirs = [
        "backend",
        "clients", 
        "shared",
        "tests/local",
        "tests/web_client",
        "tests/mobile",
        "tests/windows_modem",
        "tests/shared"
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Diretório obrigatório não encontrado: {dir_path}"

def test_configuration_files():
    """Verifica se os arquivos de configuração estão presentes."""
    project_root = Path(__file__).parent.parent.parent
    
    config_files = [
        "pytest.ini",
        "conftest.py",
        ".env.test",
        "requirements-test.txt"
    ]
    
    for config_file in config_files:
        full_path = project_root / config_file
        assert full_path.exists(), f"Arquivo de configuração não encontrado: {config_file}"

def test_python_path():
    """Verifica se os caminhos Python estão configurados."""
    project_root = Path(__file__).parent.parent.parent
    
    required_paths = [
        str(project_root / "backend"),
        str(project_root / "shared")
    ]
    
    for path in required_paths:
        assert path in sys.path or Path(path).exists(), f"Caminho Python não configurado: {path}"

def test_environment_variables():
    """Verifica se as variáveis de ambiente de teste estão configuradas."""
    required_env_vars = [
        "TESTING",
        "DEBUG", 
        "DATABASE_URL"
    ]
    
    # Load .env.test if available
    env_test_path = Path(__file__).parent.parent.parent / ".env.test"
    if env_test_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_test_path)
    
    for var in required_env_vars:
        value = os.getenv(var)
        assert value is not None, f"Variável de ambiente não configurada: {var}"

def test_test_directories():
    """Verifica se todas as pastas de teste existem."""
    project_root = Path(__file__).parent.parent.parent / "tests"
    
    test_dirs = [
        "shared",
        "local/unit",
        "local/integration", 
        "local/e2e",
        "web_client/ui",
        "web_client/api",
        "mobile/android",
        "mobile/ios",
        "windows_modem/hardware",
        "windows_modem/drivers",
        "cloud_test/performance",
        "cloud_test/stress",
        "cloud_production/smoke",
        "cloud_production/security"
    ]
    
    for test_dir in test_dirs:
        full_path = project_root / test_dir
        assert full_path.exists(), f"Diretório de teste não encontrado: {test_dir}"

def test_conftest_files():
    """Verifica se os arquivos conftest.py específicos existem."""
    project_root = Path(__file__).parent.parent.parent / "tests"
    
    conftest_locations = [
        "local/conftest.py",
        "web_client/conftest.py", 
        "mobile/conftest.py",
        "windows_modem/conftest.py"
    ]
    
    for location in conftest_locations:
        full_path = project_root / location
        assert full_path.exists(), f"Arquivo conftest.py não encontrado: {location}"

@pytest.mark.slow
def test_database_connection():
    """Testa conexão com base de dados de teste."""
    try:
        # Import here to avoid issues if backend is not available
        from sqlalchemy import create_engine
        
        test_db_url = os.getenv("DATABASE_URL", "sqlite:///test_amamessage.db")
        engine = create_engine(test_db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
            
    except ImportError:
        pytest.skip("SQLAlchemy não disponível - pulando teste de BD")

def test_logging_setup():
    """Verifica se o sistema de logging está configurado."""
    import logging
    
    # Check if logging is configured
    logger = logging.getLogger("amamessage.test")
    logger.info("Teste de logging")
    
    # Verify log directory exists
    log_dir = Path(__file__).parent.parent.parent / "tests" / "logs"
    assert log_dir.exists(), "Diretório de logs não encontrado"

def test_mock_fixtures_available():
    """Verifica se as fixtures de mock estão disponíveis."""
    # Test if we can import mock fixtures
    try:
        from unittest.mock import Mock, patch
        assert Mock is not None
        assert patch is not None
    except ImportError:
        pytest.fail("Bibliotecas de mock não disponíveis")

def test_requirements_installed():
    """Verifica se as dependências de teste estão instaladas."""
    required_packages = [
        "pytest",
        "selenium", 
        "requests",
        "sqlalchemy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        pytest.fail(f"Pacotes não instalados: {', '.join(missing_packages)}")

if __name__ == "__main__":
    # Run setup tests directly
    print("🔧 Executando testes de configuração...")
    
    test_functions = [
        test_project_structure,
        test_configuration_files,
        test_python_path,
        test_environment_variables,
        test_test_directories,
        test_conftest_files,
        test_logging_setup,
        test_mock_fixtures_available,
        test_requirements_installed
    ]
    
    failed_tests = []
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
        except Exception as e:
            print(f"❌ {test_func.__name__}: {str(e)}")
            failed_tests.append(test_func.__name__)
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} testes falharam:")
        for test in failed_tests:
            print(f"  - {test}")
        print("\n💡 Execute: python run_tests.py setup")
    else:
        print("\n✅ Todos os testes de configuração passaram!")
        print("🚀 Sistema pronto para testes!")
