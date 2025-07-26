#!/usr/bin/env python3
"""
Teste do novo modem Qualcomm detectado
"""
import serial
import time
import requests

def test_port_direct(port):
    """Teste direto de uma porta COM"""
    print(f"\n🔍 Testando porta {port}:")
    try:
        # Configurações padrão para modem GSM
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            timeout=2,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        
        # Comando AT básico
        ser.write(b'AT\r\n')
        time.sleep(0.5)
        response = ser.read(100).decode('utf-8', errors='ignore').strip()
        
        if 'OK' in response:
            print(f"  ✅ Resposta AT: {response}")
            
            # Teste identificação do modem
            ser.write(b'ATI\r\n')
            time.sleep(0.5)
            info = ser.read(200).decode('utf-8', errors='ignore').strip()
            print(f"  📋 Info: {info}")
            
            # Teste status SIM
            ser.write(b'AT+CPIN?\r\n')
            time.sleep(0.5)
            sim_status = ser.read(100).decode('utf-8', errors='ignore').strip()
            print(f"  📱 SIM: {sim_status}")
            
            ser.close()
            return True
        else:
            print(f"  ❌ Sem resposta AT válida: {response}")
            ser.close()
            return False
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def update_modem_config(working_port):
    """Atualizar configuração do modem no sistema"""
    print(f"\n🔧 Atualizando configuração para {working_port}...")
    
    # Ler arquivo de configuração atual
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Atualizar porta COM
        lines = env_content.split('\n')
        updated_lines = []
        port_updated = False
        
        for line in lines:
            if line.startswith('MODEM_PORT='):
                updated_lines.append(f'MODEM_PORT={working_port}')
                port_updated = True
                print(f"  ✅ Linha atualizada: MODEM_PORT={working_port}")
            else:
                updated_lines.append(line)
        
        # Se não existia, adicionar
        if not port_updated:
            updated_lines.append(f'MODEM_PORT={working_port}')
            print(f"  ✅ Linha adicionada: MODEM_PORT={working_port}")
        
        # Escrever arquivo atualizado
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("  ✅ Arquivo .env atualizado com sucesso")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao atualizar .env: {e}")
        return False

def restart_server():
    """Tentar reiniciar o servidor via API"""
    print("\n🔄 Reiniciando servidor...")
    try:
        response = requests.post('http://127.0.0.1:8000/modem/api/restart', timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("  ✅ Servidor reiniciado com sucesso")
                return True
        print("  ⚠️ Reinício não confirmado via API")
        return False
    except Exception as e:
        print(f"  ❌ Erro ao reiniciar via API: {e}")
        return False

def main():
    print("=== Teste e Configuração do Novo Modem Qualcomm ===")
    
    # Portas identificadas do modem Qualcomm
    test_ports = ['COM4', 'COM5', 'COM6']
    working_port = None
    
    # Testar cada porta
    for port in test_ports:
        if test_port_direct(port):
            working_port = port
            break
    
    if working_port:
        print(f"\n🎉 Modem encontrado em {working_port}!")
        
        # Atualizar configuração
        if update_modem_config(working_port):
            # Reiniciar servidor
            if restart_server():
                print("\n✅ Configuração completa!")
            else:
                print("\n⚠️ Reinicie manualmente o servidor: uvicorn main:app --reload")
        
        print(f"\n📋 Instruções finais:")
        print(f"1. Modem Qualcomm configurado em {working_port}")
        print(f"2. Arquivo .env atualizado")
        print(f"3. Acesse http://127.0.0.1:8000/modem/ para verificar")
        print(f"4. Se necessário, reinicie o servidor")
        
    else:
        print("\n❌ Nenhuma porta do modem respondeu aos comandos AT")
        print("💡 Verifique:")
        print("  - Driver do modem instalado")
        print("  - Modem não está sendo usado por outro programa")
        print("  - SIM card inserido e ativo")

if __name__ == "__main__":
    main()
