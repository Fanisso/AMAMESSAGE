@echo off
echo ================================================
echo        AMA MESSAGE - Preparar Deploy
echo ================================================
echo.

set TIMESTAMP=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

if "%~1"=="" (
    echo Uso: prepare_deploy.bat [development^|production^|docker^|list]
    echo.
    echo Exemplos:
    echo   prepare_deploy.bat development
    echo   prepare_deploy.bat production
    echo   prepare_deploy.bat docker
    echo   prepare_deploy.bat list
    echo.
    pause
    exit /b 1
)

set DEPLOY_TYPE=%~1
set DEST_DIR=amamessage_deploy_%DEPLOY_TYPE%_%TIMESTAMP%

if "%DEPLOY_TYPE%"=="list" (
    echo Ficheiros que seriam incluidos no deploy:
    echo.
    echo CORE:
    echo   main.py
    echo   requirements.txt
    echo   .env.example
    echo   alembic.ini
    echo   deploy.ini
    echo   init_db.py
    echo   run_migration.py
    echo   deploy.py
    echo.
    echo APPLICATION:
    echo   app\ (todo o diretorio)
    echo   migrations\
    echo   alembic\
    echo.
    echo DOCUMENTATION:
    echo   README.md
    echo   LICENSE
    echo   docs\
    echo.
    echo SCRIPTS:
    echo   scripts\
    echo.
    if "%DEPLOY_TYPE%"=="production" (
        echo PRODUCTION ADICIONAL:
        echo   iniciar_producao.py
        echo   verificar_sistema.py
    )
    if "%DEPLOY_TYPE%"=="docker" (
        echo DOCKER ADICIONAL:
        echo   start_server.py
    )
    echo.
    pause
    exit /b 0
)

echo Preparando deploy para: %DEPLOY_TYPE%
echo Destino: %DEST_DIR%
echo.

:: Criar diretorio de destino
mkdir "%DEST_DIR%" 2>nul

:: Copiar ficheiros core
echo Copiando ficheiros core...
copy main.py "%DEST_DIR%\" >nul 2>&1
copy requirements.txt "%DEST_DIR%\" >nul 2>&1
copy .env.example "%DEST_DIR%\" >nul 2>&1
copy alembic.ini "%DEST_DIR%\" >nul 2>&1
copy deploy.ini "%DEST_DIR%\" >nul 2>&1
copy init_db.py "%DEST_DIR%\" >nul 2>&1
copy run_migration.py "%DEST_DIR%\" >nul 2>&1
copy deploy.py "%DEST_DIR%\" >nul 2>&1

:: Copiar diretorios principais
echo Copiando aplicacao...
xcopy app "%DEST_DIR%\app" /E /I /Q >nul 2>&1
xcopy migrations "%DEST_DIR%\migrations" /E /I /Q >nul 2>&1
xcopy alembic "%DEST_DIR%\alembic" /E /I /Q >nul 2>&1
xcopy scripts "%DEST_DIR%\scripts" /E /I /Q >nul 2>&1

:: Copiar documentacao
echo Copiando documentacao...
copy README.md "%DEST_DIR%\" >nul 2>&1
copy LICENSE "%DEST_DIR%\" >nul 2>&1
xcopy docs "%DEST_DIR%\docs" /E /I /Q >nul 2>&1

:: Ficheiros adicionais baseados no tipo
if "%DEPLOY_TYPE%"=="production" (
    echo Copiando ficheiros de producao...
    copy iniciar_producao.py "%DEST_DIR%\" >nul 2>&1
    copy verificar_sistema.py "%DEST_DIR%\" >nul 2>&1
)

if "%DEPLOY_TYPE%"=="docker" (
    echo Copiando ficheiros Docker...
    copy start_server.py "%DEST_DIR%\" >nul 2>&1
)

:: Criar ficheiro .env baseado no tipo
echo Criando ficheiro .env...
if "%DEPLOY_TYPE%"=="development" (
    echo # AMA MESSAGE - Configuracao Desenvolvimento > "%DEST_DIR%\.env"
    echo DEBUG=True >> "%DEST_DIR%\.env"
    echo LOG_LEVEL=DEBUG >> "%DEST_DIR%\.env"
    echo DATABASE_URL=sqlite:///amamessage.db >> "%DEST_DIR%\.env"
    echo HOST=127.0.0.1 >> "%DEST_DIR%\.env"
    echo PORT=8000 >> "%DEST_DIR%\.env"
)

