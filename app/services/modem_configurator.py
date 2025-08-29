import usb.core
import usb.util
import time

def configurar_modem_auto():
    """
    Tenta configurar automaticamente modem em modo RNDIS para modo serial
    Retorna True se bem-sucedido
    """
    try:
        print("   [CONFIG] Verificando modems em modo RNDIS...")

        # IDs comuns de modems em modo RNDIS (internet)
        modems_rndis = [
            (0x12d1, 0x1f01),  # Huawei mode switch
            (0x12d1, 0x14dc),  # Huawei E3372
            (0x19d2, 0xfff5),  # ZTE mode switch
            (0x1c9e, 0x9605),  # Quectel
        ]

        for vid, pid in modems_rndis:
            dev = usb.core.find(idVendor=vid, idProduct=pid)
            if dev:
                print(f"   [MODEM] Modem encontrado: VID:{vid:04x} PID:{pid:04x}")
                print("   [CONFIG] Tentando alternar para modo serial...")

                try:
                    # Comando para alternar modo (Huawei)
                    dev.ctrl_transfer(0x40, 0, 0, 0, b'USBC\x00\x00\x00\x00\x00\x00\x00')
                    print("   [SUCESSO] Comando de alternancia enviado!")
                    print("   [ACAO] Reconecte o modem manualmente")
                    return True

                except Exception as e:
                    print(f"   [ERRO] Erro ao alternar modo: {e}")
                    return False

        print("   [INFO] Nenhum modem em modo RNDIS detectado")
        return False

    except ImportError:
        print("   [AVISO] Biblioteca pyusb nao instalada. Instale com: pip install pyusb")
        return False
    except Exception as e:
        print(f"   [ERRO] Erro inesperado: {e}")
        return False