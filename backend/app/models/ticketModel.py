from sqlalchemy import Column,String,Integer,Enum,ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.session import Base


class Ticket(Base):
    __tablename__ = "tickets"

    # Columns
    ticket_id = Column(Integer,primary_key=True,autoincrement=True)
    ticket_type = Column(
        Enum('Bug', 'Feature Request', 'Inquiry', 'Billing', 'Access'), 
        nullable=False, 
        default='Inquiry'
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum('Open', 'In Progress', 'Closed'), nullable=False, default='Open')
    priority = Column(Enum('Critical', 'High', 'Medium', 'Low'), nullable=False, default='Medium')
    
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("employees.employee_id"))
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    resolved_at = Column(DateTime)

    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    assignee = relationship("Employee", back_populates="tickets_assigned")