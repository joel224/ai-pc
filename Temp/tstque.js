const amqp = require('amqplib');

async function receiveAndTrigger() {
  try {
    const connection = await amqp.connect('amqp://localhost'); // Replace with your RabbitMQ connection string
    const channel = await connection.createChannel();
    const queue = 'started'; // Queue name

    await channel.assertQueue(queue, { durable: true }); // Ensure queue exists

    console.log(` [*] Waiting for messages in ${queue}. To exit press CTRL+C`);

    channel.consume(queue, (msg) => {
      if (msg !== null) {
        const messageContent = msg.content.toString();
        console.log(` [x] Received ${messageContent}`);
    
        try {
            // Directly check if the content is "true" (string comparison)
            if (messageContent === "true") {
                console.log("Data is true! Calling main()...");
                main(); // Call your main function
            } else {
                console.log("Received data is not true.");
            }
    
        } catch (error) {
                console.error("Error parsing message content or invalid format:", error);
                // Handle the error appropriately, perhaps by nacking the message
                channel.nack(msg); // Reject the message to requeue or dead-letter queue
                return; // Important to exit the consumer callback after nacking
            }

            channel.ack(msg); // Acknowledge the message after processing.
        }
    });

  } catch (error) {
    console.error("Error connecting to RabbitMQ:", error);
  }
}

function main() {
  console.log("Executing main() function!");
  console.log("Your main function logic goes here.");
  // Your main function logic here
}

receiveAndTrigger();