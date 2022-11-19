from datetime import datetime
from typing import Optional, List, Any

from pydantic.fields import Field
from pydantic.main import BaseModel


class Intent(BaseModel):
    id: str = Field(..., alias='intentId')
    name: str = Field(..., alias='intentName')
    description: Optional[str] = ""


class IntentInfo(BaseModel):
    utterances: List[str]
    response_message: str


class CreateIntent(IntentInfo):
    name: str
    description: Optional[str] = ""


class Chat(BaseModel):
    id: int
    created_at: datetime
    text_message: str
    session_id: int


class Feedback(BaseModel):
    id: int
    is_helpful: bool
    session_id: int
    created_at: datetime


class ChatSession(BaseModel):
    id: int
    session_uuid: str
    created_at: datetime
