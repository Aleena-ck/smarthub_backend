# services/rabbitmq_service.py

import aio_pika
import json
import os
from typing import Optional

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
connection = None
channel = None

async def get_rabbitmq_connection():
    """Get or create RabbitMQ connection (optional)"""
    global connection, channel
    if not connection or connection.is_closed:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL, timeout=5)
            channel = await connection.channel()
            
            # Declare exchanges
            await channel.declare_exchange("cixio.delayed", aio_pika.ExchangeType.DIRECT)
            await channel.declare_exchange("cixio.topic", aio_pika.ExchangeType.TOPIC)
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}")
            connection = None
            channel = None
            raise e
    return connection, channel

async def publish_delayed_message(exchange: str, routing_key: str, payload: dict, delay_ms: int):
    """Publish a message with delay (if RabbitMQ is available)"""
    try:
        conn, ch = await get_rabbitmq_connection()
        if conn is None:
            print(f"RabbitMQ not available, skipping message: {payload}")
            return
        exchange_obj = await ch.get_exchange(exchange)
        
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            headers={"x-delay": delay_ms} if delay_ms > 0 else {}
        )
        
        await exchange_obj.publish(message, routing_key=routing_key)
    except Exception as e:
        print(f"Failed to publish message: {e}")

async def publish_message(exchange: str, routing_key: str, payload: dict):
    """Publish a message immediately"""
    await publish_delayed_message(exchange, routing_key, payload, 0)