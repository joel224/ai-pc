import re

def find_first_curly_brace_and_closing_tag(text):
    curly_brace_index = re.search(r"{", text).start() if re.search(r"{", text) else -1
    if curly_brace_index != -1:
        closing_tag_index = re.search(r"</", text[curly_brace_index:]).start()
        if closing_tag_index is not None:
            closing_tag_index += curly_brace_index
        return curly_brace_index, closing_tag_index
    else:
        return curly_brace_index, None  # Return -1 and None for clarity

with open(r"E:\Temp\product_data.txt", "r", encoding="utf-8") as file:
         text = file.read() 

       
def remove_non_ascii(text):
         import re

         cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
         return cleaned_text        
         
cleaned_text = remove_non_ascii(text) 