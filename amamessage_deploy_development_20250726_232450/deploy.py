#!/usr/bin/env python3
"""
AMA MESSAGE - Sistema de SMS
Central de Deploy e Gestão
"""

import sys
import os
import argparse
import subprocess
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeployManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.scripts_dir = self.project_root / "scripts"
        
    def install_local(self):
        """Instalação local"""
        logger.info("Executando instalação local...")
        
        if os.name == 'nt':  # Windows
            script = self.scripts_dir / "install.bat"
            subprocess.run([str(script)], shell=True)
        else:  # Linux/Mac
            script = self.scripts_dir / "install.sh"
            subprocess.run(["bash", str(script)])
            
    def deploy_production(self, path="/opt/amamessage"):
        """Deploy em produção"""
        logger.info("Executando deploy em produção...")
        
        script = self.scripts_dir / "deploy.py"
        cmd = [sys.executable, str(script)]
        if path != "/opt/amamessage":
            cmd.extend(["--path", path])
            
        subprocess.run(cmd)
        
    def deploy_docker(self):
        """Deploy com Docker"""
        logger.info("Executando deploy Docker...")
        
        script = self.scripts_dir / "deploy_docker.py"
        subprocess.run([sys.executable, str(script)])
        
    def check_system(self):
        """Verificar sistema"""
        logger.info("Verificando sistema...")
        
        if os.name == 'nt':  # Windows
            script = self.scripts_dir / "check_system.bat"
            subprocess.run([str(script)], shell=True)
        else:  # Linux/Mac
            script = self.scripts_dir / "check_system.sh"
            subprocess.run(["bash", str(script)])
            
    def test_deploy(self):
        """Testar deploy"""
        logger.info("Executando testes de deploy...")
        
        script = self.scripts_dir / "test_deploy.py"
        subprocess.run([sys.executable, str(script)])
        
    def update_system(self, skip_backup=False, skip_restart=False):
        """Atualizar sistema"""
        logger.info("Atualizando sistema...")
        
        script = self.scripts_dir / "update.py"
        cmd = [sys.executable, str(script)]
        
        if skip_backup:
            cmd.append("--skip-backup")
        if skip_restart:
            cmd.append("--skip-restart")
            
        subprocess.run(cmd)
        
    def docker_build(self):
        """Build Docker"""
        logger.info("Executando build Docker...")
        script = self.scripts_dir / "docker-build.sh"
        subprocess.run(["bash", str(script)])
        
    def docker_start(self):
        """Iniciar Docker"""
        logger.info("Iniciando serviços Docker...")
        script = self.scripts_dir / "docker-start.sh"
        subprocess.run(["bash", str(script)])
        
    def docker_stop(self):
        """Parar Docker"""
        logger.info("Parando serviços Docker...")
        script = self.scripts_dir / "docker-stop.sh"
        subprocess.run(["bash", str(script)])
        
    def docker_logs(self):
        """Ver logs Docker"""
        logger.info("Visualizando logs Docker...")
        script = self.scripts_dir / "docker-logs.sh"
        subprocess.run(["bash", str(script)])
        
    def show_status(self):
        """Mostrar status do sistema"""
        logger.info("Status do sistema AMA MESSAGE")
        
        # Verificar arquivos principais
        files_to_check = [
            (".env", "Configuração"),
            ("amamessage.db", "Base de dados"),
            ("venv", "Ambiente virtual"),
            ("requirements.txt", "Dependências")
        ]
        
        print("\n📁 Arquivos do sistema:")
        for file_name, description in files_to_check:
            file_path = self.project_root / file_name
            status = "✅" if file_path.exists() else "❌"
            print(f"  {status} {description}: {file_name}")
            
        # Verificar serviços (se Linux)
        if os.name != 'nt':
            try:
                result = subprocess.run(["systemctl", "is-active", "amamessage"], 
                                      capture_output=True, text=True)
                status = "🟢 ATIVO" if result.returncode == 0 else "🔴 INATIVO"
                print(f"\n🔧 Serviço systemd: {status}")
            except FileNotFoundError:
                print("\n🔧 Serviço systemd: Não disponível")
                
        # Verificar Docker
        try:
            result = subprocess.run(["docker-compose", "ps"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                print(f"\n🐳 Docker Compose:\n{result.stdout}")
        except FileNotFoundError:
            print("\n🐳 Docker: Não disponível")
            
    def prepare_files(self, deploy_type):
        """Preparar ficheiros para deploy"""
        logger.info(f"Preparando ficheiros para {deploy_type}...")
        
        script = self.scripts_dir / "prepare_deploy.py"
        subprocess.run([sys.executable, str(script), deploy_type])
        
    def show_help(self):
        """Mostrar ajuda detalhada"""
        help_text = """
🚀 AMA MESSAGE - Central de Deploy e Gestão

COMANDOS DISPONÍVEIS:

📦 INSTALAÇÃO E SETUP:
  install          Instalação local (Windows/Linux/Mac)
  check           Verificar sistema e dependências
  test            Testar configuração e funcionalidades
  prepare TYPE     Preparar ficheiros para deploy (development/production/docker)

🏭 DEPLOY EM PRODUÇÃO:
  production      Deploy completo em servidor Linux
  production --path /custom/path   Deploy em caminho personalizado

🐳 DEPLOY COM DOCKER:
  docker          Setup completo Docker (cria arquivos)
  docker-build    Build das imagens Docker
  docker-start    Iniciar todos os serviços
  docker-stop     Parar todos os serviços
  docker-logs     Ver logs em tempo real

🔄 MANUTENÇÃO:
  update          Atualizar sistema completo
  update --skip-backup    Atualizar sem backup
  update --skip-restart   Atualizar sem reiniciar serviço
  status          Mostrar status do sistema

📖 INFORMAÇÃO:
  help            Mostrar esta ajuda
  --version       Versão do sistema

EXEMPLOS DE USO:

  # Instalação inicial
  python deploy.py install

  # Verificar se tudo está funcionando
  python deploy.py check
  python deploy.py test

  # Preparar ficheiros
  python deploy.py prepare development
  python deploy.py prepare production
  python deploy.py prepare docker

  # Deploy em produção
  sudo python deploy.py production

  # Deploy com Docker
  python deploy.py docker
  python deploy.py docker-build
  python deploy.py docker-start

  # Atualização
  python deploy.py update

  # Ver status
  python deploy.py status

ESTRUTURA DE ARQUIVOS CRIADOS:

📁 Para produção Linux:
  /opt/amamessage/          # Aplicação
  /etc/systemd/system/      # Serviço
  /etc/nginx/sites-*/       # Nginx config

📁 Para Docker:
  Dockerfile                # Imagem da aplicação
  docker-compose.yml        # Orquestração
  nginx.conf               # Configuração proxy
  .env.docker              # Variáveis ambiente

DOCUMENTAÇÃO COMPLETA:
  docs/README.md
  scripts/README.md

SUPORTE:
  - Verificar logs em caso de erro
  - Consultar documentação completa
  - Executar diagnósticos incluídos
        """
        print(help_text)

def main():
    parser = argparse.ArgumentParser(
        description="AMA MESSAGE - Central de Deploy",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', nargs='?', 
                       help='Comando a executar (use "help" para ver todos)')
    parser.add_argument('deploy_type', nargs='?',
                       help='Tipo de deploy para comando prepare (development/production/docker)')
    parser.add_argument('--path', 
                       help='Caminho personalizado para deploy em produção')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Pular backup durante atualização')
    parser.add_argument('--skip-restart', action='store_true',
                       help='Pular reinício durante atualização')
    parser.add_argument('--version', action='version', version='AMA MESSAGE 2.0')
    
    args = parser.parse_args()
    
    if not args.command:
        print("❌ Comando necessário. Use 'python deploy.py help' para ver opções.")
        sys.exit(1)
        
    manager = DeployManager()
    
    try:
        if args.command == 'install':
            manager.install_local()
        elif args.command == 'production':
            path = args.path or "/opt/amamessage"
            manager.deploy_production(path)
        elif args.command == 'docker':
            manager.deploy_docker()
        elif args.command == 'docker-build':
            manager.docker_build()
        elif args.command == 'docker-start':
            manager.docker_start()
        elif args.command == 'docker-stop':
            manager.docker_stop()
        elif args.command == 'docker-logs':
            manager.docker_logs()
        elif args.command == 'check':
            manager.check_system()
        elif args.command == 'test':
            manager.test_deploy()
        elif args.command == 'update':
            manager.update_system(args.skip_backup, args.skip_restart)
        elif args.command == 'status':
            manager.show_status()
        elif args.command == 'prepare':
            if not args.deploy_type:
                print("❌ Tipo de deploy necessário. Use: development, production, ou docker")
                sys.exit(1)
            manager.prepare_files(args.deploy_type)
        elif args.command == 'help':
            manager.show_help()
        else:
            print(f"❌ Comando desconhecido: {args.command}")
            print("Use 'python deploy.py help' para ver comandos disponíveis.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
