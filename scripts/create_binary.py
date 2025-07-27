#!/usr/bin/env python3
"""
Script para criar binário executável do AMA MESSAGE
Remove código fonte e cria executável standalone
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinaryBuilder:
    """Constrói binário executável sem código fonte"""
    
    def __init__(self, source_dir: str, output_dir: str = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(f"amamessage_binary_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def check_dependencies(self):
        """Verificar se PyInstaller está instalado"""
        try:
            import PyInstaller
            logger.info("✅ PyInstaller encontrado")
            return True
        except ImportError:
            logger.error("❌ PyInstaller não encontrado. Instale com: pip install pyinstaller")
            return False
    
    def create_spec_file(self):
        """Criar ficheiro .spec para PyInstaller"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{self.source_dir.absolute()}'],
    binaries=[],
    datas=[
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static'),
        ('alembic', 'alembic'),
        ('migrations', 'migrations'),
        ('.env.example', '.'),
        ('alembic.ini', '.'),
        ('deploy.ini', '.'),
    ],
    hiddenimports=[
        'sqlalchemy.dialects.sqlite',
        'fastapi',
        'uvicorn',
        'jinja2',
        'starlette',
        'pydantic',
        'serial',
        'asyncio',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='amamessage',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        spec_file = self.source_dir / "amamessage.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        logger.info(f"✅ Ficheiro .spec criado: {spec_file}")
        return spec_file
    
    def build_binary(self):
        """Construir binário executável"""
        logger.info("🔨 Iniciando construção do binário...")
        
        # Verificar dependências
        if not self.check_dependencies():
            return False
        
        # Criar ficheiro .spec
        spec_file = self.create_spec_file()
        
        # Executar PyInstaller
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            logger.info(f"Executando: {' '.join(cmd)}")
            result = subprocess.run(cmd, cwd=self.source_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Binário criado com sucesso!")
                return True
            else:
                logger.error(f"❌ Erro na construção: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar PyInstaller: {e}")
            return False
    
    def create_deployment_package(self):
        """Criar pacote de deployment sem código fonte"""
        logger.info("📦 Criando pacote de deployment...")
        
        # Criar diretório de output
        self.output_dir.mkdir(exist_ok=True)
        
        # Copiar binário
        binary_src = self.source_dir / "dist" / "amamessage.exe"
        if not binary_src.exists():
            binary_src = self.source_dir / "dist" / "amamessage"
        
        if binary_src.exists():
            shutil.copy2(binary_src, self.output_dir / binary_src.name)
            logger.info(f"✅ Binário copiado: {binary_src.name}")
        
        # Copiar ficheiros de configuração (sem código fonte)
        config_files = [
            ".env.example",
            "deploy.ini",
            "README.md",
            "LICENSE"
        ]
        
        for file in config_files:
            src = self.source_dir / file
            if src.exists():
                shutil.copy2(src, self.output_dir / file)
                logger.info(f"✅ Copiado: {file}")
        
        # Criar script de inicialização
        self.create_startup_script()
        
        # Criar documentação
        self.create_deployment_docs()
        
        logger.info(f"✅ Pacote criado em: {self.output_dir}")
        return self.output_dir
    
    def create_startup_script(self):
        """Criar script de inicialização"""
        if os.name == 'nt':  # Windows
            script_content = '''@echo off
echo Iniciando AMA MESSAGE...
echo.
amamessage.exe
pause
'''
            script_file = self.output_dir / "iniciar.bat"
        else:  # Linux/Mac
            script_content = '''#!/bin/bash
echo "Iniciando AMA MESSAGE..."
echo
./amamessage
read -p "Pressione Enter para sair..."
'''
            script_file = self.output_dir / "iniciar.sh"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        if not os.name == 'nt':
            os.chmod(script_file, 0o755)
        
        logger.info(f"✅ Script de inicialização criado: {script_file.name}")
    
    def create_deployment_docs(self):
        """Criar documentação de deployment"""
        docs_content = f'''# AMA MESSAGE - Versão Binária

**Data de Compilação:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Versão:** Produção Binária

## Como Usar:

### Windows:
1. Execute: `iniciar.bat`
2. Ou execute diretamente: `amamessage.exe`

### Linux/Mac:
1. Execute: `./iniciar.sh`
2. Ou execute diretamente: `./amamessage`

## Configuração:

1. Copie `.env.example` para `.env`
2. Configure suas credenciais no ficheiro `.env`
3. Execute a aplicação

## Acesso:

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Suporte:

Esta é uma versão binária compilada.
O código fonte não está incluído por questões de segurança.

Para suporte técnico, contacte o desenvolvedor.
'''
        
        docs_file = self.output_dir / "LEIA-ME.md"
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        
        logger.info("✅ Documentação criada: LEIA-ME.md")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Criar binário do AMA MESSAGE")
    parser.add_argument("--source", default=".", help="Diretório fonte")
    parser.add_argument("--output", help="Diretório de saída")
    
    args = parser.parse_args()
    
    builder = BinaryBuilder(args.source, args.output)
    
    logger.info("🚀 Iniciando criação de binário AMA MESSAGE")
    
    if builder.build_binary():
        package_dir = builder.create_deployment_package()
        
        print("\n" + "="*50)
        print("✅ BINÁRIO CRIADO COM SUCESSO!")
        print("="*50)
        print(f"📁 Localização: {package_dir}")
        print(f"📦 Tamanho aproximado: ~50-100MB")
        print(f"🔒 Código fonte: NÃO incluído")
        print(f"⚡ Executável: Standalone")
        print("\n💡 Para distribuir:")
        print(f"   - Comprima a pasta: {package_dir}")
        print(f"   - Envie para os clientes")
        print(f"   - Clientes executam: iniciar.bat (Windows) ou iniciar.sh (Linux)")
        print("="*50)
    else:
        logger.error("❌ Falha na criação do binário")
        sys.exit(1)


if __name__ == "__main__":
    main()
