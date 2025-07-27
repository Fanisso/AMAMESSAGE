#!/usr/bin/env python3
"""
Script para obfuscar código Python do AMA MESSAGE
Torna o código ilegível mas mantém funcionalidade
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

class CodeObfuscator:
    """Obfusca código Python para proteger propriedade intelectual"""
    
    def __init__(self, source_dir: str, output_dir: str = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(f"amamessage_obfuscated_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def check_dependencies(self):
        """Verificar se pyarmor está instalado"""
        try:
            result = subprocess.run([sys.executable, "-m", "pyarmor", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ PyArmor encontrado")
                return True
            else:
                raise Exception()
        except:
            logger.error("❌ PyArmor não encontrado. Instale com: pip install pyarmor")
            return False
    
    def prepare_source(self):
        """Preparar código fonte para obfuscação"""
        logger.info("📋 Preparando ficheiros para obfuscação...")
        
        # Criar diretório temporário
        temp_dir = self.source_dir / "temp_obfuscation"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Copiar ficheiros Python
        python_files = []
        for root, dirs, files in os.walk(self.source_dir):
            # Excluir diretórios desnecessários
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'logs', 'temp_obfuscation']]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    src_path = Path(root) / file
                    rel_path = src_path.relative_to(self.source_dir)
                    dst_path = temp_dir / rel_path
                    
                    # Criar diretórios necessários
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copiar ficheiro
                    shutil.copy2(src_path, dst_path)
                    python_files.append(str(rel_path))
        
        logger.info(f"✅ {len(python_files)} ficheiros Python preparados")
        return temp_dir, python_files
    
    def obfuscate_code(self):
        """Obfuscar código Python"""
        logger.info("🔒 Iniciando obfuscação do código...")
        
        # Verificar dependências
        if not self.check_dependencies():
            return False
        
        # Preparar fonte
        temp_dir, python_files = self.prepare_source()
        
        try:
            # Configurar PyArmor
            cmd_init = [
                sys.executable, "-m", "pyarmor",
                "init", "--src", str(temp_dir), "--entry", "main.py"
            ]
            
            logger.info("Inicializando PyArmor...")
            result = subprocess.run(cmd_init, cwd=temp_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Erro na inicialização: {result.stderr}")
                return False
            
            # Obfuscar código
            cmd_build = [
                sys.executable, "-m", "pyarmor",
                "build", "--output", str(self.output_dir),
                "--recursive", "--clean"
            ]
            
            logger.info("Obfuscando código...")
            result = subprocess.run(cmd_build, cwd=temp_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Código obfuscado com sucesso!")
                
                # Limpar diretório temporário
                shutil.rmtree(temp_dir)
                return True
            else:
                logger.error(f"Erro na obfuscação: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro durante obfuscação: {e}")
            return False
    
    def create_deployment_package(self):
        """Criar pacote de deployment com código obfuscado"""
        logger.info("📦 Criando pacote de deployment...")
        
        # Copiar ficheiros não-Python necessários
        non_python_items = [
            ("app/templates", "app/templates"),
            ("app/static", "app/static"),
            ("migrations", "migrations"),
            ("alembic", "alembic"),
            (".env.example", ".env.example"),
            ("alembic.ini", "alembic.ini"),
            ("deploy.ini", "deploy.ini"),
            ("requirements.txt", "requirements.txt"),
            ("README.md", "README.md"),
            ("LICENSE", "LICENSE")
        ]
        
        for src_rel, dst_rel in non_python_items:
            src_path = self.source_dir / src_rel
            dst_path = self.output_dir / dst_rel
            
            if src_path.exists():
                if src_path.is_dir():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                logger.info(f"✅ Copiado: {src_rel}")
        
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
echo Iniciando AMA MESSAGE (Versão Protegida)...
echo.
python main.py
pause
'''
            script_file = self.output_dir / "iniciar.bat"
        else:  # Linux/Mac
            script_content = '''#!/bin/bash
echo "Iniciando AMA MESSAGE (Versão Protegida)..."
echo
python3 main.py
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
        docs_content = f'''# AMA MESSAGE - Versão Protegida

**Data de Obfuscação:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Versão:** Código Obfuscado

## ⚠️ AVISO IMPORTANTE:

Este software contém código protegido por obfuscação.
- **Engenharia reversa é PROIBIDA**
- **Redistribuição não autorizada é ILEGAL**
- **Modificação do código resultará em mau funcionamento**

## Como Usar:

### Requisitos:
- Python 3.12+
- pip install -r requirements.txt

### Windows:
1. Execute: `iniciar.bat`
2. Ou execute diretamente: `python main.py`

### Linux/Mac:
1. Execute: `./iniciar.sh`
2. Ou execute diretamente: `python3 main.py`

## Configuração:

1. Copie `.env.example` para `.env`
2. Configure suas credenciais no ficheiro `.env`
3. Execute: `python main.py`

## Acesso:

- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Licença e Proteção:

Esta versão utiliza tecnologia de proteção de código.
O código fonte está obfuscado para proteger a propriedade intelectual.

**© 2025 - Todos os direitos reservados**

Para suporte técnico, contacte o desenvolvedor original.
'''
        
        docs_file = self.output_dir / "LEIA-ME.md"
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        
        logger.info("✅ Documentação criada: LEIA-ME.md")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Obfuscar código AMA MESSAGE")
    parser.add_argument("--source", default=".", help="Diretório fonte")
    parser.add_argument("--output", help="Diretório de saída")
    
    args = parser.parse_args()
    
    obfuscator = CodeObfuscator(args.source, args.output)
    
    logger.info("🔒 Iniciando obfuscação do AMA MESSAGE")
    
    if obfuscator.obfuscate_code():
        package_dir = obfuscator.create_deployment_package()
        
        print("\n" + "="*50)
        print("🔒 CÓDIGO OBFUSCADO COM SUCESSO!")
        print("="*50)
        print(f"📁 Localização: {package_dir}")
        print(f"🔒 Código fonte: OBFUSCADO")
        print(f"⚡ Funcionalidade: PRESERVADA")
        print(f"🛡️ Proteção: ALTA")
        print("\n💡 Para distribuir:")
        print(f"   - Comprima a pasta: {package_dir}")
        print(f"   - Envie para os clientes")
        print(f"   - Clientes precisam do Python instalado")
        print(f"   - Executam: python main.py")
        print("="*50)
    else:
        logger.error("❌ Falha na obfuscação")
        sys.exit(1)


if __name__ == "__main__":
    main()
