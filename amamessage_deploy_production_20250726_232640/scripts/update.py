#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Atualizador do Sistema
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def backup_database(self):
        """Fazer backup da base de dados"""
        logger.info("Fazendo backup da base de dados...")
        
        db_file = self.project_root / "amamessage.db"
        if db_file.exists():
            backup_file = self.project_root / f"backup_amamessage_{int(time.time())}.db"
            import shutil, time
            shutil.copy2(db_file, backup_file)
            logger.info(f"Backup criado: {backup_file}")
        else:
            logger.info("Base de dados nao encontrada. Pulando backup.")
            
    def update_code(self):
        """Atualizar codigo do repositorio"""
        logger.info("Atualizando codigo...")
        
        try:
            # Verificar se eh um repositorio Git
            result = subprocess.run(["git", "status"], 
                                  cwd=self.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Pull das alteracoes
                subprocess.run(["git", "pull", "origin", "main"], 
                             cwd=self.project_root, check=True)
                logger.info("Codigo atualizado com sucesso")
            else:
                logger.warning("Nao eh um repositorio Git. Atualizacao manual necessaria.")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao atualizar codigo: {e}")
            
    def update_dependencies(self):
        """Atualizar dependencias"""
        logger.info("Atualizando dependencias...")
        
        venv_python = self.project_root / "venv" / ("Scripts" if os.name == 'nt' else "bin") / "python"
        
        if venv_python.exists():
            subprocess.run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], 
                         cwd=self.project_root, check=True)
            subprocess.run([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"], 
                         cwd=self.project_root, check=True)
            logger.info("Dependencias atualizadas")
        else:
            logger.error("Ambiente virtual nao encontrado")
            
    def run_migrations(self):
        """Executar migracoes"""
        logger.info("Executando migracoes...")
        
        venv_python = self.project_root / "venv" / ("Scripts" if os.name == 'nt' else "bin") / "python"
        
        if venv_python.exists():
            try:
                subprocess.run([str(venv_python), "run_migration.py"], 
                             cwd=self.project_root, check=True)
                logger.info("Migracoes executadas")
            except subprocess.CalledProcessError:
                logger.warning("Erro nas migracoes ou nenhuma migracao necessaria")
        else:
            logger.error("Ambiente virtual nao encontrado")
            
    def restart_service(self, service_name="amamessage"):
        """Reiniciar servico (se estiver rodando como servico)"""
        logger.info("Tentando reiniciar servico...")
        
        try:
            # Verificar se eh um servico systemd
            result = subprocess.run(["systemctl", "is-active", service_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
                logger.info(f"Servico {service_name} reiniciado")
            else:
                logger.info("Servico nao encontrado ou nao ativo")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("systemctl nao disponivel ou erro ao reiniciar")
            
    def update(self, skip_backup=False, skip_restart=False):
        """Executar atualizacao completa"""
        try:
            logger.info("Iniciando atualizacao do sistema...")
            
            if not skip_backup:
                self.backup_database()
                
            self.update_code()
            self.update_dependencies()
            self.run_migrations()
            
            if not skip_restart:
                self.restart_service()
                
            logger.info("Atualizacao concluida com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante atualizacao: {e}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Atualizar sistema AMA MESSAGE")
    parser.add_argument("--skip-backup", action="store_true", 
                       help="Pular backup da base de dados")
    parser.add_argument("--skip-restart", action="store_true", 
                       help="Pular reinicio do servico")
    
    args = parser.parse_args()
    
    updater = SystemUpdater()
    updater.update(skip_backup=args.skip_backup, skip_restart=args.skip_restart)
