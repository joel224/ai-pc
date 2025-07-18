

# ... rest of my_script.py

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
      


