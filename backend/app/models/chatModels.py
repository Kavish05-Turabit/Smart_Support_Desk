from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.session import Base


class ChatSession(Base):
    __tablename__ = "chat_session"

    # Columns
    chat_id = Column(Integer,primary_key=True,autoincrement=True)
    init_time = Column(DateTime,nullable=False,server_default=func.now())
    chat_title = Column(String(30))
    user_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)

    # Relationships
    owner = relationship("Employee",back_populates="chat_sessions")
    messages = relationship("ChatMessage",back_populates="chat")


class ChatMessage(Base):
    __tablename__ = "chat_message"

    # Columns
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chat_session.chat_id"), nullable=False)
    chat_text = Column(Text)
    sender_type = Column(Enum('user','ai'),nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    chat = relationship("ChatSession",back_populates="messages")
