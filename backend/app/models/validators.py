from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime

"""
    Enums for Pydantic validation
"""
class TicketType(str, Enum):
    BUG = "Bug"
    FEATURE = "Feature Request"
    INQUIRY = "Inquiry"
    BILLING = "Billing"
    ACCESS = "Access"

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"

class TicketPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class AccessLevel(str,Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

"""     Pydantic Classes for validation of Database Table : Tickets
        Corresponding to SQLalchemy Class Ticket
"""

class TicketBase(BaseModel):
    title: str = Field(...,max_length=255)
    description: Optional[str] = None
    ticket_type: TicketType = TicketType.INQUIRY

class TicketCreate(TicketBase):
    customer_id: int
    assignee_id: Optional[int] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ticket_type: Optional[TicketType] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assignee_id: Optional[int] = None

class TicketResponse(TicketBase):
    ticket_id: int
    customer_id: int
    assignee_id: Optional[int]
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

"""     Pydantic Classes for validation of Database Table : customers
        Corresponding to SQLalchemy Class Customer
"""

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    company: str
    email: EmailStr
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class CustomerResponse(CustomerBase):
    customer_id: int
    first_name: str
    last_name: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    created_by: int

    model_config = ConfigDict(from_attributes=True)

"""     Pydantic Classes for validation of Database Table : employees
        Corresponding to SQLalchemy Class Employee
"""

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    access_level: AccessLevel = AccessLevel.VIEWER

class EmployeeCreate(EmployeeBase):
    password_hash: str = Field(..., min_length=8)

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    access_level: Optional[AccessLevel] = None

class EmployeeResponse(EmployeeBase):
    employee_id: int

    model_config = ConfigDict(from_attributes=True)