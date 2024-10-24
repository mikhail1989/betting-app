from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from enum import Enum


class BidCreate(BaseModel):
    event_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)


class EventStatus(str, Enum):
    pending = "not_played"
    first_won = "won"
    second_won = "lost"


class EventCreate(BaseModel):
    coef: float
    deadline: datetime


class EventResponse(BaseModel):
    id: int
    coef: float
    status: EventStatus
    deadline: datetime

    class Config:
        orm_mode = True


class BidResponse(BaseModel):
    id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    placed_at: datetime
    event: EventResponse

    class Config:
        orm_mode = True
