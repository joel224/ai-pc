import asyncio
import aio_pika
import aiormq

RECEIVED_MESSAGES = []
UNIQUE_MATCHES = set()  # Variable to store unique matches


async def on_message(message):
    """
    Handles an incoming message from RabbitMQ.

    :param message: The incoming message
    """
    if message is None:
        print("Skipping null message")
        return

    global RECEIVED_MESSAGES, UNIQUE_MATCHES
    decoded_body = message.body.decode('utf-8')
    print(f"Received message: {decoded_body}")
    RECEIVED_MESSAGES.append(decoded_body)

    # Check if the message is one of Match 1 to 4
    for i in range(0, 4):
        match_prefix = f"Match {i}:\\n"
        if decoded_body.startswith(match_prefix):
            match_content = decoded_body[len(match_prefix):].split("---")[0].strip()  # Extract content and remove "---" part
            UNIQUE_MATCHES.add(match_content)  # Add to set to remove duplicates
            print("Current Unique Matches:")
            for match in UNIQUE_MATCHES:
                print(f"- {match}")
            print("-" * 20)  # Separator for clarity
            break  # No need to check other match numbers if one is found

    await asyncio.sleep(0.1)  # Simulate some processing time


async def receive_website_search_errors_async():
    """
    Asynchronous function to receive messages from RabbitMQ using aio-pika.

    :return: None
    """
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        async with connection:
            channel = await connection.channel()
            print("Connected to RabbitMQ (default channel)")
            queue = await channel.declare_queue("extracted_elements", durable=True)
            print("Waiting for messages...")
            print("RabbitMQ consumer is running and waiting for messages...")

            async def consume_callback(message: aio_pika.abc.AbstractIncomingMessage):
                """
                Handles an incoming message from RabbitMQ.

                :param message: The incoming message
                """
                try:
                    if message is None:
                        print("Skipping null message")
                        return

                    async with message.process():
                        await on_message(message)
                    # RECEIVED_MESSAGES.clear() # Removed clearing of global message list

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


def receive_website_search_errors():
    """
    Runs the asynchronous function to receive messages from RabbitMQ.

    :return: None
    """
    try:
        asyncio.run(receive_website_search_errors_async())
        return None
    except KeyboardInterrupt:
        print("Exiting...")
        print("Unique Matches Collected at Exit:")  # Final print of unique matches on exit
        for match in UNIQUE_MATCHES:
            print(f"- {match}")
        return "Exiting"


receive_website_search_errors()
print("Consumer started using queue.consume. Check console for messages.")