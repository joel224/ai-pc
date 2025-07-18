import requests
from bs4 import BeautifulSoup

def scrape_elements(url, tags):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    for tag in tags:
        elements = soup.find_all(tag)
        for element in elements:
            if element.name == 'img':
                print(element.get('src'))
            else:
                print(element.text)

# Read and parse the extracted tags from the file
with open('E:\\Temp\\ai_explanation.txt', 'r') as f:
    tags_html = f.read()
    tags_soup = BeautifulSoup(tags_html, 'html.parser')
    tags = [tag.name for tag in tags_soup.find_all()] # Extract tag names

# Specify the target URL
url = 'https://example.com'  # Replace with your target URL

# Call the scraping function
scrape_elements(url, tags)


