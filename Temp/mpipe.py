import aio_pika
import json
import asyncio

async def send_true_value(queue_name):
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()

            # Correct: Declare the queue using the channel
            queue = await channel.declare_queue(queue_name, durable=True)  

            message_data = json.dumps(True)
            await channel.default_exchange.publish(
                aio_pika.Message(message_data.encode()),
                routing_key=queue.name
            )
            print(f" 'True' to queue '{queue_name}'")
        return True

    except aio_pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


async def main():
    queue_name = "started1"
    await send_true_value(queue_name)


if __name__ == "__main__":
    asyncio.run(main())

