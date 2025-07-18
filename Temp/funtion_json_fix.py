import re

import json
from functools import partial

def validate_json_stream(file_path, schema=None):
 

    def validate_object(obj, schema=None):
        # Implement your custom validation logic here, e.g.,
        # - Check required fields
        # - Validate data types
        # - Apply custom constraints
        if schema:
            # Use a schema validation library like jsonschema
            # to validate against the schema
            pass
        return True

    with open(file_path, 'r') as f:
        parser = json.JSONDecoder()
        while True:
            try:
                obj = parser.decode(f.read())
                if not validate_object(obj, schema):
                    return False
            except json.JSONDecodeError:
                break
    return True

# Example usage:
#

def find_first_curly_brace_and_closing_tag(text):

  curly_brace_index = re.search(r"{", text).start() if re.search(r"{", text) else -1

  # Find the closing tag only if a curly brace is found
  if curly_brace_index != -1:
    closing_tag_index = re.search(r"</", text[curly_brace_index:]).start()
    # Add curly_brace_index to account for the offset within the substring
    if closing_tag_index is not None:
      closing_tag_index += curly_brace_index
  else:
    closing_tag_index = -1

  return curly_brace_index, closing_tag_index

with open(r"E:\Temp\product_data.txt", "r", encoding="utf-8") as file:
    text = file.read()
def remove_non_ascii(text):

  cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
  return cleaned_text

# Read the file with UTF-8 encoding


# Clean the text using the function
cleaned_text = remove_non_ascii(text)

# Print the cleaned text




def xz(cleaned_text, curly_brace_index, closing_tag_index):
    if curly_brace_index != -1 and closing_tag_index != -1:
        part1 = cleaned_text[:curly_brace_index]
        part2 = cleaned_text[closing_tag_index:]
        return part1, part2
     # Adjust to include the closing tag
        
        # Optionally delete the detected lines:
        # You can write the modified text to a new file or overwrite the original file
        # Here's a basic example of writing to a new file:
    else:
        print("Curly brace or closing tag not found.")
        return None





# Find indices
curly_brace_index, closing_tag_index = find_first_curly_brace_and_closing_tag(cleaned_text)

# Split the text and optionally delete lines
result = xz(cleaned_text, curly_brace_index, closing_tag_index)

if result:
    part1, part2 = result
    print("Part 1:", part1)
    print("Part 2:", part2)
else:
    print("Curly brace or closing tag not found.")




def remove_first_part(part1, curly_brace_index, closing_tag_index):
    if curly_brace_index != -1 and closing_tag_index != -1:
        # Ensure the closing tag is included in part2
        part2 = part1[curly_brace_index:closing_tag_index + 1]

        # Optionally write the modified text to a new file:
        with open("new_file.json", "w") as f:
            f.write(part2)

        return part2
    else:
        print("Curly brace or closing tag not found.")
        return None

# ... (rest of your code, including reading the file and finding indices)

result = remove_first_part(cleaned_text, curly_brace_index, closing_tag_index)



import json


def remove_invalid_characters(json_string):
    """Removes invalid characters from a JSON string.

    Args:
        json_string: The JSON string to be cleaned.

    Returns:
        The cleaned JSON string.
    """

    invalid_chars = ['<', '>','.','}<']
    cleaned_string = ''

    for char in json_string:
        if char not in invalid_chars:
            cleaned_string += char

    return cleaned_string

def main():
    """Reads a JSON file, removes invalid characters, and writes the cleaned JSON to a new file."""

    with open(r"E:\Temp\new_file.json", 'r') as f:
        json_data = f.read()

    cleaned_json_data = remove_invalid_characters(json_data)

    with open('cleaned_json.json', 'w') as f:
        f.write(cleaned_json_data)

if __name__ == '__main__':
    main()
# Example usage:
