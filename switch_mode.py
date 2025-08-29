import usb.core
import usb.util

# Desconecte e reconecte o modem primeiro
dev = usb.core.find(idVendor=0x12d1, idProduct=0x1f01)  # Valores comuns Huawei

if dev is None:
    print("Modem não encontrado. Reconecte e tente novamente.")
else:
    print("Modem encontrado! Tentando alternar modo...")
    try:
        dev.ctrl_transfer(0x40, 0, 0, 0, b'USBC\x00\x00\x00\x00\x00\x00\x00')
        print("✅ Modo alternado com sucesso! Reconecte o modem.")
    except Exception as e:
        print(f"❌ Erro: {e}")