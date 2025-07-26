#!/usr/bin/env python3
"""
Script para testar os endpoints da aplicação
"""
import sys
import asyncio
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from app.db.database import get_db
from app.db.models import SMS, SMSCommand, User, SMSStatus, SMSDirection

async def test_database():
    """Testar operações da base de dados"""
    print("🔍 Testando conexão com a base de dados...")
    
    try:
        # Obter sessão da base de dados
        db = next(get_db())
        
        # Testar query simples
        sms_count = db.query(SMS).count()
        commands_count = db.query(SMSCommand).count()
        users_count = db.query(User).count()
        
        print(f"✅ SMS na base de dados: {sms_count}")
        print(f"✅ Comandos na base de dados: {commands_count}")
        print(f"✅ Usuários na base de dados: {users_count}")
        
        # Criar dados de teste se não existirem
        if commands_count == 0:
            print("📝 Criando comandos de teste...")
            test_command = SMSCommand(
                keyword="INFO",
                description="Comando de informações",
                response_message="Este é o sistema AMA MESSAGE - SMS com Modem GSM",
                is_active=True
            )
            db.add(test_command)
            db.commit()
            print("✅ Comando de teste criado!")
        
        if users_count == 0:
            print("👤 Criando usuário administrador...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            admin_user = User(
                username="admin",
                email="admin@amamessage.com",
                full_name="Administrador",
                hashed_password=pwd_context.hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuário admin criado!")
            print("   Username: admin")
            print("   Password: admin123")
        
        print("✅ Base de dados funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ Erro na base de dados: {e}")
        return False
    finally:
        db.close()
    
    return True

def test_imports():
    """Testar importações dos módulos"""
    print("📦 Testando importações...")
    
    try:
        from main import app
        print("✅ main.app importado")
        
        from app.api import sms, admin, auth, modem
        print("✅ Routers importados")
        
        from app.services.sms_service import SMSService
        print("✅ SMSService importado")
        
        from app.services.gsm_service import GSMModem
        print("✅ GSMModem importado")
        
        from app.services.modem_detector import ModemDetector
        print("✅ ModemDetector importado")
        
        print("✅ Todas as importações funcionando!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AMA MESSAGE - Teste de Sistema")
    print("=" * 50)
    
    # Testar importações
    imports_ok = test_imports()
    print()
    
    # Testar base de dados
    database_ok = asyncio.run(test_database())
    print()
    
    # Resultado final
    if imports_ok and database_ok:
        print("🎉 Sistema funcionando corretamente!")
        print("📱 Pronto para enviar e receber SMS!")
        print()
        print("Para iniciar o servidor:")
        print("  python iniciar_dev.py")
        print()
        print("Acesso Web:")
        print("  🌐 Dashboard: http://127.0.0.1:8000")
        print("  📚 API Docs: http://127.0.0.1:8000/docs")
        print("  📱 USSD: http://127.0.0.1:8000/modem/ussd")
    else:
        print("❌ Há problemas no sistema que precisam ser corrigidos.")
    
    print("=" * 50)
