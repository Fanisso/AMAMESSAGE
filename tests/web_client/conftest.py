# Configuração para testes do cliente web
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def web_client_config():
    """Configuração para testes do cliente web."""
    return {
        "ENV": "web_client",
        "BASE_URL": "http://localhost:3000",
        "API_URL": "http://localhost:8000/api",
        "TIMEOUT": 10,
        "BROWSER": "chrome",
        "HEADLESS": True
    }

@pytest.fixture(scope="session")
def web_driver(web_client_config):
    """Driver do Selenium para testes de UI."""
    chrome_options = Options()
    
    if web_client_config["HEADLESS"]:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(web_client_config["TIMEOUT"])
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="function")
def web_driver_session(web_driver, web_client_config):
    """Sessão do driver web para cada teste."""
    web_driver.get(web_client_config["BASE_URL"])
    yield web_driver
    web_driver.delete_all_cookies()

@pytest.fixture
def authenticated_user(web_driver_session, web_client_config):
    """Usuário autenticado para testes."""
    # Navigate to login page
    web_driver_session.get(f"{web_client_config['BASE_URL']}/login")
    
    # Mock login
    username_field = web_driver_session.find_element(By.ID, "username")
    password_field = web_driver_session.find_element(By.ID, "password")
    login_button = web_driver_session.find_element(By.ID, "login-btn")
    
    username_field.send_keys("test@amamessage.com")
    password_field.send_keys("testpassword")
    login_button.click()
    
    # Wait for redirect to dashboard
    WebDriverWait(web_driver_session, 10).until(
        EC.url_contains("/dashboard")
    )
    
    return {
        "email": "test@amamessage.com",
        "name": "Usuário Teste",
        "role": "admin"
    }

@pytest.fixture
def api_client():
    """Cliente para testes de API web."""
    import requests
    
    class WebAPIClient:
        def __init__(self, base_url="http://localhost:8000"):
            self.base_url = base_url
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "User-Agent": "AMAMESSAGE-Web-Test/1.0"
            })
        
        def login(self, email, password):
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                self.session.headers["Authorization"] = f"Bearer {token}"
            return response
        
        def get_contacts(self):
            return self.session.get(f"{self.base_url}/api/contacts")
        
        def send_sms(self, to, message):
            return self.session.post(
                f"{self.base_url}/api/sms/send",
                json={"to": to, "message": message}
            )
        
        def get_sms_history(self):
            return self.session.get(f"{self.base_url}/api/sms/history")
        
        def send_ussd(self, code):
            return self.session.post(
                f"{self.base_url}/api/ussd/send",
                json={"code": code}
            )
    
    return WebAPIClient()

@pytest.fixture
def ui_elements():
    """Elementos de UI comuns para testes."""
    return {
        "login": {
            "username_field": (By.ID, "username"),
            "password_field": (By.ID, "password"),
            "login_button": (By.ID, "login-btn")
        },
        "dashboard": {
            "sms_count": (By.ID, "sms-count"),
            "contacts_count": (By.ID, "contacts-count"),
            "send_sms_btn": (By.ID, "send-sms-btn")
        },
        "sms": {
            "recipient_field": (By.ID, "sms-recipient"),
            "message_field": (By.ID, "sms-message"),
            "send_button": (By.ID, "sms-send-btn"),
            "history_table": (By.ID, "sms-history-table")
        },
        "contacts": {
            "add_contact_btn": (By.ID, "add-contact-btn"),
            "name_field": (By.ID, "contact-name"),
            "phone_field": (By.ID, "contact-phone"),
            "group_field": (By.ID, "contact-group"),
            "save_button": (By.ID, "contact-save-btn")
        },
        "ussd": {
            "code_field": (By.ID, "ussd-code"),
            "send_button": (By.ID, "ussd-send-btn"),
            "response_area": (By.ID, "ussd-response")
        }
    }

@pytest.fixture
def page_wait():
    """Helper para esperar elementos na página."""
    def wait_for_element(driver, locator, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def wait_for_clickable(driver, locator, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    def wait_for_text(driver, locator, text, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element(locator, text)
        )
    
    return {
        "element": wait_for_element,
        "clickable": wait_for_clickable,
        "text": wait_for_text
    }

@pytest.fixture
def sample_web_user_data():
    """Dados de usuário para testes web."""
    return {
        "enterprise": {
            "email": "admin@empresa.com",
            "password": "admin123",
            "name": "Administrador Empresa",
            "role": "admin",
            "company": "Empresa Teste Lda"
        },
        "individual": {
            "email": "user@gmail.com", 
            "password": "user123",
            "name": "Usuário Individual",
            "role": "user",
            "phone": "+351912345678"
        }
    }

@pytest.fixture
def mock_web_responses():
    """Respostas mock para testes web."""
    return {
        "login_success": {
            "access_token": "mock-jwt-token",
            "user": {
                "id": 1,
                "email": "test@example.com",
                "name": "Test User"
            }
        },
        "sms_sent": {
            "id": "sms-123",
            "status": "sent",
            "timestamp": "2025-01-01T10:00:00Z"
        },
        "contacts_list": [
            {"id": 1, "name": "João", "phone": "+351912345678"},
            {"id": 2, "name": "Maria", "phone": "+351923456789"}
        ],
        "ussd_response": {
            "session_id": "ussd-456",
            "response": "Saldo: 10.00 EUR",
            "status": "completed"
        }
    }
