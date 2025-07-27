#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Script de Deploy para Docker
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def check_docker(self):
        """Verificar se Docker esta instalado"""
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
            logger.info("Docker e Docker Compose encontrados")
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("Docker ou Docker Compose nao encontrados")
            logger.info("Instale Docker: https://docs.docker.com/get-docker/")
            sys.exit(1)
            
    def create_dockerfile(self):
        """Criar Dockerfile"""
        dockerfile_content = """FROM python:3.11-slim

# Instalar dependencias do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Criar usuario nao-root
RUN useradd --create-home --shell /bin/bash amamessage

# Definir diretorio de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar codigo da aplicacao
COPY . .

# Criar diretorios necessarios
RUN mkdir -p /app/logs /app/data

# Configurar permissoes
RUN chown -R amamessage:amamessage /app

# Mudar para usuario nao-root
USER amamessage

# Expor porta
EXPOSE 8000

# Comando padrao
CMD ["python", "main.py"]
"""
        
        dockerfile_path = self.project_root / "Dockerfile"
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        logger.info("Dockerfile criado")
        
    def create_docker_compose(self):
        """Criar docker-compose.yml"""
        compose_content = """version: '3.8'

services:
  amamessage:
    build: .
    container_name: amamessage
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///app/data/amamessage.db
      - LOG_FILE=/app/logs/amamessage.log
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    depends_on:
      - redis
    networks:
      - amamessage_network

  redis:
    image: redis:7-alpine
    container_name: amamessage_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - amamessage_network

  nginx:
    image: nginx:alpine
    container_name: amamessage_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - amamessage
    networks:
      - amamessage_network

volumes:
  redis_data:

networks:
  amamessage_network:
    driver: bridge
"""
        
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, 'w') as f:
            f.write(compose_content)
        logger.info("docker-compose.yml criado")
        
    def create_nginx_config(self):
        """Criar configuracao Nginx"""
        nginx_content = """upstream amamessage {
    server amamessage:8000;
}

server {
    listen 80;
    server_name localhost;
    
    client_max_body_size 10M;
    
    # Redirect HTTP to HTTPS (opcional)
    # return 301 https://$server_name$request_uri;
    
    location / {
        proxy_pass http://amamessage;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (se necessario)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files
    location /static/ {
        proxy_pass http://amamessage;
    }
    
    # Health check
    location /health {
        proxy_pass http://amamessage;
    }
}

# Configuracao HTTPS (descomente se tiver SSL)
# server {
#     listen 443 ssl http2;
#     server_name localhost;
#     
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#     
#     client_max_body_size 10M;
#     
#     location / {
#         proxy_pass http://amamessage;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header X-Forwarded-Proto $scheme;
#         
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade $http_upgrade;
#         proxy_set_header Connection "upgrade";
#     }
# }
"""
        
        nginx_path = self.project_root / "nginx.conf"
        with open(nginx_path, 'w') as f:
            f.write(nginx_content)
        logger.info("nginx.conf criado")
        
    def create_dockerignore(self):
        """Criar .dockerignore"""
        dockerignore_content = """.git
.gitignore
.vscode
__pycache__
*.pyc
*.pyo
*.log
.env
venv/
node_modules/
.DS_Store
Thumbs.db
*.md
Dockerfile
docker-compose.yml
scripts/
amamessage.db
logs/
data/
"""
        
        dockerignore_path = self.project_root / ".dockerignore"
        with open(dockerignore_path, 'w') as f:
            f.write(dockerignore_content)
        logger.info(".dockerignore criado")
        
    def create_env_docker(self):
        """Criar .env para Docker"""
        env_docker_content = """# AMA MESSAGE - Configuracao Docker
DEBUG=False
LOG_LEVEL=INFO

# Base de Dados
DATABASE_URL=sqlite:///app/data/amamessage.db

# Logs
LOG_FILE=/app/logs/amamessage.log

# Redis (para filas - opcional)
REDIS_URL=redis://redis:6379/0

# Twilio (configure com suas credenciais)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_number_here

# Modem (se usando modem fisico)
MODEM_PORT=/dev/ttyUSB0
MODEM_BAUDRATE=115200

# Alertas
ALERT_EMAIL_SMTP=smtp.gmail.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=your_email@gmail.com
ALERT_EMAIL_PASSWORD=your_app_password
ALERT_EMAIL_FROM=your_email@gmail.com
ALERT_EMAIL_TO=admin@yourcompany.com

# Webhook (opcional)
ALERT_WEBHOOK_URL=https://hooks.slack.com/your/webhook/url

# Servidor
HOST=0.0.0.0
PORT=8000
"""
        
        env_docker_path = self.project_root / ".env.docker"
        with open(env_docker_path, 'w') as f:
            f.write(env_docker_content)
        logger.info(".env.docker criado")
        
    def create_scripts(self):
        """Criar scripts de gerenciamento Docker"""
        
        # Script de build
        build_script = """#!/bin/bash
echo "Building AMA MESSAGE Docker images..."
docker-compose build --no-cache
echo "Build completed!"
"""
        
        build_path = self.project_root / "scripts" / "docker-build.sh"
        with open(build_path, 'w') as f:
            f.write(build_script)
        os.chmod(build_path, 0o755)
        
        # Script de start
        start_script = """#!/bin/bash
echo "Starting AMA MESSAGE services..."
docker-compose up -d
echo "Services started!"
echo "Access: http://localhost"
echo "View logs: docker-compose logs -f"
"""
        
        start_path = self.project_root / "scripts" / "docker-start.sh"
        with open(start_path, 'w') as f:
            f.write(start_script)
        os.chmod(start_path, 0o755)
        
        # Script de stop
        stop_script = """#!/bin/bash
echo "Stopping AMA MESSAGE services..."
docker-compose down
echo "Services stopped!"
"""
        
        stop_path = self.project_root / "scripts" / "docker-stop.sh"
        with open(stop_path, 'w') as f:
            f.write(stop_script)
        os.chmod(stop_path, 0o755)
        
        # Script de logs
        logs_script = """#!/bin/bash
echo "AMA MESSAGE logs:"
docker-compose logs -f --tail=100
"""
        
        logs_path = self.project_root / "scripts" / "docker-logs.sh"
        with open(logs_path, 'w') as f:
            f.write(logs_script)
        os.chmod(logs_path, 0o755)
        
        logger.info("Scripts Docker criados")
        
    def setup_directories(self):
        """Criar diretorios necessarios"""
        (self.project_root / "data").mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        (self.project_root / "ssl").mkdir(exist_ok=True)
        logger.info("Diretorios criados")
        
    def deploy(self):
        """Executar deploy Docker"""
        try:
            logger.info("Iniciando deploy Docker...")
            
            self.check_docker()
            self.create_dockerfile()
            self.create_docker_compose()
            self.create_nginx_config()
            self.create_dockerignore()
            self.create_env_docker()
            self.create_scripts()
            self.setup_directories()
            
            logger.info("Deploy Docker concluido!")
            logger.info("Proximos passos:")
            logger.info("1. Configure o arquivo .env.docker com suas credenciais")
            logger.info("2. Copie .env.docker para .env: cp .env.docker .env")
            logger.info("3. Build: ./scripts/docker-build.sh")
            logger.info("4. Start: ./scripts/docker-start.sh")
            logger.info("5. Access: http://localhost")
            
        except Exception as e:
            logger.error(f"Erro durante deploy Docker: {e}")
            sys.exit(1)

if __name__ == "__main__":
    deployer = DockerDeployer()
    deployer.deploy()
