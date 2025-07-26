#!/usr/bin/env python3
"""
Script para inicializar a base de dados com as tabelas necessárias
"""

import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, Base
from app.db.models import *  # Importar todos os modelos

def init_database():
    """Criar todas as tabelas na base de dados"""
    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Base de dados inicializada com sucesso!")
        print("📋 Tabelas criadas:")
        
        # Listar as tabelas criadas
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
            
    except Exception as e:
        print(f"❌ Erro ao inicializar base de dados: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 Inicializando base de dados...")
    init_database()
