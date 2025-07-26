"""
Serviço para processar fila de SMS em massa
"""
import asyncio
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import SMSQueue, SMS, SMSStatus, SMSDirection
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)

class SMSQueueProcessor:
    """Processador de fila de SMS para envios em massa"""
    
    def __init__(self):
        self.is_running = False
        self.processor_thread: Optional[threading.Thread] = None
        self.sms_service = SMSService()
        self.processing_interval = 2  # Processar a cada 2 segundos
        
    def start_processing(self):
        """Iniciar processamento da fila"""
        if not self.is_running:
            self.is_running = True
            self.processor_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.processor_thread.start()
            logger.info("🚀 Processador de fila SMS iniciado")
        
    def stop_processing(self):
        """Parar processamento da fila"""
        if self.is_running:
            self.is_running = False
            if self.processor_thread:
                self.processor_thread.join(timeout=10)
            logger.info("⏹️ Processador de fila SMS parado")
    
    def _process_queue(self):
        """Loop principal de processamento da fila"""
        while self.is_running:
            try:
                db = SessionLocal()
                
                # Buscar próximos SMS para processar
                queue_items = self._get_next_queue_items(db)
                
                if queue_items:
                    logger.info(f"📤 Processando {len(queue_items)} SMS da fila...")
                    
                    for queue_item in queue_items:
                        try:
                            self._process_queue_item(queue_item, db)
                        except Exception as e:
                            logger.error(f"Erro ao processar item {queue_item.id}: {str(e)}")
                            # Marcar como processado mesmo com erro para não ficar travado
                            queue_item.processed = True
                            queue_item.processed_at = datetime.utcnow()
                            db.commit()
                    
                    logger.info(f"✅ {len(queue_items)} SMS processados")
                
                db.close()
                
                # Aguardar antes da próxima verificação
                time.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Erro no processador de fila: {str(e)}")
                time.sleep(10)  # Aguardar mais tempo em caso de erro
    
    def _get_next_queue_items(self, db: Session, limit: int = 5) -> list:
        """Obter próximos itens da fila para processar"""
        try:
            # Buscar itens não processados, ordenados por prioridade e data de criação
            # Verificar se já é hora de enviar (para SMS agendados)
            now = datetime.utcnow()
            
            query = db.query(SMSQueue).filter(
                SMSQueue.processed == False
            ).filter(
                # SMS não agendados OU SMS agendados que já chegaram na hora
                (SMSQueue.scheduled_for.is_(None)) | 
                (SMSQueue.scheduled_for <= now)
            ).order_by(
                SMSQueue.priority.desc(),  # Prioridade maior primeiro
                SMSQueue.created_at.asc()  # Mais antigos primeiro
            ).limit(limit)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Erro ao buscar itens da fila: {str(e)}")
            return []
    
    def _process_queue_item(self, queue_item: SMSQueue, db: Session):
        """Processar um item individual da fila"""
        try:
            logger.info(f"📱 Processando SMS para {queue_item.phone_to}: {queue_item.message[:50]}...")
            
            # Criar registro SMS na tabela principal
            sms = SMS(
                phone_from="",  # Será preenchido pelo serviço
                phone_to=queue_item.phone_to,
                message=queue_item.message,
                status=SMSStatus.PENDING,
                direction=SMSDirection.OUTBOUND
            )
            db.add(sms)
            db.flush()  # Para obter o ID
            
            # Associar com item da fila
            queue_item.sms_id = sms.id
            
            # Enviar SMS (criar loop de eventos se necessário)
            import asyncio
            try:
                # Tentar usar loop existente
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Se o loop já estiver a correr, usar thread pool
                    future = asyncio.run_coroutine_threadsafe(
                        self.sms_service.send_sms(sms.id, db), 
                        loop
                    )
                    success = future.result(timeout=30)
                else:
                    # Se não houver loop, criar um
                    success = asyncio.run(self.sms_service.send_sms(sms.id, db))
            except RuntimeError:
                # Se não conseguir usar async, criar novo loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success = loop.run_until_complete(self.sms_service.send_sms(sms.id, db))
                finally:
                    loop.close()
            
            # Marcar item da fila como processado
            queue_item.processed = True
            queue_item.processed_at = datetime.utcnow()
            
            db.commit()
            
            if success:
                logger.info(f"✅ SMS {sms.id} enviado com sucesso para {queue_item.phone_to}")
            else:
                logger.warning(f"⚠️ Falha ao enviar SMS {sms.id} para {queue_item.phone_to}")
            
        except Exception as e:
            logger.error(f"Erro ao processar item da fila {queue_item.id}: {str(e)}")
            db.rollback()
            raise
    
    def get_queue_status(self) -> dict:
        """Obter status da fila de processamento"""
        try:
            db = SessionLocal()
            
            total_pending = db.query(SMSQueue).filter(SMSQueue.processed == False).count()
            total_processed = db.query(SMSQueue).filter(SMSQueue.processed == True).count()
            
            # Próximo SMS agendado
            next_scheduled = db.query(SMSQueue.scheduled_for).filter(
                SMSQueue.processed == False,
                SMSQueue.scheduled_for.isnot(None)
            ).order_by(SMSQueue.scheduled_for.asc()).first()
            
            db.close()
            
            return {
                "is_running": self.is_running,
                "total_pending": total_pending,
                "total_processed": total_processed,
                "next_scheduled": next_scheduled[0].isoformat() if next_scheduled and next_scheduled[0] else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da fila: {str(e)}")
            return {
                "is_running": self.is_running,
                "total_pending": 0,
                "total_processed": 0,
                "next_scheduled": None,
                "error": str(e)
            }
    
    def clear_processed_items(self, older_than_days: int = 7):
        """Limpar itens processados mais antigos que X dias"""
        try:
            db = SessionLocal()
            
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            deleted = db.query(SMSQueue).filter(
                SMSQueue.processed == True,
                SMSQueue.processed_at < cutoff_date
            ).delete()
            
            db.commit()
            db.close()
            
            logger.info(f"🧹 Removidos {deleted} itens antigos da fila")
            return deleted
            
        except Exception as e:
            logger.error(f"Erro ao limpar fila: {str(e)}")
            return 0

# Instância global do processador
queue_processor = SMSQueueProcessor()
