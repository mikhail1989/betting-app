from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class EventStatus(str, enum.Enum):
    pending = "pending"
    first_won = "first_won"
    second_won = "second_won"

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    coef = Column(Float, nullable=False)
    deadline = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(Enum(EventStatus), default=EventStatus.pending)

    def to_dict(self):
        return {
            "id": self.id,
            "coef": self.coef,
            "deadline": self.deadline.isoformat(),
            "status": self.status.value
        }