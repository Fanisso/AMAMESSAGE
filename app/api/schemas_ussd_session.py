from pydantic import BaseModel, Field
from typing import Optional

class USSDSessionStartRequest(BaseModel):
    ussd_code: str = Field(..., description="Código USSD para iniciar sessão", example="*123#")
    timeout: Optional[int] = Field(30, description="Timeout em segundos", ge=5, le=120)

class USSDSessionReplyRequest(BaseModel):
    reply: str = Field(..., description="Resposta do usuário para o menu USSD")
    step: Optional[int] = Field(1, description="Etapa da sessão USSD")

class USSDSessionResponse(BaseModel):
    success: bool
    response: str = ""
    error: Optional[str] = None
    session_active: bool = False
    step: Optional[int] = None
