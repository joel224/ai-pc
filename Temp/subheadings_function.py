import json

def extract_data(json_data):
    """Extracts specific data from the JSON structure.

    Args:
        json_data (str): The JSON string.

    Returns:
        list: A list of extracted subheadings and headings.
    """

    data = json.loads(json_data)

    extracted_data = []

    # Extract top-level headings
    for key, value in data.items():
        if isinstance(value, dict):
            extracted_data.append(key)

    # Extract subheadings under "info"
    if "info" in data:
        for key, value in data["info"].items():
            extracted_data.append(key)

    # Extract subheadings under "products"
    if "products" in data:
        for product in data["products"]:
            for key, value in product.items():
                extracted_data.append(key)

    return extracted_data

# Example usage:
json_string = """

only cleaned data will work here
"""
file_path = "E:\Temp\product_data.txt"

extracted_data = extract_data(file_path)
print(extracted_data)