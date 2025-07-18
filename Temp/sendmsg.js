const amqp = require('amqplib');

async function sendMessage(message) {
    try {
        const connection = await amqp.connect('amqp://guest:guest@localhost');
        const channel = await connection.createChannel();
        const queueName = 'my_queue';

        await channel.assertQueue(queueName, { durable: true }); // Make sure durable is consistent

        channel.sendToQueue(queueName, Buffer.from(message), { persistent: true }); // persistent for message durability
        console.log(` [x] Sent ${message}`);

        await channel.close();
        await connection.close();
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

async function main() {
    await sendMessage("input[name=\"search_query\"]");
    setTimeout(() => {
        process.exit(0);
    }, 500); // Exit after sending (important!)
}

main();
