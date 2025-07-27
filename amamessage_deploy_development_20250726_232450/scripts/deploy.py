#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Script de Deploy para Producao
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path

# Configuracao de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    def __init__(self, deploy_path="/opt/amamessage"):
        self.deploy_path = Path(deploy_path)
        self.project_root = Path(__file__).parent.parent
        self.service_name = "amamessage"
        
    def check_requirements(self):
        """Verificar requisitos do sistema"""
        logger.info("Verificando requisitos do sistema...")
        
        # Verificar se eh root
        if os.geteuid() != 0:
            logger.error("Este script deve ser executado como root (sudo)")
            sys.exit(1)
            
        # Verificar Python
        try:
            result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
            logger.info(f"Python encontrado: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("Python 3 nao encontrado. Instale primeiro.")
            sys.exit(1)
            
        # Verificar systemd
        if not Path("/etc/systemd/system").exists():
            logger.error("systemd nao encontrado. Sistema nao suportado.")
            sys.exit(1)
            
    def create_user(self):
        """Criar usuario do sistema"""
        logger.info("Criando usuario do sistema...")
        
        try:
            subprocess.run([
                "useradd", "--system", "--home", str(self.deploy_path),
                "--shell", "/bin/false", self.service_name
            ], check=True)
            logger.info(f"Usuario {self.service_name} criado")
        except subprocess.CalledProcessError:
            logger.info(f"Usuario {self.service_name} ja existe")
            
    def setup_directories(self):
        """Configurar diretorios"""
        logger.info("Configurando diretorios...")
        
        # Criar diretorio de deploy
        self.deploy_path.mkdir(parents=True, exist_ok=True)
        
        # Copiar arquivos do projeto
        logger.info("Copiando arquivos do projeto...")
        
        exclude_patterns = {
            '__pycache__', '.git', '.vscode', '.env', 'venv',
            '*.pyc', '*.pyo', '*.log', 'amamessage.db'
        }
        
        for item in self.project_root.iterdir():
            if item.name not in exclude_patterns:
                dest = self.deploy_path / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
                    
        # Criar diretorios necessarios
        (self.deploy_path / "logs").mkdir(exist_ok=True)
        (self.deploy_path / "data").mkdir(exist_ok=True)
        
        # Configurar permissoes
        shutil.chown(self.deploy_path, user=self.service_name, group=self.service_name)
        for root, dirs, files in os.walk(self.deploy_path):
            for d in dirs:
                shutil.chown(os.path.join(root, d), user=self.service_name, group=self.service_name)
            for f in files:
                shutil.chown(os.path.join(root, f), user=self.service_name, group=self.service_name)
                
    def setup_python_environment(self):
        """Configurar ambiente Python"""
        logger.info("Configurando ambiente Python...")
        
        venv_path = self.deploy_path / "venv"
        
        # Criar ambiente virtual
        subprocess.run([
            "python3", "-m", "venv", str(venv_path)
        ], check=True, cwd=self.deploy_path)
        
        # Instalar dependencias
        pip_path = venv_path / "bin" / "pip"
        subprocess.run([
            str(pip_path), "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(pip_path), "install", "-r", "requirements.txt"
        ], check=True, cwd=self.deploy_path)
        
        # Configurar permissoes do venv
        for root, dirs, files in os.walk(venv_path):
            for d in dirs:
                shutil.chown(os.path.join(root, d), user=self.service_name, group=self.service_name)
            for f in files:
                shutil.chown(os.path.join(root, f), user=self.service_name, group=self.service_name)
                
    def setup_configuration(self):
        """Configurar ambiente de producao"""
        logger.info("Configurando ambiente de producao...")
        
        # Criar arquivo .env de producao
        env_file = self.deploy_path / ".env"
        if not env_file.exists():
            env_example = self.deploy_path / ".env.example"
            if env_example.exists():
                shutil.copy2(env_example, env_file)
                
        # Configuracoes especificas de producao
        env_content = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.readlines()
                
        # Adicionar/atualizar configuracoes de producao
        production_config = {
            "DEBUG": "False",
            "LOG_LEVEL": "INFO",
            "DATABASE_URL": f"sqlite:///{self.deploy_path}/data/amamessage.db",
            "LOG_FILE": f"{self.deploy_path}/logs/amamessage.log"
        }
        
        for key, value in production_config.items():
            found = False
            for i, line in enumerate(env_content):
                if line.startswith(f"{key}="):
                    env_content[i] = f"{key}={value}\n"
                    found = True
                    break
            if not found:
                env_content.append(f"{key}={value}\n")
                
        with open(env_file, 'w') as f:
            f.writelines(env_content)
            
        shutil.chown(env_file, user=self.service_name, group=self.service_name)
        os.chmod(env_file, 0o600)  # Apenas owner pode ler
        
    def setup_database(self):
        """Inicializar base de dados"""
        logger.info("Inicializando base de dados...")
        
        python_path = self.deploy_path / "venv" / "bin" / "python"
        
        # Inicializar BD
        subprocess.run([
            str(python_path), "init_db.py"
        ], check=True, cwd=self.deploy_path)
        
        # Executar migracoes
        subprocess.run([
            str(python_path), "run_migration.py"
        ], check=True, cwd=self.deploy_path)
        
    def create_systemd_service(self):
        """Criar servico systemd"""
        logger.info("Criando servico systemd...")
        
        service_content = f"""[Unit]
Description=AMA MESSAGE - Sistema de SMS
After=network.target
Wants=network.target

[Service]
Type=simple
User={self.service_name}
Group={self.service_name}
WorkingDirectory={self.deploy_path}
Environment=PATH={self.deploy_path}/venv/bin
ExecStart={self.deploy_path}/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/etc/systemd/system/{self.service_name}.service")
        with open(service_file, 'w') as f:
            f.write(service_content)
            
        # Recarregar systemd
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", self.service_name], check=True)
        
    def setup_nginx(self):
        """Configurar Nginx (opcional)"""
        logger.info("Configurando Nginx...")
        
        nginx_config = f"""server {{
    listen 80;
    server_name localhost;
    
    client_max_body_size 10M;
    
    # API routes
    location /api/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Admin routes
    location /admin/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Webhook routes
    location /webhook/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Static files
    location /static/ {{
        proxy_pass http://127.0.0.1:8000;
    }}
    
    # Default route
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        
        nginx_available = Path(f"/etc/nginx/sites-available/{self.service_name}")
        nginx_enabled = Path(f"/etc/nginx/sites-enabled/{self.service_name}")
        
        if Path("/etc/nginx").exists():
            with open(nginx_available, 'w') as f:
                f.write(nginx_config)
                
            if not nginx_enabled.exists():
                nginx_enabled.symlink_to(nginx_available)
                
            try:
                subprocess.run(["nginx", "-t"], check=True)
                subprocess.run(["systemctl", "reload", "nginx"], check=True)
                logger.info("Nginx configurado com sucesso")
            except subprocess.CalledProcessError:
                logger.warning("Erro ao configurar Nginx. Configure manualmente se necessario.")
        else:
            logger.info("Nginx nao encontrado. Pulando configuracao.")
            
    def deploy(self):
        """Executar deploy completo"""
        try:
            self.check_requirements()
            self.create_user()
            self.setup_directories()
            self.setup_python_environment()
            self.setup_configuration()
            self.setup_database()
            self.create_systemd_service()
            self.setup_nginx()
            
            logger.info("Deploy concluido com sucesso!")
            logger.info(f"Servico instalado em: {self.deploy_path}")
            logger.info(f"Para iniciar: sudo systemctl start {self.service_name}")
            logger.info(f"Para ver logs: sudo journalctl -u {self.service_name} -f")
            logger.info("IMPORTANTE: Configure o arquivo .env antes de iniciar o servico!")
            
        except Exception as e:
            logger.error(f"Erro durante deploy: {e}")
            sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy AMA MESSAGE para producao")
    parser.add_argument("--path", default="/opt/amamessage", 
                       help="Caminho para instalacao (default: /opt/amamessage)")
    
    args = parser.parse_args()
    
    deployer = ProductionDeployer(args.path)
    deployer.deploy()
