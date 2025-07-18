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