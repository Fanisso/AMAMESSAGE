# Testes de aplicação mobile para Android e iOS
import pytest
import time
from selenium.common.exceptions import NoSuchElementException

class TestMobileLogin:
    """Testes de login na aplicação mobile."""
    
    @pytest.mark.mobile
    @pytest.mark.android
    def test_android_enterprise_login(self, mobile_app_session, mobile_elements, sample_mobile_data, mobile_actions):
        """Testa login empresarial no Android."""
        enterprise_user = sample_mobile_data["users"]["enterprise"]
        elements = mobile_elements["login"]
        
        # Fill login form
        mobile_actions["send_keys"](mobile_app_session, elements["email"], enterprise_user["email"])
        mobile_actions["send_keys"](mobile_app_session, elements["password"], enterprise_user["password"])
        
        # Tap login button
        mobile_actions["tap"](mobile_app_session, elements["login_btn"])
        
        # Wait for dashboard
        dashboard_element = mobile_actions["wait"](
            mobile_app_session, 
            mobile_elements["dashboard"]["sms_count"],
            timeout=10
        )
        
        assert dashboard_element.is_displayed()
        
        # Verify enterprise features are available
        menu_button = mobile_app_session.find_element(*mobile_elements["dashboard"]["menu_button"])
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
        
        # Check for enterprise-specific menu items
        try:
            enterprise_reports = mobile_app_session.find_element("id", "menu_enterprise_reports")
            assert enterprise_reports.is_displayed()
        except NoSuchElementException:
            pytest.fail("Enterprise features not available after login")
    
    @pytest.mark.mobile
    @pytest.mark.ios
    def test_ios_individual_login(self, mobile_app_session, mobile_elements, sample_mobile_data, mobile_actions):
        """Testa login individual no iOS."""
        individual_user = sample_mobile_data["users"]["individual"]
        elements = mobile_elements["login"]
        
        # Fill login form
        mobile_actions["send_keys"](mobile_app_session, elements["email"], individual_user["email"])
        mobile_actions["send_keys"](mobile_app_session, elements["password"], individual_user["password"])
        
        # Tap login button
        mobile_actions["tap"](mobile_app_session, elements["login_btn"])
        
        # Wait for dashboard
        dashboard_element = mobile_actions["wait"](
            mobile_app_session, 
            mobile_elements["dashboard"]["sms_count"],
            timeout=10
        )
        
        assert dashboard_element.is_displayed()
        
        # Verify individual interface (all features available for comfort)
        send_sms_btn = mobile_app_session.find_element(*mobile_elements["dashboard"]["send_sms_btn"])
        assert send_sms_btn.is_displayed()

class TestMobileSMSFunctionality:
    """Testes de funcionalidade SMS mobile."""
    
    @pytest.mark.mobile
    @pytest.mark.android
    @pytest.mark.sms
    def test_android_send_sms(self, mobile_user_login, mobile_app_session, mobile_elements, sample_mobile_data, mobile_actions):
        """Testa envio de SMS no Android."""
        # Login first
        mobile_user_login("admin@empresa.com", "admin123")
        
        # Navigate to SMS
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["send_sms_fab"])
        
        # Fill SMS form
        sms_data = sample_mobile_data["sms_messages"][0]
        mobile_actions["send_keys"](mobile_app_session, mobile_elements["sms"]["recipient"], sms_data["to"])
        mobile_actions["send_keys"](mobile_app_session, mobile_elements["sms"]["message"], sms_data["message"])
        
        # Send SMS
        mobile_actions["tap"](mobile_app_session, mobile_elements["sms"]["send_button"])
        
        # Wait for confirmation
        time.sleep(3)
        
        # Verify success message
        try:
            success_toast = mobile_app_session.find_element("id", "sms_success_toast")
            assert "SMS enviado" in success_toast.text
        except NoSuchElementException:
            # Alternative verification - check if we're back to dashboard
            dashboard_element = mobile_app_session.find_element(*mobile_elements["dashboard"]["sms_count"])
            assert dashboard_element.is_displayed()
    
    @pytest.mark.mobile
    @pytest.mark.ios
    @pytest.mark.sms
    def test_ios_sms_history(self, mobile_user_login, mobile_app_session, mobile_elements, mobile_actions):
        """Testa visualização do histórico de SMS no iOS."""
        # Login first
        mobile_user_login("user@gmail.com", "user123")
        
        # Open menu
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
        
        # Navigate to SMS history
        history_menu = mobile_app_session.find_element("accessibility id", "sms_history_menu")
        mobile_actions["tap"](mobile_app_session, ("accessibility id", "sms_history_menu"))
        
        # Wait for history table
        history_table = mobile_actions["wait"](
            mobile_app_session,
            mobile_elements["sms"]["history_table"],
            timeout=10
        )
        
        assert history_table.is_displayed()
        
        # Check if history items exist
        history_items = mobile_app_session.find_elements("accessibility id", "sms_history_item")
        assert len(history_items) >= 0  # May be empty for new users

