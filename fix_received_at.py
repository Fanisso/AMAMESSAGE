#!/usr/bin/env python3
"""
Script para adicionar a coluna received_at na tabela SMS
"""
import sqlite3
import os
from pathlib import Path

def add_received_at_column():
    """Adicionar coluna received_at na tabela SMS se não existir"""
    
    print("🔧 Iniciando script...")
    
    # Caminho para o arquivo da base de dados
    db_path = Path(__file__).parent / "amamessage.db"
    
    print(f"📁 Procurando base de dados em: {db_path.absolute()}")
    
    if not db_path.exists():
        print(f"❌ Base de dados não encontrada em: {db_path}")
        # Listar arquivos no diretório
        print("📁 Arquivos no diretório:")
        for file in Path(__file__).parent.glob("*.db"):
            print(f"  - {file.name}")
        return False
    
    print(f"✅ Base de dados encontrada: {db_path}")
    
    try:
        # Conectar à base de dados
        print("🔌 Conectando à base de dados...")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        print("🔍 Verificando colunas existentes...")
        cursor.execute("PRAGMA table_info(sms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Colunas atuais na tabela SMS: {columns}")
        
        if 'received_at' in columns:
            print("✅ Coluna 'received_at' já existe na tabela SMS")
            return True
        
        # Adicionar a coluna
        print("➕ Adicionando coluna 'received_at'...")
        cursor.execute("ALTER TABLE sms ADD COLUMN received_at DATETIME;")
        
        # Atualizar SMS recebidos com data de criação como data de recepção
        print("🔄 Atualizando SMS recebidos...")
        cursor.execute("""
            UPDATE sms 
            SET received_at = created_at 
            WHERE direction = 'INBOUND' AND received_at IS NULL
        """)
        
        # Confirmar mudanças
        print("💾 Salvando mudanças...")
        conn.commit()
        
        # Verificar se foi adicionada
        print("✅ Verificando resultado...")
        cursor.execute("PRAGMA table_info(sms)")
        new_columns = [column[1] for column in cursor.fetchall()]
        
        if 'received_at' in new_columns:
            print("✅ Coluna 'received_at' adicionada com sucesso!")
            print(f"📋 Colunas após mudança: {new_columns}")
            
            # Mostrar contagem de SMS com received_at
            cursor.execute("SELECT COUNT(*) FROM sms WHERE received_at IS NOT NULL")
            count = cursor.fetchone()[0]
            print(f"📊 {count} SMS agora têm received_at definido")
            
            return True
        else:
            print("❌ Falha ao adicionar coluna 'received_at'")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao modificar base de dados: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            print("🔌 Fechando conexão...")
            conn.close()

if __name__ == "__main__":
    print("🔧 Adicionando coluna 'received_at' na tabela SMS...")
    success = add_received_at_column()
    
    if success:
        print("✅ Script executado com sucesso!")
    else:
        print("❌ Script falhou!")
    
    input("Pressione Enter para continuar...")
