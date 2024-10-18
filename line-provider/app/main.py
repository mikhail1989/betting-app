from fastapi import FastAPI, Depends, HTTPException
from .database import  create_db, get_db
from contextlib import asynccontextmanager
from .models import Event
from .schemas import EventCreate, EventUpdate
from . import producer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.future import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating DB tables")
    await create_db()
    print("Tables created")
    yield
    #  cleanup 

app = FastAPI(lifespan=lifespan)

@app.post("/events/", response_model=EventCreate)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    new_event = Event(**event.dict())
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    await producer.publish_event(new_event.to_dict())

    return new_event

@app.get("/events")
async def get_active_events(db: AsyncSession = Depends(get_db)):
    events = await db.execute(select(Event).filter(Event.deadline > datetime.utcnow()))
    return events.scalars().all()

@app.put("/events/{event_id}/")
async def update_event_status(event_id: int, status: EventUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalars().first()

    if not event:
        return None 
    # Update the event's status
    if status.status is not None:
        event.status = status.status
    
    # Commit the changes to the database
    db.add(event)
    await db.commit()
    await db.refresh(event)
    await producer.publish_event(event.to_dict())
    return event