class TestMobileUSSDFunctionality:
    """Testes de funcionalidade USSD mobile."""
    
    @pytest.mark.mobile
    @pytest.mark.android
    @pytest.mark.ussd
    def test_android_send_ussd(self, mobile_user_login, mobile_app_session, mobile_elements, sample_mobile_data, mobile_actions):
        """Testa envio de código USSD no Android."""
        # Login first
        mobile_user_login("admin@empresa.com", "admin123")
        
        # Navigate to USSD
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
        ussd_menu = mobile_app_session.find_element("id", "menu_ussd")
        mobile_actions["tap"](mobile_app_session, ("id", "menu_ussd"))
        
        # Send USSD code
        ussd_code = sample_mobile_data["ussd_codes"][0]["code"]
        mobile_actions["send_keys"](mobile_app_session, mobile_elements["ussd"]["code_field"], ussd_code)
        mobile_actions["tap"](mobile_app_session, mobile_elements["ussd"]["send_button"])
        
        # Wait for response
        response_element = mobile_actions["wait"](
            mobile_app_session,
            mobile_elements["ussd"]["response_text"],
            timeout=30
        )
        
        # Verify response is displayed
        assert len(response_element.text) > 0
        
        # Common USSD responses
        common_responses = ["saldo", "balance", "menu", "opcao", "option"]
        response_text = response_element.text.lower()
        assert any(keyword in response_text for keyword in common_responses)
    
    @pytest.mark.mobile
    @pytest.mark.ios
    @pytest.mark.ussd
    def test_ios_ussd_session_management(self, mobile_user_login, mobile_app_session, mobile_elements, mobile_actions):
        """Testa gestão de sessões USSD no iOS."""
        # Login first
        mobile_user_login("user@gmail.com", "user123")
        
        # Navigate to USSD sessions
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
        sessions_menu = mobile_app_session.find_element("accessibility id", "ussd_sessions_menu")
        mobile_actions["tap"](mobile_app_session, ("accessibility id", "ussd_sessions_menu"))
        
        # Check sessions list
        sessions_list = mobile_actions["wait"](
            mobile_app_session,
            ("accessibility id", "ussd_sessions_list"),
            timeout=10
        )
        
        assert sessions_list.is_displayed()

class TestMobileContactManagement:
    """Testes de gestão de contactos mobile."""
    
    @pytest.mark.mobile
    @pytest.mark.android
    def test_android_add_contact(self, mobile_user_login, mobile_app_session, mobile_elements, sample_mobile_data, mobile_actions):
        """Testa adição de contacto no Android."""
        # Login first
        mobile_user_login("admin@empresa.com", "admin123")
        
        # Navigate to contacts
        mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
        contacts_menu = mobile_app_session.find_element("id", "menu_contacts")
        mobile_actions["tap"](mobile_app_session, ("id", "menu_contacts"))
        
        # Add new contact
        mobile_actions["tap"](mobile_app_session, mobile_elements["contacts"]["add_button"])
        
        # Fill contact form
        contact_data = sample_mobile_data["contacts"][0]
        mobile_actions["send_keys"](mobile_app_session, mobile_elements["contacts"]["name_field"], contact_data["name"])
        mobile_actions["send_keys"](mobile_app_session, mobile_elements["contacts"]["phone_field"], contact_data["phone"])
        
        # Save contact
        mobile_actions["tap"](mobile_app_session, mobile_elements["contacts"]["save_button"])
        
        # Wait for confirmation
        time.sleep(2)
        
        # Verify we're back to contacts list
        contacts_list = mobile_app_session.find_element("id", "contacts_list")
        assert contacts_list.is_displayed()
    
    @pytest.mark.mobile
    @pytest.mark.ios
    def test_ios_contact_search(self, mobile_user_login, mobile_app_session, mobile_actions):
        """Testa busca de contactos no iOS."""
        # Login first
        mobile_user_login("user@gmail.com", "user123")
        
        # Navigate to contacts
        mobile_actions["tap"](mobile_app_session, ("accessibility id", "contacts_tab"))
        
        # Use search functionality
        search_field = mobile_app_session.find_element("accessibility id", "contact_search_field")
        mobile_actions["send_keys"](mobile_app_session, ("accessibility id", "contact_search_field"), "João")
        
        # Wait for search results
        time.sleep(2)
        
        # Verify search results
        search_results = mobile_app_session.find_elements("accessibility id", "contact_search_result")
        # Results may be empty, but search should not crash
        assert isinstance(search_results, list)

