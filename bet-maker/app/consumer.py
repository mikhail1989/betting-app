import aio_pika
import json
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from .database import get_db
from .models import Event
from datetime import datetime
from contextlib import asynccontextmanager
import os



engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def consume_events():
    """
    Consume events from a RabbitMQ queue.
    """
    try:
        connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_HOST"))
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("betting_events", durable=True)
            print('1')
            
            async with queue.iterator() as queue_iter:
                print(queue_iter)
                async for message in queue_iter:
                    print(message)
                    async with message.process():
                        
                        event_data = message.body.decode()
                        print(event_data)
                        await save_event(event_data)
    except Exception as e:
        print(f"Error in consume_events: {e}")

async def save_event(event_data: str):
    """
    Save or update an event in the database.
    """
    try:
        print(f"Processing event: {event_data}")
        event_data = json.loads(event_data)
        print('4')
        async with async_session() as db:
            event_id = event_data.get("id")
            coef = event_data.get("coef")
            deadline = event_data.get("deadline")
            status = event_data.get("status")

            event_query = await db.execute(select(Event).filter(Event.id == event_id))
            existing_event = event_query.scalars().first()

            if existing_event:
                existing_event.coef = coef
                existing_event.deadline = datetime.fromisoformat(deadline)
                existing_event.status = status
            else:
                new_event = Event(id=event_id, coef=coef,deadline = datetime.fromisoformat(deadline), status=status)
                db.add(new_event)

            await db.commit()
    except Exception as e:
        print(f"Error save_event: {e}")


