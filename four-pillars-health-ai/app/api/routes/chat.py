from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, UUID4
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database.database import get_db
from app.database.models import User
from app.services.chat_service import chat_service
from app.api.routes.users import get_current_user
from app.utils.exceptions import NotFoundException, UnauthorizedException

router = APIRouter()

# Pydantic models for request/response
class SessionCreate(BaseModel):
    title: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    welcome_message: Optional[str] = None

class SessionsListResponse(BaseModel):
    sessions: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1)
    query_type: Optional[str] = Field(None, description="Type of query (medical_advice, policy, patient_history)")

class MessageResponse(BaseModel):
    message_id: Optional[str] = None
    content: str
    role: str
    timestamp: str
    model: Optional[str] = None
    query_type: Optional[str] = None
    error: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]

# Routes
@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: SessionCreate = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new chat session.
    """
    session = await chat_service.create_session(
        db=db,
        user_id=current_user.id,
        title=session_data.title
    )
    return session

@router.get("/sessions", response_model=SessionsListResponse)
async def list_chat_sessions(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List chat sessions for the current user.
    """
    # Calculate offset for pagination
    offset = (page - 1) * page_size
    
    # Get sessions from database
    sessions, total = await chat_service.list_sessions(
        db=db,
        user_id=current_user.id,
        limit=page_size,
        offset=offset
    )
    
    return {
        "sessions": sessions,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/sessions/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the chat history for a session.
    """
    try:
        history = await chat_service.get_chat_history(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        return history
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e.detail))

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: UUID4,
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to a chat session and get a response.
    """
    try:
        response = await chat_service.process_message(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            message_content=message.content,
            query_type=message.query_type
        )
        return response
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a chat session.
    """
    try:
        await chat_service.delete_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e.detail))
    except UnauthorizedException as e:
        raise HTTPException(status_code=403, detail=str(e.detail))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.post("/ask", response_model=MessageResponse)
async def ask_one_off_question(
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ask a one-off question without creating a persistent chat session.
    """
    try:
        # Create a temporary session
        session = await chat_service.create_session(
            db=db,
            user_id=current_user.id,
            title="One-off Question"
        )
        
        # Process the message
        response = await chat_service.process_message(
            db=db,
            session_id=session['session_id'],
            user_id=current_user.id,
            message_content=message.content,
            query_type=message.query_type
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}") 