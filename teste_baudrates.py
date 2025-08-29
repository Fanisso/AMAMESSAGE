import serial
import time
# Tente estes comandos em diferentes baud rates
comandos_testes = [
    b'AT+CGMM\r\n',      # Model identification
    b'ATI\r\n',          # Product information
    b'AT+GMM\r\n',       # Model request
    b'AT^VERSION\r\n',   # Version information
]
def testar_todos_baudrates(porta='COM1'):
    baudrates = [115200, 57600, 38400, 19200, 14400, 9600, 4800, 2400, 1200]
    
    print(f"🔍 Testando todos os baud rates na {porta}...")
    
    for baud in baudrates:
        try:
            print(f"⚡ Testando baudrate {baud}...")
            
            ser = serial.Serial(
                port=porta,
                baudrate=baud,
                timeout=2,
                writeTimeout=2,
                bytesize=8,
                parity='N',
                stopbits=1
            )
            
            time.sleep(2)  # Aguardar inicialização
            
            # Limpar buffer de entrada
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Enviar comando AT várias vezes (alguns modens precisam de múltiplas tentativas)
            for i in range(3):
                ser.write(b'AT\r\n')
                time.sleep(0.5)
                resposta = ser.read(100)
                
                if resposta and (b'OK' in resposta or b'AT' in resposta):
                    print(f"✅ SUCESSO! Baudrate correto: {baud}")
                    print(f"📡 Resposta: {resposta}")
                    
                    # Testar comando de identificação
                    ser.write(b'ATI\r\n')
                    time.sleep(1)
                    resposta_id = ser.read(200)
                    print(f"🆔 Identificação: {resposta_id}")
                    
                    ser.close()
                    return baud
                
                time.sleep(0.5)
            
            ser.close()
            print(f"❌ Sem resposta em {baud}")
                
        except Exception as e:
            print(f"❌ Erro em {baud}: {e}")
    
    return None

# Executar teste
baud_correto = testar_todos_baudrates('COM1')
if baud_correto:
    print(f"🎉 Baudrate correto encontrado: {baud_correto}")
    print(f"💡 Use esta configuração no sistema AMA MESSAGE!")
else:
    print("😞 Nenhum baudrate funcionou.")
    print("\n📋 Possíveis soluções:")
    print("1. 🔌 Reconecte o modem USB")
    print("2. 🔄 Reinicie o computador")
    print("3. 📲 Verifique se o modem está ligado")
    print("4. 🔧 Instale drivers específicos do modem")