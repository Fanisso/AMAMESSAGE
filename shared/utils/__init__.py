"""
Utilitários compartilhados - AMAMESSAGE
Funções auxiliares que serão usadas em todo o sistema
"""

import re
import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

# Validação de dados
def validate_phone_number(phone: str) -> bool:
    """
    Valida número de telefone.
    Aceita formatos: +351912345678, 351912345678, 912345678
    """
    if not phone:
        return False
    
    # Remove espaços e caracteres especiais
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Padrões aceitos
    patterns = [
        r'^\+351[0-9]{9}$',  # +351912345678
        r'^351[0-9]{9}$',    # 351912345678
        r'^[0-9]{9}$'        # 912345678
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def normalize_phone_number(phone: str) -> Optional[str]:
    """
    Normaliza número de telefone para formato padrão +351XXXXXXXXX
    """
    if not validate_phone_number(phone):
        return None
    
    # Remove espaços e caracteres especiais
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Adiciona código do país se necessário
    if clean_phone.startswith('+351'):
        return clean_phone
    elif clean_phone.startswith('351'):
        return '+' + clean_phone
    elif len(clean_phone) == 9:
        return '+351' + clean_phone
    
    return None

def validate_email(email: str) -> bool:
    """Valida endereço de email."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_ussd_code(code: str) -> bool:
    """Valida código USSD."""
    if not code:
        return False
    
    # Padrão básico: *código# ou #código*
    pattern = r'^[\*#][0-9\*#]+[\*#]$'
    return re.match(pattern, code) is not None

# Geração de IDs e tokens
def generate_uuid() -> str:
    """Gera UUID único."""
    return str(uuid.uuid4())

def generate_session_token() -> str:
    """Gera token de sessão seguro."""
    return secrets.token_urlsafe(32)

def generate_api_key() -> str:
    """Gera chave de API."""
    return 'ama_' + secrets.token_urlsafe(24)

def hash_password(password: str) -> str:
    """Hash de senha usando SHA-256 com salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hash_string: str) -> bool:
    """Verifica senha contra hash."""
    try:
        salt, stored_hash = hash_string.split(':')
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash == stored_hash
    except:
        return False

# Manipulação de datas
def get_current_timestamp() -> datetime:
    """Retorna timestamp atual com timezone UTC."""
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formata datetime para string."""
    if dt is None:
        return ""
    return dt.strftime(format_str)

def parse_datetime(dt_string: str) -> Optional[datetime]:
    """Parse string para datetime."""
    if not dt_string:
        return None
    
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except ValueError:
            continue
    
    return None

# Formatação de texto
def sanitize_text(text: str, max_length: int = 160) -> str:
    """Sanitiza texto removendo caracteres perigosos."""
    if not text:
        return ""
    
    # Remove caracteres de controle
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Trunca se necessário
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized.strip()

def extract_keywords(text: str) -> List[str]:
    """Extrai palavras-chave de um texto."""
    if not text:
        return []
    
    # Remove pontuação e converte para minúsculas
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = clean_text.split()
    
    # Remove palavras muito curtas
    keywords = [word for word in words if len(word) > 2]
    
    return list(set(keywords))  # Remove duplicatas

# Validação de configurações
def validate_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """Valida se configuração tem todas as chaves necessárias."""
    return all(key in config for key in required_keys)

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge duas configurações, override tem precedência."""
    result = base_config.copy()
    result.update(override_config)
    return result

# Utilitários de rede
def validate_url(url: str) -> bool:
    """Valida URL."""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_domain(url: str) -> Optional[str]:
    """Extrai domínio de uma URL."""
    if not validate_url(url):
        return None
    
    try:
        return urlparse(url).netloc
    except:
        return None

# Utilitários de arquivo
def get_file_extension(filename: str) -> str:
    """Retorna extensão do arquivo."""
    if not filename or '.' not in filename:
        return ""
    return filename.split('.')[-1].lower()

def is_safe_filename(filename: str) -> bool:
    """Verifica se nome do arquivo é seguro."""
    if not filename:
        return False
    
    # Caracteres proibidos
    forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    return not any(char in filename for char in forbidden_chars)

# Utilitários de formatação
def format_file_size(size_bytes: int) -> str:
    """Formata tamanho de arquivo."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def format_currency(amount: float, currency: str = "EUR") -> str:
    """Formata valor monetário."""
    return f"{amount:.2f} {currency}"

def format_duration(seconds: int) -> str:
    """Formata duração em formato legível."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

# Utilitários de criptografia (básica)
def simple_encrypt(text: str, key: str) -> str:
    """Criptografia simples para dados não críticos."""
    if not text or not key:
        return text
    
    # XOR simples (apenas para dados não sensíveis)
    result = ""
    key_len = len(key)
    
    for i, char in enumerate(text):
        result += chr(ord(char) ^ ord(key[i % key_len]))
    
    # Encode em base64 para tornar printable
    import base64
    return base64.b64encode(result.encode()).decode()

def simple_decrypt(encrypted_text: str, key: str) -> str:
    """Descriptografia simples."""
    if not encrypted_text or not key:
        return encrypted_text
    
    try:
        import base64
        # Decode base64
        decoded = base64.b64decode(encrypted_text.encode()).decode()
        
        # XOR reverso
        result = ""
        key_len = len(key)
        
        for i, char in enumerate(decoded):
            result += chr(ord(char) ^ ord(key[i % key_len]))
        
        return result
    except:
        return encrypted_text

# Utilitários de logging
def create_log_entry(level: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Cria entrada de log estruturada."""
    entry = {
        "timestamp": get_current_timestamp().isoformat(),
        "level": level.upper(),
        "message": message,
        "id": generate_uuid()
    }
    
    if context:
        entry["context"] = context
    
    return entry
