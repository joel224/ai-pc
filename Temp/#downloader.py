import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import time
import os
import time

def open_link(url, retries=3, delay=5):
    """Opens a specified URL using Selenium webdriver with retry logic.

    Args:
        url: The URL to open.
        retries: The number of times to retry opening the URL.
        delay: The delay in seconds between retries.
    """

    options = Options()
    # options.add_argument("--headless=new")  # Uncomment for headless mode
    # If using webdriver_manager (recommended):
    # from webdriver_manager.chrome import ChromeDriverManager
    # service = Service(ChromeDriverManager().install())

    for attempt in range(retries):
        try:
            # If not using webdriver_manager, provide the path directly:
            # service = Service(executable_path="path/to/chromedriver")
            # driver = webdriver.Chrome(service=service, options=options)
            driver = webdriver.Chrome(options=options)  # or with service if using webdriver_manager

            driver.get(url)

            # Check for specific SSL-related errors in the page source
            if "ERR_SSL_PROTOCOL_ERROR" in driver.page_source or "net::ERR_CERT" in driver.page_source:
                raise WebDriverException("SSL certificate error detected in page source.")

            page_source = driver.page_source
            save_as_json(page_source)
            break

        except WebDriverException as e:
            if "ERR_SSL_PROTOCOL_ERROR" in str(e) or "net::ERR_CERT" in str(e):
                print(f"SSL certificate error: {e}. Attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
            else:  # If error isn't SSL related
                print(f"An error occurred: {e}")
                return  # Exit the program if there are other errors

        finally:
            if 'driver' in locals():
                driver.quit()

        time.sleep(delay)

    else:  # If all retries fail
        print(f"Failed to open URL after {retries} attempts.")


def save_as_json(page_source, filename="downloaded_data.json"):

    try:
        # Assuming the JSON data is already in the page_source
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
        print(f"JSON data saved to {filename}")

    except Exception as e:
        print(f"An error occurred during saving: {e}")


# Example usage:
link_to_open = "https://www.adidas.co.in/api/search/tf/suggestions/boots"  # Or any URL with product data JSON
open_link(link_to_open)

