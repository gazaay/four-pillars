import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai_model_service import ai_model_service
from app.services.database_service import db_service
from app.database.models import ChatSession, ChatMessage, User
from app.utils.exceptions import NotFoundException, UnauthorizedException
from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat-related logic."""
    
    async def create_session(
        self, 
        db: AsyncSession, 
        user_id: UUID,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new chat session.
        
        Args:
            db: Database session
            user_id: User ID
            title: Optional session title
            
        Returns:
            Dictionary with session information
        """
        try:
            # Create a new chat session
            session = await db_service.create_chat_session(
                db=db,
                user_id=user_id,
                title=title or "New Chat"
            )
            
            # Add a system message to initialize the chat
            system_message = (
                "Welcome to the Four Pillars Health AI assistant. "
                "I can provide health information, explain health policies, "
                "and help you manage your medical history. What can I help you with today?"
            )
            
            await db_service.add_chat_message(
                db=db,
                session_id=session.id,
                role="system",
                content=system_message
            )
            
            return {
                "session_id": str(session.id),
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "welcome_message": system_message
            }
        except Exception as e:
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    async def get_chat_history(
        self, 
        db: AsyncSession, 
        session_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get the chat history for a session.
        
        Args:
            db: Database session
            session_id: Chat session ID
            user_id: User ID requesting the history (for authorization)
            
        Returns:
            Dictionary with session information and messages
        """
        # Get the chat session with messages
        session = await db_service.get_chat_session(db, session_id)
        
        if not session:
            raise NotFoundException(f"Chat session {session_id} not found")
        
        # Check if the user is authorized to access this session
        if session.user_id != user_id:
            raise UnauthorizedException("You are not authorized to access this chat session")
        
        # Format the response
        messages = [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "model": msg.model
            }
            for msg in session.messages
        ]
        
        return {
            "session_id": str(session.id),
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": messages
        }
    
    async def process_message(
        self, 
        db: AsyncSession, 
        session_id: UUID,
        user_id: UUID,
        message_content: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            db: Database session
            session_id: Chat session ID
            user_id: User ID sending the message
            message_content: Content of the user's message
            query_type: Optional type of query (medical_advice, policy, patient_history)
            
        Returns:
            Dictionary with the assistant's response
        """
        try:
            # Get the chat session
            session = await db_service.get_chat_session(db, session_id)
            
            if not session:
                raise NotFoundException(f"Chat session {session_id} not found")
            
            # Check if the user is authorized to access this session
            if session.user_id != user_id:
                raise UnauthorizedException("You are not authorized to access this chat session")
            
            # Add the user message to the database
            user_message = await db_service.add_chat_message(
                db=db,
                session_id=session_id,
                role="user",
                content=message_content
            )
            
            # Prepare the message history for the AI
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in session.messages
                if msg.role in ["user", "assistant", "system"]
            ]
            
            # Determine query type if not provided
            if not query_type:
                query_type = await self._classify_query(message_content)
            
            # Get user profile for context
            user = await db_service.get_user_by_id(db, user_id)
            patient_profile = await db_service.get_patient_profile(db, user_id)
            
            # Process the message based on query type
            response = None
            if query_type == "medical_advice":
                # Get relevant patient info if available
                patient_info = None
                if patient_profile:
                    patient_info = {
                        "allergies": patient_profile.allergies,
                        "chronic_conditions": patient_profile.chronic_conditions,
                        "medical_history_summary": patient_profile.medical_history_summary
                    }
                
                # Get response from medical advice model
                response = await ai_model_service.get_medical_advice(
                    user_query=message_content,
                    chat_history=chat_history[-10:],  # Use last 10 messages for context
                    patient_info=patient_info
                )
                
            elif query_type == "policy":
                # Search for relevant policies
                policies, _ = await db_service.search_health_policies(
                    db=db,
                    query=message_content,
                    limit=5
                )
                
                # Format policy data for the model
                policy_data = None
                if policies:
                    policy_data = [
                        {
                            "name": policy.policy_name,
                            "category": policy.policy_category,
                            "text": policy.policy_text[:500] + "..." if len(policy.policy_text) > 500 else policy.policy_text,
                            "source": policy.source
                        }
                        for policy in policies
                    ]
                
                # Get response from policy expert model
                response = await ai_model_service.get_policy_information(
                    user_query=message_content,
                    chat_history=chat_history[-10:],
                    policy_data=policy_data
                )
                
            elif query_type == "patient_history":
                # Get patient records if available
                patient_history = {}
                if patient_profile:
                    records, _ = await db_service.get_medical_records(
                        db=db,
                        patient_id=patient_profile.id,
                        limit=20
                    )
                    
                    if records:
                        patient_history = {
                            "profile": {
                                "allergies": patient_profile.allergies,
                                "chronic_conditions": patient_profile.chronic_conditions,
                                "medical_history_summary": patient_profile.medical_history_summary
                            },
                            "records": [
                                {
                                    "type": record.record_type,
                                    "date": record.record_date.isoformat(),
                                    "description": record.description,
                                    "provider": record.provider
                                }
                                for record in records
                            ]
                        }
                
                # Get response from patient history model
                response = await ai_model_service.process_patient_history(
                    user_query=message_content,
                    patient_history=patient_history,
                    chat_history=chat_history[-10:]
                )
                
            else:
                # Use default chat model
                response = await ai_model_service.get_completion(
                    messages=chat_history[-10:] + [{"role": "user", "content": message_content}],
                    model_type="default"
                )
            
            # Add the assistant response to the database
            assistant_message = await db_service.add_chat_message(
                db=db,
                session_id=session_id,
                role="assistant",
                content=response["content"],
                model=response["model"],
                tokens_used=response.get("tokens_used"),
                metadata={
                    "query_type": query_type,
                    "processing_time": response.get("processing_time"),
                    "finish_reason": response.get("finish_reason")
                }
            )
            
            # Update the session title if it's the first user message
            if len(chat_history) <= 2:  # Only system welcome message and this user message
                # Generate a title from the first user message
                await self._update_session_title(db, session, message_content)
            
            return {
                "message_id": str(assistant_message.id),
                "content": assistant_message.content,
                "role": "assistant",
                "timestamp": assistant_message.timestamp.isoformat(),
                "model": assistant_message.model,
                "query_type": query_type
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            # Add an error message to the chat session
            try:
                error_message = f"I'm sorry, I encountered an error processing your message. Please try again."
                await db_service.add_chat_message(
                    db=db,
                    session_id=session_id,
                    role="assistant",
                    content=error_message,
                    metadata={"error": str(e)}
                )
                return {
                    "content": error_message,
                    "role": "assistant",
                    "timestamp": db.func.now(),
                    "error": str(e)
                }
            except:
                # If adding error message fails, just raise the original exception
                raise
    
    async def _classify_query(self, message: str) -> str:
        """
        Classify the type of query based on the message content.
        
        Args:
            message: The user's message
            
        Returns:
            Query type (medical_advice, policy, patient_history, or default)
        """
        # In a real implementation, this would use a more sophisticated classifier
        # For now, use simple keyword matching
        message_lower = message.lower()
        
        if any(term in message_lower for term in ["symptom", "disease", "condition", "diagnosis", "treatment", "medicine", "drug", "health advice"]):
            return "medical_advice"
        
        if any(term in message_lower for term in ["policy", "regulation", "law", "insurance", "coverage", "guideline", "rule"]):
            return "policy"
        
        if any(term in message_lower for term in ["history", "record", "my health", "my condition", "my treatment", "my medicine", "my doctor"]):
            return "patient_history"
        
        return "default"
    
    async def _update_session_title(
        self, 
        db: AsyncSession, 
        session: ChatSession, 
        first_message: str
    ) -> None:
        """
        Update the session title based on the first user message.
        
        Args:
            db: Database session
            session: Chat session to update
            first_message: The first user message
        """
        try:
            # Simple title generation logic - truncate the first message
            if len(first_message) > 50:
                title = first_message[:47] + "..."
            else:
                title = first_message
            
            # Update the session title
            session.title = title
            await db.commit()
            await db.refresh(session)
        except Exception as e:
            logger.error(f"Error updating session title: {str(e)}")
            # Non-critical error, just log it

# Create a global instance of the chat service
chat_service = ChatService() 