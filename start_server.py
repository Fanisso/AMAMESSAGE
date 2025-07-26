import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando AMA MESSAGE...")
    print("📱 Sistema de SMS com Modem GSM")
    print("🌐 Acesse: http://127.0.0.1:8000")
    print("📚 Documentação API: http://127.0.0.1:8000/docs")
    print("📱 USSD Menu: http://127.0.0.1:8000/modem/ussd")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Desabilitar reloader para evitar problemas com modem
        log_level="info"
    )
