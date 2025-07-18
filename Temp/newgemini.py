import os
import google.generativeai as genai
import api_scraper  # Assuming this is your custom module for network scraping
import pika
# Configure Gemini
genai.configure(api_key="AIzaSyD14hafXeyls4ZpIdjrp56xsnuei0u_oBQ")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")


# RabbitMQ connection details (replace with your server address if necessary)

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

 # Global list to store extracted elements



import asyncio
import aio_pika
import aiormq


RECEIVED_MESSAGES = []

async def on_message(message):
    """
    Handles an incoming message from RabbitMQ.

    :param message: The incoming message
    """
    if message is None:
        print("Skipping null message")
        return

    global RECEIVED_MESSAGES
    decoded_body = message.body.decode('utf-8')
    print(f"Received message: {decoded_body}")
    RECEIVED_MESSAGES.append(decoded_body)
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
        return "Exiting"


receive_website_search_errors()
print("Consumer started using queue.consume. Check console for messages.")

    
async def print_received_messages_periodically():
    """
    Prints the received messages from the global variable every 5 seconds.
    """
    while True:
        await asyncio.sleep(5)
        print("\n--- Received Messages (from global variable) ---")
        if RECEIVED_MESSAGES:
            for msg in RECEIVED_MESSAGES:
                print(msg)
        else:
            print("No messages received yet in global list.")
        print("--- End of Received Messages ---")


receive_website_search_errors()
print("Consumer started using queue.consume. Check console for messages.")


 

   
# Call the function to start receiving messages


# alredy called in function




    




import json

def send_message(queue_name, message_data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue with durable=True
        channel.queue_declare(queue=queue_name, durable=True)  # Key change here

        if not isinstance(message_data, str):
            message_data = json.dumps(message_data)

        channel.basic_publish(exchange='', routing_key=queue_name, body=message_data,
                              properties=pika.BasicProperties(delivery_mode=2)) # Make messages persistent

        print(f" [x] Sent '{message_data}' to queue '{queue_name}'")
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")






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


   



 




# Output directory
output_dir = r"E\Temp"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  # Corrected file path






def chat_with_gemini(prompt, extracted_elements, select_preprompt):
    """Chats with Gemini using the provided prompt and returns the response."""
    
    
    with open(r"E:\Temp\requests.json", "r", encoding="utf-8") as file:
        file_content = file.read()

    pre_prompts = [
        f"Task: act like a function, Analyze the provided text file of network log and identify the most relevant link that has the information to extract from the target website. I need you to provide me the exact link required.]\n file: {file_content}\nForce selection of one link only.\nIf no robust link is found elseif request or responce is empty, respond with 'not found'.",
        f"**help prompt:**\n, \n {extracted_elements}\n  can you create a css selector  to get the search bar, i dont need a simple css selector  \n i need you to respond with exact selectors ,please avoid sentences or paragraphs or unwanted symbols   ",
        "\n\n please select a robest link that i can use to recive product datas or all to get all database throuh ,like a reverce api enginering \n\n"
    ]

    if select_preprompt < len(pre_prompts):
        full_prompt = pre_prompts[select_preprompt] + "\n" + prompt
        print(f"Generating response for prompt: {full_prompt}")
        try:
            response = model.generate_content(full_prompt)
            response_text = response.text.strip()  # Remove leading/trailing whitespace

            if response_text.lower() == "not found":
                return "not found", select_preprompt  # Returns a TUPLE!
            else:
                return response_text, select_preprompt  # Returns a string
        except Exception as e:  # Catching potential errors during API call
            print(f"Error during Gemini API call: {e}")
            return "Error during API call"  # Return an error message
    else:
        print(f"Invalid select_preprompt index. select_preprompt = {select_preprompt}") # Added print here
        return None  # Return an error message
# Initialize errors and extracted_data *before* the loop
#errors = """ ["input[type=\"text\"]","input[type=\"search\"]","[name=\"q\"]","#search",".search-input","input.gLFyf","#lst-ib"]"  """
 # Initialize extracted_data



while True:
    prompt = input("Enter your prompt: ")
    select_preprompt = 0
    extracted_elements = ''
    print(extracted_elements)
    response_text, select_preprompt = chat_with_gemini(prompt,extracted_elements, select_preprompt)
    link_fail = response_text.lower() == "not found"
    print(link_fail)
    print(response_text)
    print(select_preprompt)
    if prompt.lower() == "exit":
        print("Exiting...")
    else:
        break
    break
 # ... code for handling no link found on initial prompt
receive_website_search_errors()
if receive_website_search_errors:
    extracted_elements=asyncio.run(print_received_messages_periodically())
    
    import time
    if link_fail and select_preprompt == 0:

        async def main():
            queue_name = "started1"
            await send_true_value(queue_name)
            time.sleep(3)

        if __name__ == "__main__":
            asyncio.run(main())

        

        


        select_preprompt = 1
        prompt=""

        response_text, select_preprompt = chat_with_gemini(prompt,extracted_elements, select_preprompt)
        if __name__ == '__main__':
            queue_name = 'my_queue'
            message_string = response_text
            print("\n",message_string)
            send_message(queue_name, message_string)

    errors="true"                            
    if link_fail and select_preprompt == 1:  #problem
        
        file_content = "uhgu"
        if errors:
           prompt=file_content
           select_preprompt=2
           response_text, select_preprompt = chat_with_gemini(prompt,extracted_elements, select_preprompt)
           print(response_text)
           print(f"Error(s) encountered during search: {errors}")
        else:
           print("No errors reported. Link extraction failed.")
           Continue = input("Continue searching? (y/n) ")
           Continue = Continue.lower() == "y"
           print("Program terminated.")  

    if not link_fail:
        url = response_text
        print("Extracted link:", url)
        try:
            valid_url = True  # Placeholder
            if valid_url:
                api_scraper.open_link(url)
            else:  
                print(f"Invalid link: {url}")
        except Exception as e:
            print(f"Error during link validation: {e}")
            find_element = False
    else:
            print(response_text, "\n")


    if hasattr(response_text, 'text'):
        output_filename = "ai_explanation.txt"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w") as f:
            f.write(response_text.text)
    else:
        print("No response text to save.")

    print("Program terminated.")

