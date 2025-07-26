#!/usr/bin/env python3
"""
Diagnóstico do processador de fila SMS
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.db.models import SMSQueue, SMS
from app.services.queue_processor import queue_processor
import time

def diagnose_queue():
    """Diagnosticar estado da fila de SMS"""
    print("🔍 Diagnóstico do Processador de Fila SMS")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # 1. Verificar estado do processador
        print("1. Estado do Processador:")
        print(f"   - Está a correr: {queue_processor.is_running}")
        print(f"   - Thread ativo: {queue_processor.processor_thread is not None}")
        if queue_processor.processor_thread:
            print(f"   - Thread vivo: {queue_processor.processor_thread.is_alive()}")
        
        # 2. Verificar fila de SMS
        print("\n2. Estado da Fila:")
        total_queue = db.query(SMSQueue).count()
        pending_queue = db.query(SMSQueue).filter(SMSQueue.processed == False).count()
        processed_queue = db.query(SMSQueue).filter(SMSQueue.processed == True).count()
        
        print(f"   - Total na fila: {total_queue}")
        print(f"   - Pendentes: {pending_queue}")
        print(f"   - Processados: {processed_queue}")
        
        # 3. Mostrar últimos SMS da fila
        print("\n3. Últimos 5 SMS na fila:")
        recent_queue = db.query(SMSQueue).order_by(SMSQueue.created_at.desc()).limit(5).all()
        
        if recent_queue:
            for item in recent_queue:
                status = "✅ Processado" if item.processed else "⏳ Pendente"
                print(f"   #{item.id}: {item.phone_to} - {status}")
                print(f"      Mensagem: {item.message[:50]}...")
                if item.processed_at:
                    print(f"      Processado em: {item.processed_at}")
        else:
            print("   - Nenhum item na fila")
        
        # 4. Verificar SMS enviados recentemente
        print("\n4. Últimos 5 SMS enviados:")
        recent_sms = db.query(SMS).order_by(SMS.created_at.desc()).limit(5).all()
        
        if recent_sms:
            for sms in recent_sms:
                direction = "📥" if sms.direction.value == 'inbound' else "📤"
                print(f"   #{sms.id}: {direction} {sms.phone_from} -> {sms.phone_to}")
                print(f"      Status: {sms.status.value}")
                print(f"      Criado: {sms.created_at}")
        else:
            print("   - Nenhum SMS encontrado")
        
        # 5. Testar status do processador
        print("\n5. Status do Processador:")
        try:
            status = queue_processor.get_queue_status()
            print(f"   - Método get_queue_status() funciona: ✅")
            print(f"   - Status retornado: {status}")
        except Exception as e:
            print(f"   - Erro ao obter status: ❌ {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def start_processor_if_needed():
    """Iniciar processador se não estiver a correr"""
    if not queue_processor.is_running:
        print("\n🚀 Iniciando processador de fila...")
        queue_processor.start_processing()
        time.sleep(2)  # Aguardar inicialização
        
        if queue_processor.is_running:
            print("✅ Processador iniciado com sucesso!")
        else:
            print("❌ Falha ao iniciar processador!")
        return True
    else:
        print("\n✅ Processador já está a correr")
        return False

def add_test_sms():
    """Adicionar SMS de teste à fila"""
    print("\n📤 Adicionando SMS de teste à fila...")
    
    db = SessionLocal()
    try:
        test_sms = SMSQueue(
            phone_to="+258841234567",
            message="Teste do processador de fila - " + str(int(time.time())),
            priority=1
        )
        
        db.add(test_sms)
        db.commit()
        
        print(f"✅ SMS de teste #{test_sms.id} adicionado à fila")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar SMS de teste: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Diagnóstico do Sistema de Fila SMS")
    
    # Executar diagnóstico
    diagnose_queue()
    
    # Perguntar se quer iniciar processador
    if not queue_processor.is_running:
        response = input("\n❓ Processador não está a correr. Iniciar? (s/N): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            start_processor_if_needed()
            
            # Perguntar se quer adicionar SMS de teste
            response = input("\n❓ Adicionar SMS de teste à fila? (s/N): ")
            if response.lower() in ['s', 'sim', 'y', 'yes']:
                add_test_sms()
                
                print("\n⏳ Aguardando processamento (10 segundos)...")
                time.sleep(10)
                
                print("\n🔍 Diagnóstico final:")
                diagnose_queue()
    
    print("\n✅ Diagnóstico concluído!")
