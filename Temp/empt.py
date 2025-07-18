import os
import google.generativeai as genai
import api_scraper  # Assuming this is your custom module for network scraping

# Configure Gemini
genai.configure(api_key="AIzaSyD14hafXeyls4ZpIdjrp56xsnuei0u_oBQ")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

import pika
# RabbitMQ connection details (replace with your server address if necessary)
RABBITMQ_HOST = 'amqp://localhost'

def receive_website_search_errors():
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.queue_declare(queue='website_search_errors', durable=True)

  def callback(ch, method, properties, body):
    # Process the received error message (string) from the queue
    error_message = body.decode()
    # Update the `errors` variable or use it for other purposes
    # (e.g., modify the pre-prompts)
    global errors
    errors = error_message

  channel.basic_consume(queue='website_search_errors', on_message_callback=callback)
  channel.start_consuming()  # Start consuming messages

  return errors  # Return the accumulated errors (optional)


import pika

def receive_website_search_errors():
 
  # Initialize an empty list to store errors
  errors = []

  try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='website_search_errors', durable=True)

    def callback(ch, method, properties, body):
      """Processes the received error message."""
      error_message = body.decode()
      errors.append(error_message)
        # Log the received error

    channel.basic_consume(queue='website_search_errors', on_message_callback=callback)

    
    channel.start_consuming()

  except pika.exceptions.ConnectionClosed:
    pass

  finally:
    connection.close()  # Always close the connection

  # Now you can access the received errors in the 'errors' list
  return errors

# Call the function to start consuming errors







def receive_website_links():
    """Receives website links from the 'website_links' queue."""
    _receive_from_queue('website_links')



def _receive_from_queue():
    """Generic function to receive messages from a specified queue."""
    print("Waiting for messages...")

# Output directory
output_dir = r"E\Temp"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

with open(r"E:\Temp\E\Temp\response_Task", "r") as file:
    data = file.read()
getLinks = data




Continue = True
while Continue:
    prompt = str(input("Enter your prompt: "))
    errors=receive_website_search_errors()

    if prompt.lower() == "exit":
        print("Exiting...")
        break
  

    find_element = True
    while find_element:
        # Pre-prompts with clear instructions and placeholders
        pre_prompts = [
            f"Task: act like a function, Analyze the provided text file of network log and identify the most relevant link that has the information to extract from the target website. I need you to provide me the exact link required.]\n file: {getLinks}\nForce selection of one link only.\nIf no robust link is found elseif request or responce is empty, respond with 'not found'.",
            f"**Correction prompt:** {errors}\nPlease correct the errors in the previously identified link."  # Placeholder for errors
        ]

        # Iterate through pre-prompts
        for select_preprompt in range(len(pre_prompts)):
            full_prompt = pre_prompts[select_preprompt] + "\n" + prompt

            # Generate response
            print(f"Generating response for prompt: {full_prompt}")
            try:
                response = model.generate_content(full_prompt)
                response_text = response.text.strip()  # Remove leading/trailing whitespace

                # Handle "not found" and assign variable
                link_fail = response_text.lower() == "not found"

                # Process successful response (link extraction)
                if link_fail and select_preprompt == 0:  # Check if it's the FIRST prompt
                    print("No link found based on the initial prompt.")
                    find_element = False # Stop the inner loop
                    break # Exit the pre-prompt loop as well

                    # Check for link validity (optional)
            
                        # Implement link validation logic using a library like validators or urllib.parse
                 # Placeholder for validation result
                if not link_fail:
                    url = response_text
                    print("Extracted link:", url)
                    try:
                        valid_url = True  # Placeholder
                        if valid_url:
                            api_scraper.open_link(url)
                            find_element = False
                        else:
                            print(f"Invalid link: {url}")
                    except Exception as e:
                        print(f"Error during link validation: {e}")
                    break # break the pre_prompts loop after finding a url
                else:
                    print(response_text, "\n")                

            except Exception as e:
                print(f"Error during Gemini API call: {e}")
                continue 
            
            
        if link_fail and select_preprompt == 0: # Check if it's the FIRST prompt
            print("No errors reported. Link extraction failed.")
            find_element = False
            
        elif link_fail and select_preprompt == 1:
             receive_website_search_errors()
             
             if errors:
                  print(f"Error(s) encountered during search: {errors}")
             else:
                  print("No errors reported. Link extraction failed.")
             find_element = False

    if find_element == False and link_fail: #check if the inner loop ended and link_fail is true
        Continue = input("Continue searching? (y/n) ")
        Continue = Continue.lower() == "y"

        print("Program terminated.")     # Continue to the next pre-prompt or loop iteration

        # Handle link failure and "correct the errors" prompt
        if link_fail:
            # Call function to retrieve errors from website_search_errors queue (assuming implemented)
            #errors = receive_website_search_errors()  # Placeholder until implemented
            errors = receive_website_search_errors()
            if errors:
                print(f"Error(s) encountered during search: {errors}")
                select_preprompt = 1  # Use "correct the errors" pre-prompt
            else:
                print("No errors reported. Link extraction failed.")
                find_element = False  # Stop inner loop after failed extraction

    # Save the final response (optional)
    if hasattr(response, 'text'):
        output_filename = "ai_explanation.txt"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w") as f:
            f.write(response.text)
    else:
        print("No response text to save.")

    print(f"Output saved to: {output_path}" if hasattr(response, 'text') else "")

    if link_fail:
        Continue = input("Continue searching? (y/n) ")
        Continue = Continue.lower() == "y"

print("Program terminated.")