from typing import List

from fastapi import APIRouter, HTTPException, status

from app.core.auth import AgentDependency
from app.core.session import DBdependency
from app.models.chatModels import ChatSession, ChatMessage
from app.models.validators import ChatMessageCreate, ChatSessionResponse, ChatMessageResponse

router = APIRouter()


@router.get("/")
async def get_new_chat(db: DBdependency, user: AgentDependency):
    try:
        new_session = ChatSession(
            user_id=user.employee_id,
            chat_title="New Session"
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        resp = {
            "new_id": new_session.chat_id
        }
        return resp
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Chat Session Creation failed."
        )


@router.post("/")
async def add_chat_message(chat_message: ChatMessageCreate,db: DBdependency, user: AgentDependency):
    try:
        new_message = ChatMessage(**chat_message.model_dump())
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Chat Message Creation failed."
        )


@router.get("/sessions",response_model=List[ChatSessionResponse])
async def get_user_chats(db: DBdependency, user: AgentDependency):
    try:
        chats = db.query(ChatSession).filter(ChatSession.user_id == user.employee_id).all()
        return chats
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Cannot fetch previous sessions"
        )


@router.get("/messages/{chat_id}",response_model=List[ChatMessageResponse])
async def get_chat_messages(chat_id: int, db: DBdependency, user: AgentDependency):
    try:
        messages = db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id)\
            .order_by(ChatMessage.created_at.asc()).all()
        return messages
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database Error! Cannot fetch previous messages"
        )