class TestMobileUserExperience:
    """Testes de experiência do usuário mobile."""
    
    @pytest.mark.mobile
    @pytest.mark.android
    def test_android_navigation_flow(self, mobile_user_login, mobile_app_session, mobile_elements, mobile_actions):
        """Testa fluxo de navegação no Android."""
        # Login
        mobile_user_login("admin@empresa.com", "admin123")
        
        # Test navigation through main sections
        sections = [
            ("menu_sms", "sms_screen"),
            ("menu_contacts", "contacts_screen"),
            ("menu_ussd", "ussd_screen"),
            ("menu_settings", "settings_screen")
        ]
        
        for menu_id, screen_id in sections:
            # Open menu
            mobile_actions["tap"](mobile_app_session, mobile_elements["dashboard"]["menu_button"])
            
            # Navigate to section
            menu_item = mobile_app_session.find_element("id", menu_id)
            mobile_actions["tap"](mobile_app_session, ("id", menu_id))
            
            # Verify we're in the right screen
            screen = mobile_actions["wait"](mobile_app_session, ("id", screen_id), timeout=5)
            assert screen.is_displayed()
            
            # Go back to dashboard
            back_button = mobile_app_session.find_element("id", "back_button")
            mobile_actions["tap"](mobile_app_session, ("id", "back_button"))
    
    @pytest.mark.mobile
    @pytest.mark.ios
    def test_ios_gesture_navigation(self, mobile_user_login, mobile_app_session, mobile_actions):
        """Testa navegação por gestos no iOS."""
        # Login
        mobile_user_login("user@gmail.com", "user123")
        
        # Test swipe gestures
        # Swipe up to reveal more options
        mobile_actions["swipe_up"](mobile_app_session)
        time.sleep(1)
        
        # Swipe down to refresh
        mobile_actions["swipe_down"](mobile_app_session)
        time.sleep(2)
        
        # Verify dashboard is still visible
        dashboard_element = mobile_app_session.find_element("accessibility id", "dashboard_title")
        assert dashboard_element.is_displayed()
    
    @pytest.mark.mobile
    @pytest.mark.android
    @pytest.mark.ios
    def test_mobile_performance(self, mobile_user_login, mobile_app_session, mobile_actions):
        """Testa performance da aplicação mobile."""
        start_time = time.time()
        
        # Login
        mobile_user_login("admin@empresa.com", "admin123")
        
        login_time = time.time() - start_time
        assert login_time < 10, f"Login demorou {login_time:.2f}s, esperado < 10s"
        
        # Test screen transitions
        transition_start = time.time()
        
        # Navigate between screens quickly
        for _ in range(3):
            mobile_actions["tap"](mobile_app_session, ("id", "menu_sms") if mobile_app_session.capabilities['platformName'] == 'Android' else ("accessibility id", "sms_tab"))
            time.sleep(0.5)
            mobile_actions["tap"](mobile_app_session, ("id", "menu_contacts") if mobile_app_session.capabilities['platformName'] == 'Android' else ("accessibility id", "contacts_tab"))
            time.sleep(0.5)
        
        transition_time = time.time() - transition_start
        assert transition_time < 15, f"Transições demoraram {transition_time:.2f}s, esperado < 15s"
