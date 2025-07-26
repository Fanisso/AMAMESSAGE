#!/usr/bin/env python3
"""
Teste simples para verificar se o problema foi corrigido
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.db.models import SMS

def test_sms_access():
    """Testar se conseguimos acessar SMS sem erro"""
    db = SessionLocal()
    
    try:
        print("🔍 Testando acesso aos SMS...")
        
        # Tentar obter alguns SMS
        sms_list = db.query(SMS).limit(5).all()
        
        print(f"✅ Encontrados {len(sms_list)} SMS")
        
        for sms in sms_list:
            print(f"📱 SMS #{sms.id}: {sms.phone_from} -> {sms.phone_to}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar SMS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Teste de acesso aos SMS...")
    success = test_sms_access()
    
    if success:
        print("✅ Teste bem-sucedido!")
    else:
        print("❌ Teste falhou!")
