"""
API v2 - AMAMESSAGE
Endpoints modernos usando componentes compartilhados
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .sms import router as sms_router
from .ussd import router as ussd_router
from .contacts import router as contacts_router
from .forwarding_rules import router as forwarding_rules_router
from .system import router as system_router
from .users import router as users_router

# Router principal da API v2
api_router = APIRouter(prefix="/api/v2")

# Registrar todos os routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(sms_router, prefix="/sms", tags=["SMS"])
api_router.include_router(ussd_router, prefix="/ussd", tags=["USSD"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(forwarding_rules_router, prefix="/forwarding-rules", tags=["Forwarding Rules"])
api_router.include_router(system_router, prefix="/system", tags=["System"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

# Health check da API v2
@api_router.get("/health")
async def health_check():
    """Health check endpoint para monitorização."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "api_version": "v2"
    }

__all__ = ["api_router"]
