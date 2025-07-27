#!/bin/bash

# AMA MESSAGE - Sistema de SMS
# Script de Instalacao Linux/Mac

set -e

echo "================================================"
echo "        AMA MESSAGE - Sistema de SMS"
echo "        Script de Instalacao Linux/Mac"
echo "================================================"
echo

# Verificar se Python esta instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 nao encontrado. Instale Python 3.8+ primeiro."
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

echo "[INFO] Python encontrado."

# Verificar se Git esta instalado
if ! command -v git &> /dev/null; then
    echo "[ERRO] Git nao encontrado. Instale Git primeiro."
    echo "Ubuntu/Debian: sudo apt install git"
    echo "CentOS/RHEL: sudo yum install git"
    echo "macOS: brew install git"
    exit 1
fi

echo "[INFO] Git encontrado."

# Criar ambiente virtual
echo "[INFO] Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "[INFO] Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "[INFO] Atualizando pip..."
python -m pip install --upgrade pip

# Instalar dependencias
echo "[INFO] Instalando dependencias..."
pip install -r requirements.txt

# Criar arquivo .env se nao existir
if [ ! -f .env ]; then
    echo "[INFO] Criando arquivo .env..."
    cp .env.example .env
    echo "[AVISO] Configure o arquivo .env com suas credenciais antes de executar."
fi

# Inicializar base de dados
echo "[INFO] Inicializando base de dados..."
python init_db.py

# Executar migracoes
echo "[INFO] Executando migracoes..."
python run_migration.py

echo
echo "================================================"
echo "           INSTALACAO CONCLUIDA!"
echo "================================================"
echo
echo "Proximos passos:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Para desenvolvimento: python iniciar_dev.py"
echo "3. Para producao: python iniciar_producao.py"
echo
echo "Documentacao: docs/README.md"
echo
