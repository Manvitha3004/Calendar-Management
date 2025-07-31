from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .schema import PyObjectId

class EmailBase(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    sender: str
    recipient: str
    body: str
    snippet: str
    timestamp: datetime
    is_read: bool = False
    labels: List[str] = []
    attachments: List[Dict[str, Any]] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailDB(EmailBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class EmailDraft(BaseModel):
    email_id: str
    draft_content: str
    generated_at: datetime
    status: str = "pending"  # pending, approved, sent, rejected
    ai_confidence: float = 0.0
    user_id: str
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailDraftDB(EmailDraft):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class EmailReminder(BaseModel):
    email_id: str
    user_id: str
    reminder_time: datetime
    calendar_event_id: Optional[str] = None
    status: str = "active"  # active, completed, cancelled
    created_at: datetime
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailReminderDB(EmailReminder):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class EmailContext(BaseModel):
    email_id: str
    extracted_entities: Dict[str, Any] = {}
    sentiment: str = "neutral"
    priority: str = "medium"  # low, medium, high, urgent
    category: str = "general"  # meeting, task, information, etc.
    key_points: List[str] = []
    suggested_actions: List[str] = []
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EmailContextDB(EmailContext):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
