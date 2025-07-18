
const fs = require('fs').promises; // Use promises for file system operations
// scraper.js (Main script - Producer)
const puppeteer = require('puppeteer');
const amqplib = require('amqplib');

const RABBITMQ_HOST = 'amqp://localhost'; // Or your RabbitMQ server address
const ERROR_QUEUE = 'website_search_errors';

async function connectToRabbitMQ() {
    try {
        const connection = await amqplib.connect(RABBITMQ_HOST);
        const channel = await connection.createChannel();
        await channel.assertQueue(ERROR_QUEUE);
        return channel;
    } catch (error) {
        console.error("Error connecting to RabbitMQ:", error);
        return null;
    }
}

async function searchOnWebsite(url, searchTerm, buttonSelector, elementsToScrollTo) {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  const channel = await connectToRabbitMQ();

    try {
        // Navigate to the specified URL and wait for the network to be idle.
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 140000 });
    
        // Check for page errors by examining the title.
        const errorTitle = await page.$eval('title', title => title.textContent).catch(() => null);
        if (errorTitle && (errorTitle.includes('404') || errorTitle.includes('Error'))) {
            throw new Error(`Page returned an error: ${errorTitle}`);
        }
    
        // Find the search bar element.
        const searchBar = await page.waitForSelector(
            'input[type="text"], input[type="search"], [name="q"], #search, .search-input, input.gLFyf, #lst-ib',
            { timeout: 30000 }
        ).catch(() => null);
    
        if (searchBar) {
            // Type the search term into the search bar.
            await searchBar.type(searchTerm);
    
            // Initialize a flag to track whether the search was triggered.
            let searchTriggered = false;
    
            // Check if the search bar is part of a form and submit it if so.
            if (await searchBar.evaluate(el => el.form)) {
                await Promise.all([
                    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 120000 }),
                    searchBar.press('Enter')
                ]).catch(() => {});
                searchTriggered = true;
            }
    
            // If the search hasn't been triggered yet, try clicking common search button selectors.
            async function searchOnWebsite(url, searchTerm, buttonSelector, elementsToScrollTo) {
              const browser = await puppeteer.launch({ headless: false });
              const page = await browser.newPage();
              const channel = await connectToRabbitMQ();
            
              try {
                // ...
            
                // If the search hasn't been triggered yet, try clicking common search button selectors.
                if (!searchTriggered) {
                  const searchButtonSelectors = [
                    '[type="submit"]',
                    'button[type="submit"]',
                    '#search-button',
                    '.search-submit',
                    '.search-button',
                    '#searchBtn',
                    '.btnK',
                    '[aria-label="Search"]',
                    'button:contains("Search")',
                    'input[type="image"][alt="Search"]'
                  ];
            
                  let errorOccurred = false;
            
                  for (const selector of searchButtonSelectors) {
                    try {
                      const searchButton = await page.waitForSelector(selector, { timeout: 5000 });
                      await Promise.all([
                        page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 120000 }),
                        searchButton.click()
                      ]);
                      searchTriggered = true;
                      break;
                    } catch (error) {
                      errorOccurred = true;
                      await sendErrorToRabbitMQ(channel, error);
                    }
                  }
            
                  if (errorOccurred) {
                    throw new Error('Error occurred while trying to trigger search');
                  }
                }
            
                // ...
              } catch (error) {
                console.error('Error occurred:', error);
              }
            }
            
            async function sendErrorToRabbitMQ(channel, error) {
              try {
                const errorData = {
                  message: error.message,
                  stack: error.stack,
                };
            
                channel.sendToQueue(ERROR_QUEUE, Buffer.from(JSON.stringify(errorData)));
                console.log('Error sent to RabbitMQ');
              } catch (error) {
                console.error('Error sending error to RabbitMQ:', error);
              }
            }
    




            
            // Check if the search was triggered successfully.
            if (!searchTriggered) {
                console.log("Could not trigger search automatically.");
            } else {
                console.log('Search results loaded!');
    
                // Scroll to specified elements on the search results page.
                // ... other code ...
                
                // Scroll to specified elements on the search results page.
                if (elementsToScrollTo && elementsToScrollTo.length > 0) {
                    for (const elementSelector of elementsToScrollTo) {
                        const element = await page.evaluate((selector) => document.querySelector(selector), elementSelector);
                        if (element) {
                            await element.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
                        } else {
                            console.log(`Element with selector '${elementSelector}' not found for scrolling. Trying fallback elements.`);
                
                            // Use fallback elements from file if original selector not found
                            const fallbackElements = await loadElementsFromFile('fallback_elements.json'); // Use a different file for fallback
                            if (fallbackElements && fallbackElements.length > 0) {
                                for (const fallbackSelector of fallbackElements) {
                                    const fallbackElement = await page.evaluate((selector) => document.querySelector(selector), fallbackSelector);
                                    if (fallbackElement) {
                                        await fallbackElement.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
                                        console.log(`Scrolled to fallback element: ${fallbackSelector}`);
                                    } else {
                                        console.log(`Fallback element with selector '${fallbackSelector}' not found.`);
                                    }
                                }
                            }
                
                
                        }
                        await page.waitForTimeout(1000);
                    }
                }
                
               
                // Find and click the specified button.
                const button = await page.waitForSelector(buttonSelector, { timeout: 5000 }).catch(() => null);
                if (button) {
                    await button.evaluate(element => element.scrollIntoView({ block: 'center', inline: 'center' }));
                    await button.click();
                    console.log('Button clicked!');
                } else {
                    console.log(`Button with selector '${buttonSelector}' not found.`);
                }
            }
        } else {
            console.log("Could not find a suitable search bar.");
        }
    } catch (error) {
        console.error('An error occurred:', error.message);
        await sendErrorThroughRabbitMQ(error);
      throw error;

        

    } finally {
        await browser.close();
        if (channel) {
            await channel.close(); // Close the channel
        }
    }
}

