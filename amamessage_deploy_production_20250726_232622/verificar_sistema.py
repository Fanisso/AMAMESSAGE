#!/usr/bin/env python3
"""
Script para verificar e resolver problemas do servidor AMA MESSAGE
"""
import sys
import subprocess
import time
import requests
from pathlib import Path

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import serial
        print("✅ Todas as dependências encontradas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        return False

def verificar_porta(host="127.0.0.1", port=8000):
    """Verifica se a porta está livre"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            print(f"✅ Porta {port} está livre")
            return True
        except socket.error:
            print(f"❌ Porta {port} está ocupada")
            return False

def iniciar_servidor():
    """Inicia o servidor"""
    print("🚀 Iniciando servidor AMA MESSAGE...")
    print("📱 Sistema de SMS com Modem GSM")
    print("🌐 URL: http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("=" * 50)
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def verificar_servidor_rodando():
    """Verifica se o servidor está respondendo"""
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
    except:
        pass
    print("❌ Servidor não está respondendo")
    return False

def diagnostico_completo():
    """Executa diagnóstico completo do sistema"""
    print("🔧 DIAGNÓSTICO DO SISTEMA AMA MESSAGE")
    print("=" * 50)
    
    # Verificar dependências
    if not verificar_dependencias():
        print("\n💡 Solução: Execute 'pip install -r requirements.txt'")
        return False
    
    # Verificar porta
    if not verificar_porta():
        print("\n💡 Solução: Feche outros serviços na porta 8000 ou use outra porta")
        return False
    
    # Verificar arquivos principais
    arquivos_importantes = ["main.py", "app/__init__.py", "app/core/config.py"]
    for arquivo in arquivos_importantes:
        if not Path(arquivo).exists():
            print(f"❌ Arquivo faltando: {arquivo}")
            return False
    print("✅ Todos os arquivos importantes encontrados")
    
    print("\n✅ Sistema parece estar OK! Tentando iniciar...")
    return True

if __name__ == "__main__":
    print("🛠️  AMA MESSAGE - Verificador do Sistema\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnostico":
        diagnostico_completo()
    else:
        # Verificar se servidor já está rodando
        if verificar_servidor_rodando():
            print("ℹ️  Servidor já está rodando em http://127.0.0.1:8000")
        else:
            if diagnostico_completo():
                iniciar_servidor()
