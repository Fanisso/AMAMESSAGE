# Testes unitários para desenvolvimento local
import pytest
from unittest.mock import Mock, patch

class TestSMSService:
    """Testes unitários para o serviço de SMS."""
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_send_sms_success(self, mock_modem, local_test_config):
        """Testa envio de SMS com sucesso."""
        # Mock do serviço SMS
        from backend.app.services.sms_service import SMSService
        
        service = SMSService(modem=mock_modem)
        result = service.send_sms("+351912345678", "Teste SMS")
        
        assert result["status"] == "sent"
        assert "id" in result
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_send_sms_invalid_number(self, mock_modem):
        """Testa envio de SMS com número inválido."""
        from backend.app.services.sms_service import SMSService
        
        service = SMSService(modem=mock_modem)
        
        with pytest.raises(ValueError, match="Número inválido"):
            service.send_sms("123", "Teste SMS")
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_send_sms_empty_message(self, mock_modem):
        """Testa envio de SMS com mensagem vazia."""
        from backend.app.services.sms_service import SMSService
        
        service = SMSService(modem=mock_modem)
        
        with pytest.raises(ValueError, match="Mensagem não pode estar vazia"):
            service.send_sms("+351912345678", "")

class TestUSSDService:
    """Testes unitários para o serviço USSD."""
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.ussd
    def test_send_ussd_success(self, mock_modem):
        """Testa envio de código USSD com sucesso."""
        from backend.app.services.ussd_service import USSDService
        
        service = USSDService(modem=mock_modem)
        result = service.send_ussd("*100#")
        
        assert result["response"] == "Mock USSD response"
        assert "session_id" in result
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.ussd
    def test_send_ussd_invalid_code(self, mock_modem):
        """Testa envio de código USSD inválido."""
        from backend.app.services.ussd_service import USSDService
        
        service = USSDService(modem=mock_modem)
        
        with pytest.raises(ValueError, match="Código USSD inválido"):
            service.send_ussd("123")

class TestForwardingRules:
    """Testes unitários para regras de reencaminhamento."""
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.forwarding
    def test_create_forwarding_rule(self, sample_forwarding_rules):
        """Testa criação de regra de reencaminhamento."""
        from backend.app.services.forwarding_service import ForwardingService
        
        service = ForwardingService()
        rule_data = sample_forwarding_rules[0]
        
        rule = service.create_rule(
            name=rule_data["name"],
            condition=rule_data["condition"],
            action=rule_data["action"],
            target=rule_data["target"]
        )
        
        assert rule.name == rule_data["name"]
        assert rule.active == True
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.forwarding
    def test_apply_forwarding_rule(self, sample_sms_messages, sample_forwarding_rules):
        """Testa aplicação de regra de reencaminhamento."""
        from backend.app.services.forwarding_service import ForwardingService
        
        service = ForwardingService()
        sms = sample_sms_messages[0]
        
        # Simula SMS com palavra "URGENTE"
        sms["body"] = "URGENTE: Mensagem importante"
        
        rules = service.get_matching_rules(sms)
        assert len(rules) > 0
        
        # Aplica regra
        result = service.apply_rules(sms, rules)
        assert result["forwarded"] == True

class TestContactManagement:
    """Testes unitários para gestão de contactos."""
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_add_contact(self, sample_contacts, clean_database):
        """Testa adição de contacto."""
        from backend.app.services.contact_service import ContactService
        
        service = ContactService()
        contact_data = sample_contacts[0]
        
        contact = service.add_contact(
            name=contact_data["name"],
            phone=contact_data["phone"],
            group=contact_data["group"]
        )
        
        assert contact.name == contact_data["name"]
        assert contact.phone == contact_data["phone"]
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_duplicate_contact(self, sample_contacts, clean_database):
        """Testa adição de contacto duplicado."""
        from backend.app.services.contact_service import ContactService
        
        service = ContactService()
        contact_data = sample_contacts[0]
        
        # Adiciona contacto
        service.add_contact(
            name=contact_data["name"],
            phone=contact_data["phone"],
            group=contact_data["group"]
        )
        
        # Tenta adicionar novamente
        with pytest.raises(ValueError, match="Contacto já existe"):
            service.add_contact(
                name=contact_data["name"],
                phone=contact_data["phone"],
                group=contact_data["group"]
            )

class TestDatabaseOperations:
    """Testes unitários para operações de base de dados."""
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.database
    def test_database_connection(self, temp_database):
        """Testa conexão com a base de dados."""
        from backend.app.db.database import get_db_connection
        
        connection = get_db_connection(temp_database)
        assert connection is not None
    
    @pytest.mark.unit
    @pytest.mark.local
    @pytest.mark.database
    def test_create_tables(self, temp_database):
        """Testa criação de tabelas."""
        from backend.app.db.database import create_tables
        
        result = create_tables(temp_database)
        assert result == True

class TestConfigurationManagement:
    """Testes unitários para gestão de configuração."""
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_load_config(self, local_test_config):
        """Testa carregamento de configuração."""
        from backend.app.core.config import load_config
        
        config = load_config("local")
        
        assert config["DEBUG"] == True
        assert config["HOST"] == "127.0.0.1"
        assert config["PORT"] == 8000
    
    @pytest.mark.unit
    @pytest.mark.local
    def test_validate_config(self, local_test_config):
        """Testa validação de configuração."""
        from backend.app.core.config import validate_config
        
        is_valid = validate_config(local_test_config)
        assert is_valid == True
