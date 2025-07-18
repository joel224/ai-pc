import json
        

def remove_invalid_characters(json_string):
          """Removes invalid characters from a JSON string.
               """

          invalid_chars = ['<', '>','.']
          cleaned_string = ''

          for char in json_string:
           
           if char not in invalid_chars:
             cleaned_string += char
          return cleaned_string


"""Reads a JSON file, removes invalid characters, and writes the cleaned JSON to a new file."""

with open(r"E:\Temp\new_file.json", 'r') as f:
    json_data = f.read()

cleaned_json_data = remove_invalid_characters(json_data)
with open('cleaned_json.json', 'w') as f:
          f.write(cleaned_json_data)

        