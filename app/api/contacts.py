"""
API endpoints para gestão de contactos
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Contact, ContactGroup, ContactGroupMember
from app.api.schemas import (
    ContactCreate, ContactUpdate, ContactResponse,
    ContactGroupCreate, ContactGroupUpdate, ContactGroupResponse, ContactGroupWithMembers,
    ContactGroupMemberCreate, ContactGroupMemberResponse,
    MessageResponse
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["contacts"])

# ========== CONTACTOS ==========

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """Criar novo contacto"""
    try:
        logger.info(f"Tentativa de criar contacto: {contact_data.name}")
        
        # Verificar se já existe contacto com o mesmo nome
        existing = db.query(Contact).filter(Contact.name == contact_data.name).first()
        if existing:
            logger.warning(f"Contacto já existe: {contact_data.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um contacto com este nome"
            )
        
        contact = Contact(
            name=contact_data.name,
            description=contact_data.description,
            phone1=contact_data.phone1,
            phone2=contact_data.phone2,
            phone3=contact_data.phone3,
            is_favorite=contact_data.is_favorite or False
        )
        
        logger.info(f"Contacto criado em memória: {contact}")
        db.add(contact)
        logger.info("Contacto adicionado à sessão")
        
        db.commit()
        logger.info("Commit realizado")
        
        db.refresh(contact)
        logger.info(f"Contacto atualizado após commit: ID={contact.id}")
        
        # Verificar se realmente foi salvo
        saved_contact = db.query(Contact).filter(Contact.id == contact.id).first()
        if saved_contact:
            logger.info(f"Contacto confirmado no banco: {saved_contact.name}")
        else:
            logger.error("Contacto NÃO encontrado no banco após commit!")
        
        logger.info(f"Contacto criado com sucesso: {contact.name} (ID: {contact.id})")
        return ContactResponse.from_orm(contact)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    active_only: bool = True,
    favorites_only: bool = False,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Listar contactos"""
    try:
        query = db.query(Contact)
        
        if active_only:
            query = query.filter(Contact.is_active == True)
        
        if favorites_only:
            query = query.filter(Contact.is_favorite == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Contact.name.ilike(search_term)) |
                (Contact.phone1.ilike(search_term)) |
                (Contact.phone2.ilike(search_term)) |
                (Contact.phone3.ilike(search_term))
            )
        
        contacts = query.order_by(Contact.name.asc()).offset(offset).limit(limit).all()
        
        return [ContactResponse.from_orm(contact) for contact in contacts]
        
    except Exception as e:
        logger.error(f"Erro ao listar contactos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Obter contacto por ID"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto não encontrado"
        )
    
    return ContactResponse.from_orm(contact)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar contacto"""
    try:
        logger.info(f"Tentativa de atualizar contacto ID: {contact_id}, dados: {contact_data.dict(exclude_unset=True)}")
        
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            logger.warning(f"Contacto não encontrado: ID {contact_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        # Verificar se nome já existe (se estiver a ser alterado)
        if contact_data.name and contact_data.name != contact.name:
            existing = db.query(Contact).filter(
                Contact.name == contact_data.name,
                Contact.id != contact_id
            ).first()
            if existing:
                logger.warning(f"Nome já existe: {contact_data.name}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um contacto com este nome"
                )
        
        # Atualizar campos
        update_data = contact_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            logger.info(f"Atualizando campo {field}: {getattr(contact, field)} -> {value}")
            setattr(contact, field, value)
        
        # Forçar atualização do timestamp
        from datetime import datetime
        contact.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Contacto atualizado com sucesso: {contact.name} (ID: {contact.id})")
        return ContactResponse.from_orm(contact)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/{contact_id}", response_model=MessageResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Excluir contacto"""
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        # Remover das associações de grupos
        db.query(ContactGroupMember).filter(ContactGroupMember.contact_id == contact_id).delete()
        
        # Excluir contacto
        db.delete(contact)
        db.commit()
        
        logger.info(f"Contacto excluído: {contact.name}")
        return MessageResponse(message="Contacto excluído com sucesso")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir contacto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# ========== GRUPOS ==========

@router.post("/groups", response_model=ContactGroupResponse)
async def create_group(
    group_data: ContactGroupCreate,
    db: Session = Depends(get_db)
):
    """Criar novo grupo de contactos"""
    try:
        # Verificar se já existe grupo com o mesmo nome
        existing = db.query(ContactGroup).filter(ContactGroup.name == group_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um grupo com este nome"
            )
        
        group = ContactGroup(
            name=group_data.name,
            description=group_data.description,
            color=group_data.color or "#007bff"
        )
        
        db.add(group)
        db.commit()
        db.refresh(group)
        
        logger.info(f"Grupo criado: {group.name}")
        return ContactGroupResponse.from_orm(group)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/groups", response_model=List[ContactGroupResponse])
async def list_groups(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Listar grupos de contactos"""
    try:
        query = db.query(ContactGroup)
        
        if active_only:
            query = query.filter(ContactGroup.is_active == True)
        
        groups = query.order_by(ContactGroup.name.asc()).all()
        
        return [ContactGroupResponse.from_orm(group) for group in groups]
        
    except Exception as e:
        logger.error(f"Erro ao listar grupos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/groups/{group_id}", response_model=ContactGroupWithMembers)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """Obter grupo com membros"""
    group = db.query(ContactGroup).filter(ContactGroup.id == group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo não encontrado"
        )
    
    # Carregar membros
    members = db.query(Contact).join(ContactGroupMember).filter(
        ContactGroupMember.group_id == group_id,
        Contact.is_active == True
    ).all()
    
    group_response = ContactGroupWithMembers.from_orm(group)
    group_response.members = [ContactResponse.from_orm(member) for member in members]
    
    return group_response

@router.put("/groups/{group_id}", response_model=ContactGroupResponse)
async def update_group(
    group_id: int,
    group_data: ContactGroupUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar grupo"""
    try:
        group = db.query(ContactGroup).filter(ContactGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado"
            )
        
        # Verificar se nome já existe (se estiver a ser alterado)
        if group_data.name and group_data.name != group.name:
            existing = db.query(ContactGroup).filter(
                ContactGroup.name == group_data.name,
                ContactGroup.id != group_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe um grupo com este nome"
                )
        
        # Atualizar campos
        for field, value in group_data.dict(exclude_unset=True).items():
            setattr(group, field, value)
        
        db.commit()
        db.refresh(group)
        
        logger.info(f"Grupo atualizado: {group.name}")
        return ContactGroupResponse.from_orm(group)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar grupo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/groups/{group_id}", response_model=MessageResponse)
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Excluir grupo"""
    try:
        group = db.query(ContactGroup).filter(ContactGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado"
            )
        
        # Remover membros do grupo
        db.query(ContactGroupMember).filter(ContactGroupMember.group_id == group_id).delete()
        
        # Excluir grupo
        db.delete(group)
        db.commit()
        
        logger.info(f"Grupo excluído: {group.name}")
        return MessageResponse(message="Grupo excluído com sucesso")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir grupo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# ========== MEMBROS DE GRUPOS ==========

@router.post("/groups/{group_id}/members/{contact_id}", response_model=MessageResponse)
async def add_contact_to_group(
    group_id: int,
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Adicionar contacto ao grupo"""
    try:
        # Verificar se grupo existe
        group = db.query(ContactGroup).filter(ContactGroup.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grupo não encontrado"
            )
        
        # Verificar se contacto existe
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não encontrado"
            )
        
        # Verificar se já está no grupo
        existing = db.query(ContactGroupMember).filter(
            ContactGroupMember.group_id == group_id,
            ContactGroupMember.contact_id == contact_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contacto já está neste grupo"
            )
        
        # Adicionar ao grupo
        member = ContactGroupMember(
            group_id=group_id,
            contact_id=contact_id
        )
        
        db.add(member)
        db.commit()
        
        logger.info(f"Contacto {contact.name} adicionado ao grupo {group.name}")
        return MessageResponse(message=f"Contacto adicionado ao grupo com sucesso")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar contacto ao grupo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/groups/{group_id}/members/{contact_id}", response_model=MessageResponse)
async def remove_contact_from_group(
    group_id: int,
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Remover contacto do grupo"""
    try:
        member = db.query(ContactGroupMember).filter(
            ContactGroupMember.group_id == group_id,
            ContactGroupMember.contact_id == contact_id
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contacto não está neste grupo"
            )
        
        db.delete(member)
        db.commit()
        
        logger.info(f"Contacto removido do grupo")
        return MessageResponse(message="Contacto removido do grupo com sucesso")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover contacto do grupo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
