# Configuração de testes para desenvolvimento local
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture(scope="session")
def local_test_config():
    """Configuração específica para testes locais."""
    return {
        "ENV": "local",
        "HOST": "127.0.0.1",
        "PORT": 8000,
        "DATABASE_URL": "sqlite:///local_test.db",
        "MODEM_PORT": "COM3",  # Porta comum para desenvolvimento
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG"
    }

@pytest.fixture(scope="function")
def temp_database():
    """Cria uma base de dados temporária para cada teste."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    yield f"sqlite:///{db_path}"
    
    # Cleanup
    if Path(db_path).exists():
        Path(db_path).unlink()

@pytest.fixture(scope="function")
def mock_modem():
    """Mock do modem para testes locais."""
    class MockModem:
        def __init__(self):
            self.connected = True
            self.port = "COM3"
            self.baudrate = 115200
        
        def send_sms(self, number, message):
            return {"status": "sent", "id": "test-sms-123"}
        
        def send_ussd(self, code):
            return {"response": "Mock USSD response", "session_id": "test-123"}
        
        def check_connection(self):
            return self.connected
    
    return MockModem()

@pytest.fixture(scope="function") 
def local_test_client():
    """Cliente de teste para API local."""
    # Import here to avoid circular imports
    from fastapi.testclient import TestClient
    
    # Mock da aplicação para testes
    class MockApp:
        def __init__(self):
            pass
    
    return TestClient(MockApp())

@pytest.fixture(autouse=True)
def setup_local_test_env():
    """Setup automático para ambiente de teste local."""
    # Set environment variables for local testing
    os.environ["TESTING"] = "true"
    os.environ["ENV"] = "local"
    os.environ["DATABASE_URL"] = "sqlite:///local_test.db"
    
    yield
    
    # Cleanup
    test_files = ["local_test.db", "test_logs.txt"]
    for file in test_files:
        if Path(file).exists():
            Path(file).unlink()

@pytest.fixture
def sample_contacts():
    """Contactos de exemplo para testes."""
    return [
        {"name": "João Silva", "phone": "+351912345678", "group": "Amigos"},
        {"name": "Maria Santos", "phone": "+351923456789", "group": "Trabalho"},
        {"name": "Pedro Costa", "phone": "+351934567890", "group": "Família"}
    ]

@pytest.fixture
def sample_sms_messages():
    """Mensagens SMS de exemplo para testes."""
    return [
        {
            "from": "+351912345678",
            "to": "+351923456789", 
            "body": "Olá, como estás?",
            "timestamp": "2025-01-01T10:00:00Z"
        },
        {
            "from": "+351923456789",
            "to": "+351912345678",
            "body": "Estou bem, obrigada!",
            "timestamp": "2025-01-01T10:01:00Z"
        }
    ]

@pytest.fixture
def sample_forwarding_rules():
    """Regras de reencaminhamento de exemplo."""
    return [
        {
            "name": "Encaminhar urgentes",
            "condition": "body contains 'URGENTE'",
            "action": "forward_to",
            "target": "+351912345678",
            "active": True
        },
        {
            "name": "Resposta automática",
            "condition": "from contains '+351'", 
            "action": "auto_reply",
            "target": "Mensagem recebida, responderemos em breve.",
            "active": True
        }
    ]
