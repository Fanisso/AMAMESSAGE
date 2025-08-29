import serial
import time

def testar_modem(porta='COM1'):
    try:
        print(f"🔍 Testando comunicação na {porta}...")
        
        # Conectar na porta serial
        ser = serial.Serial(
            port=porta,
            baudrate=9600,      # Velocidade mais comum
            timeout=2,          # Timeout de 2 segundos
            writeTimeout=2,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        
        time.sleep(2)  # Aguardar inicialização
        
        # Enviar comando AT básico
        ser.write(b'AT\r\n')
        time.sleep(1)
        
        # Ler resposta
        resposta = ser.read(100)
        print(f"📡 Resposta do modem: {resposta}")
        
        # Testar comando de identificação
        ser.write(b'ATI\r\n')
        time.sleep(1)
        resposta_id = ser.read(200)
        print(f"🆔 Identificação: {resposta_id}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na {porta}: {e}")
        return False

# Executar teste
testar_modem('COM1')