from bs4 import BeautifulSoup
import requests
def scrape_h1_tags(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find all h1 tags
  h1_tags = soup.find_all('h1')

  # Extract text from the h1 tags
  h1_text_list = [tag.text.strip() for tag in h1_tags]
  return h1_text_list

def extract_headings(soup):
    headings = {}
    for tag in ['id', 'url', 'products', 'analyticsName']:
        tags = soup.find_all(tag)
        if tags:
            headings[tag] = [tag.text.strip() for tag in tags]
    return headings

def extract_title(soup):
    title = soup.title
    return title.text.strip() if title else None

def extract_images(soup):
    images = []
    for img in soup.find_all('img'):
        images.append({'src': img.get('src'), 'alt': img.get('alt')})
    return images

def extract_divs_and_classes(soup, class_name):
    divs = soup.find_all('div')
    specific_class_elements = soup.find_all(class_=class_name)

    return divs, specific_class_elements

def extract_info(file_path):
    with open(file_path, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    info = {}
    info['products'] = extract_headings(soup)
    info['id'] = extract_title(soup)
    info['images'] = extract_images(soup)
  

    info['divs'], info['specific_class_elements'] = extract_divs_and_classes(soup, "your_class_name")

    return info

# Example usage:
file_path = "E:\Temp\product_data.txt"
extracted_info = extract_info(file_path)

# Accessing specific information:
print(extracted_info)
print(extracted_info)
print(extracted_info)
print(extracted_info)
print(extracted_info)