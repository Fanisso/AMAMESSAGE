#!/usr/bin/env python3
"""
Script para iniciar o servidor AMA MESSAGE sem reloader
Evita problemas de multiprocessing com o modem GSM
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Iniciando AMA MESSAGE (Modo Produção)...")
    print("📱 Sistema de SMS com Modem GSM")
    print("🌐 Acesse: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("💡 Modo sem reloader - para desenvolvimento use: uvicorn main:app --reload")
    print("=" * 50)
    
    # Executar sem reloader para evitar problemas com multiprocessing
    uvicorn.run(
        app,  # Usar instância direta ao invés de string
        host="127.0.0.1",
        port=8000,
        reload=False,  # Desabilitar reloader
        log_level="info"
    )
