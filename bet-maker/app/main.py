from fastapi import FastAPI, Depends, HTTPException
from .database import  create_db, get_db
from contextlib import asynccontextmanager
from .models import Base, Event,Bid
from .schemas import EventCreate, BidCreate, BidResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.future import select
from .consumer import consume_events
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating DB tables...")
    await create_db()
    print("Tables created.")

    print("Start consuming events .")
    task = asyncio.create_task(consume_events())

    yield 
    
    print("Shutting down...")
    task.cancel()  
    await task  


app = FastAPI(lifespan=lifespan)


@app.post("/events/", response_model=EventCreate)
async def create_event(event: EventCreate, db: AsyncSession = Depends(get_db)):
    new_event = Event(**event.dict())
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event

@app.get("/events/")
async def get_active_events(db: AsyncSession = Depends(get_db)):
    events = await db.execute(select(Event).filter(Event.deadline > datetime.utcnow()))
    return events.scalars().all()

@app.post("/bet/")
async def place_bid(bid: BidCreate, db: AsyncSession = Depends(get_db)):
    # Check if the event exists in the local database and is still active
    event_query = await db.execute(select(Event).filter(Event.id == bid.event_id))
    event = event_query.scalars().first()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Expired event")

    # Save the bid in the local database
    new_bid = Bid(event_id=bid.event_id, amount=bid.amount)
    db.add(new_bid)
    await db.commit()
    await db.refresh(new_bid)

    return {"message": "Bid placed successfully", "bid": new_bid}


@app.get("/bets/", response_model=list[BidResponse])
async def get_bid_history(db: AsyncSession = Depends(get_db)):
    results = await db.execute(
        select(Bid, Event)
        .join(Event, Bid.event_id == Event.id)
    )
    
    bid_history = results.all()

    return [
        {
            "id": bid.id,
            "amount": bid.amount,
            "placed_at": bid.placed_at,
            "event": {
                "id": event.id,
                "coef": event.coef,
                "status": event.status,
                "deadline": event.deadline
            }
        }
        for bid, event in bid_history
    ]