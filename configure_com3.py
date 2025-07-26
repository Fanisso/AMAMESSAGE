#!/usr/bin/env python3
"""
Configuração direta para COM3 (Qualcomm modem)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def configure_com3():
    print("🔧 CONFIGURANDO DIRETAMENTE PARA COM3")
    print("=" * 50)
    
    try:
        # 1. Atualizar arquivo .env
        env_path = Path(__file__).parent / ".env"
        
        print("📝 Atualizando arquivo .env...")
        if env_path.exists():
            # Ler conteúdo atual
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir GSM_PORT
            if "GSM_PORT=AUTO" in content:
                content = content.replace("GSM_PORT=AUTO", "GSM_PORT=COM3")
                print("   ✅ Mudado de AUTO para COM3")
            elif "GSM_PORT=" in content:
                import re
                content = re.sub(r'GSM_PORT=.*', 'GSM_PORT=COM3', content)
                print("   ✅ Porta atualizada para COM3")
            else:
                content += "\nGSM_PORT=COM3\n"
                print("   ✅ Adicionado GSM_PORT=COM3")
            
            # Salvar
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   💾 Arquivo .env atualizado")
        else:
            # Criar arquivo .env
            env_content = """# Configuração da Base de Dados (SQLite para desenvolvimento)
DATABASE_URL=sqlite:///./amamessage.db

# Configuração do Modem GSM
GSM_PORT=COM3
GSM_BAUDRATE=115200
GSM_TIMEOUT=10
GSM_PIN=
GSM_SMSC=

# Redis (Filas)
REDIS_URL=redis://localhost:6379/0

# Segurança
SECRET_KEY=sua_chave_secreta_muito_forte_aqui_mude_em_producao
"""
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("   ✅ Arquivo .env criado com COM3")
        
        # 2. Testar conexão COM3
        print(f"\n🧪 Testando conexão COM3...")
        try:
            from app.services.gsm_service import GSMModem
            
            # Forçar uso da COM3
            gsm = GSMModem("COM3")
            print(f"   📍 Tentando conectar na COM3...")
            
            if gsm.connect():
                print(f"   ✅ CONEXÃO BEM-SUCEDIDA!")
                print(f"   📱 Modem conectado na COM3")
                
                # Testar comando AT
                try:
                    response = gsm._send_command("AT")
                    if response:
                        print(f"   📞 Responde a comandos AT: ✅")
                        
                        # Obter info do fabricante
                        try:
                            info = gsm._get_command_response("AT+CGMI")
                            print(f"   🏭 Fabricante: {info}")
                        except:
                            print(f"   ⚠️ Não conseguiu obter fabricante")
                    else:
                        print(f"   ❌ Não responde a comandos AT")
                except Exception as e:
                    print(f"   💥 Erro AT: {e}")
                
                gsm.disconnect()
                print(f"   🔌 Desconectado")
                return True
            else:
                print(f"   ❌ Falha na conexão COM3")
                return False
                
        except Exception as e:
            print(f"   💥 Erro ao testar COM3: {e}")
            return False
    
    except Exception as e:
        print(f"💥 ERRO: {e}")
        return False

def show_instructions():
    print(f"\n📋 INSTRUÇÕES:")
    print(f"   1. Sistema configurado para usar COM3 diretamente")
    print(f"   2. Não há mais detecção automática (mais rápido)")
    print(f"   3. Para iniciar: python start_server.py")
    print(f"   4. Acesse: http://127.0.0.1:8000/admin/modem")
    print(f"\n🔄 Para voltar à detecção automática:")
    print(f"   1. Editar arquivo .env")
    print(f"   2. Mudar GSM_PORT=COM3 para GSM_PORT=AUTO")

if __name__ == "__main__":
    print("🚀 AMA MESSAGE - Configuração Direta COM3")
    success = configure_com3()
    
    print("=" * 50)
    if success:
        print("🎉 COM3 configurada e testada com sucesso!")
        show_instructions()
    else:
        print("⚠️ Problema na configuração COM3")
        print("💡 Verifique se o modem está conectado e drivers instalados")
