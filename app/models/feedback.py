from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class FeedbackBase(BaseModel):
    date: date
    nps: int = Field(ge=0, le=10)
    csat: int = Field(ge=1, le=5)
    ces: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class Feedback(FeedbackBase):
    id: str

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackRead(FeedbackBase):
    id: str
