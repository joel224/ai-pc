import scrapy
import json
import random

class GenericSpider(scrapy.Spider):
    name = 'generic_spider'
    # You can define start_urls or dynamically set them in the constructor or from command line
    # For demonstration, we will use a placeholder, and you should replace it.
    start_urls = ['https://www.adidas.co.in/api/plp/content-engine/search?query=boots&startIndex=0'] # Replace with a real website to test

    # Realistic User-Agent strings - consider using a larger list
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers=self.get_headers(url))

    def get_headers(self, url):
        """
        Returns realistic browser-like headers.
        Customize as needed for specific websites.
        """
        return {
            'User-Agent': random.choice(self.user_agent_list),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': url, # Or a more generic referer like the website's base URL
            'DNT': '1', # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'same-origin', # Adjust these based on request origin during actual browsing
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            # Add cookies if needed - for session persistence or bypassing simple bot detection
            # 'Cookie': '...',
        }

    def parse(self, response):
        """
        Main parsing function to handle API or HTML responses robustly.
        """
        self.logger.info(f"Processing URL: {response.url}")
    
        # Check for common API response types (JSON)
        if b'application/json' in response.headers.get(b'Content-Type', b'').lower():
            try:
                api_data = json.loads(response.body)
                self.process_api_data(api_data, response) # Dedicated API processing
            except json.JSONDecodeError:
                self.logger.warning(f"Failed to decode JSON from {response.url}, falling back to HTML parsing.")
                self.process_html_data(response) # Fallback to HTML if JSON fails
        else:
            # Assume HTML content if not JSON
            self.process_html_data(response)
    

    def process_api_data(self, api_data, response):
        """
        Process API data (JSON). Customize data extraction based on API structure.
        """
        self.logger.info(f"Processing API data from: {response.url}")
        # Example: Print the entire JSON response (customize based on actual API response)
        print("API Data:")
        print(json.dumps(api_data, indent=4)) # Pretty print JSON

        # Example: Extract specific fields - adjust based on the API response structure
        # items = api_data.get('items', [])
        # for item in items:
        #     title = item.get('title')
        #     # ... extract other data ...
        #     print(f"Title: {title}")

    def process_html_data(self, response):
        """
        Process HTML data. Extract relevant information using CSS selectors or XPath.
        """
        self.logger.info(f"Processing HTML data from: {response.url}")
        print("HTML Data:")

        # Example: Extract the title of the page
        page_title = response.css('title::text').get()
        if page_title:
            print(f"Page Title: {page_title}")

        # Example: Extract all links on the page (just an example - customize selectors)
        links = response.css('a::attr(href)').getall()
        # for link in links:
        #     absolute_link = response.urljoin(link) # Make relative links absolute
        #     print(f"Link: {absolute_link}")

        # Add more sophisticated HTML parsing logic here based on the target website structure.
        # Use Scrapy selectors (CSS or XPath) to target specific elements and extract data.


# --- How to Run this Spider ---
# 1. Save this code as a .py file in your Scrapy project's 'spiders' directory (e.g., generic_spider.py).
# 2. In your Scrapy project's settings.py, configure settings for robustness:

# settings.py (Example Robust Settings)
# ----------------------------------
# DOWNLOAD_DELAY = 2  # Delay between requests (in seconds) - adjust as needed
# RANDOMIZE_DOWNLOAD_DELAY = True # Randomize the download delay

# # Configure item pipelines
# # See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'your_project.pipelines.YourPipeline': 300,
# }

# # Enable and configure Retry middleware
# RETRY_ENABLED = True
# RETRY_TIMES = 3  # Number of times to retry
# RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 429] # HTTP codes to retry

# # Enable and configure the AutoThrottle extension (adjust as needed)
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 5.0
# AUTOTHROTTLE_MAX_DELAY = 60.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# AUTOTHROTTLE_DEBUG = False

# # Configure a realistic User-Agent (you can also use a UserAgentMiddleware for rotation)
# # USER_AGENT = 'Your Advanced Scraper User Agent' # Or remove from settings and use the spider's user_agent_list

# # If you need proxies, configure them here or use a Proxy Middleware
# # HTTPPROXY_ENABLED = True
# # PROXY_POOL = [
# #     {'url': 'http://username:password@host:port'},
# #     {'url': 'http://host:port'},
# #     # ... more proxies ...
# # ]
# # DOWNLOADER_MIDDLEWARES = {
# #     'your_project.middlewares.ProxyMiddleware': 100, # Custom Proxy Middleware (example needed if using PROXY_POOL)
# #     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110, # Built-in HTTP Proxy Middleware
# # }
# ----------------------------------

