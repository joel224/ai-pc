const fs = require('fs').promises;
const puppeteer = require('puppeteer');
const amqplib = require('amqplib');
const { testScrape } = require('./source_code');

const RABBITMQ_HOST = 'amqp://localhost';
const ERROR_QUEUE = 'website_search_errors';
const LINK_QUEUE = 'website_links';
const LINK_QUEUE_GEMINI = 'website_links_gemini'; // Queue for sending URLs on search bar failure

async function connectToRabbitMQ() {
    try {
        const connection = await amqplib.connect(RABBITMQ_HOST);
        const channel = await connection.createChannel();
        await channel.assertQueue(ERROR_QUEUE);
        await channel.assertQueue(LINK_QUEUE);
        await channel.assertQueue(LINK_QUEUE_GEMINI); // Assert the new queue
        return {connection, channel}; //return both the connection and channel
    } catch (error) {
        console.error("Error connecting to RabbitMQ:", error);
        return null;
    }
}


async function receiveMessages() {
    try {
        const connection = await amqplib.connect('amqp://guest:guest@localhost');
        const channel = await connection.createChannel();
        const queueName = 'my_queue';

        await channel.assertQueue(queueName, { durable: true });

        const msg = await channel.get(queueName, { noAck: false }); // Get a single message

        if (msg) {
            console.log(` [x] Received ${msg.content.toString()}`);
            channel.ack(msg); // Acknowledge the message
            await channel.close();
            await connection.close();
            return msg.content.toString(); // Return the message content
        } else {
            console.log("No messages in the queue.");
            await channel.close();
            await connection.close();
            return ""; // Return an empty string if no message is available
        }
    } catch (error) {
        console.error('Error receiving messages:', error);
        return ""; // Return an empty string in case of an error
    }
}


async function sendErrorToRabbitMQ(channel, error2) {
    try {
        channel.sendToQueue(ERROR_QUEUE, Buffer.from(JSON.stringify(error2)));
        console.log('Error sent to RabbitMQ', error2);
    } catch (error2) {
        console.error('Error sending error to RabbitMQ:', error2);
    }
}



async function sendUrlToRabbitMQ(channel, targetUrl) {
    try {
        const cleanUrl = targetUrl.replace(/<br>/g, '');
        channel.sendToQueue(LINK_QUEUE, Buffer.from(cleanUrl));
        channel.sendToQueue(LINK_QUEUE_GEMINI, Buffer.from(cleanUrl));
        console.log(`URL sent to RabbitMQ queue ${LINK_QUEUE}: ${cleanUrl}`);

        await testScrape(); // Await the result of testScrape

    } catch (sendError) {
        console.error('Error sending URL to RabbitMQ:', sendError);
        sendErrorToRabbitMQ(channel, { message: 'Error sending URL to RabbitMQ', error: sendError });
    }
}


