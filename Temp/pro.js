const fs = require('fs').promises;
const puppeteer = require('puppeteer');
const amqplib = require('amqplib');
const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const { Key } = require('selenium-webdriver');
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

    let driver;
    let browser;
    let page;
    let searchBarSelectors;

    const { connection, channel } = await connectToRabbitMQ();
    if (!channel) {
        console.log("Failed to connect to RabbitMQ");
        return false;
    }

    // Selector prioritization logic
    let receivedSelector = await receiveMessages();
    if (customSearchBarSelector) {
        searchBarSelectors = [customSearchBarSelector];
        console.log("Using custom search bar selector:", customSearchBarSelector);
    } else if (receivedSelector) {
        searchBarSelectors = [receivedSelector];
        console.log("Using search bar selector from RabbitMQ:", receivedSelector);
    } else {
        searchBarSelectors = ['.css-1upamjb','#lst-ib', 'input[name="q"]', '.gLFyf', 'input[type="search"]'];
        console.log("Using default search bar selectors");
    }

    try {
        // Selenium Initialization
        console.log('Launching Selenium browser...');
        const options = new chrome.Options();
         // Use headless mode for Chrome
        driver = await new Builder()
            .forBrowser('chrome')
            .setChromeOptions(options)
            .build();
        console.log('Browser launched.');

        await driver.manage().window().setRect({ width: 1280, height: 720 });
        console.log('Viewport set.');

        // Navigation and Search Logic
        for (let attempt = 1; attempt <= 3; attempt++) {
            try {
                console.log(`Attempt ${attempt} to find search bar...`);
                await driver.get(targetUrl);
                console.log('Page loaded.');

                let searchBar;
                for (const selector of searchBarSelectors) {
                    try {
                        console.log(`Attempting selector: ${selector}`);
                        searchBar = await driver.wait(
                            until.elementLocated(By.css(selector)),
                            7000
                        );
                        console.log(`Search bar found with selector: ${selector}`);
                        break;
                    } catch (err) {
                        console.error(`Selector "${selector}" failed:`, err.message);
                    }
                }

                if (!searchBar) {
                    throw new Error('Search bar not found with any selector');
                }

                // Perform search
                await searchBar.sendKeys(searchTerm + Key.ENTER);
                console.log('Typed searchTerm into search bar.');

                // Wait for navigation
                await driver.wait(until.urlContains('search'), 30000);
                console.log('Search results loaded!');
                break;

            } catch (error) {
                console.error(`Attempt ${attempt} failed:`, error.message);
                if (attempt === 3) throw error;
            }
        }

        // Puppeteer Network Capture
        console.log('Launching Puppeteer for network capture...');
        browser = await puppeteer.launch({ headless: false });
        page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 720 });

        const requests = [];
        const responses = [];
        await page.setRequestInterception(true);

        page.on('request', request => {
            requests.push({
                url: request.url(),
                method: request.method(),
                type: request.resourceType()
            });
            request.continue();
        });

        page.on('response', response => {
            responses.push({
                url: response.url(),
                status: response.status()
            });
        });

        // Navigate to final URL captured by Selenium
        const finalUrl = await driver.getCurrentUrl();
        await page.goto(finalUrl, { waitUntil: 'networkidle2', timeout: 30000 });
        console.log('Network capture complete.');

        // Save network data
        await fs.writeFile('requests.json', JSON.stringify(requests, null, 2));
        await fs.writeFile('responses.json', JSON.stringify(responses, null, 2));
        console.log('Network data saved successfully.');

        return true;

    } catch (error) {
        console.error('An error occurred:', error.message);

        // Capture screenshot using Selenium
        if (driver) {
            try {
                const screenshot = await driver.takeScreenshot();
                await fs.writeFile('searchbar_not_found_screenshot.png', screenshot, 'base64');
                console.log('Screenshot saved.');
            } catch (screenshotError) {
                console.error('Failed to capture screenshot:', screenshotError);
            }
        }

        const errorMsg = `Search failed: ${error.message}. URL: ${targetUrl}. Selectors tried: ${JSON.stringify(searchBarSelectors)}`;
        await sendErrorToRabbitMQ(channel, errorMsg);
        await sendUrlToRabbitMQ(channel, targetUrl);

        return false;

    } finally {
        // Cleanup
        if (driver) await driver.quit();
        if (browser) await browser.close();
        if (channel) await channel.close();
        if (connection) await connection.close();
    }
}

async function main() {
    const targetUrl = 'https://www.nykaa.com/'; // Example URL
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
