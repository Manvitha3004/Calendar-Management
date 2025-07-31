from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler):
        from pydantic_core import core_schema
        def validate(v):
            if isinstance(v, ObjectId):
                return v
            if isinstance(v, str) and ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")
        return core_schema.no_info_after_validator_function(
            validate,
            core_schema.str_schema()
        )

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
    id: str = Field(alias="_id")

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass