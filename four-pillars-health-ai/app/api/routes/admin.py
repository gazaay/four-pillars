from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, UUID4
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database.database import get_db
from app.database.models import User, HealthPolicy, MedicalKnowledgeBase
from app.api.routes.users import get_current_user
from app.utils.exceptions import NotFoundException, UnauthorizedException

router = APIRouter()

# Pydantic models for request/response
class HealthPolicyCreate(BaseModel):
    policy_name: str = Field(..., min_length=3, max_length=255)
    policy_category: str = Field(..., min_length=3, max_length=100)
    policy_text: str = Field(..., min_length=10)
    source: str = Field(..., min_length=3, max_length=255)
    source_url: Optional[str] = Field(None, max_length=255)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None

class HealthPolicyResponse(BaseModel):
    id: UUID4
    policy_name: str
    policy_category: str
    policy_text: str
    source: str
    source_url: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class MedicalKnowledgeCreate(BaseModel):
    topic: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    source: Optional[str] = Field(None, max_length=255)
    source_url: Optional[str] = Field(None, max_length=255)
    is_verified: bool = False
    verified_by: Optional[str] = None

class MedicalKnowledgeResponse(BaseModel):
    id: UUID4
    topic: str
    content: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_verified: bool
    verified_by: Optional[str] = None

# Helper function to check if user is admin
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Get current user and verify they are an admin."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform admin operations"
        )
    return current_user

# Routes for health policy management
@router.post("/policies", response_model=HealthPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_health_policy(
    policy_data: HealthPolicyCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new health policy (admin only).
    """
    # Create a new health policy
    new_policy = HealthPolicy(
        policy_name=policy_data.policy_name,
        policy_category=policy_data.policy_category,
        policy_text=policy_data.policy_text,
        source=policy_data.source,
        source_url=policy_data.source_url,
        effective_date=policy_data.effective_date,
        expiration_date=policy_data.expiration_date,
        is_active=True
    )
    
    # Add policy to database
    db.add(new_policy)
    await db.commit()
    await db.refresh(new_policy)
    
    return new_policy

@router.get("/policies", response_model=List[HealthPolicyResponse])
async def list_health_policies(
    category: Optional[str] = None,
    active_only: bool = True,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List health policies, with optional filtering (admin only).
    """
    # Build the query
    query = db.query(HealthPolicy)
    
    # Apply filters
    if category:
        query = query.filter(HealthPolicy.policy_category == category)
    if active_only:
        query = query.filter(HealthPolicy.is_active == True)
    
    # Execute query
    result = await db.execute(query.order_by(HealthPolicy.policy_name))
    policies = result.scalars().all()
    
    return policies

@router.get("/policies/{policy_id}", response_model=HealthPolicyResponse)
async def get_health_policy(
    policy_id: UUID4,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific health policy by ID (admin only).
    """
    # Get the policy
    result = await db.execute(db.query(HealthPolicy).filter(HealthPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health policy not found"
        )
    
    return policy

@router.put("/policies/{policy_id}", response_model=HealthPolicyResponse)
async def update_health_policy(
    policy_id: UUID4,
    policy_data: HealthPolicyCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a health policy (admin only).
    """
    # Get the policy
    result = await db.execute(db.query(HealthPolicy).filter(HealthPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health policy not found"
        )
    
    # Update policy fields
    for field, value in policy_data.dict().items():
        setattr(policy, field, value)
    
    # Update timestamp
    policy.updated_at = datetime.utcnow()
    
    # Save changes
    await db.commit()
    await db.refresh(policy)
    
    return policy

@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_policy(
    policy_id: UUID4,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a health policy (admin only).
    """
    # Get the policy
    result = await db.execute(db.query(HealthPolicy).filter(HealthPolicy.id == policy_id))
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health policy not found"
        )
    
    # Delete the policy
    await db.delete(policy)
    await db.commit()

# Routes for medical knowledge management
@router.post("/medical-knowledge", response_model=MedicalKnowledgeResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_knowledge(
    knowledge_data: MedicalKnowledgeCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add new medical knowledge entry (admin only).
    """
    # Create a new knowledge entry
    new_knowledge = MedicalKnowledgeBase(
        topic=knowledge_data.topic,
        content=knowledge_data.content,
        source=knowledge_data.source,
        source_url=knowledge_data.source_url,
        is_verified=knowledge_data.is_verified,
        verified_by=knowledge_data.verified_by or admin_user.full_name if knowledge_data.is_verified else None
    )
    
    # Add to database
    db.add(new_knowledge)
    await db.commit()
    await db.refresh(new_knowledge)
    
    return new_knowledge

@router.get("/medical-knowledge", response_model=List[MedicalKnowledgeResponse])
async def list_medical_knowledge(
    topic_filter: Optional[str] = None,
    verified_only: bool = False,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List medical knowledge entries, with optional filtering (admin only).
    """
    # Build the query
    query = db.query(MedicalKnowledgeBase)
    
    # Apply filters
    if topic_filter:
        query = query.filter(MedicalKnowledgeBase.topic.ilike(f"%{topic_filter}%"))
    if verified_only:
        query = query.filter(MedicalKnowledgeBase.is_verified == True)
    
    # Execute query
    result = await db.execute(query.order_by(MedicalKnowledgeBase.topic))
    entries = result.scalars().all()
    
    return entries

@router.get("/medical-knowledge/{knowledge_id}", response_model=MedicalKnowledgeResponse)
async def get_medical_knowledge(
    knowledge_id: UUID4,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific medical knowledge entry (admin only).
    """
    # Get the knowledge entry
    result = await db.execute(db.query(MedicalKnowledgeBase).filter(MedicalKnowledgeBase.id == knowledge_id))
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical knowledge entry not found"
        )
    
    return knowledge

@router.put("/medical-knowledge/{knowledge_id}", response_model=MedicalKnowledgeResponse)
async def update_medical_knowledge(
    knowledge_id: UUID4,
    knowledge_data: MedicalKnowledgeCreate,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a medical knowledge entry (admin only).
    """
    # Get the knowledge entry
    result = await db.execute(db.query(MedicalKnowledgeBase).filter(MedicalKnowledgeBase.id == knowledge_id))
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical knowledge entry not found"
        )
    
    # Update fields
    for field, value in knowledge_data.dict().items():
        setattr(knowledge, field, value)
    
    # Handle verification
    if knowledge_data.is_verified and not knowledge.is_verified:
        knowledge.verified_by = knowledge_data.verified_by or admin_user.full_name
    
    # Update timestamp
    knowledge.updated_at = datetime.utcnow()
    
    # Save changes
    await db.commit()
    await db.refresh(knowledge)
    
    return knowledge

@router.delete("/medical-knowledge/{knowledge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_knowledge(
    knowledge_id: UUID4,
    admin_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a medical knowledge entry (admin only).
    """
    # Get the knowledge entry
    result = await db.execute(db.query(MedicalKnowledgeBase).filter(MedicalKnowledgeBase.id == knowledge_id))
    knowledge = result.scalar_one_or_none()
    
    if not knowledge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical knowledge entry not found"
        )
    
    # Delete the entry
    await db.delete(knowledge)
    await db.commit() 