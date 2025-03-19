import logging
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload
from app.database.models import (
    User, PatientProfile, MedicalRecord, HealthPolicy,
    ChatSession, ChatMessage, MedicalKnowledgeBase
)
from app.utils.exceptions import NotFoundException, DatabaseException

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for interacting with the database."""
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        try:
            result = await db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def get_user_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def get_patient_profile(self, db: AsyncSession, user_id: UUID) -> Optional[PatientProfile]:
        """Get a patient profile by user ID."""
        try:
            result = await db.execute(
                select(PatientProfile).where(PatientProfile.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting patient profile: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def get_medical_records(
        self, 
        db: AsyncSession, 
        patient_id: UUID,
        record_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[MedicalRecord], int]:
        """
        Get medical records for a patient.
        
        Args:
            db: Database session
            patient_id: Patient ID
            record_type: Optional filter by record type
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of medical records, total count)
        """
        try:
            # Build query
            query = select(MedicalRecord).where(MedicalRecord.patient_id == patient_id)
            
            # Add filters if provided
            if record_type:
                query = query.where(MedicalRecord.record_type == record_type)
            
            # Get count of total records
            count_query = select(db.func.count()).select_from(query.subquery())
            count_result = await db.execute(count_query)
            total_count = count_result.scalar_one()
            
            # Add limit and offset for pagination
            query = query.order_by(MedicalRecord.record_date.desc())
            query = query.limit(limit).offset(offset)
            
            # Execute query
            result = await db.execute(query)
            records = result.scalars().all()
            
            return records, total_count
        except Exception as e:
            logger.error(f"Error getting medical records: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def get_chat_session(self, db: AsyncSession, session_id: UUID) -> Optional[ChatSession]:
        """
        Get a chat session by ID, including its messages.
        
        Args:
            db: Database session
            session_id: Chat session ID
            
        Returns:
            Chat session with messages, or None if not found
        """
        try:
            result = await db.execute(
                select(ChatSession)
                .where(ChatSession.id == session_id)
                .options(selectinload(ChatSession.messages))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting chat session: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def get_user_chat_sessions(
        self, 
        db: AsyncSession, 
        user_id: UUID,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[ChatSession], int]:
        """
        Get chat sessions for a user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of sessions to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of chat sessions, total count)
        """
        try:
            # Get count of total sessions
            count_query = select(db.func.count(ChatSession.id)).where(
                ChatSession.user_id == user_id
            )
            count_result = await db.execute(count_query)
            total_count = count_result.scalar_one()
            
            # Get the sessions with pagination
            query = (
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await db.execute(query)
            sessions = result.scalars().all()
            
            return sessions, total_count
        except Exception as e:
            logger.error(f"Error getting user chat sessions: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def create_chat_session(
        self, 
        db: AsyncSession, 
        user_id: UUID,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            db: Database session
            user_id: User ID
            title: Optional session title
            metadata: Optional session metadata
            
        Returns:
            The created chat session
        """
        try:
            # Create a new chat session
            new_session = ChatSession(
                user_id=user_id,
                title=title,
                metadata=metadata
            )
            
            # Add to the database and commit
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            
            return new_session
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating chat session: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def add_chat_message(
        self,
        db: AsyncSession,
        session_id: UUID,
        role: str,
        content: str,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Add a message to a chat session.
        
        Args:
            db: Database session
            session_id: Chat session ID
            role: Message role (user, assistant, system)
            content: Message content
            model: Optional AI model used
            tokens_used: Optional token count
            metadata: Optional message metadata
            
        Returns:
            The created chat message
        """
        try:
            # Create a new chat message
            new_message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                model=model,
                tokens_used=tokens_used,
                metadata=metadata
            )
            
            # Add to the database and commit
            db.add(new_message)
            await db.commit()
            await db.refresh(new_message)
            
            # Update the chat session updated_at timestamp
            await db.execute(
                update(ChatSession)
                .where(ChatSession.id == session_id)
                .values(updated_at=db.func.now())
            )
            await db.commit()
            
            return new_message
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding chat message: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def search_health_policies(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[HealthPolicy], int]:
        """
        Search health policies by text query.
        
        Args:
            db: Database session
            query: Search query
            category: Optional policy category filter
            limit: Maximum number of policies to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of health policies, total count)
        """
        try:
            # Simple text search for now - in a real app, this would use 
            # full-text search capabilities or vector embeddings
            search_term = f"%{query}%"
            
            # Build the base query
            base_query = (
                select(HealthPolicy)
                .where(
                    (HealthPolicy.policy_text.ilike(search_term)) |
                    (HealthPolicy.policy_name.ilike(search_term))
                )
                .where(HealthPolicy.is_active == True)
            )
            
            # Add category filter if provided
            if category:
                base_query = base_query.where(HealthPolicy.policy_category == category)
            
            # Get count of total matching policies
            count_query = select(db.func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total_count = count_result.scalar_one()
            
            # Add pagination
            query = base_query.order_by(HealthPolicy.updated_at.desc()).limit(limit).offset(offset)
            result = await db.execute(query)
            policies = result.scalars().all()
            
            return policies, total_count
        except Exception as e:
            logger.error(f"Error searching health policies: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")
    
    async def search_medical_knowledge(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[MedicalKnowledgeBase], int]:
        """
        Search medical knowledge base by text query.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results to return
            offset: Offset for pagination
            
        Returns:
            Tuple of (list of medical knowledge entries, total count)
        """
        try:
            # Simple text search for now - in a real app, this would use 
            # full-text search or vector search for better results
            search_term = f"%{query}%"
            
            # Build the base query
            base_query = (
                select(MedicalKnowledgeBase)
                .where(
                    (MedicalKnowledgeBase.topic.ilike(search_term)) |
                    (MedicalKnowledgeBase.content.ilike(search_term))
                )
            )
            
            # Get count of total matching entries
            count_query = select(db.func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total_count = count_result.scalar_one()
            
            # Add pagination
            query = base_query.order_by(MedicalKnowledgeBase.topic).limit(limit).offset(offset)
            result = await db.execute(query)
            entries = result.scalars().all()
            
            return entries, total_count
        except Exception as e:
            logger.error(f"Error searching medical knowledge: {str(e)}")
            raise DatabaseException(f"Database error: {str(e)}")

# Create a global instance of the database service
db_service = DatabaseService() 