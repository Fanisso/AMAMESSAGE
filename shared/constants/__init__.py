"""
Constantes do sistema AMAMESSAGE
Valores constantes compartilhados entre todos os componentes
"""

# Versão do sistema
SYSTEM_VERSION = "2.0.0"
API_VERSION = "v2"

# Limites do sistema
MAX_SMS_LENGTH = 160
MAX_SMS_PARTS = 3
MAX_USSD_TIMEOUT = 60
MAX_USSD_SESSION_DURATION = 300  # 5 minutos para sessões USSD
MAX_CONTACTS_PER_USER = 1000
MAX_FORWARDING_RULES = 20
MAX_FORWARDING_RULES_PER_USER = 20  # Limite de regras por usuário
MAX_SESSION_DURATION = 86400  # 24 horas em segundos
MAX_BULK_RECIPIENTS = 100  # Máximo de destinatários por envio em massa

# Limites de rate limiting
RATE_LIMIT_SMS_PER_MINUTE = 10
RATE_LIMIT_SMS_PER_HOUR = 100
RATE_LIMIT_SMS_PER_DAY = 500
RATE_LIMIT_USSD_PER_MINUTE = 5
RATE_LIMIT_API_CALLS_PER_MINUTE = 60

# Configurações de SMS
SMS_ENCODINGS = {
    'GSM_7BIT': 'gsm',
    'UCS2': 'ucs2',
    'UTF8': 'utf-8'
}

SMS_STATUS_CODES = {
    0: 'pending',
    1: 'sent',
    2: 'delivered',
    3: 'failed',
    4: 'expired',
    5: 'unknown'
}

# Códigos USSD comuns
COMMON_USSD_CODES = {
    'BALANCE': ['*100#', '*111#', '*123#'],
    'RECHARGE': ['*121*', '*123*'],
    'CALL_HISTORY': ['*646#', '*555#'],
    'SERVICES': ['*144#', '*555#']
}

# Configurações de conectividade
MODEM_BAUDRATES = [9600, 19200, 38400, 57600, 115200, 230400]
MODEM_TIMEOUT = 30
MODEM_MAX_RETRIES = 3

# Códigos de país suportados
SUPPORTED_COUNTRY_CODES = {
    'PT': '+351',  # Portugal
    'BR': '+55',   # Brasil
    'AO': '+244',  # Angola
    'MZ': '+258',  # Moçambique
    'CV': '+238',  # Cabo Verde
    'GW': '+245',  # Guiné-Bissau
    'ST': '+239',  # São Tomé e Príncipe
    'TL': '+670'   # Timor-Leste
}

# Operadoras suportadas (Portugal)
PORTUGUESE_OPERATORS = {
    'MEO': ['96', '93'],      # Prefixos MEO
    'NOS': ['91', '93'],      # Prefixos NOS  
    'VODAFONE': ['92', '93']  # Prefixos Vodafone
}

# Tipos de usuário e permissões
USER_TYPES = {
    'INDIVIDUAL': {
        'max_sms_per_day': 100,
        'max_contacts': 200,
        'max_forwarding_rules': 5,
        'features': ['send_sms', 'receive_sms', 'ussd', 'contacts', 'basic_forwarding']
    },
    'ENTERPRISE': {
        'max_sms_per_day': 1000,
        'max_contacts': 1000,
        'max_forwarding_rules': 20,
        'features': ['send_sms', 'receive_sms', 'ussd', 'contacts', 'advanced_forwarding', 
                    'bulk_sms', 'analytics', 'api_access', 'webhooks']
    },
    'ADMIN': {
        'max_sms_per_day': -1,  # Ilimitado
        'max_contacts': -1,
        'max_forwarding_rules': -1,
        'features': ['all']
    }
}

