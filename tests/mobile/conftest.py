# Configuração para testes mobile (Android/iOS)
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
import subprocess
import time

@pytest.fixture(scope="session")
def mobile_config(mobile_platform):
    """Configuração específica para testes mobile."""
    base_config = {
        "PLATFORM": mobile_platform,
        "APP_PACKAGE": "com.amamessage.client",
        "TIMEOUT": 15,
        "IMPLICIT_WAIT": 10
    }
    
    if mobile_platform == "android":
        base_config.update({
            "PLATFORM_VERSION": "11.0",
            "DEVICE_NAME": "Android Emulator",
            "AUTOMATION_NAME": "UiAutomator2",
            "APK_PATH": "clients/mobile/android/app/build/outputs/apk/debug/app-debug.apk"
        })
    elif mobile_platform == "ios":
        base_config.update({
            "PLATFORM_VERSION": "15.0", 
            "DEVICE_NAME": "iPhone 13",
            "AUTOMATION_NAME": "XCUITest",
            "APP_PATH": "clients/mobile/ios/build/AMAMESSAGE.app"
        })
    
    return base_config

@pytest.fixture(scope="session")
def appium_driver(mobile_config):
    """Driver do Appium para testes mobile."""
    if mobile_config["PLATFORM"] == "android":
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.platform_version = mobile_config["PLATFORM_VERSION"]
        options.device_name = mobile_config["DEVICE_NAME"]
        options.app_package = mobile_config["APP_PACKAGE"]
        options.app_activity = "com.amamessage.client.MainActivity"
        options.automation_name = mobile_config["AUTOMATION_NAME"]
        options.no_reset = False
        options.full_reset = False
        
        if "APK_PATH" in mobile_config:
            options.app = mobile_config["APK_PATH"]
    
    elif mobile_config["PLATFORM"] == "ios":
        options = XCUITestOptions()
        options.platform_name = "iOS"
        options.platform_version = mobile_config["PLATFORM_VERSION"]
        options.device_name = mobile_config["DEVICE_NAME"]
        options.bundle_id = mobile_config["APP_PACKAGE"]
        options.automation_name = mobile_config["AUTOMATION_NAME"]
        options.no_reset = False
        
        if "APP_PATH" in mobile_config:
            options.app = mobile_config["APP_PATH"]
    
    # Start Appium server
    appium_server = start_appium_server()
    
    driver = webdriver.Remote(
        "http://127.0.0.1:4723",  # Appium server URL
        options=options
    )
    
    driver.implicitly_wait(mobile_config["IMPLICIT_WAIT"])
    
    yield driver
    
    driver.quit()
    stop_appium_server(appium_server)

