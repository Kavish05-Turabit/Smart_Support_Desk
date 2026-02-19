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


class AccessLevel(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"


"""     Pydantic Classes for validation of Database Table : Tickets
        Corresponding to SQAlchemy Class Ticket
"""


class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title Cannot be empty")
    description: Optional[str] = None
    ticket_type: TicketType = TicketType.INQUIRY


class TicketCreate(TicketBase):
    customer_id: int
    assignee_id: Optional[int] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Title Cannot be empty")
    description: Optional[str] = None
    ticket_type: Optional[TicketType] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assignee_id: Optional[int] = None


class TicketResponse(TicketBase):
    ticket_id: int
    customer_id: int
    assignee_id: Optional[int]
    created_by_id: int
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


"""     Pydantic Classes for validation of Database Table : customers
        Corresponding to SQAlchemy Class Customer
"""


class CustomerBase(BaseModel):
    first_name: str = Field(..., min_length=1, description="Name Cannot be empty")
    last_name: str = Field(..., min_length=1, description="Name Cannot be empty")
    company: str
    email: EmailStr
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, description="Name Cannot be empty")
    last_name: Optional[str] = Field(None, min_length=1, description="Name Cannot be empty")
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
        Corresponding to SQAlchemy Class Employee
"""


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, description="Name Cannot be empty")
    last_name: str = Field(..., min_length=1, description="Name Cannot be empty")
    email: EmailStr
    phone: str
    access_level: AccessLevel = AccessLevel.AGENT


class EmployeeCreate(EmployeeBase):
    password_hash: str = Field(..., min_length=8)


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, description="Name Cannot be empty")
    last_name: Optional[str] = Field(None, min_length=1, description="Name Cannot be empty")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    access_level: Optional[AccessLevel] = None


class EmployeeResponse(EmployeeBase):
    employee_id: int
    first_name: str
    last_name: str
    email: EmailStr
    access_level: AccessLevel

    model_config = ConfigDict(from_attributes=True)


"""     Pydantic Classes for validation of Database Table : notes
        Corresponding to SQAlchemy Class Note
"""


class NoteBase(BaseModel):
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteResponse(NoteBase):
    note_id: int
    ticket_id: int
    author_id: int
    content: str = Field(..., min_length=1, description="Note Cannot be empty")
    created_at: datetime

    author_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


"""     Pydantic Classes for validation of Database Table : notes
        Corresponding to SQAlchemy Class Note
"""


class SenderType(str, Enum):
    USER = "user"
    AI = "ai"


class ChatSessionResponse(BaseModel):
    chat_id: int
    chat_title: str
    init_time: datetime


class ChatMessageCreate(BaseModel):
    sender_type: SenderType
    chat_id: int
    chat_text: str


class ChatMessageResponse(BaseModel):
    chat_text: str
    sender_type: SenderType
    created_at: datetime
