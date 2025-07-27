#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Script para Preparar Ficheiros de Deploy
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeployFileManager:
    def __init__(self, source_dir: str = None):
        self.source_dir = Path(source_dir or os.getcwd())
        
        # Ficheiros obrigatórios por categoria
        self.essential_files = {
            "core": [
                "main.py",
                "requirements.txt",
                ".env.example",
                "alembic.ini",
                "deploy.ini",
                "init_db.py",
                "run_migration.py",
                "deploy.py"
            ],
            "application": [
                "app/",
                "migrations/",
                "alembic/"
            ],
            "documentation": [
                "README.md",
                "LICENSE",
                "docs/",
                ".github/copilot-instructions.md"
            ],
            "scripts": [
                "scripts/"
            ]
        }
        
        # Ficheiros para produção adicional
        self.production_files = [
            "iniciar_producao.py",
            "verificar_sistema.py"
        ]
        
        # Ficheiros para Docker adicional
        self.docker_files = [
            "start_server.py"
        ]
        
        # Ficheiros a excluir sempre
        self.exclude_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.log",
            "logs/",
            ".git/",
            ".vscode/",
            ".idea/",
            "amamessage.db",
            "*.db-journal",
            ".env",
            "test_*.py",
            "*_test.py",
            "debug_*.py",
            "quick_*.py",
            "diagnose_*.py",
            "fix_*.py",
            "configure_*.py",
            "check_*.py",
            "diag_*.py",
            "iniciar_dev.py",
            "iniciar.bat",
            "*.tmp",
            "*.temp",
            "Thumbs.db",
            ".DS_Store"
        ]
        
    def should_exclude(self, file_path: Path) -> bool:
        """Verificar se ficheiro deve ser excluído"""
        file_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if pattern.endswith('/'):
                # Diretório
                if pattern[:-1] in file_str:
                    return True
            elif '*' in pattern:
                # Padrão com wildcard
                import fnmatch
                if fnmatch.fnmatch(file_path.name, pattern):
                    return True
            else:
                # Ficheiro específico
                if file_path.name == pattern or file_str.endswith(pattern):
                    return True
                    
        return False
        
    def copy_files(self, file_list: List[str], dest_dir: Path) -> None:
        """Copiar lista de ficheiros para destino"""
        for file_path in file_list:
            source_path = self.source_dir / file_path
            dest_path = dest_dir / file_path
            
            if not source_path.exists():
                logger.warning(f"Ficheiro não encontrado: {source_path}")
                continue
                
            if self.should_exclude(source_path):
                logger.info(f"Excluído: {source_path}")
                continue
                
            # Criar diretório pai se necessário
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                self.copy_directory(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copiado: {file_path}")
                
    def copy_directory(self, source_dir: Path, dest_dir: Path) -> None:
        """Copiar diretório recursivamente, excluindo ficheiros desnecessários"""
        if dest_dir.exists():
            shutil.rmtree(dest_dir)
            
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        for item in source_dir.rglob('*'):
            if self.should_exclude(item):
                continue
                
            relative_path = item.relative_to(source_dir)
            dest_item = dest_dir / relative_path
            
            if item.is_dir():
                dest_item.mkdir(exist_ok=True)
            else:
                dest_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest_item)
                
        logger.info(f"Diretório copiado: {source_dir} -> {dest_dir}")
        
    def create_env_template(self, dest_dir: Path, deploy_type: str) -> None:
        """Criar ficheiro .env template baseado no tipo de deploy"""
        env_templates = {
            "development": {
                "DEBUG": "True",
                "LOG_LEVEL": "DEBUG",
                "DATABASE_URL": "sqlite:///amamessage.db",
                "HOST": "127.0.0.1",
                "PORT": "8000"
            },
            "production": {
                "DEBUG": "False",
                "LOG_LEVEL": "INFO",
                "DATABASE_URL": "sqlite:///data/amamessage.db",
                "HOST": "0.0.0.0",
                "PORT": "8000",
                "TWILIO_ACCOUNT_SID": "your_account_sid_here",
                "TWILIO_AUTH_TOKEN": "your_auth_token_here",
                "TWILIO_PHONE_NUMBER": "your_twilio_number_here"
            },
            "docker": {
                "DEBUG": "False",
                "LOG_LEVEL": "INFO",
                "DATABASE_URL": "sqlite:///app/data/amamessage.db",
                "HOST": "0.0.0.0",
                "PORT": "8000",
                "REDIS_URL": "redis://redis:6379/0"
            }
        }
        
        template = env_templates.get(deploy_type, env_templates["development"])
        
        env_content = [
            f"# AMA MESSAGE - Configuração {deploy_type.title()}",
            f"# Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        for key, value in template.items():
            env_content.append(f"{key}={value}")
            
        env_file = dest_dir / ".env"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_content))
            
        logger.info(f"Ficheiro .env criado: {env_file}")
        
    def generate_deploy_info(self, dest_dir: Path, deploy_type: str) -> None:
        """Gerar ficheiro com informações do deploy"""
        from datetime import datetime
        
        info_content = f"""# AMA MESSAGE - Informações do Deploy

**Tipo de Deploy:** {deploy_type.title()}
**Data/Hora:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Diretório de Origem:** {self.source_dir}
**Diretório de Destino:** {dest_dir}

## Próximos Passos:

### {deploy_type.title()}:
"""

        if deploy_type == "development":
            info_content += """
1. Configure o arquivo .env com suas credenciais
2. Execute: python deploy.py install
3. Execute: python deploy.py check
4. Execute: python deploy.py test
5. Inicie: python main.py

Acesso: http://localhost:8000
"""
        elif deploy_type == "production":
            info_content += """
1. Configure o arquivo .env com suas credenciais de produção
2. Execute como root: sudo python deploy.py production
3. Configure: sudo nano /opt/amamessage/.env
4. Inicie: sudo systemctl start amamessage
5. Ver logs: sudo journalctl -u amamessage -f

Acesso: http://seu-servidor
"""
        elif deploy_type == "docker":
            info_content += """
1. Configure o arquivo .env com suas credenciais
2. Execute: python deploy.py docker
3. Execute: python deploy.py docker-build
4. Execute: python deploy.py docker-start
5. Ver logs: docker-compose logs -f

Acesso: http://localhost
"""

        info_content += f"""
## Ficheiros Incluídos:

Total de ficheiros copiados: {sum(1 for _ in dest_dir.rglob('*') if _.is_file())}
Tamanho total: {self.get_directory_size(dest_dir):.2f} MB

## Suporte:

- Documentação: README.md
- Scripts: deploy.py help
- Logs: verificar ficheiros .log
- Testes: python deploy.py test
"""

        info_file = dest_dir / "DEPLOY_INFO.md"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_content)
            
        logger.info(f"Informações do deploy criadas: {info_file}")
        
    def get_directory_size(self, directory: Path) -> float:
        """Calcular tamanho do diretório em MB"""
        total_size = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)  # Convert to MB
        
    def prepare_development(self, dest_dir: str) -> None:
        """Preparar ficheiros para desenvolvimento"""
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Preparando ficheiros para desenvolvimento...")
        
        # Copiar ficheiros essenciais
        all_files = []
        for category, files in self.essential_files.items():
            all_files.extend(files)
            
        self.copy_files(all_files, dest_path)
        self.create_env_template(dest_path, "development")
        self.generate_deploy_info(dest_path, "development")
        
        logger.info(f"Deploy de desenvolvimento preparado em: {dest_path}")
        
    def prepare_production(self, dest_dir: str) -> None:
        """Preparar ficheiros para produção"""
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Preparando ficheiros para produção...")
        
        # Copiar ficheiros essenciais + produção
        all_files = []
        for category, files in self.essential_files.items():
            all_files.extend(files)
        all_files.extend(self.production_files)
        
        self.copy_files(all_files, dest_path)
        self.create_env_template(dest_path, "production")
        self.generate_deploy_info(dest_path, "production")
        
        logger.info(f"Deploy de produção preparado em: {dest_path}")
        
    def prepare_docker(self, dest_dir: str) -> None:
        """Preparar ficheiros para Docker"""
        dest_path = Path(dest_dir)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Preparando ficheiros para Docker...")
        
        # Copiar ficheiros essenciais + Docker
        all_files = []
        for category, files in self.essential_files.items():
            all_files.extend(files)
        all_files.extend(self.docker_files)
        
        self.copy_files(all_files, dest_path)
        self.create_env_template(dest_path, "docker")
        self.generate_deploy_info(dest_path, "docker")
        
        logger.info(f"Deploy Docker preparado em: {dest_path}")
        
    def list_files(self, deploy_type: str = "all") -> None:
        """Listar ficheiros que seriam incluídos no deploy"""
        logger.info(f"Ficheiros para deploy ({deploy_type}):")
        
        all_files = []
        for category, files in self.essential_files.items():
            logger.info(f"\n{category.upper()}:")
            for file_path in files:
                source_path = self.source_dir / file_path
                if source_path.exists():
                    if source_path.is_dir():
                        size = self.get_directory_size(source_path)
                        logger.info(f"  📁 {file_path}/ ({size:.2f} MB)")
                    else:
                        size = source_path.stat().st_size / 1024  # KB
                        logger.info(f"  📄 {file_path} ({size:.1f} KB)")
                    all_files.append(file_path)
                else:
                    logger.warning(f"  ❌ {file_path} (não encontrado)")
                    
        # Ficheiros adicionais baseado no tipo
        if deploy_type in ["production", "all"]:
            logger.info(f"\nPRODUÇÃO ADICIONAL:")
            for file_path in self.production_files:
                source_path = self.source_dir / file_path
                if source_path.exists():
                    size = source_path.stat().st_size / 1024
                    logger.info(f"  📄 {file_path} ({size:.1f} KB)")
                    
        if deploy_type in ["docker", "all"]:
            logger.info(f"\nDOCKER ADICIONAL:")
            for file_path in self.docker_files:
                source_path = self.source_dir / file_path
                if source_path.exists():
                    size = source_path.stat().st_size / 1024
                    logger.info(f"  📄 {file_path} ({size:.1f} KB)")
                    
        logger.info(f"\nTotal de ficheiros base: {len(all_files)}")

def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Preparar ficheiros para deploy do AMA MESSAGE")
    parser.add_argument('command', choices=['development', 'production', 'docker', 'list'],
                       help='Tipo de deploy a preparar')
    parser.add_argument('--dest', default=None,
                       help='Diretório de destino (default: amamessage_deploy_TYPE)')
    parser.add_argument('--source', default=None,
                       help='Diretório de origem (default: atual)')
    
    args = parser.parse_args()
    
    # Determinar diretório de destino
    if args.dest is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.dest = f"amamessage_deploy_{args.command}_{timestamp}"
    
    manager = DeployFileManager(args.source)
    
    try:
        if args.command == 'list':
            manager.list_files("all")
        elif args.command == 'development':
            manager.prepare_development(args.dest)
        elif args.command == 'production':
            manager.prepare_production(args.dest)
        elif args.command == 'docker':
            manager.prepare_docker(args.dest)
            
        if args.command != 'list':
            print(f"\n✅ Deploy preparado com sucesso!")
            print(f"📁 Diretório: {args.dest}")
            print(f"📋 Consulte DEPLOY_INFO.md para próximos passos")
            
    except Exception as e:
        logger.error(f"Erro ao preparar deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
