# Testes de interface web para cliente empresarial e individual
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class TestWebLogin:
    """Testes de login para cliente web."""
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_enterprise_login_success(self, web_driver_session, ui_elements, sample_web_user_data, page_wait):
        """Testa login bem-sucedido para cliente empresarial."""
        enterprise_user = sample_web_user_data["enterprise"]
        
        # Navigate to login
        login_btn = page_wait["clickable"](web_driver_session, (By.ID, "login-link"))
        login_btn.click()
        
        # Fill login form
        email_field = web_driver_session.find_element(*ui_elements["login"]["username_field"])
        password_field = web_driver_session.find_element(*ui_elements["login"]["password_field"])
        
        email_field.send_keys(enterprise_user["email"])
        password_field.send_keys(enterprise_user["password"])
        
        # Submit login
        login_button = web_driver_session.find_element(*ui_elements["login"]["login_button"])
        login_button.click()
        
        # Verify redirect to enterprise dashboard
        page_wait["text"](web_driver_session, (By.TAG_NAME, "h1"), "Dashboard Empresarial")
        
        # Verify enterprise features are visible
        enterprise_menu = web_driver_session.find_element(By.ID, "enterprise-menu")
        assert enterprise_menu.is_displayed()
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_individual_login_success(self, web_driver_session, ui_elements, sample_web_user_data, page_wait):
        """Testa login bem-sucedido para cliente individual."""
        individual_user = sample_web_user_data["individual"]
        
        # Navigate to login
        login_btn = web_driver_session.find_element(By.ID, "login-link")
        login_btn.click()
        
        # Fill login form
        email_field = web_driver_session.find_element(*ui_elements["login"]["username_field"])
        password_field = web_driver_session.find_element(*ui_elements["login"]["password_field"])
        
        email_field.send_keys(individual_user["email"])
        password_field.send_keys(individual_user["password"])
        
        # Submit login
        login_button = web_driver_session.find_element(*ui_elements["login"]["login_button"])
        login_button.click()
        
        # Verify redirect to individual dashboard
        page_wait["text"](web_driver_session, (By.TAG_NAME, "h1"), "Meu Painel")
        
        # Verify individual interface (simplified)
        individual_menu = web_driver_session.find_element(By.ID, "user-menu")
        assert individual_menu.is_displayed()

class TestWebSMSFunctionality:
    """Testes de funcionalidade SMS via web."""
    
    @pytest.mark.ui
    @pytest.mark.web_client
    @pytest.mark.sms
    def test_send_sms_enterprise(self, authenticated_user, web_driver_session, ui_elements, page_wait):
        """Testa envio de SMS pela interface empresarial."""
        # Navigate to SMS section
        sms_menu = web_driver_session.find_element(By.ID, "sms-menu")
        sms_menu.click()
        
        # Click send SMS button
        send_sms_btn = page_wait["clickable"](web_driver_session, ui_elements["sms"]["send_button"])
        send_sms_btn.click()
        
        # Fill SMS form
        recipient_field = web_driver_session.find_element(*ui_elements["sms"]["recipient_field"])
        message_field = web_driver_session.find_element(*ui_elements["sms"]["message_field"])
        
        recipient_field.send_keys("+351912345678")
        message_field.send_keys("Mensagem de teste via web empresarial")
        
        # Send SMS
        send_button = web_driver_session.find_element(By.ID, "send-sms-submit")
        send_button.click()
        
        # Verify success message
        success_msg = page_wait["element"](web_driver_session, (By.CLASS_NAME, "alert-success"))
        assert "SMS enviado com sucesso" in success_msg.text
    
    @pytest.mark.ui
    @pytest.mark.web_client
    @pytest.mark.sms
    def test_sms_history_view(self, authenticated_user, web_driver_session, ui_elements, page_wait):
        """Testa visualização do histórico de SMS."""
        # Navigate to SMS history
        history_menu = web_driver_session.find_element(By.ID, "sms-history-menu")
        history_menu.click()
        
        # Wait for history table to load
        history_table = page_wait["element"](web_driver_session, ui_elements["sms"]["history_table"])
        
        # Verify table headers
        headers = history_table.find_elements(By.TAG_NAME, "th")
        expected_headers = ["Data", "Destinatário", "Mensagem", "Status"]
        
        for i, header in enumerate(headers):
            assert header.text == expected_headers[i]
        
        # Verify at least one row exists
        rows = history_table.find_elements(By.TAG_NAME, "tr")
        assert len(rows) > 1  # Headers + at least one data row

