from sqlalchemy import Column, Integer, Float, DateTime, String, Enum, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class EventStatus(str, enum.Enum):
    pending = "not_played"
    first_won = "won"
    second_won = "lost"


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    coef = Column(Float, nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.pending)

    bids = relationship("Bid", back_populates="event")


class Bid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    placed_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="bids")
