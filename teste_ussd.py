import serial
import time

PORTA_SERIAL = 'COM3'  # Atualiza conforme tua porta
BAUDRATE = 115200
TIMEOUT = 10

def enviar_ussd(comando):
    try:
        with serial.Serial(PORTA_SERIAL, BAUDRATE, timeout=TIMEOUT) as modem:
            modem.write(b'AT\r')
            time.sleep(1)
            print("->", modem.read(modem.in_waiting).decode())

            modem.write(b'AT+CUSD=1\r')
            time.sleep(1)
            print("->", modem.read(modem.in_waiting).decode())

            ussd_cmd = f'AT+CUSD=1,"{comando}",15\r'
            modem.write(ussd_cmd.encode())
            time.sleep(5)

            resposta = modem.read(modem.in_waiting).decode()
            print("Resposta USSD:", resposta)

    except serial.SerialException as e:
        print("Erro ao conectar com o modem:", e)

if __name__ == "__main__":
    enviar_ussd("*155#")
