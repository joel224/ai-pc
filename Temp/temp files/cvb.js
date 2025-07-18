const amqplib = require('amqplib');

async function main() {
    console.log("Hello from the main function!");
    const name = "John Doe";
    console.log("Name:", name);
    greetUser("Alice");
}

function greetUser(userName) {
    console.log("Hello,", userName + "!");
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
                    if(require.main === module){
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