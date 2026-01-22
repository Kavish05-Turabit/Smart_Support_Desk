from sqlalchemy import Column, String, Integer, Enum, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.session import Base


class Employee(Base):
    __tablename__ = "employees"

    # Columns
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    access_level = Column(Enum('admin', 'agent'), nullable=False, default='agent')

    # Relationships
    customers_created = relationship("Customer", back_populates="creator")
    tickets_assigned = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assignee_id")
    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.created_by_id")
    notes_created = relationship("Note",back_populates="author")