# Configurações de autenticação
AUTH_CONFIG = {
    'JWT_EXPIRY': 86400,  # 24 horas
    'REFRESH_TOKEN_EXPIRY': 604800,  # 7 dias
    'PASSWORD_MIN_LENGTH': 8,
    'PASSWORD_REQUIRE_UPPER': True,
    'PASSWORD_REQUIRE_LOWER': True,
    'PASSWORD_REQUIRE_DIGIT': True,
    'PASSWORD_REQUIRE_SPECIAL': False,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION': 900  # 15 minutos
}

# Constantes JWT para compatibilidade
JWT_SECRET_KEY = "sua_chave_secreta_muito_forte_aqui_mude_em_producao"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurações de API
API_CONFIG = {
    'BASE_PATH': '/api/v2',
    'DOCS_PATH': '/docs',
    'OPENAPI_PATH': '/openapi.json',
    'MAX_CONTENT_LENGTH': 10485760,  # 10MB
    'REQUEST_TIMEOUT': 30,
    'CORS_ORIGINS': ['http://localhost:3000', 'https://*.amamessage.com']
}

# Configurações de base de dados
DATABASE_CONFIG = {
    'POOL_SIZE': 10,
    'MAX_OVERFLOW': 20,
    'POOL_TIMEOUT': 30,
    'POOL_RECYCLE': 3600,
    'ECHO_SQL': False
}

# Configurações de cache
CACHE_CONFIG = {
    'DEFAULT_TIMEOUT': 300,  # 5 minutos
    'USER_SESSION_TIMEOUT': 3600,  # 1 hora
    'API_RESPONSE_TIMEOUT': 60,  # 1 minuto
    'MODEM_STATUS_TIMEOUT': 30  # 30 segundos
}

# Configurações de logging
LOG_CONFIG = {
    'LEVELS': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    'DEFAULT_LEVEL': 'INFO',
    'MAX_FILE_SIZE': 10485760,  # 10MB
    'MAX_FILES': 5,
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
    'MESSAGE_FORMAT': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
}

# Configurações de notificações
NOTIFICATION_CONFIG = {
    'EMAIL_TIMEOUT': 30,
    'WEBHOOK_TIMEOUT': 15,
    'MAX_RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 5  # segundos
}

# Templates de mensagens
MESSAGE_TEMPLATES = {
    'WELCOME_INDIVIDUAL': 'Bem-vindo ao AMAMESSAGE! Sua conta individual foi criada com sucesso.',
    'WELCOME_ENTERPRISE': 'Bem-vindo ao AMAMESSAGE Business! Sua conta empresarial está ativa.',
    'SMS_DELIVERY_FAILED': 'Falha no envio da mensagem para {number}: {error}',
    'USSD_TIMEOUT': 'Sessão USSD expirou. Código: {code}',
    'ACCOUNT_LOCKED': 'Conta bloqueada por múltiplas tentativas de login. Tente novamente em {minutes} minutos.',
    'PASSWORD_RESET': 'Código de recuperação de senha: {code}. Válido por 15 minutos.',
    'FORWARDING_ACTIVATED': 'Regra de reencaminhamento "{rule_name}" foi ativada.',
    'MODEM_DISCONNECTED': 'Modem desconectado: {port}. Tentando reconectar...',
    'QUOTA_EXCEEDED': 'Limite de {type} excedido. Upgrade sua conta para continuar.'
}

