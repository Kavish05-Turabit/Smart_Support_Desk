from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text, DateTime, func, TIMESTAMP
from sqlalchemy.orm import relationship
from app.core.session import Base

class Note(Base):
    __tablename__ = "notes"

    # Columns
    note_id = Column(Integer,primary_key=True,autoincrement=True)
    ticket_id = Column(Integer,ForeignKey("tickets.ticket_id"),nullable=False)
    author_id = Column(Integer,ForeignKey("employees.employee_id"),nullable=False)
    content = Column(Text,nullable=False)
    created_at = Column(TIMESTAMP,server_default=func.now())

    # Relationship
    topic = relationship("Ticket",back_populates="notes")
    author = relationship("Employee",back_populates="notes_created")