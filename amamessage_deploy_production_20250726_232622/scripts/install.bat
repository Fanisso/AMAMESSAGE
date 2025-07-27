@echo off
echo ================================================
echo        AMA MESSAGE - Sistema de SMS
echo         Script de Instalacao Windows
echo ================================================
echo.

:: Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale Python 3.8+ primeiro.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python encontrado.

:: Verificar se Git esta instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Git nao encontrado. Instale Git primeiro.
    echo Download: https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [INFO] Git encontrado.

:: Criar ambiente virtual
echo [INFO] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar ambiente virtual.
    pause
    exit /b 1
)

:: Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip

:: Instalar dependencias
echo [INFO] Instalando dependencias...
pip install -r requirements.txt

:: Criar arquivo .env se nao existir
if not exist .env (
    echo [INFO] Criando arquivo .env...
    copy .env.example .env
    echo [AVISO] Configure o arquivo .env com suas credenciais antes de executar.
)

:: Inicializar base de dados
echo [INFO] Inicializando base de dados...
python init_db.py

:: Executar migracoes
echo [INFO] Executando migracoes...
python run_migration.py

echo.
echo ================================================
echo           INSTALACAO CONCLUIDA!
echo ================================================
echo.
echo Proximos passos:
echo 1. Configure o arquivo .env com suas credenciais
echo 2. Para desenvolvimento: execute iniciar_dev.py
echo 3. Para producao: execute iniciar_producao.py
echo.
echo Documentacao: docs/README.md
echo.
pause
