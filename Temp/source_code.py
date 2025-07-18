import requests
from time import sleep

def get_source_code(url):
  headers = {'User-Agent': 'Your User-Agent String'}  # Replace with your desired User-Agent

  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for error HTTP statuses

    if response.status_code == 200:
      return response.text
    else:
      print(f"Error fetching URL: {response.status_code} - {response.reason}")
      return None

  except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}")
    return None

if __name__ == "__main__":
    url = input("Enter the URL of the website: ")

    while True:
        source_code = get_source_code(url)
        if source_code:
            print(source_code)
            break
        else:
            print("Failed to fetch source code. Retrying in 5 seconds...")
            sleep(5)

  