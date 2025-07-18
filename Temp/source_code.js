const amqplib = require('amqplib');

async function getUrlsFromRabbitMQ(queueName) {
    try {
        const connection = await amqplib.connect('amqp://localhost');
        const channel = await connection.createChannel();

        await channel.assertQueue(queueName, { durable: true });

        let urls = [];

        // Use a promise to handle the asynchronous nature of consume
        await new Promise((resolve, reject) => {
            channel.consume(queueName, (msg) => {
                if (msg !== null) {
                    try {
                        const url = msg.content.toString();
                        urls.push(url);
                        channel.ack(msg); // Acknowledge message processing
                    } catch (error) {
                        console.error("Error processing message:", error);
                        channel.nack(msg); // Reject the message if processing fails
                    }
                }

                if (urls.length > 0) resolve(); // Resolve after first successful message


            }, { noAck: false }).catch((consumeError) => {
                console.error("Consume error:", consumeError);
                reject(consumeError); // Reject the outer promise in case of consume error
            });


        });

        await channel.close();
        await connection.close();
        return urls;

    } catch (error) {
        console.error('Error getting URLs from RabbitMQ:', error);
        return [];
    }
}


const amqp = require('amqplib');


async function sendToRabbitMQ(queueNames, message) { // Modified to accept an array of queue names
    try {
        // Establish a connection to RabbitMQ
        const connection = await amqp.connect('amqp://localhost');
        const channel = await connection.createChannel();

        // Iterate over each queue name and send the message
        for (const queueName of queueNames) {
            // Declare the queue with durability option
            await channel.assertQueue(queueName, { durable: true });

            // Publish the message with options for better reliability
            const options = { persistent: true }; // Ensure message is persisted to disk
            channel.sendToQueue(queueName, Buffer.from(message), options);

            console.log(`Sent message to ${queueName}:`, message);
        }


        // Graceful channel and connection closure
        await channel.close();
        await connection.close();

    } catch (error) {
        console.error("Error sending to RabbitMQ:", error);
        // Optionally retry or handle the error more gracefully
    }
}

// Example usage


async function testScrape() {
    const queueName = 'website_links';
    const elementQueueName = 'extracted_elements';
    const trainerQueueName = 'trainer';
    // The queue for extracted elements
    const testUrls = await getUrlsFromRabbitMQ(queueName);
    if (testUrls && testUrls.length > 0) {
        for (const url of testUrls) {
            console.log(`[testScrape] Processing URL: ${url}`); // ADD THIS LINE
            console.log(`Scraping: ${url}`);
            const results = await scrapeAndSortImproved(url); // Use the improved version
            if (results && results.length > 0) {
                console.log(`Found ${results.length} matches:`);
                // Limit output to up to 4 matches
                const displayCount = Math.min(results.length, 4); // Display up to 4
                const matchesToSend = results.slice(0, displayCount).map((match, index) => {
                    const formattedMatch = `Match ${index + 1}:\n${match}\n---\n \n`; // Format the match
                    console.log(formattedMatch); // Log the formatted match
                    return formattedMatch; // Return the formatted match for sending
                });
                const message = JSON.stringify(matchesToSend); // Send as JSON string
                await sendToRabbitMQ([elementQueueName, trainerQueueName], message); // Send to both queues
                console.log("\n");
            }
            console.log("\n");
        }
    } else {
        console.log("No URLs found in the queue.");
    }
}
module.exports = { testScrape };


//Improved version with better error handling and more robust matching
async function scrapeAndSortImproved(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const html = await response.text();

        // Regex without the s flag (compatible with older Node.js)
        const regexImproved = /(<input[^>]+type\s*=\s*['"]?(search|text)['"]?[^>]*>)|(<button[^>]*>.*?<\/button>)|(<form[^>]*>.*?<input[^>]+type\s*=\s*['"]?(search|text)['"]?[^>]*>.*?<\/form>)|<(\w+|div)[^>]+(?:class|id)\s*=\s*['"](?:search|search-box|searchbox|yt-searchbox|ytSearchboxComponentHost)\b[^'"]*['"][^>]*>[\s\S]*?<\/\1>|<input[^>]+(?:placeholder|aria-label)\s*=\s*['"][^'"]*search[^'"]*['"][^>]*>|(<input[^>]+data-(?:auto-id|test-id)\s*=\s*['"][^'"]*search[^'"]*['"][^>]*>)|(?:search)\b[^'"]*['"][^>]*>[\s\S]*?<\/\1>/gi;
        const matches = Array.from(html.matchAll(regexImproved), m => m[0]);

        return matches;
    } catch (error) {
        console.error("Error scraping or processing:", error);
        return null;
    }
}