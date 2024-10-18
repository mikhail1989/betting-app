from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class EventCreate(BaseModel):
    coef: float
    deadline: datetime

class EventUpdate(BaseModel):
    status: Optional[str]