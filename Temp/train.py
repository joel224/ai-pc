
import google.generativeai as genai  # Correct import statement

# Configure GenAI with your API key
genai.configure(api_key="AIzaSyD14hafXeyls4ZpIdjrp56xsnuei0u_oBQ") # Use genai.configure

# For Gemini Pro model (text-only):
model = genai.GenerativeModel('gemini-1.5-flash') 

# Initialize the model

import asyncio
import aio_pika
import aiormq

RECEIVED_MESSAGES = []

async def on_message(message):
    global RECEIVED_MESSAGES
    decoded_body = message.body.decode('utf-8')
    print(f"Received message: {decoded_body}")
    RECEIVED_MESSAGES.append(decoded_body)
    await asyncio.sleep(0.1)  # Simulate some processing time

async def trainerdata():
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()
            print("Connected to RabbitMQ (default channel)")
            queue = await channel.declare_queue("trainer", durable=True)
            print("Waiting for messages...")
            print("RabbitMQ consumer is running and waiting for messages...")

            async def consume_callback(message: aio_pika.abc.AbstractIncomingMessage):
                try:
                    async with message.process():
                        await on_message(message)
                    RECEIVED_MESSAGES.clear()  # <-- Clear the list AFTER processing each message
                    print("Global message list cleared after processing.") # Optional confirmation message
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


x=asyncio.run(trainerdata())
            
print(x)


response = model.generate_content("Explain how AI works") # Use model.generate_content
print(response.text)