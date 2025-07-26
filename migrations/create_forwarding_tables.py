"""
Script de migração para criar tabelas de regras de reencaminhamento
Execute este script para atualizar o banco de dados com as novas tabelas
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Executar migração do banco de dados"""
    try:
        # Criar engine de conexão
        engine = create_engine(settings.DATABASE_URL)
        
        logger.info("Conectando ao banco de dados...")
        
        # Criar todas as tabelas (incluindo as novas)
        logger.info("Criando tabelas de regras de reencaminhamento...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Tabelas criadas/atualizadas com sucesso!")
        logger.info("🎉 Migração concluída com sucesso!")
        
        # Criar algumas regras de exemplo
        create_sample_rules(engine)
        
    except Exception as e:
        logger.error(f"❌ Erro durante a migração: {str(e)}")
        raise

def create_sample_rules(engine):
    """Criar regras de exemplo"""
    try:
        from sqlalchemy.orm import sessionmaker
        from app.db.models import ForwardingRule, ForwardingRuleType, ForwardingRuleAction
        import json
        
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Verificar se já existem regras
        existing_count = db.query(ForwardingRule).count()
        if existing_count > 0:
            logger.info("Regras já existem, pulando criação de exemplos")
            db.close()
            return
        
        logger.info("Criando regras de exemplo...")
        
        # Regra 1: Reencaminhar mensagens de um número específico
        rule1 = ForwardingRule(
            name="Reencaminhar Mensagens do Chefe",
            description="Reencaminha todas as mensagens vindas do número do chefe para o assistente",
            rule_type=ForwardingRuleType.SENDER_BASED,
            action=ForwardingRuleAction.FORWARD,
            sender_pattern="+55 11 99999-0001",
            forward_to_numbers=json.dumps(["+55 11 88888-0001"]),
            is_active=True,
            priority=10
        )
        
        # Regra 2: Bloquear palavrões
        rule2 = ForwardingRule(
            name="Bloquear Palavrões",
            description="Bloqueia mensagens que contenham palavras ofensivas",
            rule_type=ForwardingRuleType.BLOCK_KEYWORD,
            action=ForwardingRuleAction.BLOCK,
            keyword_pattern="spam, lixo, ofensivo",
            case_sensitive=False,
            whole_word_only=False,
            is_active=True,
            priority=20
        )
        
        # Regra 3: Reencaminhar mensagens urgentes
        rule3 = ForwardingRule(
            name="Mensagens Urgentes",
            description="Reencaminha mensagens que contenham palavras-chave de urgência",
            rule_type=ForwardingRuleType.KEYWORD_BASED,
            action=ForwardingRuleAction.FORWARD,
            keyword_pattern="urgente, emergência, importante",
            forward_to_numbers=json.dumps(["+55 11 77777-0001", "+55 11 77777-0002"]),
            case_sensitive=False,
            whole_word_only=False,
            is_active=True,
            priority=15
        )
        
        # Regra 4: Deletar mensagens de spam
        rule4 = ForwardingRule(
            name="Deletar Spam",
            description="Remove automaticamente mensagens identificadas como spam",
            rule_type=ForwardingRuleType.BLOCK_KEYWORD,
            action=ForwardingRuleAction.DELETE,
            keyword_pattern="promoção, desconto, ganhe dinheiro, clique aqui",
            case_sensitive=False,
            whole_word_only=False,
            is_active=False,  # Desabilitada por padrão por ser uma ação destrutiva
            priority=5
        )
        
        # Adicionar regras ao banco
        db.add_all([rule1, rule2, rule3, rule4])
        db.commit()
        
        logger.info("✅ 4 regras de exemplo criadas com sucesso!")
        db.close()
        
    except Exception as e:
        logger.error(f"Erro ao criar regras de exemplo: {str(e)}")

if __name__ == "__main__":
    run_migration()
