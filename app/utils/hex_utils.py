import binascii

def decode_hex_message(hex_string: str) -> str:
    """
    Decodifica uma mensagem hexadecimal para texto legível.
    Tenta múltiplos encodings comuns usados em mensagens USSD/SMS.
    """
    # Limpeza da string: remove espaços e quebras
    clean_hex = hex_string.replace(" ", "").replace("\n", "").replace("\r", "")

    # Verifica se a mensagem tem só caracteres hexadecimais
    is_hex = all(c in "0123456789abcdefABCDEF" for c in clean_hex)
    
    if not is_hex or len(clean_hex) % 2 != 0:
        return "[Mensagem não é hexadecimal válida]"

    try:
        # Converte hex → bytes
        raw_bytes = binascii.unhexlify(clean_hex)

        # Tenta diferentes codificações
        for encoding in ["utf-8", "latin1", "utf-16-be"]:
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return "[Hex decodificado, mas não pôde ser interpretado como texto legível]"
    except Exception as e:
        return f"[Erro na decodificação: {str(e)}]"
