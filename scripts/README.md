# Scripts de Deploy e Instalação - AMA MESSAGE

Este diretório contém scripts para instalação, deploy e manutenção do sistema AMA MESSAGE.

## 📋 Índice

- [Instalação Local](#instalação-local)
- [Deploy em Produção](#deploy-em-produção)
- [Deploy com Docker](#deploy-com-docker)
- [Manutenção](#manutenção)
- [Estrutura dos Scripts](#estrutura-dos-scripts)

## 🚀 Instalação Local

### Windows

```batch
# Executar como Administrador
scripts\install.bat
```

### Linux/Mac

```bash
# Dar permissão e executar
chmod +x scripts/install.sh
./scripts/install.sh
```

### O que faz:
- ✅ Verifica Python 3.8+ e Git
- ✅ Cria ambiente virtual
- ✅ Instala dependências
- ✅ Cria arquivo `.env`
- ✅ Inicializa base de dados
- ✅ Executa migrações

## 🏭 Deploy em Produção

### Linux (Ubuntu/CentOS/Debian)

```bash
# Executar como root (sudo)
sudo python3 scripts/deploy.py

# Ou com caminho personalizado
sudo python3 scripts/deploy.py --path /opt/amamessage
```

### O que faz:
- ✅ Cria usuário do sistema
- ✅ Configura diretórios com permissões corretas
- ✅ Instala ambiente Python isolado
- ✅ Configura variáveis de produção
- ✅ Cria serviço systemd
- ✅ Configura Nginx (se disponível)
- ✅ Inicializa base de dados

### Após o deploy:
```bash
# Configurar .env
sudo nano /opt/amamessage/.env

# Iniciar serviço
sudo systemctl start amamessage

# Ver logs
sudo journalctl -u amamessage -f

# Habilitar inicialização automática
sudo systemctl enable amamessage
```

## 🐳 Deploy com Docker

### Preparação

```bash
# Executar script de deploy Docker
python3 scripts/deploy_docker.py
```

### Configuração

```bash
# Copiar e configurar variáveis
cp .env.docker .env
nano .env

# Configurar credenciais Twilio, email, etc.
```

### Execução

```bash
# Build das imagens
./scripts/docker-build.sh

# Iniciar serviços
./scripts/docker-start.sh

# Ver logs
./scripts/docker-logs.sh

# Parar serviços
./scripts/docker-stop.sh
```

### Serviços incluídos:
- **amamessage**: Aplicação principal
- **redis**: Cache e filas
- **nginx**: Proxy reverso
- **volumes**: Dados persistentes

### Acesso:
- **Web**: http://localhost
- **API**: http://localhost/api
- **Admin**: http://localhost/admin

## 🔧 Manutenção

### Verificação do Sistema

**Windows:**
```batch
scripts\check_system.bat
```

**Linux/Mac:**
```bash
./scripts/check_system.sh
```

### Atualização do Sistema

```bash
# Atualização completa (recomendado)
python3 scripts/update.py

# Pular backup da BD
python3 scripts/update.py --skip-backup

# Pular reinício do serviço
python3 scripts/update.py --skip-restart
```

### O que a atualização faz:
- ✅ Backup automático da base de dados
- ✅ Pull do código mais recente (Git)
- ✅ Atualização das dependências Python
- ✅ Execução de novas migrações
- ✅ Reinício do serviço (se aplicável)

## 📁 Estrutura dos Scripts

```
scripts/
├── install.bat              # Instalação Windows
├── install.sh               # Instalação Linux/Mac
├── deploy.py                # Deploy produção Linux
├── deploy_docker.py         # Setup Docker completo
├── check_system.bat         # Verificação Windows
├── check_system.sh          # Verificação Linux/Mac
├── update.py                # Atualizador universal
├── docker-build.sh          # Build Docker
├── docker-start.sh          # Start Docker
├── docker-stop.sh           # Stop Docker
├── docker-logs.sh           # Logs Docker
└── README.md                # Esta documentação
```

## 🔐 Configuração de Segurança

### Produção Linux

```bash
# Firewall (UFW)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# SSL/TLS (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com
```

### Docker

```bash
# SSL com Docker
mkdir ssl
# Copiar certificados para ./ssl/
# Descomentar configuração HTTPS no nginx.conf
```

## 📊 Monitorização

### Logs do Sistema

```bash
# Serviço Linux
sudo journalctl -u amamessage -f

# Docker
docker-compose logs -f

# Arquivo de log
tail -f /opt/amamessage/logs/amamessage.log
```

### Status do Serviço

```bash
# Linux
sudo systemctl status amamessage

# Docker
docker-compose ps
```

## 🆘 Resolução de Problemas

### Problemas Comuns

1. **Porta COM não encontrada (Windows)**
   ```bash
   python diagnose_modem.py
   python test_all_ports.py
   ```

2. **Permissões (Linux)**
   ```bash
   sudo chown -R amamessage:amamessage /opt/amamessage
   ```

3. **Base de dados corrompida**
   ```bash
   # Restaurar backup
   cp backup_amamessage_*.db amamessage.db
   python run_migration.py
   ```

4. **Dependências em falta**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

### Logs de Debug

Ativar modo debug no `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🔄 Processo de Atualização Recomendado

1. **Backup** - Sempre fazer backup antes de atualizar
2. **Teste** - Testar em ambiente de desenvolvimento primeiro
3. **Manutenção** - Colocar sistema em manutenção se necessário
4. **Atualização** - Executar script de atualização
5. **Verificação** - Verificar se tudo funciona corretamente
6. **Monitorização** - Acompanhar logs por algumas horas

## 📞 Suporte

Para problemas com os scripts:

1. Verificar logs detalhados
2. Consultar documentação em `docs/`
3. Verificar issues no repositório
4. Executar diagnósticos incluídos

---

**Desenvolvido para AMA MESSAGE - Sistema de SMS**  
**Versão:** 2.0  
**Compatibilidade:** Windows 10+, Ubuntu 18+, CentOS 7+, macOS 10.15+
