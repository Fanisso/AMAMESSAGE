"""
Cliente API - AMAMESSAGE
Cliente Python para interação com a API do sistema
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from urllib.parse import urljoin
import logging

# Imports dos modelos compartilhados
from ..models import MessageStatus, USSDSessionStatus, UserType
from ..schemas import (
    LoginRequest, LoginResponse, UserProfile, SMSSendRequest, 
    SMSBulkSendRequest, SMSResponse, USSDSendRequest, USSDResponse,
    ContactCreate, ContactResponse, ForwardingRuleCreate
)
from ..constants import API_ENDPOINTS, API_VERSION

logger = logging.getLogger(__name__)

class APIException(Exception):
    """Exceção customizada para erros da API."""
    
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class AMAMessageAPIClient:
    """Cliente para interação com a API do AMAMESSAGE."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Inicializa o cliente da API.
        
        Args:
            base_url: URL base da API
            timeout: Timeout para requisições em segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        self.access_token = None
        self.refresh_token = None
        
    async def __aenter__(self):
        """Context manager para inicializar sessão."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={'Content-Type': 'application/json'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager para fechar sessão."""
        if self.session:
            await self.session.close()
    
    def _build_url(self, endpoint: str) -> str:
        """Constrói URL completa para endpoint."""
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers padrão para requisições."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
            
        return headers
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict = None, 
        params: Dict = None
    ) -> Dict[str, Any]:
        """
        Faz requisição HTTP para a API.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API
            data: Dados para enviar no body
            params: Parâmetros de query string
            
        Returns:
            Response da API como dict
            
        Raises:
            APIException: Em caso de erro na requisição
        """
        if not self.session:
            raise APIException("Cliente não inicializado. Use async with.")
            
        url = self._build_url(endpoint)
        headers = self._get_headers()
        
        try:
            json_data = json.dumps(data) if data else None
            
            async with self.session.request(
                method=method,
                url=url,
                data=json_data,
                params=params,
                headers=headers
            ) as response:
                
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {'raw_response': response_text}
                
                if response.status >= 400:
                    error_msg = response_data.get('message', f'HTTP {response.status}')
                    error_code = response_data.get('error_code', 'UNKNOWN_ERROR')
                    raise APIException(error_msg, response.status, error_code)
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            raise APIException(f"Erro de conexão: {str(e)}")
    
    # Métodos de autenticação
    async def login(self, email: str, password: str, platform: str = 'web') -> LoginResponse:
        """
        Realiza login na API.
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            platform: Plataforma (web, android, ios)
            
        Returns:
            Dados do login com tokens
        """
        login_data = {
            'email': email,
            'password': password,
            'platform': platform
        }
        
        response = await self._make_request('POST', API_ENDPOINTS['AUTH_LOGIN'], login_data)
        
        # Armazena tokens para próximas requisições
        self.access_token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')
        
        return LoginResponse(**response)
    
    async def refresh_access_token(self) -> str:
        """
        Renova o token de acesso.
        
        Returns:
            Novo access token
        """
        if not self.refresh_token:
            raise APIException("Refresh token não disponível")
        
        refresh_data = {'refresh_token': self.refresh_token}
        response = await self._make_request('POST', API_ENDPOINTS['AUTH_REFRESH'], refresh_data)
        
        self.access_token = response.get('access_token')
        return self.access_token
    
    async def logout(self) -> bool:
        """
        Realiza logout da API.
        
        Returns:
            True se logout foi bem-sucedido
        """
        try:
            await self._make_request('POST', API_ENDPOINTS['AUTH_LOGOUT'])
            self.access_token = None
            self.refresh_token = None
            return True
        except APIException:
            return False
    
    # Métodos de SMS
    async def send_sms(self, to: str, message: str, schedule_at: datetime = None) -> SMSResponse:
        """
        Envia SMS individual.
        
        Args:
            to: Número de destino
            message: Mensagem
            schedule_at: Agendamento opcional
            
        Returns:
            Dados do SMS enviado
        """
        sms_data = {
            'to': to,
            'message': message
        }
        
        if schedule_at:
            sms_data['schedule_at'] = schedule_at.isoformat()
        
        response = await self._make_request('POST', API_ENDPOINTS['SMS_SEND'], sms_data)
        return SMSResponse(**response)
    
    async def send_bulk_sms(
        self, 
        recipients: List[str], 
        message: str, 
        schedule_at: datetime = None
    ) -> List[SMSResponse]:
        """
        Envia SMS em lote.
        
        Args:
            recipients: Lista de números de destino
            message: Mensagem
            schedule_at: Agendamento opcional
            
        Returns:
            Lista com dados dos SMS enviados
        """
        bulk_data = {
            'recipients': recipients,
            'message': message
        }
        
        if schedule_at:
            bulk_data['schedule_at'] = schedule_at.isoformat()
        
        response = await self._make_request('POST', API_ENDPOINTS['SMS_BULK_SEND'], bulk_data)
        return [SMSResponse(**sms) for sms in response.get('messages', [])]
    
    async def get_sms_list(
        self, 
        page: int = 1, 
        per_page: int = 20,
        status: MessageStatus = None,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """
        Lista SMS enviados.
        
        Args:
            page: Número da página
            per_page: Items por página
            status: Filtro por status
            date_from: Data inicial
            date_to: Data final
            
        Returns:
            Lista paginada de SMS
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if status:
            params['status'] = status.value
        if date_from:
            params['date_from'] = date_from.isoformat()
        if date_to:
            params['date_to'] = date_to.isoformat()
        
        response = await self._make_request('GET', API_ENDPOINTS['SMS_LIST'], params=params)
        return response
    
    async def get_sms_detail(self, sms_id: str) -> SMSResponse:
        """
        Obtém detalhes de um SMS específico.
        
        Args:
            sms_id: ID do SMS
            
        Returns:
            Dados detalhados do SMS
        """
        endpoint = f"{API_ENDPOINTS['SMS_DETAIL']}/{sms_id}"
        response = await self._make_request('GET', endpoint)
        return SMSResponse(**response)
    
    # Métodos de USSD
    async def send_ussd(self, code: str) -> USSDResponse:
        """
        Envia comando USSD.
        
        Args:
            code: Código USSD
            
        Returns:
            Dados da sessão USSD
        """
        ussd_data = {'code': code}
        response = await self._make_request('POST', API_ENDPOINTS['USSD_SEND'], ussd_data)
        return USSDResponse(**response)
    
    async def get_ussd_sessions(
        self, 
        page: int = 1, 
        per_page: int = 20,
        status: USSDSessionStatus = None
    ) -> Dict[str, Any]:
        """
        Lista sessões USSD.
        
        Args:
            page: Número da página
            per_page: Items por página
            status: Filtro por status
            
        Returns:
            Lista paginada de sessões USSD
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if status:
            params['status'] = status.value
        
        endpoint = API_ENDPOINTS['USSD_SESSIONS']
        response = await self._make_request('GET', endpoint, params=params)
        return response
    
    async def get_ussd_session_detail(self, session_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma sessão USSD.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dados detalhados da sessão
        """
        endpoint = f"{API_ENDPOINTS['USSD_SESSION_DETAIL']}/{session_id}"
        response = await self._make_request('GET', endpoint)
        return response
    
    # Métodos de contactos
    async def create_contact(self, contact_data: ContactCreate) -> ContactResponse:
        """
        Cria novo contacto.
        
        Args:
            contact_data: Dados do contacto
            
        Returns:
            Dados do contacto criado
        """
        data = contact_data.dict()
        response = await self._make_request('POST', API_ENDPOINTS['CONTACTS'], data)
        return ContactResponse(**response)
    
    async def get_contacts(
        self, 
        page: int = 1, 
        per_page: int = 20,
        search: str = None,
        group: str = None
    ) -> Dict[str, Any]:
        """
        Lista contactos.
        
        Args:
            page: Número da página
            per_page: Items por página
            search: Termo de busca
            group: Filtro por grupo
            
        Returns:
            Lista paginada de contactos
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if search:
            params['search'] = search
        if group:
            params['group'] = group
        
        response = await self._make_request('GET', API_ENDPOINTS['CONTACTS'], params=params)
        return response
    
    async def update_contact(self, contact_id: int, contact_data: Dict[str, Any]) -> ContactResponse:
        """
        Atualiza contacto existente.
        
        Args:
            contact_id: ID do contacto
            contact_data: Dados para atualização
            
        Returns:
            Dados do contacto atualizado
        """
        endpoint = f"{API_ENDPOINTS['CONTACTS']}/{contact_id}"
        response = await self._make_request('PUT', endpoint, contact_data)
        return ContactResponse(**response)
    
    async def delete_contact(self, contact_id: int) -> bool:
        """
        Remove contacto.
        
        Args:
            contact_id: ID do contacto
            
        Returns:
            True se removido com sucesso
        """
        endpoint = f"{API_ENDPOINTS['CONTACTS']}/{contact_id}"
        try:
            await self._make_request('DELETE', endpoint)
            return True
        except APIException:
            return False
    
    # Métodos de regras de reencaminhamento
    async def create_forwarding_rule(self, rule_data: ForwardingRuleCreate) -> Dict[str, Any]:
        """
        Cria nova regra de reencaminhamento.
        
        Args:
            rule_data: Dados da regra
            
        Returns:
            Dados da regra criada
        """
        data = rule_data.dict()
        response = await self._make_request('POST', API_ENDPOINTS['FORWARDING_RULES'], data)
        return response
    
    async def get_forwarding_rules(
        self, 
        page: int = 1, 
        per_page: int = 20,
        is_active: bool = None
    ) -> Dict[str, Any]:
        """
        Lista regras de reencaminhamento.
        
        Args:
            page: Número da página
            per_page: Items por página
            is_active: Filtro por status ativo
            
        Returns:
            Lista paginada de regras
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if is_active is not None:
            params['is_active'] = is_active
        
        response = await self._make_request('GET', API_ENDPOINTS['FORWARDING_RULES'], params=params)
        return response
    
    # Métodos de sistema
    async def get_system_health(self) -> Dict[str, Any]:
        """
        Obtém status de saúde do sistema.
        
        Returns:
            Dados de saúde do sistema
        """
        response = await self._make_request('GET', API_ENDPOINTS['SYSTEM_HEALTH'])
        return response
    
    async def get_modem_status(self) -> List[Dict[str, Any]]:
        """
        Obtém status dos modems conectados.
        
        Returns:
            Lista com status dos modems
        """
        response = await self._make_request('GET', API_ENDPOINTS['SYSTEM_MODEM_STATUS'])
        return response.get('modems', [])
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do sistema.
        
        Returns:
            Estatísticas gerais do sistema
        """
        response = await self._make_request('GET', API_ENDPOINTS['SYSTEM_STATS'])
        return response

# Classe auxiliar para integração síncrona
class SyncAMAMessageAPIClient:
    """Wrapper síncrono para o cliente da API."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self._client = None
    
    def _run_async(self, coro):
        """Executa corrotina de forma síncrona."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def __enter__(self):
        self._client = AMAMessageAPIClient(self.base_url, self.timeout)
        self._run_async(self._client.__aenter__())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._run_async(self._client.__aexit__(exc_type, exc_val, exc_tb))
    
    def __getattr__(self, name):
        """Proxy para métodos do cliente assíncrono."""
        if self._client and hasattr(self._client, name):
            method = getattr(self._client, name)
            if asyncio.iscoroutinefunction(method):
                return lambda *args, **kwargs: self._run_async(method(*args, **kwargs))
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Factory functions
def create_async_client(base_url: str, timeout: int = 30) -> AMAMessageAPIClient:
    """
    Cria cliente assíncrono da API.
    
    Args:
        base_url: URL base da API
        timeout: Timeout em segundos
        
    Returns:
        Cliente assíncrono
    """
    return AMAMessageAPIClient(base_url, timeout)

def create_sync_client(base_url: str, timeout: int = 30) -> SyncAMAMessageAPIClient:
    """
    Cria cliente síncrono da API.
    
    Args:
        base_url: URL base da API
        timeout: Timeout em segundos
        
    Returns:
        Cliente síncrono
    """
    return SyncAMAMessageAPIClient(base_url, timeout)

# Export dos clientes
__all__ = [
    'AMAMessageAPIClient', 
    'SyncAMAMessageAPIClient', 
    'APIException',
    'create_async_client', 
    'create_sync_client'
]
