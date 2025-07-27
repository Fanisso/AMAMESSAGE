#!/usr/bin/env python3
"""
Script para criar deployment SaaS do AMA MESSAGE
Cliente acede via web, código fica no servidor
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

class SaaSDeployer:
    """Cria deployment para modelo SaaS (Software as a Service)"""
    
    def __init__(self, source_dir: str, output_dir: str = None):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(f"amamessage_saas_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def create_docker_setup(self):
        """Criar configuração Docker para SaaS"""
        logger.info("🐳 Criando configuração Docker SaaS...")
        
        # Dockerfile otimizado para produção
        dockerfile_content = '''FROM python:3.12-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para dados
RUN mkdir -p /app/data /app/logs

# Criar usuário não-root
RUN useradd -m -u 1000 amamessage && \\
    chown -R amamessage:amamessage /app
USER amamessage

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "main.py"]
'''
        
        dockerfile_path = self.output_dir / "Dockerfile"
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # Docker Compose para ambiente completo
        compose_content = '''version: '3.8'

services:
  amamessage:
    build: .
    container_name: amamessage_app
    restart: unless-stopped
    ports:
      - "8000:8000"
      - "8001:8001"  # WebSocket para agentes de modem
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - DATABASE_URL=sqlite:///data/amamessage.db
      - HOST=0.0.0.0
      - PORT=8000
      - WS_PORT=8001
      - SAAS_MODE=True
      - ENABLE_REMOTE_MODEMS=True
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    networks:
      - amamessage_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: amamessage_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - amamessage
    networks:
      - amamessage_network

  redis:
    image: redis:alpine
    container_name: amamessage_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - amamessage_network

networks:
  amamessage_network:
    driver: bridge

volumes:
  redis_data:
'''
        
        compose_path = self.output_dir / "docker-compose.yml"
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(compose_content)
        
        logger.info("✅ Configuração Docker criada")
    
    def create_nginx_config(self):
        """Criar configuração Nginx para proxy reverso"""
        nginx_content = '''events {
    worker_connections 1024;
}

http {
    upstream amamessage_backend {
        server amamessage:8000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        listen 80;
        server_name _;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        # Proxy para aplicação
        location / {
            proxy_pass http://amamessage_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Static files
        location /static/ {
            proxy_pass http://amamessage_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # Health check endpoint
        location /health {
            proxy_pass http://amamessage_backend;
            access_log off;
        }
    }
}
'''
        
        nginx_path = self.output_dir / "nginx.conf"
        with open(nginx_path, 'w', encoding='utf-8') as f:
            f.write(nginx_content)
        
        logger.info("✅ Configuração Nginx criada")
    
    def create_client_dashboard(self):
        """Criar dashboard personalizado para cliente"""
        logger.info("🎨 Criando dashboard personalizado...")
        
        # Modificar template base para remover informações técnicas
        client_base_template = '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AMA MESSAGE{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', path='/css/style.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-sms me-2"></i>AMA MESSAGE
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/sms">SMS</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/forwarding-rules">Regras</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/admin/contacts">Contactos</a>
                    </li>
                </ul>
                <span class="navbar-text">
                    Versão SaaS - Serviço Gerido
                </span>
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Remover informações técnicas do footer -->
    <footer class="bg-light mt-5 py-3">
        <div class="container text-center">
            <p class="mb-0">&copy; 2025 AMA MESSAGE - Serviço de SMS Profissional</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', path='/js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>'''
        
        # Criar diretório de templates customizados
        client_templates_dir = self.output_dir / "client_templates"
        client_templates_dir.mkdir(exist_ok=True)
        
        with open(client_templates_dir / "base.html", 'w', encoding='utf-8') as f:
            f.write(client_base_template)
    
    def create_deployment_package(self):
        """Criar pacote completo SaaS"""
        logger.info("📦 Criando pacote SaaS...")
        
        # Criar diretório de output
        self.output_dir.mkdir(exist_ok=True)
        
        # Copiar código fonte (será protegido no servidor)  
        app_items = [
            "main.py",
            "requirements.txt",
            "alembic.ini",
            "deploy.ini",
            "init_db.py",
            "run_migration.py",
            "app/",
            "migrations/",
            "alembic/"
        ]
        
        for item in app_items:
            src_path = self.source_dir / item
            dst_path = self.output_dir / item
            
            if src_path.exists():
                if src_path.is_dir():
                    if dst_path.exists():
                        shutil.rmtree(dst_path)
                    shutil.copytree(src_path, dst_path)
                else:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                logger.info(f"✅ Copiado: {item}")
        
        # Criar configurações Docker
        self.create_docker_setup()
        self.create_nginx_config()
        
        # Criar dashboard personalizado
        self.create_client_dashboard()
        
        # Criar scripts de gerenciamento
        self.create_management_scripts()
        
        # Criar documentação
        self.create_saas_docs()
        
        logger.info(f"✅ Pacote SaaS criado em: {self.output_dir}")
        return self.output_dir
    
    def create_management_scripts(self):
        """Criar scripts de gerenciamento do serviço"""
        
        # Script de inicialização
        start_script = '''#!/bin/bash
echo "🚀 Iniciando AMA MESSAGE SaaS..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale o Docker Compose primeiro."
    exit 1
fi

# Criar diretórios necessários
mkdir -p data logs ssl

# Configurar .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando configuração inicial..."
    cp .env.example .env
    echo "⚠️  Configure o arquivo .env antes de continuar"
    exit 1
fi

# Iniciar serviços
echo "🐳 Iniciando containers..."
docker-compose up -d

echo "✅ AMA MESSAGE SaaS iniciado!"
echo "🌐 Acesso: https://localhost"
echo "📊 Logs: docker-compose logs -f"
'''
        
        with open(self.output_dir / "start.sh", 'w', encoding='utf-8') as f:
            f.write(start_script)
        os.chmod(self.output_dir / "start.sh", 0o755)
        
        # Script de parar
        stop_script = '''#!/bin/bash
echo "🛑 Parando AMA MESSAGE SaaS..."
docker-compose down
echo "✅ Serviços parados"
'''
        
        with open(self.output_dir / "stop.sh", 'w', encoding='utf-8') as f:
            f.write(stop_script)
        os.chmod(self.output_dir / "stop.sh", 0o755)
    
    def create_saas_docs(self):
        """Criar documentação SaaS"""
        docs_content = f'''# AMA MESSAGE - Versão SaaS

**Data de Criação:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Modelo:** Software as a Service (SaaS)

## 🛡️ PROTEÇÃO DE CÓDIGO:

- **Código fonte**: Permanece no SERVIDOR
- **Cliente acede**: Apenas via interface web
- **Sem acesso**: A ficheiros de código
- **Proteção máxima**: Propriedade intelectual

## 🚀 Como Configurar:

### Requisitos do Servidor:
- Docker + Docker Compose
- Certificado SSL
- Domínio configurado

### Instalação:
```bash
# 1. Configurar ambiente
cp .env.example .env
# Edite .env com suas configurações

# 2. Iniciar serviço
./start.sh

# 3. Verificar status
docker-compose ps
```

## 🌐 Acesso do Cliente:

- **URL**: https://seudominio.com
- **Dashboard**: Interface web completa
- **Sem instalação**: Cliente usa apenas browser
- **Sempre atualizado**: Atualizações automáticas

## 🔧 Gerenciamento:

```bash
# Iniciar serviços
./start.sh

# Parar serviços  
./stop.sh

# Ver logs
docker-compose logs -f

# Atualizar
docker-compose pull && docker-compose up -d
```

## 💰 Vantagens do Modelo SaaS:

### Para o Desenvolvedor:
- ✅ Código 100% protegido
- ✅ Controle total sobre atualizações
- ✅ Modelo de receita recorrente
- ✅ Suporte centralizado

### Para o Cliente:
- ✅ Sem instalação complexa
- ✅ Atualizações automáticas
- ✅ Acesso de qualquer lugar
- ✅ Suporte técnico incluído

## 🔒 Segurança:

- HTTPS obrigatório (SSL/TLS)
- Rate limiting configurado
- Headers de segurança
- Isolamento por container
- Backups automáticos

## 📞 Suporte:

Como este é um serviço gerido:
- Suporte técnico incluído
- Monitoramento 24/7
- Backups automáticos
- Atualizações de segurança

**© 2025 - Serviço SaaS Protegido**
'''
        
        with open(self.output_dir / "README_SAAS.md", 'w', encoding='utf-8') as f:
            f.write(docs_content)
        
        # Criar .env.example para SaaS
        env_example = '''# AMA MESSAGE - Configuração SaaS
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/amamessage.db
HOST=0.0.0.0  
PORT=8000

# Configurações de SMS (obrigatório)
TWILIO_ACCOUNT_SID=seu_account_sid_aqui
TWILIO_AUTH_TOKEN=seu_auth_token_aqui
TWILIO_PHONE_NUMBER=seu_numero_twilio

# Configurações de segurança
SECRET_KEY=sua_chave_secreta_muito_forte_aqui
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Redis para cache
REDIS_URL=redis://redis:6379/0

# Configurações de email para alertas
ALERT_EMAIL_SMTP=smtp.seuservidor.com
ALERT_EMAIL_PORT=587
ALERT_EMAIL_USER=noreply@seudominio.com
ALERT_EMAIL_PASSWORD=sua_senha_email
ALERT_EMAIL_FROM=noreply@seudominio.com
ALERT_EMAIL_TO=admin@seudominio.com
'''
        
        with open(self.output_dir / ".env.example", 'w', encoding='utf-8') as f:
            f.write(env_example)


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Criar deployment SaaS do AMA MESSAGE")
    parser.add_argument("--source", default=".", help="Diretório fonte")
    parser.add_argument("--output", help="Diretório de saída")
    
    args = parser.parse_args()
    
    deployer = SaaSDeployer(args.source, args.output)
    
    logger.info("☁️ Iniciando criação de deployment SaaS")
    
    package_dir = deployer.create_deployment_package()
    
    print("\n" + "="*60)
    print("☁️  DEPLOYMENT SAAS CRIADO COM SUCESSO!")
    print("="*60)
    print(f"📁 Localização: {package_dir}")
    print(f"🛡️ Proteção: MÁXIMA (código no servidor)")
    print(f"🌐 Acesso cliente: Via web browser")
    print(f"💰 Modelo: SaaS (receita recorrente)")
    print("\n💡 Próximos passos:")
    print(f"   1. Configure o servidor com Docker")
    print(f"   2. Configure SSL/HTTPS")
    print(f"   3. Configure .env")
    print(f"   4. Execute: ./start.sh")
    print(f"   5. Cliente acede: https://seudominio.com")
    print("="*60)


if __name__ == "__main__":
    main()
