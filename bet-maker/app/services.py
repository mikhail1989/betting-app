# services.py
from .models import Event, Bid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime


async def create_event_service(event_data: dict, db: AsyncSession):
    """
    Create an event.
    """
    new_event = Event(**event_data)
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    return new_event


async def place_bid_service(bid_data: dict, db: AsyncSession):
    """
    Place a bid on an event.
    """
    event_query = await db.execute(select(Event).filter(Event.id == bid_data['event_id']))
    event = event_query.scalars().first()

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Expired event")

    new_bid = Bid(event_id=bid_data['event_id'], amount=bid_data['amount'])
    db.add(new_bid)
    await db.commit()
    await db.refresh(new_bid)
    return new_bid


async def get_active_events_service(db: AsyncSession):
    """
    Get all active events.
    """
    print("Events from DB")
    result = await db.execute(select(Event).filter(Event.deadline > datetime.utcnow()))
    events = result.scalars().all()
    return [{
        "id": event.id,
        "coef": float(event.coef),  # Convert Decimal to float
        "status": event.status,
        "deadline": event.deadline.isoformat(),
    } for event in events]


async def get_bid_history_service(db: AsyncSession):
    """
    Retrieve the bid history.
    """
    results = await db.execute(
        select(Bid, Event)
        .join(Event, Bid.event_id == Event.id)
    )
    print('Bids from DB')
    bid_history = results.all()

    return [
        {
            "id": bid.id,
            "amount": float(bid.amount),
            "placed_at": str(bid.placed_at),
            "event": {
                "id": event.id,
                "coef": float(event.coef),
                "status": event.status,
                "deadline": str(event.deadline)
            }
        }
        for bid, event in bid_history
    ]