# Códigos de erro padrão
ERROR_CODES = {
    # Autenticação
    'AUTH_001': 'Credenciais inválidas',
    'AUTH_002': 'Token expirado',
    'AUTH_003': 'Acesso negado',
    'AUTH_004': 'Conta bloqueada',
    'AUTH_005': 'Sessão inválida',
    
    # SMS
    'SMS_001': 'Número de telefone inválido',
    'SMS_002': 'Mensagem muito longa',
    'SMS_003': 'Falha no envio',
    'SMS_004': 'Quota excedida',
    'SMS_005': 'Modem não disponível',
    
    # USSD
    'USSD_001': 'Código USSD inválido',
    'USSD_002': 'Sessão expirou',
    'USSD_003': 'Operação cancelada',
    'USSD_004': 'Resposta inválida',
    
    # Sistema
    'SYS_001': 'Erro interno do servidor',
    'SYS_002': 'Serviço temporariamente indisponível',
    'SYS_003': 'Manutenção programada',
    'SYS_004': 'Limite de recursos excedido',
    'SYS_005': 'Configuração inválida',
    
    # Validação
    'VAL_001': 'Dados obrigatórios ausentes',
    'VAL_002': 'Formato de dados inválido',
    'VAL_003': 'Valor fora do intervalo permitido',
    'VAL_004': 'Duplicata não permitida',
    'VAL_005': 'Referência não encontrada'
}

# Configurações por ambiente
ENVIRONMENT_CONFIGS = {
    'development': {
        'DEBUG': True,
        'LOG_LEVEL': 'DEBUG',
        'DATABASE_ECHO': True,
        'RATE_LIMITING': False,
        'CACHE_TIMEOUT': 60
    },
    'testing': {
        'DEBUG': True,
        'LOG_LEVEL': 'INFO',
        'DATABASE_ECHO': False,
        'RATE_LIMITING': True,
        'CACHE_TIMEOUT': 30
    },
    'staging': {
        'DEBUG': False,
        'LOG_LEVEL': 'INFO',
        'DATABASE_ECHO': False,
        'RATE_LIMITING': True,
        'CACHE_TIMEOUT': 300
    },
    'production': {
        'DEBUG': False,
        'LOG_LEVEL': 'WARNING',
        'DATABASE_ECHO': False,
        'RATE_LIMITING': True,
        'CACHE_TIMEOUT': 600
    }
}

# Configurações de plataforma
PLATFORM_CONFIGS = {
    'web': {
        'session_timeout': 3600,
        'max_file_upload': 5242880,  # 5MB
        'supported_browsers': ['chrome', 'firefox', 'safari', 'edge']
    },
    'android': {
        'min_version': 21,  # Android 5.0
        'target_version': 34,
        'permissions': ['SMS', 'PHONE', 'INTERNET', 'ACCESS_NETWORK_STATE']
    },
    'ios': {
        'min_version': '12.0',
        'target_version': '17.0',
        'permissions': ['MessageUI', 'CoreTelephony']
    }
}

# URLs e endpoints
EXTERNAL_SERVICES = {
    'sms_providers': {
        'twilio': 'https://api.twilio.com/2010-04-01',
        'vonage': 'https://rest.nexmo.com',
        'messagebird': 'https://rest.messagebird.com'
    },
    'notification_services': {
        'pushover': 'https://api.pushover.net/1',
        'slack': 'https://hooks.slack.com/services',
        'discord': 'https://discord.com/api/webhooks'
    }
}

# Configurações de monitoramento
MONITORING_CONFIG = {
    'health_check_interval': 60,
    'metrics_retention_days': 30,
    'alert_thresholds': {
        'cpu_usage': 80,
        'memory_usage': 85,
        'disk_usage': 90,
        'error_rate': 5,
        'response_time': 2000  # ms
    }
}

# Export das constantes principais
__all__ = [
    'SYSTEM_VERSION', 'API_VERSION', 'MAX_SMS_LENGTH', 'MAX_BULK_RECIPIENTS', 'MAX_USSD_SESSION_DURATION', 
    'MAX_FORWARDING_RULES_PER_USER', 'SUPPORTED_COUNTRY_CODES',
    'USER_TYPES', 'AUTH_CONFIG', 'API_CONFIG', 'ERROR_CODES', 'MESSAGE_TEMPLATES',
    'ENVIRONMENT_CONFIGS', 'PLATFORM_CONFIGS', 'JWT_SECRET_KEY', 'JWT_ALGORITHM', 
    'JWT_ACCESS_TOKEN_EXPIRE_MINUTES'
]
