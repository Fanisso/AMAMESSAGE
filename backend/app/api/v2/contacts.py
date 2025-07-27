"""
Endpoints de Contactos - API v2
Gestão completa de contactos com grupos, importação/exportação
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import csv
import io
import tempfile
import os

# Imports dos componentes compartilhados
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.schemas import (
    ContactCreate, ContactUpdate, ContactResponse, ContactListResponse,
    PaginationQuery, SearchQuery
)
from shared.constants import MAX_CONTACTS_PER_USER
from shared.utils import validate_phone_number

# Imports locais
from ...db.database import get_db
from ...db.models import User, Contact
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria novo contacto.
    
    - **name**: Nome do contacto (obrigatório)
    - **phone**: Número de telefone (obrigatório, formato internacional)
    - **email**: Email (opcional)
    - **group**: Grupo do contacto (opcional)
    - **notes**: Observações (opcional)
    """
    try:
        # Verificar limite de contactos
        contact_count = db.query(Contact).filter(Contact.user_id == current_user.id).count()
        if contact_count >= MAX_CONTACTS_PER_USER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limite máximo de {MAX_CONTACTS_PER_USER} contactos atingido"
            )
        
        # Verificar se número já existe para este usuário
        existing_phone = db.query(Contact).filter(
            Contact.user_id == current_user.id,
            Contact.phone == contact_data.phone
        ).first()
        
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um contacto com este número de telefone"
            )
        
        # Verificar se email já existe para este usuário (se fornecido)
        if contact_data.email:
            existing_email = db.query(Contact).filter(
                Contact.user_id == current_user.id,
                Contact.email == contact_data.email
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um contacto com este email"
                )
        
        # Criar novo contacto
        new_contact = Contact(
            user_id=current_user.id,
            name=contact_data.name,
            phone=contact_data.phone,
            email=contact_data.email,
            group=contact_data.group,
            notes=contact_data.notes,
            created_at=datetime.utcnow()
        )
        
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        
        logger.info(f"Contacto criado: {new_contact.id} - {new_contact.name}")
        
        return ContactResponse(
            id=new_contact.id,
            name=new_contact.name,
            phone=new_contact.phone,
            email=new_contact.email,
            group=new_contact.group,
            notes=new_contact.notes,
            is_blocked=new_contact.is_blocked,
            created_at=new_contact.created_at,
            updated_at=new_contact.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/", response_model=ContactListResponse)
async def list_contacts(
    page: int = Query(1, ge=1, description="Número da página"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página"),
    search: Optional[str] = Query(None, description="Buscar por nome ou telefone"),
    group: Optional[str] = Query(None, description="Filtrar por grupo"),
    is_blocked: Optional[bool] = Query(None, description="Filtrar por status bloqueado"),
    sort_by: Optional[str] = Query("name", description="Campo para ordenação"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Ordem"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista contactos do usuário com paginação, busca e filtros.
    
    - **page**: Número da página (inicia em 1)
    - **per_page**: Items por página (1-100)
    - **search**: Buscar por nome ou telefone
    - **group**: Filtrar por grupo específico
    - **is_blocked**: Filtrar por status de bloqueio
    - **sort_by**: Campo para ordenação (name, phone, created_at)
    - **sort_order**: Ordem de classificação (asc/desc)
    """
    try:
        # Construir query base
        query = db.query(Contact).filter(Contact.user_id == current_user.id)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                db.or_(
                    Contact.name.contains(search),
                    Contact.phone.contains(search)
                )
            )
        
        if group:
            query = query.filter(Contact.group == group)
        
        if is_blocked is not None:
            query = query.filter(Contact.is_blocked == is_blocked)
        
        # Contar total
        total = query.count()
        
        # Aplicar ordenação
        if sort_by == "name":
            order_field = Contact.name
        elif sort_by == "phone":
            order_field = Contact.phone
        elif sort_by == "created_at":
            order_field = Contact.created_at
        else:
            order_field = Contact.name
        
        if sort_order == "desc":
            order_field = order_field.desc()
        
        # Aplicar paginação
        contacts = query.order_by(order_field)\
                       .offset((page - 1) * per_page)\
                       .limit(per_page)\
                       .all()
        
        # Preparar response
        contact_responses = []
        for contact in contacts:
            contact_responses.append(ContactResponse(
                id=contact.id,
                name=contact.name,
                phone=contact.phone,
                email=contact.email,
                group=contact.group,
                notes=contact.notes,
                is_blocked=contact.is_blocked,
                created_at=contact.created_at,
                updated_at=contact.updated_at
            ))
        
        return ContactListResponse(
            contacts=contact_responses,
            total=total,
            page=page,
            per_page=per_page,
            has_next=total > page * per_page
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar contactos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém detalhes de um contacto específico.
    
    - **contact_id**: ID único do contacto
    """
    try:
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        return ContactResponse(
            id=contact.id,
            name=contact.name,
            phone=contact.phone,
            email=contact.email,
            group=contact.group,
            notes=contact.notes,
            is_blocked=contact.is_blocked,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza contacto existente.
    
    - **contact_id**: ID único do contacto
    - **name**: Nome do contacto (opcional)
    - **phone**: Número de telefone (opcional)
    - **email**: Email (opcional)
    - **group**: Grupo do contacto (opcional)
    - **notes**: Observações (opcional)
    - **is_blocked**: Status de bloqueio (opcional)
    """
    try:
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        # Verificar se novo telefone já existe (se foi alterado)
        if contact_update.phone and contact_update.phone != contact.phone:
            if not validate_phone_number(contact_update.phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Número de telefone inválido"
                )
                
            existing_phone = db.query(Contact).filter(
                Contact.user_id == current_user.id,
                Contact.phone == contact_update.phone,
                Contact.id != contact_id
            ).first()
            
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um contacto com este número de telefone"
                )
        
        # Verificar se novo email já existe (se foi alterado)
        if contact_update.email and contact_update.email != contact.email:
            existing_email = db.query(Contact).filter(
                Contact.user_id == current_user.id,
                Contact.email == contact_update.email,
                Contact.id != contact_id
            ).first()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um contacto com este email"
                )
        
        # Atualizar campos
        update_data = contact_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        contact.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Contacto atualizado: {contact.id} - {contact.name}")
        
        return ContactResponse(
            id=contact.id,
            name=contact.name,
            phone=contact.phone,
            email=contact.email,
            group=contact.group,
            notes=contact.notes,
            is_blocked=contact.is_blocked,
            created_at=contact.created_at,
            updated_at=contact.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove contacto.
    
    - **contact_id**: ID único do contacto
    """
    try:
        contact = db.query(Contact).filter(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        contact_name = contact.name
        db.delete(contact)
        db.commit()
        
        logger.info(f"Contacto removido: {contact_id} - {contact_name}")
        
        return {
            "success": True,
            "message": "Contacto removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/import")
async def import_contacts(
    file: UploadFile = File(...),
    overwrite: bool = Query(False, description="Substituir contactos existentes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Importa contactos de arquivo CSV.
    
    - **file**: Arquivo CSV com contactos
    - **overwrite**: Se deve substituir contactos existentes
    
    Formato CSV esperado: name,phone,email,group,notes
    """
    try:
        # Verificar tipo de arquivo
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos CSV são suportados"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse do CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Linha 2 (após header)
            try:
                # Validar campos obrigatórios
                if not row.get('name') or not row.get('phone'):
                    errors.append(f"Linha {row_num}: Nome e telefone são obrigatórios")
                    error_count += 1
                    continue
                
                # Validar telefone
                phone = row['phone'].strip()
                if not validate_phone_number(phone):
                    errors.append(f"Linha {row_num}: Número de telefone inválido - {phone}")
                    error_count += 1
                    continue
                
                # Verificar se contacto já existe
                existing_contact = db.query(Contact).filter(
                    Contact.user_id == current_user.id,
                    Contact.phone == phone
                ).first()
                
                if existing_contact:
                    if overwrite:
                        # Atualizar contacto existente
                        existing_contact.name = row['name'].strip()
                        existing_contact.email = row.get('email', '').strip() or None
                        existing_contact.group = row.get('group', '').strip() or None
                        existing_contact.notes = row.get('notes', '').strip() or None
                        existing_contact.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        errors.append(f"Linha {row_num}: Contacto já existe - {phone}")
                        error_count += 1
                        continue
                else:
                    # Verificar limite de contactos
                    contact_count = db.query(Contact).filter(Contact.user_id == current_user.id).count()
                    if contact_count >= MAX_CONTACTS_PER_USER:
                        errors.append(f"Limite máximo de {MAX_CONTACTS_PER_USER} contactos atingido")
                        break
                    
                    # Criar novo contacto
                    new_contact = Contact(
                        user_id=current_user.id,
                        name=row['name'].strip(),
                        phone=phone,
                        email=row.get('email', '').strip() or None,
                        group=row.get('group', '').strip() or None,
                        notes=row.get('notes', '').strip() or None,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_contact)
                    imported_count += 1
                
            except Exception as e:
                errors.append(f"Linha {row_num}: Erro - {str(e)}")
                error_count += 1
        
        # Commit das alterações
        db.commit()
        
        logger.info(f"Importação de contactos: {imported_count} novos, {updated_count} atualizados, {error_count} erros")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "updated_count": updated_count,
            "error_count": error_count,
            "errors": errors[:10]  # Limitar a 10 erros na response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na importação de contactos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/export/csv")
async def export_contacts_csv(
    group: Optional[str] = Query(None, description="Exportar apenas grupo específico"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exporta contactos para arquivo CSV.
    
    - **group**: Exportar apenas contactos de um grupo específico
    """
    try:
        # Construir query
        query = db.query(Contact).filter(Contact.user_id == current_user.id)
        
        if group:
            query = query.filter(Contact.group == group)
        
        contacts = query.all()
        
        # Criar arquivo CSV temporário
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8')
        
        writer = csv.writer(temp_file)
        
        # Header
        writer.writerow(['name', 'phone', 'email', 'group', 'notes', 'is_blocked', 'created_at'])
        
        # Dados
        for contact in contacts:
            writer.writerow([
                contact.name,
                contact.phone,
                contact.email or '',
                contact.group or '',
                contact.notes or '',
                contact.is_blocked,
                contact.created_at.isoformat()
            ])
        
        temp_file.close()
        
        # Definir nome do arquivo
        filename = f"contactos_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        if group:
            filename = f"contactos_{group}_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        logger.info(f"Exportação de contactos: {len(contacts)} contactos")
        
        return FileResponse(
            path=temp_file.name,
            filename=filename,
            media_type='text/csv',
            background=lambda: os.unlink(temp_file.name)  # Remover arquivo após download
        )
        
    except Exception as e:
        logger.error(f"Erro na exportação de contactos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/groups/list")
async def list_contact_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os grupos de contactos do usuário.
    """
    try:
        # Query para grupos únicos
        groups = db.query(Contact.group, db.func.count(Contact.id).label('count'))\
                   .filter(
                       Contact.user_id == current_user.id,
                       Contact.group.isnot(None),
                       Contact.group != ''
                   )\
                   .group_by(Contact.group)\
                   .order_by(Contact.group)\
                   .all()
        
        return {
            "groups": [
                {
                    "name": group,
                    "contact_count": count
                }
                for group, count in groups
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar grupos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/bulk-action")
async def bulk_contact_action(
    action_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa ação em lote em contactos.
    
    - **contact_ids**: Lista de IDs dos contactos
    - **action**: Ação a executar (block, unblock, delete, set_group)
    - **value**: Valor para ação (usado para set_group)
    """
    try:
        contact_ids = action_data.get('contact_ids', [])
        action = action_data.get('action')
        value = action_data.get('value')
        
        if not contact_ids or not action:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IDs dos contactos e ação são obrigatórios"
            )
        
        # Buscar contactos
        contacts = db.query(Contact).filter(
            Contact.id.in_(contact_ids),
            Contact.user_id == current_user.id
        ).all()
        
        if not contacts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum contacto encontrado"
            )
        
        affected_count = 0
        
        # Executar ação
        if action == 'block':
            for contact in contacts:
                contact.is_blocked = True
                contact.updated_at = datetime.utcnow()
                affected_count += 1
        
        elif action == 'unblock':
            for contact in contacts:
                contact.is_blocked = False
                contact.updated_at = datetime.utcnow()
                affected_count += 1
        
        elif action == 'delete':
            for contact in contacts:
                db.delete(contact)
                affected_count += 1
        
        elif action == 'set_group':
            if value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Valor do grupo é obrigatório para esta ação"
                )
            
            for contact in contacts:
                contact.group = value if value else None
                contact.updated_at = datetime.utcnow()
                affected_count += 1
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ação inválida"
            )
        
        db.commit()
        
        logger.info(f"Ação em lote executada: {action} em {affected_count} contactos")
        
        return {
            "success": True,
            "action": action,
            "affected_count": affected_count,
            "message": f"Ação '{action}' executada em {affected_count} contactos"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na ação em lote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

__all__ = ["router"]
