import aio_pika
import json
import os


async def get_rabbit_connection():
    return await aio_pika.connect_robust(os.getenv("RABBITMQ_HOST"))

async def publish_event(event_data: dict):
    connection = await get_rabbit_connection()
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(event_data).encode()),
            routing_key="betting_events",
        )
        print(f"Event {event_data['id']} sent to RabbitMQ")