class TestWebUSSDFunctionality:
    """Testes de funcionalidade USSD via web."""
    
    @pytest.mark.ui
    @pytest.mark.web_client
    @pytest.mark.ussd
    def test_send_ussd_code(self, authenticated_user, web_driver_session, ui_elements, page_wait):
        """Testa envio de código USSD via web."""
        # Navigate to USSD section
        ussd_menu = web_driver_session.find_element(By.ID, "ussd-menu")
        ussd_menu.click()
        
        # Fill USSD form
        code_field = web_driver_session.find_element(*ui_elements["ussd"]["code_field"])
        code_field.send_keys("*100#")
        
        # Send USSD
        send_button = web_driver_session.find_element(*ui_elements["ussd"]["send_button"])
        send_button.click()
        
        # Wait for response
        response_area = page_wait["element"](web_driver_session, ui_elements["ussd"]["response_area"])
        
        # Verify response is displayed
        WebDriverWait(web_driver_session, 30).until(
            lambda driver: response_area.text != ""
        )
        
        assert len(response_area.text) > 0
    
    @pytest.mark.ui
    @pytest.mark.web_client
    @pytest.mark.ussd
    def test_ussd_session_management(self, authenticated_user, web_driver_session, page_wait):
        """Testa gestão de sessões USSD via web."""
        # Navigate to USSD sessions
        sessions_menu = web_driver_session.find_element(By.ID, "ussd-sessions-menu")
        sessions_menu.click()
        
        # Wait for sessions table
        sessions_table = page_wait["element"](web_driver_session, (By.ID, "ussd-sessions-table"))
        
        # Verify table structure
        headers = sessions_table.find_elements(By.TAG_NAME, "th")
        expected_headers = ["Sessão", "Código", "Status", "Resposta", "Data"]
        
        for i, header in enumerate(headers):
            assert header.text == expected_headers[i]

class TestWebContactManagement:
    """Testes de gestão de contactos via web."""
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_add_contact_enterprise(self, authenticated_user, web_driver_session, ui_elements, page_wait):
        """Testa adição de contacto pela interface empresarial."""
        # Navigate to contacts
        contacts_menu = web_driver_session.find_element(By.ID, "contacts-menu")
        contacts_menu.click()
        
        # Click add contact button
        add_btn = page_wait["clickable"](web_driver_session, ui_elements["contacts"]["add_contact_btn"])
        add_btn.click()
        
        # Fill contact form
        name_field = web_driver_session.find_element(*ui_elements["contacts"]["name_field"])
        phone_field = web_driver_session.find_element(*ui_elements["contacts"]["phone_field"])
        group_field = web_driver_session.find_element(*ui_elements["contacts"]["group_field"])
        
        name_field.send_keys("Contacto Teste Web")
        phone_field.send_keys("+351912345678")
        group_field.send_keys("Teste")
        
        # Save contact
        save_button = web_driver_session.find_element(*ui_elements["contacts"]["save_button"])
        save_button.click()
        
        # Verify success message
        success_msg = page_wait["element"](web_driver_session, (By.CLASS_NAME, "alert-success"))
        assert "Contacto adicionado com sucesso" in success_msg.text
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_contact_list_view(self, authenticated_user, web_driver_session, page_wait):
        """Testa visualização da lista de contactos."""
        # Navigate to contacts
        contacts_menu = web_driver_session.find_element(By.ID, "contacts-menu")
        contacts_menu.click()
        
        # Wait for contacts table
        contacts_table = page_wait["element"](web_driver_session, (By.ID, "contacts-table"))
        
        # Verify table headers
        headers = contacts_table.find_elements(By.TAG_NAME, "th")
        expected_headers = ["Nome", "Telefone", "Grupo", "Acções"]
        
        for i, header in enumerate(headers):
            assert header.text == expected_headers[i]

class TestWebUserInterface:
    """Testes gerais da interface web."""
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_responsive_design(self, web_driver_session):
        """Testa design responsivo da interface."""
        # Test desktop view
        web_driver_session.set_window_size(1920, 1080)
        menu = web_driver_session.find_element(By.ID, "main-menu")
        assert menu.is_displayed()
        
        # Test tablet view
        web_driver_session.set_window_size(768, 1024)
        menu_toggle = web_driver_session.find_element(By.ID, "menu-toggle")
        assert menu_toggle.is_displayed()
        
        # Test mobile view
        web_driver_session.set_window_size(375, 667)
        mobile_menu = web_driver_session.find_element(By.ID, "mobile-menu")
        assert mobile_menu.is_displayed()
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_navigation_menu(self, authenticated_user, web_driver_session, page_wait):
        """Testa navegação pelo menu principal."""
        menu_items = [
            ("dashboard-menu", "Dashboard"),
            ("sms-menu", "SMS"),
            ("contacts-menu", "Contactos"),
            ("ussd-menu", "USSD"),
            ("settings-menu", "Definições")
        ]
        
        for menu_id, expected_text in menu_items:
            menu_item = web_driver_session.find_element(By.ID, menu_id)
            menu_item.click()
            
            # Verify page content changed
            page_title = page_wait["element"](web_driver_session, (By.TAG_NAME, "h1"))
            assert expected_text.lower() in page_title.text.lower()
    
    @pytest.mark.ui
    @pytest.mark.web_client
    def test_form_validation(self, authenticated_user, web_driver_session, ui_elements, page_wait):
        """Testa validação de formulários."""
        # Navigate to SMS form
        sms_menu = web_driver_session.find_element(By.ID, "sms-menu")
        sms_menu.click()
        
        send_sms_btn = page_wait["clickable"](web_driver_session, ui_elements["sms"]["send_button"])
        send_sms_btn.click()
        
        # Try to send without filling required fields
        send_button = web_driver_session.find_element(By.ID, "send-sms-submit")
        send_button.click()
        
        # Verify validation messages
        error_msg = page_wait["element"](web_driver_session, (By.CLASS_NAME, "alert-danger"))
        assert "Campos obrigatórios não preenchidos" in error_msg.text