# 3. Run the spider from the command line:
#    scrapy crawl generic_spider -a start_urls='http://targetwebsite.com,http://anotherwebsite.com'
#    Or to run with the default start_urls:
#    scrapy crawl generic_spider


# --- Explanation and Advanced Considerations ---

# 1. Realistic Headers:
#    - The `get_headers` method creates a dictionary of headers that mimic a real browser.
#    - 'User-Agent' is randomized from a list to further avoid simple bot detection.
#    - 'Accept', 'Accept-Language', 'Referer', etc., are standard browser headers.
#    - You can customize these further based on your browser's headers for a specific website.
#    - 'Sec-Fetch-*' headers are modern browser security/fetch metadata; including them makes requests look more legitimate.

# 2. API and HTML Handling:
#    - The `parse` method intelligently checks the 'Content-Type' header of the response.
#    - If it's 'application/json', it attempts to parse it as JSON and calls `process_api_data`.
#    - If JSON parsing fails or the content type is not JSON, it falls back to `process_html_data`.
#    - This allows the spider to handle both API endpoints and regular HTML pages from "any website".

# 3. Robust Error Handling:
#    - Settings (see settings.py example) enable Retry middleware to handle transient errors (server errors, timeouts, etc.).
#    - `RETRY_HTTP_CODES` specifies which HTTP codes should trigger a retry.
#    - `AUTOTHROTTLE_ENABLED` helps to prevent overloading the website by automatically adjusting download delays based on website load.

# 4. Anti-Blocking Measures:
#    - User-Agent rotation (within the spider).
#    - `DOWNLOAD_DELAY` and `RANDOMIZE_DOWNLOAD_DELAY` in settings to slow down crawling and make it less bot-like.
#    - Consider enabling and configuring Proxy Middleware (example commented out in settings.py) for more advanced scenarios where IP blocking is a concern. You would need to provide a list of proxies.

# 5. API Data Processing (`process_api_data`):
#    - This method is designed to handle JSON API responses.
#    - It currently just pretty-prints the entire JSON.
#    - You need to customize this section to extract specific data based on the structure of the API responses you expect from "any website".
#    - Inspect the API response structure (e.g., using browser's developer tools Network tab when the website uses an API) and then write code to navigate the JSON and extract the fields you need.

# 6. HTML Data Processing (`process_html_data`):
#    - This method handles HTML responses.
#    - It currently extracts the page title and all links as examples.
#    - For "any website", you'll need to inspect the HTML structure of the specific websites you are targeting.
#    - Use browser developer tools (Inspect Element) to identify CSS selectors or XPath expressions that target the data you want to extract.
#    - Replace the example selectors in `process_html_data` with your custom selectors.

# 7. Dynamic Start URLs:
#    - The `start_urls` is currently a placeholder.
#    - You can:
#        a) Replace the placeholder with a specific URL when you run the spider.
#        b) Pass `start_urls` as a command-line argument when running the spider (as shown in "How to Run").
#        c) Generate `start_urls` dynamically within the spider's `__init__` or `start_requests` method, e.g., reading from a file or an API.

# 8. Advanced Features (Beyond this Basic Example):
#    - Proxy Rotation: Implement a robust Proxy Middleware with proxy lists, proxy testing, and rotation logic for large-scale or block-prone scraping.
#    - CAPTCHA Handling: For websites with CAPTCHA protection, you would need to integrate a CAPTCHA solving service.
#    - Cookie Management: For websites that rely on cookies for sessions or tracking, handle cookies appropriately, potentially using Scrapy's CookieJar middleware or custom logic.
#    - Login and Session Handling: If data is behind a login, implement login functionality (form submissions, session cookies).
#    - Distributed Crawling: For very large-scale data collection, consider distributed Scrapy setups (e.g., using Scrapy Cluster or Scrapyd).
#    - Data Pipelines: Instead of just printing data, use Scrapy Item Pipelines to store data in databases, files (CSV, JSON, etc.), or process it further.

# Remember to replace 'http://example.com' in `start_urls` with the actual website you want to scrape and adjust the parsing logic (CSS/XPath selectors in `process_html_data` and data extraction in `process_api_data`) to match the structure of that website.  Always respect website's `robots.txt` and terms of service. Use responsible scraping practices.