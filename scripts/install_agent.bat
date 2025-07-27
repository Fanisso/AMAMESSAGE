@echo off
echo.
echo ===============================================
echo    AMA MESSAGE - Instalacao do Agente
echo ===============================================
echo.

REM Verificar se está sendo executado como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Executando como administrador
) else (
    echo ❌ Este script precisa ser executado como administrador
    echo    Clique com botao direito e "Executar como administrador"
    pause
    exit /b 1
)

echo 🔍 Verificando sistema...

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python nao encontrado
    echo 📥 Baixando e instalando Python 3.12...
    
    REM Baixar Python
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe', 'python-installer.exe')"
    
    REM Instalar Python silenciosamente
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    REM Aguardar instalação
    timeout /t 30 /nobreak >nul
    
    REM Limpar
    del python-installer.exe
    
    echo ✅ Python instalado
) else (
    echo ✅ Python encontrado
)

echo.
echo 📦 Instalando dependencias...
pip install websocket-client pyserial requests pywin32

echo.
echo 📋 Criando configuracao...

REM Criar arquivo de configuração
(
echo {
echo   "server_url": "https://seuservico.com",
echo   "api_key": "CONFIGURE_SUA_API_KEY_AQUI",
echo   "client_id": "cliente_%COMPUTERNAME%",
echo   "modem_port": "COM3",
echo   "modem_baud": 115200,
echo   "reconnect_interval": 30,
echo   "heartbeat_interval": 60,
echo   "ssl_verify": true
echo }
) > agent_config.json

echo ✅ Configuracao criada: agent_config.json

echo.
echo 🔧 Instalando como servico Windows...

REM Instalar como serviço
python modem_agent.py --install-service
python modem_service.py install

echo ✅ Servico instalado

echo.
echo ⚙️ CONFIGURACAO NECESSARIA:
echo.
echo 1. Edite o arquivo: agent_config.json
echo 2. Configure:
echo    - server_url: URL do seu servidor
echo    - api_key: Chave fornecida pelo administrador
echo    - modem_port: Porta do seu modem (ex: COM3)
echo.
echo 3. Inicie o servico:
echo    python modem_service.py start
echo.
echo 4. Acesse o sistema:
echo    https://seuservico.com
echo.

echo ===============================================
echo         Instalacao Concluida!
echo ===============================================
echo.
echo 📝 Para configurar e iniciar:
echo    1. Edite: agent_config.json
echo    2. Execute: python modem_service.py start
echo    3. Acesse: https://seuservico.com
echo.
echo 🆘 Suporte: suporte@seuservico.com
echo.

pause
