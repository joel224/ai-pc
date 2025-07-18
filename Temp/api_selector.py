import requests
from bs4 import BeautifulSoup
import time
from random import choice
from itertools import cycle

USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    # ... add more user agents
]


def get_website_info(url):
    """
    Visits a website and retrieves headers and the user-agent
    used by the requests library.

    Args:
        url (str): The URL of the website to visit (e.g., "https://www.example.com").

    Returns:
        tuple or None: A tuple containing (headers, user_agent) if successful,
                        None if there's an error visiting the website.
                        headers is a dictionary-like object of HTTP headers.
                        user_agent is the string representing the user-agent.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        headers = response.headers
        # The user-agent used by requests is sent in the request headers.
        # We can access it via the request attribute of the response.
        user_agent = response.request.headers.get('User-Agent')

        return headers, user_agent

    except requests.exceptions.RequestException as e:
        print(f"Error visiting website (get_website_info): {e}")
        return None


def extract_cookie_or_token_generalized(url, base_headers, base_user_agent, retries=3, delay=5):
    """
    Attempts to extract cookies or tokens, using provided base headers and user-agent,
    with retry logic and User-Agent rotation (though base user-agent is preferred now).
    Proxies have been removed from this version.
    """
    for attempt in range(retries):
        try:
            # 1. Use Provided Base User-Agent and Headers, but still rotate User-Agent from list for robustness
            headers = base_headers.copy() if base_headers else {} # Start with base headers if available
            headers['User-Agent'] = base_user_agent if base_user_agent else choice(USER_AGENT_LIST) # Prefer base user-agent if available, else rotate.


            session = requests.Session()
            response = session.get(url, headers=headers, timeout=10) # Proxies removed
            response.raise_for_status()

            # --- Extract data from response (simplified for this example) ---
            if response.cookies:
                print("\nCookies found in response headers:")
                for cookie in response.cookies:
                    print(f"  {cookie.name}: {cookie.value[:50]}...") # print first 50 chars of value

            # Parse HTML (if needed for token extraction - example, you can adapt this part)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Example: look for meta tags with tokens (adjust selector based on website structure)
            meta_token_tag = soup.find('meta', attrs={'name': 'csrf-token'}) # Example, adjust name as needed
            if meta_token_tag:
                token = meta_token_tag.get('content')
                if token:
                    print(f"\nPotential CSRF Token (from meta tag): {token[:50]}...") # Print first 50 chars


            return response.cookies # Or return extracted token, or both in a dict, etc.

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:  # Retry on 403
                print(f"403 Forbidden. Attempt {attempt + 1}/{retries}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            elif e.response.status_code == 407:  # Handle Proxy Authentication Required - REMOVED
                print(f"407 Proxy Authentication Required: {e}")
                return None
            else: # other HTTP errors
                print(f"HTTP Error: {e}")
                return None
        except requests.exceptions.RequestException as e:  # Handle network errors
            print(f"Request Exception: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    print(f"Failed to extract data after {retries} attempts.")
    return None


if __name__ == '__main__':
    reference_website_url = "https://api.publicapis.org" # Use a reliable website to get base info
    target_url = "https://api.publicapis.org/entries" # Or any URL you want to target for extraction

    base_website_info = get_website_info(reference_website_url) # Get base info from reference site

    if base_website_info:
        base_headers, base_user_agent = base_website_info
        print("\n--- Base Website Headers (from example.com)---") # Indicate where headers are from
        for key, value in base_headers.items():
            print(f"{key}: {value}")
        print(f"\n--- Base User-Agent (from example.com)---") # Indicate where user-agent is from
        print(base_user_agent)


        print(f"\n--- Attempting to extract data from: {target_url} using base headers & user-agent ---")
        extracted_data = extract_cookie_or_token_generalized(target_url, base_headers, base_user_agent)

        if extracted_data:
            print("\nExtracted Data (Type):", type(extracted_data)) # Indicate the type of extracted data
            if isinstance(extracted_data, requests.cookies.RequestsCookieJar): # Check if it's a cookie jar
                print("\nExtracted Cookies:")
                for name, value in extracted_data.items():
                    print(f"  {name}: {value[:50]}...")
            # You can add more checks for different types of extracted_data if needed
        else:
            print("\nNo significant data extracted from target URL.")

    else:
        print(f"\nCould not retrieve base website information from {reference_website_url}.  Cannot proceed with extraction.")