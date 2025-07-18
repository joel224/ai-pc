const puppeteer = require('puppeteer');
const amqp = require('amqplib');

const RABBITMQ_HOST = 'amqp://localhost'; // Your RabbitMQ server address
const LINK_QUEUE = 'website_links'; // Queue to receive URLs from
const ELEMENT_QUEUE = 'website_search_elements'; // Queue to send elements to

async function sendToQueue(elements) {
    try {
        const connection = await amqp.connect(RABBITMQ_HOST);
        const channel = await connection.createChannel();

        await channel.assertQueue(ELEMENT_QUEUE, { durable: true });

        const message = JSON.stringify(elements);
        channel.sendToQueue(ELEMENT_QUEUE, Buffer.from(message), { persistent: true });

        console.log("Sent to queue:", ELEMENT_QUEUE);

        await channel.close();
        await connection.close();
    } catch (error) {
        console.error("Error sending to queue:", error);
    }
}

async function scrapeElements(url) {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        page.setDefaultNavigationTimeout(60000); // 1 minute timeout
        await page.goto(url, { waitUntil: 'networkidle2' }); // Wait for network idle

        const elements = await page.evaluate(() => {
            const links = document.querySelectorAll('a');
            return Array.from(links).map(link => link.href).filter(href => href.startsWith('http'));
        });

        await browser.close();
        return elements;
    } catch (error) {
        console.error("Error scraping elements:", error);
        return []; // Return an empty array in case of error
    }
}

async function receiveUrl() {
    try {
        const connection = await amqp.connect(RABBITMQ_HOST);
        const channel = await connection.createChannel();

        await channel.assertQueue(LINK_QUEUE, { durable: true }); // Make queue durable

        console.log('Waiting for URLs on queue:', LINK_QUEUE);

        channel.consume(LINK_QUEUE, async (msg) => {
            if (msg !== null) {
                try {
                    const messageContent = msg.content.toString();
                    const messageObject = JSON.parse(messageContent);

                    if (!messageObject || !messageObject.url) {
                        console.error("Invalid message format received:", messageContent);
                        channel.ack(msg); // Still acknowledge invalid messages to avoid infinite loop
                        return;
                    }

                    const url = messageObject.url;
                    console.log('Received URL:', url);

                    const elements = await scrapeElements(url);
                    await sendToQueue(elements);

                    channel.ack(msg);
                } catch (parseError) {
                    console.error("Error parsing message content:", parseError);
                    channel.nack(msg); // Nack message on parse error so it can be redelivered
                }
            }
        });
    } catch (error) {
        console.error("Error receiving URL:", error);
    }
}

// Start the receiver
receiveUrl();