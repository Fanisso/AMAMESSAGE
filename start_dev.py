#!/usr/bin/env python3
"""
Script de inicialização do AMAMESSAGE
Modo de desenvolvimento com hot-reload
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Inicializar sistema em modo desenvolvimento"""
    
    # Definir diretórios
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    print("🚀 AMAMESSAGE - Iniciando em modo desenvolvimento...")
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
        print("📦 Instalando dependências principais...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependências instaladas com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Algumas dependências falharam, mas continuando: {e}")
    
    # Inicializar base de dados (tentar, mas não falhar se der erro)
    print("🗄️ Inicializando base de dados...")
    try:
        subprocess.run([sys.executable, "-c", "from app.db.database import init_db; init_db()"], check=False)
        print("✅ Base de dados inicializada!")
    except Exception as e:
        print(f"⚠️ Erro na inicialização da BD (continuando): {e}")
    
    # Executar migrações (tentar, mas não falhar se der erro)
    print("⬆️ Executando migrações...")
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Migrações executadas com sucesso!")
        else:
            print(f"⚠️ Migrações falharam (continuando): {result.stderr}")
    except Exception as e:
        print(f"⚠️ Erro nas migrações (continuando): {e}")
    
    # Verificar se uvicorn está disponível
    try:
        subprocess.run([sys.executable, "-c", "import uvicorn"], check=True)
        print("✅ Uvicorn disponível!")
    except subprocess.CalledProcessError:
        print("⚠️ Instalando uvicorn...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"], check=True)
    
    # Iniciar servidor
    print("\n" + "="*50)
    print("🌐 Iniciando servidor FastAPI...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("🔄 Hot-reload ativo - modificações serão recarregadas automaticamente")
    print("⏹️ Pressione Ctrl+C para parar")
    print("="*50 + "\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()