if "%DEPLOY_TYPE%"=="production" (
    echo # AMA MESSAGE - Configuracao Producao > "%DEST_DIR%\.env"
    echo DEBUG=False >> "%DEST_DIR%\.env"
    echo LOG_LEVEL=INFO >> "%DEST_DIR%\.env"
    echo DATABASE_URL=sqlite:///data/amamessage.db >> "%DEST_DIR%\.env"
    echo HOST=0.0.0.0 >> "%DEST_DIR%\.env"
    echo PORT=8000 >> "%DEST_DIR%\.env"
    echo TWILIO_ACCOUNT_SID=your_account_sid_here >> "%DEST_DIR%\.env"
    echo TWILIO_AUTH_TOKEN=your_auth_token_here >> "%DEST_DIR%\.env"
    echo TWILIO_PHONE_NUMBER=your_twilio_number_here >> "%DEST_DIR%\.env"
)

if "%DEPLOY_TYPE%"=="docker" (
    echo # AMA MESSAGE - Configuracao Docker > "%DEST_DIR%\.env"
    echo DEBUG=False >> "%DEST_DIR%\.env"
    echo LOG_LEVEL=INFO >> "%DEST_DIR%\.env"
    echo DATABASE_URL=sqlite:///app/data/amamessage.db >> "%DEST_DIR%\.env"
    echo HOST=0.0.0.0 >> "%DEST_DIR%\.env"
    echo PORT=8000 >> "%DEST_DIR%\.env"
    echo REDIS_URL=redis://redis:6379/0 >> "%DEST_DIR%\.env"
)

:: Limpar ficheiros desnecessarios
echo Limpando ficheiros desnecessarios...
del /S /Q "%DEST_DIR%\*.pyc" >nul 2>&1
del /S /Q "%DEST_DIR%\*.pyo" >nul 2>&1
del /S /Q "%DEST_DIR%\*.log" >nul 2>&1
del /S /Q "%DEST_DIR%\test_*.py" >nul 2>&1
del /S /Q "%DEST_DIR%\debug_*.py" >nul 2>&1
del /S /Q "%DEST_DIR%\quick_*.py" >nul 2>&1
del /S /Q "%DEST_DIR%\diagnose_*.py" >nul 2>&1
del /S /Q "%DEST_DIR%\fix_*.py" >nul 2>&1
del /S /Q "%DEST_DIR%\*.db" >nul 2>&1
rmdir /S /Q "%DEST_DIR%\__pycache__" >nul 2>&1
rmdir /S /Q "%DEST_DIR%\app\__pycache__" >nul 2>&1

:: Criar informacoes do deploy
echo Criando informacoes do deploy...
echo # AMA MESSAGE - Deploy %DEPLOY_TYPE% > "%DEST_DIR%\DEPLOY_INFO.txt"
echo Data: %DATE% %TIME% >> "%DEST_DIR%\DEPLOY_INFO.txt"
echo. >> "%DEST_DIR%\DEPLOY_INFO.txt"
echo Proximos passos: >> "%DEST_DIR%\DEPLOY_INFO.txt"

if "%DEPLOY_TYPE%"=="development" (
    echo 1. Configure o arquivo .env >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 2. Execute: python deploy.py install >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 3. Execute: python deploy.py test >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 4. Inicie: python main.py >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo Acesso: http://localhost:8000 >> "%DEST_DIR%\DEPLOY_INFO.txt"
)

if "%DEPLOY_TYPE%"=="production" (
    echo 1. Configure o arquivo .env >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 2. Execute: sudo python deploy.py production >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 3. Configure: sudo nano /opt/amamessage/.env >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 4. Inicie: sudo systemctl start amamessage >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo Acesso: http://seu-servidor >> "%DEST_DIR%\DEPLOY_INFO.txt"
)

if "%DEPLOY_TYPE%"=="docker" (
    echo 1. Configure o arquivo .env >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 2. Execute: python deploy.py docker >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 3. Execute: python deploy.py docker-build >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo 4. Execute: python deploy.py docker-start >> "%DEST_DIR%\DEPLOY_INFO.txt"
    echo Acesso: http://localhost >> "%DEST_DIR%\DEPLOY_INFO.txt"
)

echo.
echo ================================================
echo           DEPLOY PREPARADO COM SUCESSO!
echo ================================================
echo.
echo Tipo: %DEPLOY_TYPE%
echo Destino: %DEST_DIR%
echo.
echo Consulte DEPLOY_INFO.txt para proximos passos.
echo.
pause
