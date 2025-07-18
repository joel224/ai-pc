const puppeteer = require('puppeteer');
const fs = require('fs');
const amqp = require('amqplib');
const path = require('path'); // Added path module for file path manipulation

// Create 'output' directory if it doesn't exist
const outputDir = 'output';
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

async function scrapeWebsite(url) {
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    try {
        await page.goto(url, { waitUntil: 'domcontentloaded' });

        const pageContent = await page.evaluate(() => {
            return document.body.innerText;
        });

        console.log('Raw Page Content for', url, ':');
        console.log(pageContent);

        const isJson = isContentJson(pageContent);
        console.log('Is JSON:', isJson);

        // Generate filename from URL
        const filename = generateFilenameFromUrl(url);
        const filePath = path.join(outputDir, `${filename}.json`);

        // Prepare data to be saved
        let dataToSave;
        if (isJson) {
            dataToSave = JSON.parse(pageContent); // Parse if it's JSON for proper JSON file
        } else {
            dataToSave = { content: pageContent }; // Wrap in an object if not JSON
        }

        // Save content to a separate JSON file
        fs.writeFileSync(filePath, JSON.stringify(dataToSave, null, 2)); // Use 2 spaces for indentation

        console.log(`Data saved to ${filePath}`);

        await browser.close();
        return true; // Indicate success
    } catch (error) {
        console.error('Error scraping website', url, ':', error);
        await browser.close();
        return false; // Indicate failure
    }
}

function isContentJson(content) {
    try {
        JSON.parse(content);
        return true;
    } catch (e) {
        return false;
    }
}

function generateFilenameFromUrl(url) {
    // Remove protocol (http://, https://) and replace invalid characters for filenames
    let filename = url.replace(/^https?:\/\//, '').replace(/[^a-zA-Z0-9._-]+/g, '_');
    // Limit filename length to avoid issues with file systems
    filename = filename.substring(0, 150);
    return filename;
}


async function scrapeUrlsFromFile(filePath) {
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const urlsData = JSON.parse(fileContent);

        if (Array.isArray(urlsData)) {
            const successfulUrls = [];
            for (const item of urlsData) {
                if (item && item.url) {
                    let url = item.url;
                    if (url.startsWith(':')) {
                        url = url.substring(1);
                    }
                    const success = await scrapeWebsite(url); // scrapeWebsite now saves the file
                    if (success) {
                        successfulUrls.push(url);
                        await sendToRabbitMQ(url, 'URLSERVER'); // Send successful URL to RabbitMQ
                    }
                } else {
                    console.error('Invalid URL item:', item);
                }
            }
            console.log('\nSuccessful URLs:');
            successfulUrls.forEach((url) => console.log(url));
            console.log('\nNumber of successful links:', successfulUrls.length);
        } else {
            console.error('File content is not an array.');
        }
    } catch (error) {
        console.error('Error reading or parsing file:', error);
    }
}

async function sendToRabbitMQ(url, queueName) {
    try {
        const connection = await amqp.connect('amqp://localhost'); // Replace with your RabbitMQ connection string
        const channel = await connection.createChannel();

        await channel.assertQueue(queueName, { durable: false });
        channel.sendToQueue(queueName, Buffer.from(url));
        console.log(`Sent URL "${url}" to RabbitMQ queue "${queueName}"`);

        await channel.close();
        await connection.close();
    } catch (error) {
        console.error('Error sending to RabbitMQ:', error);
    }
}

// Example usage: Replace 'urls.json' with the actual file path
const filePath = 'requests.json'; // Replace with your file path
scrapeUrlsFromFile(filePath);