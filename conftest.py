# Test environment configuration
import os
import sys
import pytest
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "shared"))

# Test database configuration
TEST_DATABASE_URL = "sqlite:///test_amamessage.db"

# Fixtures globais para todos os testes
@pytest.fixture(scope="session")
def project_root():
    """Retorna o caminho raiz do projeto."""
    return Path(__file__).parent

@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Retorna o diretório de dados de teste."""
    return project_root / "tests" / "shared" / "data"

@pytest.fixture(scope="function")
def clean_database():
    """Limpa a base de dados de teste antes de cada teste."""
    # Remove test database if exists
    test_db_path = Path("test_amamessage.db")
    if test_db_path.exists():
        test_db_path.unlink()
    
    yield
    
    # Cleanup after test
    if test_db_path.exists():
        test_db_path.unlink()

@pytest.fixture(scope="session")
def test_config():
    """Configuração de teste global."""
    return {
        "DEBUG": True,
        "TESTING": True,
        "DATABASE_URL": TEST_DATABASE_URL,
        "SECRET_KEY": "test-secret-key",
        "LOG_LEVEL": "DEBUG",
    }

# Configuração para diferentes linhas de deploy
def pytest_configure(config):
    """Configuração inicial do pytest."""
    # Create test directories if they don't exist
    test_dirs = [
        "tests/logs",
        "tests/tmp",
        "reports",
    ]
    
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def pytest_addoption(parser):
    """Adiciona opções personalizadas ao pytest."""
    parser.addoption(
        "--cloud-env",
        action="store",
        default="test",
        help="Cloud environment: test or prod"
    )
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="Mobile platform: android or ios"
    )
    parser.addoption(
        "--modem-test",
        action="store_true",
        default=False,
        help="Run modem hardware tests"
    )
    parser.addoption(
        "--driver-test",
        action="store_true",
        default=False,
        help="Run driver tests"
    )

@pytest.fixture
def cloud_env(request):
    """Retorna o ambiente de nuvem configurado."""
    return request.config.getoption("--cloud-env")

@pytest.fixture
def mobile_platform(request):
    """Retorna a plataforma mobile configurada."""
    return request.config.getoption("--platform")

@pytest.fixture
def modem_test_enabled(request):
    """Indica se os testes de modem estão habilitados."""
    return request.config.getoption("--modem-test")

@pytest.fixture
def driver_test_enabled(request):
    """Indica se os testes de driver estão habilitados."""
    return request.config.getoption("--driver-test")

# Fixtures para mock de SMS/USSD
@pytest.fixture
def mock_sms_response():
    """Mock de resposta SMS."""
    return {
        "id": "test-sms-id",
        "from": "+1234567890",
        "to": "+0987654321",
        "body": "Test SMS message",
        "status": "delivered",
        "timestamp": "2025-01-01T10:00:00Z"
    }

@pytest.fixture
def mock_ussd_response():
    """Mock de resposta USSD."""
    return {
        "session_id": "test-ussd-session",
        "code": "*100#",
        "response": "Your balance is $10.50",
        "status": "completed",
        "timestamp": "2025-01-01T10:00:00Z"
    }

# Skip markers para testes que requerem recursos específicos
def pytest_runtest_setup(item):
    """Setup executado antes de cada teste."""
    # Skip testes que requerem hardware se não estiver disponível
    if "hardware" in item.keywords and not item.config.getoption("--modem-test"):
        pytest.skip("Hardware tests disabled. Use --modem-test to enable.")
    
    # Skip testes de driver se não estiver habilitado
    if "drivers" in item.keywords and not item.config.getoption("--driver-test"):
        pytest.skip("Driver tests disabled. Use --driver-test to enable.")

# Configuração de logging para testes
import logging

@pytest.fixture(scope="session", autouse=True)
def configure_test_logging():
    """Configura logging para testes."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler('tests/logs/test.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduz verbosidade de algumas bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
