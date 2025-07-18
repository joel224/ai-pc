import asyncio
import aio_pika
import aiormq

RECEIVED_URLS = []

async def on_url(message):
    global RECEIVED_URLS
    decoded_body = message.body.decode('utf-8')
    print(f"Received URL: {decoded_body}")
    RECEIVED_URLS.append(decoded_body)
    await asyncio.sleep(0.1)  # Simulate some processing time

async def receive_website_search_urls_async():
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()
            print("Connected to RabbitMQ (default channel)")
            queue = await channel.declare_queue("URLSERVER", durable=False)
            print("Waiting for URLs...")
            print("RabbitMQ consumer is running and waiting for URLs...")

            async def consume_callback(message: aio_pika.abc.AbstractIncomingMessage):
                try:
                    async with message.process():
                        await on_url(message)
                    RECEIVED_URLS.clear()  # <-- Clear the list AFTER processing each message
                    print("Global URL list cleared after processing.") # Optional confirmation URL
                except (asyncio.exceptions.CancelledError, aiormq.exceptions.ChannelInvalidStateError):
                    pass
                except Exception as e:
                    print(f"Error in consume_callback: {e}")

            await queue.consume(consume_callback)

    except aio_pika.exceptions.AMQPConnectionError as e:
        print(f"Connection error: {e}")
        return f"Connection error: {e}"
    except KeyboardInterrupt:
        print("Exiting...")
        return "Exiting"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

def receive_website_search_urls():
    try:
        asyncio.run(receive_website_search_urls_async())
        return None
    except KeyboardInterrupt:
        print("Exiting...")
        return "Exiting"
x=str(input("enter here"))
while x:

  
  if x:

    extracted_URLs=receive_website_search_urls()
    print(extracted_URLs)
  else:
    print("No URLs received.")
  break
else:
  print("Consumer started using queue.consume. Check console for URLs.")
