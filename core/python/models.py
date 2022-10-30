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
