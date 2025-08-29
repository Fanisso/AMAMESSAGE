#!/usr/bin/env python3
"""
Teste rápido para verificar se o sistema está funcionando
"""

try:
    print("🔍 Testando importações...")
    
    # Testar FastAPI
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__} importado com sucesso")
    
    # Testar SQLAlchemy
    import sqlalchemy
    print(f"✅ SQLAlchemy {sqlalchemy.__version__} importado com sucesso")
    
    # Testar Pydantic
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__} importado com sucesso")
    
    # Testar Uvicorn
    import uvicorn
    print(f"✅ Uvicorn importado com sucesso")
    
    print("\n🎉 Todas as dependências principais estão funcionando!")
    
    # Testar se podemos importar a aplicação
    print("\n🔍 Testando importação da aplicação...")
    
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
    
    try:
        from backend.main import app
        print("✅ Aplicação AMAMESSAGE importada com sucesso!")
        print(f"✅ Tipo da aplicação: {type(app)}")
        
        print("\n🚀 Sistema pronto para inicializar!")
        print("📍 Execute: uvicorn backend.main:app --reload")
        
    except Exception as e:
        print(f"⚠️ Erro ao importar aplicação: {e}")
        print("📋 Detalhes do erro:")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"❌ Erro nas dependências: {e}")
    import traceback
    traceback.print_exc()