// Example usage:

async function sendErrorThroughRabbitMQ(error) {
  try {
    const connection = await amqplib.connect(RABBITMQ_HOST);
    const channel = await connection.createChannel();
    await channel.assertQueue(ERROR_QUEUE);

    const errorData = {
      message: error.message,
      stack: error.stack,
    };

    channel.sendToQueue(ERROR_QUEUE, Buffer.from(JSON.stringify(errorData)));
    console.log('Error sent through RabbitMQ');
  } catch (error) {
    console.error('Error sending error through RabbitMQ:', error);
  }
}

// consumer.js (Consumer script)




async function consumeErrors() {
  try {
    const connection = await amqplib.connect(RABBITMQ_HOST);
    const channel = await connection.createChannel();
    await channel.assertQueue(ERROR_QUEUE);

    console.log('Waiting for errors...');

    channel.consume(ERROR_QUEUE, (msg) => {
      if (msg) {
        const errorData = JSON.parse(msg.content.toString());
        console.error('Received error:', errorData);

        // Implement your error handling logic here
        console.log('Handling error... (Implement your logic)');

        channel.ack(msg); // Acknowledge message processing
      }
    });
  } catch (error) {
    console.error('Error connecting to RabbitMQ or consuming messages:', error);
  }
}

consumeErrors();


async function loadElementsFromFile(filePath) {
    try {
        const data = await fs.readFile(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`Error loading elements from file: ${error.message}`);
        return []; // Return an empty array in case of error
    }
}

async function main() {
    const targetUrl = 'https://www.google.com';
    const searchTerm = 'puppeteer';
    const buttonSelector = '#rso > div:nth-child(1) > div > div > div > div > div > div > div > div.yuRUbf > a';

    // Load elements from file (e.g., elements.json)
    const elementsToScrollTo = await loadElementsFromFile('elements.json');
    console.log("elementsToScrollTo:", elementsToScrollTo)

    searchOnWebsite(targetUrl, searchTerm, buttonSelector, elementsToScrollTo);
}

main();