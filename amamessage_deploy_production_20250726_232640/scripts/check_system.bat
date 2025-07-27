@echo off
echo ================================================
echo        AMA MESSAGE - Sistema de SMS
echo        Verificacao do Sistema Windows
echo ================================================
echo.

:: Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [INFO] Ambiente virtual ativado.
) else (
    echo [AVISO] Ambiente virtual nao encontrado. Execute install.bat primeiro.
)

:: Verificar arquivo .env
if not exist .env (
    echo [ERRO] Arquivo .env nao encontrado. Configure primeiro.
    pause
    exit /b 1
)

echo [INFO] Arquivo .env encontrado.

:: Verificar base de dados
if not exist amamessage.db (
    echo [INFO] Base de dados nao encontrada. Inicializando...
    python init_db.py
    python run_migration.py
)

echo [INFO] Base de dados verificada.

:: Testar conexoes
echo [INFO] Testando sistema...
python verificar_sistema.py

echo.
echo ================================================
echo         VERIFICACAO CONCLUIDA
echo ================================================
echo.
echo Para iniciar o sistema:
echo - Desenvolvimento: python iniciar_dev.py
echo - Producao: python iniciar_producao.py
echo.
pause
