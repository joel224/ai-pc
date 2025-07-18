import os
import google.generativeai as genai
import api_scraper  # Assuming this is your custom module for network scraping

# Configure Gemini
genai.configure(api_key="AIzaSyD14hafXeyls4ZpIdjrp56xsnuei0u_oBQ")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")



import threading
import pika

# RabbitMQ connection details (replace with your server address if necessary)
RABBITMQ_HOST = 'amqp://localhost'

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

with open(r"E:\Temp\adidas_network_data.txt", "r") as file:
    data = file.read()
getLinks = data

Continue = True
while Continue:
    prompt = str(input("Enter your prompt: "))

    if prompt.lower() == "exit":
        print("Exiting...")
        break

    find_element = True
    while find_element:# like a mechine gun, shoots pre promt in each itration!!
        pre_prompts = [
            f"Task: Analyze the provided text file of network log and identify the most relevant link that has the information to extract from the target website, I need you to provide me the exact link required without any paragraph, {getLinks}, I force you to select one link only and if there is no robust link found, I want you to respond with 'not found'"
            f"correct the errors {errors}"
        ]
        select_preprompt=0
        # Combine pre-prompt and user input
        for select_preprompt in pre_prompts:
            full_prompt = pre_prompts + "\n" + prompt

            # Generate response
            print(f"Generating response for prompt: {full_prompt}")
            try:
                response = model.generate_content(full_prompt)
                response_text = response.text.strip()  # Remove leading/trailing whitespace

                # Check for "not found" and assign variable accordingly
                if response_text.lower() == "not found":
                    link_fail = False  # Stop inner loop
                      # Assign "not found" to variable
                else:
                     
                    pass  # Stop inner loop

                print(response_text, "\n")

            except Exception as e:  # Catch potential errors during Gemini API call
                print(f"Error during Gemini API call: {e}")
                continue  # Continue to the next pre-prompt or loop iteration

        # Process the extracted element (e.g., print it)
        
        
        # No need to break the outer loop here, continue prompting the user

    # Save the final response (optional)
    if hasattr(response, 'text'):  # Check if response has attribute text.
        output_filename = "ai_explanation.txt"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "w") as f:
            f.write(response.text)
    else:
        print("No response text to save.")

    print(f"Output saved to: {output_path}")

    if link_fail == False:
        Continue = False  # optional break

        def receive_website_search_errors():
            """Receives website search errors from the 'website_search_errors' queue."""
           
    
        errors = receive_website_search_errors()
        select_preprompt=1
        # send response to api scraper if possible
    else:  # yes correct link
        url = "https://www.amazon.in/s/query?crid=1VBAJ0SHSMCC8&high-price=8400&k=mobiles&low-price=&page=1&qid=17339262031&sprefix=mobiles%2Caps%2C867"
        api_scraper.open_link(url)
        pass