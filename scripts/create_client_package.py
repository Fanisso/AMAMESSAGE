#!/usr/bin/env python3
"""
Criador de pacote do agente para clientes SaaS
Gera pacote mínimo para instalação no cliente
"""

import os
import sys
import shutil
import zipfile
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClientPackageBuilder:
    """Constrói pacote para cliente SaaS"""
    
    def __init__(self, server_url: str = "https://seuservico.com", output_dir: str = None):
        self.server_url = server_url
        self.output_dir = Path(output_dir) if output_dir else Path(f"cliente_amamessage_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def create_package(self):
        """Criar pacote completo para cliente"""
        logger.info("📦 Criando pacote para cliente...")
        
        # Criar diretório
        self.output_dir.mkdir(exist_ok=True)
        
        # Copiar agente
        self.copy_agent_files()
        
        # Criar configuração personalizada
        self.create_client_config()
        
        # Criar scripts de instalação
        self.create_installation_scripts()
        
        # Criar documentação
        self.create_client_documentation()
        
        # Criar pacote ZIP
        zip_file = self.create_zip_package()
        
        logger.info(f"✅ Pacote criado: {zip_file}")
        return zip_file
    
    def copy_agent_files(self):
        """Copiar ficheiros do agente"""
        scripts_dir = Path(__file__).parent
        
        files_to_copy = [
            "modem_agent.py",
            "install_agent.bat"
        ]
        
        for file in files_to_copy:
            src = scripts_dir / file
            if src.exists():
                shutil.copy2(src, self.output_dir / file)
                logger.info(f"✅ Copiado: {file}")
    
    def create_client_config(self):
        """Criar configuração personalizada"""
        config_content = f'''{{
  "server_url": "{self.server_url}",
  "api_key": "CONFIGURE_SUA_API_KEY_AQUI",
  "client_id": "cliente_novo",
  "modem_port": "COM3",
  "modem_baud": 115200,
  "reconnect_interval": 30,
  "heartbeat_interval": 60,
  "ssl_verify": true
}}'''
        
        config_file = self.output_dir / "agent_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        logger.info("✅ Configuração criada")
    
    def create_installation_scripts(self):
        """Criar scripts de instalação"""
        
        # Script Windows melhorado
        windows_script = f'''@echo off
title AMA MESSAGE - Instalacao do Agente
color 0B

echo.
echo ================================================
echo     AMA MESSAGE - Instalacao do Agente
echo ================================================
echo.
echo 🌐 Servidor: {self.server_url}
echo 📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
echo.

REM Verificar administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ ERRO: Execute como administrador
    echo.
    echo 👆 Clique com botao direito neste arquivo
    echo    e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo ✅ Executando como administrador
echo.

echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado
    echo.
    echo 📝 INSTRUCOES:
    echo 1. Baixe Python em: https://python.org/downloads
    echo 2. Durante a instalacao, marque "Add Python to PATH"
    echo 3. Execute este script novamente
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python %%i encontrado
)

echo.
echo 📦 Instalando dependencias...
pip install websocket-client pyserial requests pywin32 --quiet --no-warn-script-location
if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo 🔧 Configurando servico...
python modem_agent.py --install-service
if exist modem_service.py (
    python modem_service.py install
    echo ✅ Servico instalado
) else (
    echo ⚠️  Arquivo de servico nao encontrado, executar manualmente
)

echo.
echo ================================================
echo           INSTALACAO CONCLUIDA!
echo ================================================
echo.
echo 📋 PROXIMOS PASSOS:
echo.
echo 1. 🔑 Configure sua API Key:
echo    - Edite: agent_config.json
echo    - Substitua: CONFIGURE_SUA_API_KEY_AQUI
echo    - Por sua chave fornecida
echo.
echo 2. 📱 Configure seu modem:
echo    - Conecte o modem GSM ao PC
echo    - Verifique a porta (ex: COM3, COM4)
echo    - Atualize "modem_port" no config
echo.
echo 3. ▶️  Inicie o servico:
echo    - Execute: INICIAR_AGENTE.bat
echo    - Ou: python modem_service.py start
echo.
echo 4. 🌐 Acesse o sistema:
echo    - Abra: {self.server_url}
echo    - Use suas credenciais
echo.
echo 🆘 Suporte: suporte@seudominio.com
echo.

pause'''
        
        with open(self.output_dir / "INSTALAR.bat", 'w', encoding='utf-8') as f:
            f.write(windows_script)
        
        # Script de inicialização
        start_script = '''@echo off
title AMA MESSAGE - Agente
echo 🚀 Iniciando AMA MESSAGE Agent...
echo.

REM Verificar se serviço existe
sc query AMAMessageModemAgent >nul 2>&1
if %errorLevel% == 0 (
    echo 📋 Usando servico Windows...
    net start AMAMessageModemAgent
    echo ✅ Servico iniciado
    echo 🌐 Acesse: ''' + self.server_url + '''
    echo.
    echo 📊 Para ver status: VERIFICAR_STATUS.bat
) else (
    echo 📋 Executando diretamente...
    python modem_agent.py
)

pause
'''
        
        with open(self.output_dir / "INICIAR_AGENTE.bat", 'w', encoding='utf-8') as f:
            f.write(start_script)
        
        # Script de verificação
        check_script = f'''@echo off
title AMA MESSAGE - Status
echo ================================================
echo        AMA MESSAGE - Status do Sistema
echo ================================================
echo.

echo 🔍 Verificando servico...
sc query AMAMessageModemAgent >nul 2>&1
if %errorLevel% == 0 (
    sc query AMAMessageModemAgent | find "RUNNING" >nul
    if %errorLevel% == 0 (
        echo ✅ Servico: ATIVO
    ) else (
        echo ⚠️  Servico: PARADO
        echo 💡 Execute: INICIAR_AGENTE.bat
    )
) else (
    echo ❌ Servico: NAO INSTALADO
    echo 💡 Execute: INSTALAR.bat
)

echo.
echo 🔍 Verificando conexao...
ping -n 1 google.com >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Internet: CONECTADO
) else (
    echo ❌ Internet: SEM CONEXAO
)

echo.
echo 🔍 Verificando Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python: %%i
) else (
    echo ❌ Python: NAO ENCONTRADO
)

echo.
echo 🌐 Sistema: {self.server_url}
echo 📅 Verificado em: %date% %time%
echo.
echo 💡 Para reiniciar: INICIAR_AGENTE.bat
echo 🆘 Suporte: suporte@seudominio.com
echo.

pause'''
        
        with open(self.output_dir / "VERIFICAR_STATUS.bat", 'w', encoding='utf-8') as f:
            f.write(check_script)
        
        logger.info("✅ Scripts de instalação criados")
    
    def create_client_documentation(self):
        """Criar documentação para cliente"""
        
        readme_content = f'''# 📱 AMA MESSAGE - Agente Cliente

## 🚀 Instalação Rápida

### 1. Pré-requisitos
- Windows 10/11
- Modem GSM conectado ao PC
- Conexão à Internet
- Permissões de administrador

### 2. Instalação
1. **Execute como administrador**: `INSTALAR.bat`
2. **Configure API Key**: Edite `agent_config.json`
3. **Configure modem**: Verifique porta COM
4. **Inicie agente**: Execute `INICIAR_AGENTE.bat`

### 3. Configuração

Edite o arquivo `agent_config.json`:

```json
{{
  "server_url": "{self.server_url}",
  "api_key": "SUA_API_KEY_AQUI",
  "client_id": "seu_cliente_id",
  "modem_port": "COM3",
  "modem_baud": 115200
}}
```

### 4. Uso

1. **Acesse o sistema**: {self.server_url}
2. **Faça login** com suas credenciais
3. **Use a interface web** para enviar SMS
4. **O modem local** processará os envios

## 🔧 Comandos Úteis

- **Instalar**: `INSTALAR.bat`
- **Iniciar**: `INICIAR_AGENTE.bat` 
- **Verificar**: `VERIFICAR_STATUS.bat`
- **Parar**: `net stop AMAMessageModemAgent`

## 📋 Resolução de Problemas

### Modem não detectado
- Verifique se o modem está conectado
- Confirme a porta COM no Gestor de Dispositivos
- Atualize `modem_port` na configuração

### Agente não conecta
- Verifique conexão à Internet
- Confirme se a API Key está correta
- Verifique se o servidor está acessível

### Serviço não inicia
- Execute `INSTALAR.bat` novamente
- Verifique permissões de administrador
- Consulte logs em `modem_agent.log`

## 📞 Suporte

- **Sistema Web**: {self.server_url}
- **Email**: suporte@seudominio.com
- **Documentação**: README_CLIENTE.md

---

**© 2025 AMA MESSAGE - Versão Cliente**
'''
        
        with open(self.output_dir / "README_CLIENTE.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Guia rápido
        quick_guide = f'''📱 GUIA RÁPIDO - AMA MESSAGE

🚀 INSTALAÇÃO:
1. Execute: INSTALAR.bat (como administrador)
2. Configure: agent_config.json (API Key)
3. Inicie: INICIAR_AGENTE.bat

🔧 CONFIGURAÇÃO:
- API Key: Fornecida pelo administrador
- Porta Modem: Verificar no Windows (ex: COM3)
- Servidor: {self.server_url}

🌐 USO:
- Acesse: {self.server_url}
- Login: Usar credenciais fornecidas
- Interface: Totalmente web

📞 SUPORTE:
- Email: suporte@seudominio.com
- Status: VERIFICAR_STATUS.bat
- Logs: modem_agent.log

⚠️  IMPORTANTE:
- Sempre executar como administrador
- Manter agente sempre ativo
- Verificar conexão Internet

✅ Instalação concluída com sucesso!
'''
        
        with open(self.output_dir / "GUIA_RAPIDO.txt", 'w', encoding='utf-8') as f:
            f.write(quick_guide)
        
        logger.info("✅ Documentação criada")
    
    def create_zip_package(self):
        """Criar pacote ZIP"""
        zip_filename = f"{self.output_dir.name}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.output_dir.parent)
                    zipf.write(file_path, arc_path)
        
        logger.info(f"✅ Pacote ZIP criado: {zip_filename}")
        return zip_filename


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Criar pacote cliente SaaS")
    parser.add_argument("--server", default="https://seuservico.com", help="URL do servidor")
    parser.add_argument("--output", help="Diretório de saída")
    
    args = parser.parse_args()
    
    builder = ClientPackageBuilder(args.server, args.output)
    
    logger.info("📦 Criando pacote para cliente AMA MESSAGE SaaS")
    
    zip_file = builder.create_package()
    
    print("\n" + "="*60)
    print("📦 PACOTE CLIENTE CRIADO COM SUCESSO!")
    print("="*60)
    print(f"📁 Arquivo: {zip_file}")
    print(f"🌐 Servidor: {args.server}")
    print(f"📏 Tamanho: ~50KB (sem dependências)")
    print("\n💡 Para o cliente:")
    print(f"   1. Extrair: {zip_file}")
    print(f"   2. Executar: INSTALAR.bat (como admin)")
    print(f"   3. Configurar: agent_config.json")
    print(f"   4. Iniciar: INICIAR_AGENTE.bat")
    print(f"   5. Acessar: {args.server}")
    print("="*60)


if __name__ == "__main__":
    main()
