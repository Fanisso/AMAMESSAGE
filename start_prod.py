#!/usr/bin/env python3
"""
Script de inicialização do AMAMESSAGE para produção
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Inicializar sistema em modo produção"""
    
    # Definir diretórios
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    print("🚀 AMAMESSAGE - Iniciando em modo PRODUÇÃO...")
    print(f"📁 Diretório do projeto: {project_root}")
    print(f"🔧 Backend: {backend_dir}")
    
    # Verificar se o backend existe
    if not backend_dir.exists():
        print("❌ Erro: Diretório backend não encontrado!")
        return False
    
    # Mudar para o diretório backend
    os.chdir(backend_dir)
    
    # Verificar dependências
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print("📦 Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Inicializar base de dados
    print("🗄️ Inicializando base de dados...")
    subprocess.run([sys.executable, "-c", "from app.db.database import init_db; init_db()"], check=True)
    
    # Executar migrações
    print("⬆️ Executando migrações...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    # Iniciar servidor em modo produção
    print("🌐 Iniciando servidor em modo PRODUÇÃO...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("⏹️ Pressione Ctrl+C para parar")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--workers", "4"
    ])

if __name__ == "__main__":
    main()
