from sqlalchemy import Column,String,Integer,Enum,ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.core.session import Base


class Customer(Base):
    __tablename__ = "customers"

    # Columns
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(100))
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20),nullable=True)
    created_by = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)

    # Relationships
    creator = relationship("Employee", back_populates="customers_created")
    tickets = relationship("Ticket", back_populates="customer")
