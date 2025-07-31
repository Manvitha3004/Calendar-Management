from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class EventBase(BaseModel):
    title: str
    start: datetime
    end: datetime
    allDay: bool = False
    meetingLink: Optional[str] = None
    meetingDescription: Optional[str] = None
    attendees: List[str] = []
    reminders: List[int] = []
    recurrence: Optional[str] = None
    summaryPoints: List[str] = []
    status: str = "upcoming"
    cardColor: Optional[str] = None
    agendaOrder: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class EventDB(EventBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass