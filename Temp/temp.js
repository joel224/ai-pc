const amqplib = require('amqplib');
const LINK_QUEUE = 'website_links';
const ERROR_QUEUE = 'website_search_errors';

async function getWebsiteContent(queueName) {
  try {
    const connection = await amqplib.connect('amqp://localhost'); 
    const channel = await connection.createChannel();

    await channel.assertQueue(queueName, { durable: true });

    let content = ''; 

    await channel.consume(
      queueName,
      (msg) => {
        if (msg) {
          const decodedContent = msg.content.toString('utf-8'); // Decode message
          content += decodedContent + '<br>';
          channel.ack(msg); 
        }
      },
      { noAck: false }
    );

    return content; 
  } catch (error) {
    console.error('Error getting content:', error);
    return ''; 
  }
}

async function getSearchErrors(queueName) {
  try {
    const connection = await amqplib.connect('amqp://localhost'); 
    const channel = await connection.createChannel();

    await channel.assertQueue(queueName, { durable: true });

    let errors = ''; 

    await channel.consume(
      queueName,
      (msg) => {
        if (msg) {
          const decodedError = msg.content.toString('utf-8'); // Decode message
          errors += decodedError + '<br>';
          channel.ack(msg); 
        }
      },
      { noAck: false }
    );

    return errors; 
  } catch (error) {
    console.error('Error getting search errors:', error);
    return ''; 
  }
}

async function main() {
  const websiteContent = await getWebsiteContent(LINK_QUEUE);
  const searchErrors = await getSearchErrors(ERROR_QUEUE);

  console.log('Website Content:\n', websiteContent);
  console.log('Search Errors:\n', searchErrors);
}

main();