import os
import subprocess

def interact_with_module(input_text):
    """
    Interacts with the external module E:\Temp\temperapi.py.

    Args:
        input_text: The text to be sent to the module.

    Returns:
        A tuple containing:
            - True/False: Whether the module's response was successful.
            - output_text: The output from the module.
    """
    try:
        # Execute the module with the input text
        result = subprocess.run(
            ["python", "E:\Temp\temperapi.py", input_text], 
            capture_output=True, 
            text=True
        )

        # Check if the module executed successfully
        if result.returncode == 0:
            # Extract the output from the module
            output_text = result.stdout.strip()
            return True, output_text
        else:
            # Handle errors from the module
            error_message = result.stderr.strip()
            return False, f"Module execution failed: {error_message}"

    except Exception as e:
        return False, f"An error occurred: {e}"

# Example usage:
input_data = "some_input_text"
success, module_output = interact_with_module(input_data)

if success:
    print("Module output:", module_output)
else:
    print("Module interaction failed.")
#####################################################################################################
def interact_with_module(input_text):
    """
    Interacts with the real external module.
    """
    try:
        # 1. Parse the input_text (e.g., extract the link)
        extracted_link = extract_link(input_text)  # Replace with your extraction logic

        # 2. Send the link to the external module (e.g., make an API call)
        module_response = call_external_module(extracted_link)  # Replace with your module interaction

        # 3. Check the module's response for success/failure
        if module_response["status"] == "success":  # Example: Assuming the module returns a JSON response
            return True, module_response["message"]
        else:
            return False, module_response["error"]

    except Exception as e:  # Handle potential errors during module interaction
        return False, f"Error interacting with module: {e}"