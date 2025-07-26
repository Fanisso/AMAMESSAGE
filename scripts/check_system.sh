#!/bin/bash

# AMA MESSAGE - Sistema de SMS
# Verificacao do Sistema Linux/Mac

echo "================================================"
echo "        AMA MESSAGE - Sistema de SMS"
echo "        Verificacao do Sistema"
echo "================================================"
echo

# Ativar ambiente virtual se existir
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
    echo "[INFO] Ambiente virtual ativado."
else
    echo "[AVISO] Ambiente virtual nao encontrado. Execute install.sh primeiro."
fi

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo "[ERRO] Arquivo .env nao encontrado. Configure primeiro."
    exit 1
fi

echo "[INFO] Arquivo .env encontrado."

# Verificar base de dados
if [ ! -f amamessage.db ]; then
    echo "[INFO] Base de dados nao encontrada. Inicializando..."
    python init_db.py
    python run_migration.py
fi

echo "[INFO] Base de dados verificada."

# Testar conexoes
echo "[INFO] Testando sistema..."
python verificar_sistema.py

echo
echo "================================================"
echo "         VERIFICACAO CONCLUIDA"
echo "================================================"
echo
echo "Para iniciar o sistema:"
echo "- Desenvolvimento: python iniciar_dev.py"
echo "- Producao: python iniciar_producao.py"
echo