async function searchOnWebsite(targetUrl, searchTerm, customSearchBarSelector) {
    console.log('Searching on website:', targetUrl);
    const browser = await puppeteer.launch({ headless: false }); // Keep headless: false for debugging
    console.log('Browser launched.');
    const page = await browser.newPage();
    console.log('Page created.');
    await page.setViewport({ width: 1280, height: 720 }); // Or other suitable dimensions
    console.log('Viewport set.');


    const {connection, channel} = await connectToRabbitMQ(); // Get the channel object from the proper connection
    if(!channel){
      console.log("Failed to connect to rabbitMQ")
      return false
    }

    // Prioritize custom selector, then received selector, then defaults
    let searchBarSelectors;
    let receivedSelector = await receiveMessages(); // Get receivedSelector from RabbitMQ (mocked for now)

    if (customSearchBarSelector) {
        searchBarSelectors = [customSearchBarSelector];
        console.log("Using custom search bar selector:", customSearchBarSelector);
    } else if (receivedSelector) {
        searchBarSelectors = [receivedSelector];
        console.log("Using search bar selector from RabbitMQ:", receivedSelector);
    } else {
        searchBarSelectors = [

            '#lst-ib'
        ];
        console.log("Using default search bar selectors");
    }

    for (let attempt = 1; attempt <= 1; attempt++) { // Keep only one attempt for now for clarity.
        try {
            await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 }); // Try 'domcontentloaded' or remove waitUntil entirely
            console.log('Page loaded.');

            const requests = [];
            const responses = [];
            await page.setRequestInterception(true);
            console.log('Request interception set.');

            page.on('request', request => {
                requests.push({
                    url: request.url(),
                    method: request.method(),
                    postData: request.postData(),
                    headers: request.headers(),
                    type: request.resourceType(),
                    indicator: request.method()
                });
                request.continue();
            });

            page.on('response', response => {
                responses.push({
                    url: response.url(),
                    headers: response.request().headers(),
                    type: response.request().resourceType(),
                    indicator: response.status(),
                    networkStatus: response.statusText()
                });
            });

            let searchBar;

            if (searchBarSelectors && searchBarSelectors.length > 0) {
                for (const selector of searchBarSelectors) {
                    try {
                        console.log(`Attempting selector: ${selector}`);
                        const selectorTimeout = 7000; // Time limit for each selector attempt (5 seconds)
                        const searchBarPromise = page.waitForSelector(selector, { timeout: 90000 }); // Increased timeout to 60 seconds (60000 ms)
                        const timeoutPromise = new Promise((resolve, reject) => {
                            setTimeout(() => reject(new Error(`Selector "${selector}" timed out after ${selectorTimeout}ms`)), selectorTimeout);
                        });

                        searchBar = await Promise.race([searchBarPromise, timeoutPromise]);
                        console.log(`Search bar found with selector: ${selector}`);
                        break; // If found, break the loop
                    } catch (selectorError) {
                        console.error(`Selector "${selector}" failed:`, selectorError.message);
                        searchBar = null;
                    }
                }
            }

            if (!searchBar) {
                const errorMsg = `Search bar not found. Selectors: ${JSON.stringify(searchBarSelectors)}. URL: ${targetUrl}`;
                console.error("Error finding search bar:", errorMsg);
                await sendErrorToRabbitMQ(channel, errorMsg);
                await sendUrlToRabbitMQ(channel, targetUrl);

                await page.screenshot({ path: 'searchbar_not_found_screenshot.png' });
                console.log("Screenshot saved to searchbar_not_found_screenshot.png");

                throw new Error("Search bar not found."); // Re-throw to be caught by the outer catch
            }

            if (searchBar) {
                await searchBar.type(searchTerm);
                console.log('Typed searchTerm into search bar.'); // Added log
                await Promise.all([
                    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }), // Increased timeout here to 30 seconds
                    searchBar.press('Enter')
                ]);

                console.log('Search results loaded!');

                // Save network requests and responses to a file
                const requestsFile = 'requests.json';
                const responsesFile = 'responses.json';

                await fs.writeFile(requestsFile, JSON.stringify(requests, null, 2));
                await fs.writeFile(responsesFile, JSON.stringify(responses, null, 2));
                console.log(`Network requests saved to ${requestsFile}`);
                console.log(`Network responses saved to ${responsesFile}`);
                console.log("Search completed successfully!");
                return true;
            } else {
                console.log("Search bar not found.");
                return false;
            }
        } catch (error) {
            console.error('An error occurred:', error.message);
            if (!error.url) {
                error.url = targetUrl;
                const error2 = `Search bar not found within timeout. Selectors: ${JSON.stringify(searchBarSelectors)}. URL: ${targetUrl}. Error: ${error.message}`;
                await sendErrorToRabbitMQ(channel, error2);
                console.log(`[searchOnWebsite] Re-queuing URL due to GENERAL ERROR: ${targetUrl}`); // ADD THIS LOG
                
                receiveMessages(); // Keep this line as in original code
            }
        } finally {
            await browser.close();
            if (channel) {
                await channel.close();
            }
            if (connection){
              await connection.close()
            }
        }
    }
}

async function main() {
    const targetUrl = 'https://www.yahoo.com/'; // Example URL
    const searchTerm = 'puppeteer';
    let customSearchBarSelector = null;

    let searchSucceeded = false;
    let mainAttempts = 0;
    const maxMainAttempts = 2;
    const retryDelay = 5000;

    while (!searchSucceeded && mainAttempts < maxMainAttempts) {
        mainAttempts++;
        console.log(`Main attempt ${mainAttempts}...`);

        try {
            searchSucceeded = await searchOnWebsite(targetUrl, searchTerm, customSearchBarSelector);
        } catch (error) {
            console.error(`Main attempt ${mainAttempts} failed. Retrying...`, error.message); // Reduced log
            await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
    }

    if (searchSucceeded) {
        console.log("Overall search process completed successfully!");
    } else {
        console.error(`Overall search process failed after ${maxMainAttempts} attempts.`);
    }
}




let shouldCallMain = false;

async function receiveAndTrigger() {
    try {
        const connection = await amqplib.connect('amqp://localhost');
        const channel = await connection.createChannel();
        const queue = 'started1';

        await channel.assertQueue(queue, { durable: true });

        console.log(` [*] Waiting for messages in ${queue}. To exit press CTRL+C`);

        channel.consume(queue, (msg) => {
            if (msg !== null) {
                const messageContent = msg.content.toString();
                console.log(` [x] Received: ${messageContent}`);

                if (messageContent === "true") {
                    console.log("Data is true! Setting flag to call main()...");
                    shouldCallMain = true;
                    if (require.main === module) {
                        main();
                    }
                } else {
                    console.log("Received data is not true.");
                }
                channel.ack(msg);
            }
        });
    } catch (error) {
        console.error("Error connecting to RabbitMQ:", error);
    }
}

async function start() {
    await receiveAndTrigger();
}

start();
