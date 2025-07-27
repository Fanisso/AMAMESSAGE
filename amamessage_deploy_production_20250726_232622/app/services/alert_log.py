import logging
from datetime import datetime
from typing import List, Dict

_ALERT_LOG: List[Dict] = []

class AlertLog:
    @staticmethod
    def add(event: str, details: str = "", success: bool = False):
        _ALERT_LOG.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event,
            "details": details,
            "success": success
        })
        # Limitar tamanho do log em memória
        if len(_ALERT_LOG) > 100:
            _ALERT_LOG.pop(0)

    @staticmethod
    def get_all() -> List[Dict]:
        return list(_ALERT_LOG)

    @staticmethod
    def clear():
        _ALERT_LOG.clear()
