import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
import os
import re

#scrape API data ONLY


# Imported functions
def find_first_curly_brace_and_closing_tag(text):
    curly_brace_index = re.search(r"{", text).start() if re.search(r"{", text) else -1
    if curly_brace_index != -1:
        closing_tag_index = re.search(r"</", text[curly_brace_index:]).start() if re.search(r"</", text[curly_brace_index:]) else -1
        if closing_tag_index != -1:
            closing_tag_index += curly_brace_index
        return curly_brace_index, closing_tag_index
    else:
        return -1, -1  # Return -1, -1 for consistency

def remove_non_ascii(text):
    cleaned_text = re.sub(r'[^\x00-\x7F]+', '', text)
    return cleaned_text

def xz(cleaned_text, curly_brace_index, closing_tag_index):
    if curly_brace_index != -1 and closing_tag_index != -1:
        part1 = cleaned_text[:curly_brace_index]
        part2 = cleaned_text[closing_tag_index:]
        return part1, part2
    else:
        print("Curly brace or closing tag not found.")
        return None

def remove_first_part(part1, curly_brace_index, closing_tag_index):
    if curly_brace_index != -1 and closing_tag_index != -1:
        part2 = part1[curly_brace_index:closing_tag_index + 1]
        with open("new_file.json", "w") as f:
            f.write(part2)
        return part2
    else:
        print("Curly brace or closing tag not found.")
        return None

def remove_invalid_characters(json_string):
    invalid_chars = ['<', '>', '.']
    cleaned_string = ''
    for char in json_string:
        if char not in invalid_chars:
            cleaned_string += char
    return cleaned_string


def open_link(url, retries=3, delay=5):
    options = Options()
    # options.add_argument("--headless=new")  # Uncomment for headless mode

    for attempt in range(retries):
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            driver.get(url)

            if "ERR_SSL_PROTOCOL_ERROR" in driver.page_source or "net::ERR_CERT" in driver.page_source:
                raise WebDriverException("SSL certificate error detected in page source.")

            page_source = driver.page_source
            save_as_json(page_source)
            break

        except WebDriverException as e:
            if "ERR_SSL_PROTOCOL_ERROR" in str(e) or "net::ERR_CERT" in str(e):
                print(f"SSL certificate error: {e}. Attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
            else:
                print(f"An error occurred: {e}")
                return

        finally:
            if 'driver' in locals():
                driver.quit()

        time.sleep(delay)

    else:  # If all retries fail
        print(f"Failed to open URL after {retries} attempts.")


def save_as_json(page_source, filename="product_data1.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"JSON data saved to {filename}")

        # Data cleaning and processing after saving
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()

        cleaned_text = remove_non_ascii(text)
        curly_brace_index, closing_tag_index = find_first_curly_brace_and_closing_tag(cleaned_text)

        if curly_brace_index != -1 and closing_tag_index != -1:
           extracted_part = remove_first_part(cleaned_text, curly_brace_index, closing_tag_index)
           if extracted_part:
               cleaned_json = remove_invalid_characters(extracted_part)
               with open('cleaned_json.json', 'w') as f:
                    f.write(cleaned_json)



        return True

    except Exception as e:
        print(f"An error occurred during saving or processing: {e}")
        return False

def main():
    url = "https://www.adidas.co.in/"
    open_link(url)

if __name__ == '__main__':
    main()


