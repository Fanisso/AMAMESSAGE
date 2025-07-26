"""
Script de teste para o sistema de regras de reencaminhamento
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.forwarding_service import ForwardingRuleService
from app.db.models import SMS, SMSDirection, SMSStatus

def test_forwarding_system():
    """Testar o sistema de regras de reencaminhamento"""
    print("🧪 Testando Sistema de Regras de Reencaminhamento\n")
    
    db = SessionLocal()
    try:
        service = ForwardingRuleService(db)
        
        # 1. Listar regras existentes
        print("📋 Regras configuradas:")
        rules = service.get_rules()
        for rule in rules:
            print(f"  - {rule.name} ({rule.rule_type.value}) -> {rule.action.value}")
        print()
        
        # 2. Testar com SMS simulado
        print("📱 Testando com SMS simulado:")
        
        # Criar SMS de teste e salvar temporariamente
        test_sms = SMS(
            phone_from="+55 11 99999-0001",  # Número que corresponde à regra de exemplo
            phone_to="+55 11 88888-0000",
            message="Esta é uma mensagem de teste do chefe",
            direction=SMSDirection.INBOUND,
            status=SMSStatus.RECEIVED
        )
        
        # Salvar SMS para ter um ID válido
        db.add(test_sms)
        db.commit()
        db.refresh(test_sms)
        
        result = service.process_sms(test_sms)
        
        print(f"  SMS: '{test_sms.message}'")
        print(f"  De: {test_sms.phone_from}")
        print(f"  Para: {test_sms.phone_to}")
        print(f"  Resultado: {result}")
        print()
        
        # 3. Obter estatísticas
        print("📊 Estatísticas:")
        stats = service.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
        
        # 4. Testar com palavra-chave
        print("🔑 Testando com palavra-chave:")
        test_sms2 = SMS(
            phone_from="+55 11 77777-0001",
            phone_to="+55 11 88888-0000", 
            message="Temos uma situação URGENTE aqui!",
            direction=SMSDirection.INBOUND,
            status=SMSStatus.RECEIVED
        )
        
        # Salvar SMS para ter um ID válido
        db.add(test_sms2)
        db.commit()
        db.refresh(test_sms2)
        
        result2 = service.process_sms(test_sms2)
        print(f"  SMS: '{test_sms2.message}'")
        print(f"  De: {test_sms2.phone_from}")
        print(f"  Resultado: {result2}")
        print()
        
        print("✅ Testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_forwarding_system()