def start_appium_server():
    """Inicia o servidor Appium."""
    try:
        # Check if Appium is already running
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:4723/status"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return None  # Already running
    except:
        pass
    
    # Start Appium server
    process = subprocess.Popen(
        ["appium", "--port", "4723"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    return process

def stop_appium_server(process):
    """Para o servidor Appium."""
    if process:
        process.terminate()
        process.wait()

@pytest.fixture(scope="function")
def mobile_app_session(appium_driver):
    """Sessão da aplicação mobile para cada teste."""
    # Reset app state
    appium_driver.reset()
    yield appium_driver

@pytest.fixture
def mobile_user_login(mobile_app_session, mobile_config):
    """Realiza login na aplicação mobile."""
    def login(email="test@amamessage.com", password="testpass"):
        if mobile_config["PLATFORM"] == "android":
            # Android selectors
            email_field = mobile_app_session.find_element("id", "et_email")
            password_field = mobile_app_session.find_element("id", "et_password")
            login_button = mobile_app_session.find_element("id", "btn_login")
        else:
            # iOS selectors  
            email_field = mobile_app_session.find_element("accessibility id", "email_field")
            password_field = mobile_app_session.find_element("accessibility id", "password_field")
            login_button = mobile_app_session.find_element("accessibility id", "login_button")
        
        email_field.send_keys(email)
        password_field.send_keys(password)
        login_button.click()
        
        # Wait for dashboard
        time.sleep(3)
        
        return {
            "email": email,
            "logged_in": True
        }
    
    return login

@pytest.fixture
def mobile_elements(mobile_config):
    """Elementos da UI mobile por plataforma."""
    if mobile_config["PLATFORM"] == "android":
        return {
            "login": {
                "email": ("id", "et_email"),
                "password": ("id", "et_password"),
                "login_btn": ("id", "btn_login")
            },
            "dashboard": {
                "sms_count": ("id", "tv_sms_count"),
                "send_sms_fab": ("id", "fab_send_sms"),
                "menu_button": ("id", "btn_menu")
            },
            "sms": {
                "recipient": ("id", "et_recipient"),
                "message": ("id", "et_message"),
                "send_button": ("id", "btn_send"),
                "history_list": ("id", "rv_sms_history")
            },
            "contacts": {
                "add_button": ("id", "fab_add_contact"),
                "name_field": ("id", "et_contact_name"),
                "phone_field": ("id", "et_contact_phone"),
                "save_button": ("id", "btn_save_contact")
            },
            "ussd": {
                "code_field": ("id", "et_ussd_code"),
                "send_button": ("id", "btn_send_ussd"),
                "response_text": ("id", "tv_ussd_response")
            }
        }
    else:  # iOS
        return {
            "login": {
                "email": ("accessibility id", "email_field"),
                "password": ("accessibility id", "password_field"),
                "login_btn": ("accessibility id", "login_button")
            },
            "dashboard": {
                "sms_count": ("accessibility id", "sms_count_label"),
                "send_sms_btn": ("accessibility id", "send_sms_button"),
                "menu_button": ("accessibility id", "menu_button")
            },
            "sms": {
                "recipient": ("accessibility id", "recipient_field"),
                "message": ("accessibility id", "message_field"),
                "send_button": ("accessibility id", "send_button"),
                "history_table": ("accessibility id", "history_table")
            },
            "contacts": {
                "add_button": ("accessibility id", "add_contact_button"),
                "name_field": ("accessibility id", "name_field"),
                "phone_field": ("accessibility id", "phone_field"),
                "save_button": ("accessibility id", "save_button")
            },
            "ussd": {
                "code_field": ("accessibility id", "ussd_code_field"),
                "send_button": ("accessibility id", "send_ussd_button"),
                "response_label": ("accessibility id", "ussd_response_label")
            }
        }

@pytest.fixture
def mobile_actions():
    """Ações comuns para testes mobile."""
    def tap_element(driver, locator):
        element = driver.find_element(*locator)
        element.click()
    
    def send_keys_to_element(driver, locator, text):
        element = driver.find_element(*locator)
        element.clear()
        element.send_keys(text)
    
    def wait_for_element(driver, locator, timeout=10):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def swipe_up(driver):
        size = driver.get_window_size()
        start_x = size["width"] // 2
        start_y = size["height"] * 0.8
        end_y = size["height"] * 0.2
        driver.swipe(start_x, start_y, start_x, end_y, 1000)
    
    def swipe_down(driver):
        size = driver.get_window_size()
        start_x = size["width"] // 2
        start_y = size["height"] * 0.2
        end_y = size["height"] * 0.8
        driver.swipe(start_x, start_y, start_x, end_y, 1000)
    
    return {
        "tap": tap_element,
        "send_keys": send_keys_to_element,
        "wait": wait_for_element,
        "swipe_up": swipe_up,
        "swipe_down": swipe_down
    }

@pytest.fixture
def sample_mobile_data():
    """Dados de exemplo para testes mobile."""
    return {
        "users": {
            "enterprise": {
                "email": "admin@empresa.com",
                "password": "admin123",
                "name": "Admin Empresa",
                "type": "enterprise"
            },
            "individual": {
                "email": "user@gmail.com",
                "password": "user123", 
                "name": "Usuário Individual",
                "type": "individual"
            }
        },
        "contacts": [
            {"name": "João Mobile", "phone": "+351912000001"},
            {"name": "Maria Mobile", "phone": "+351912000002"}
        ],
        "sms_messages": [
            {
                "to": "+351912000001",
                "message": "Teste SMS via mobile"
            },
            {
                "to": "+351912000002", 
                "message": "Mensagem de exemplo mobile"
            }
        ],
        "ussd_codes": [
            {"code": "*100#", "description": "Consultar saldo"},
            {"code": "*101#", "description": "Consultar dados"}
        ]
    }
