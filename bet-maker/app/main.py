from fastapi import FastAPI, Depends, HTTPException
from .database import create_db, get_db, get_redis
from contextlib import asynccontextmanager
from .models import Base, Event, Bid
from .schemas import EventCreate, BidCreate, BidResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.future import select
from .consumer import consume_events
import asyncio
import json
from .services import create_event_service, place_bid_service, get_active_events_service, get_bid_history_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for setting up database tables and consuming events.
    """
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
async def create_event(event: EventCreate,
                       db: AsyncSession = Depends(get_db)):
    """
    Create an event.
    """
    return await create_event_service(event.dict(), db)


@app.post("/bet/")
async def place_bid(bid: BidCreate, db: AsyncSession = Depends(get_db)):
    """
    Place a bid on an event.
    """
    return await place_bid_service(bid.dict(), db)


@app.get("/events/")
async def get_active_events(db: AsyncSession = Depends(get_db),
                            redis=Depends(get_redis)):
    """
    Get all active events.
    """
    cached_events = await redis.get("all_events")
    if cached_events:
        print("Events from cache")
        return json.loads(cached_events)

    events_list = await get_active_events_service(db)

    # Cache the events for 5 minutes (300 seconds)
    await redis.set("all_events", json.dumps(events_list), ex=300)
    return events_list


@app.get("/bets/", response_model=list[BidResponse])
async def get_bid_history(db: AsyncSession = Depends(get_db),
                          redis=Depends(get_redis)):
    """
    Retrieve the bid history.
    """
    cached_bids = await redis.get("all_bids")
    if cached_bids:
        print("Bids from cache")
        return json.loads(cached_bids)

    bids_list = await get_bid_history_service(db)

    # Cache the events for 5 minutes (300 seconds)
    await redis.set("all_bids", json.dumps(bids_list), ex=300)

    return bids_list
