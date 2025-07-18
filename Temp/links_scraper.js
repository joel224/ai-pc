const { random } = require('user-agents');
let fs = require('fs/promises');
let puppeteer = require('puppeteer');

async function scrapeAdidasNetworkData() {
  let browser; // Declare browser outside the try block
  try {
    browser = await puppeteer.launch({ headless: false, args: ['--user-agent=' + random().toString()] });
    const page = await browser.newPage();
    await page.goto('https://www.google.com/', { waitUntil: 'networkidle2' });

    // Wait for initial page load
    await Promise.race([
      page.waitForNavigation({ waitUntil: 'networkidle2' }),
      new Promise(resolve => setTimeout(resolve, 4000)),
    ]);

    page.on('request', (request) => {
      if (request.url().includes('adidas.co.in')) {
        writeEventToFile('request', `"${request.method()}" "${request.url()}"`);
      }
    });

    page.on('response', (response) => {
      if (response.url().includes('adidas.co.in')) {
        writeEventToFile('response', `"${response.status()}" "${response.url()}"`);
      }
    });

    // Scroll down the page progressively
    for (let i = 0; i < 3; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await Promise.race([
        page.waitForNavigation({ waitUntil: 'networkidle2' }),
        new Promise(resolve => setTimeout(resolve, 5000)),
      ]);
    }

    // Solve CAPTCHA if necessary
    const captcha = await page.$('iframe[src*="recaptcha"]');
    if (captcha) {
      console.error('CAPTCHA encountered, solving logic not implemented!');
      return; // Or throw an error if you want to stop execution
    }

    console.log('Network data captured, implement logic to save requestData and responseData');

  } catch (error) {
    console.error("Error during scraping:", error);
  } finally {
    if (browser) { // Check if browser is defined before closing
      await browser.close();
    }
  }
}

function writeEventToFile(eventType, data) {
  try {
    const message = `${eventType} , ${data}`;
    fs.writeFile('event_log.txt', message + '\n');
  } catch (error) {
    console.error('Error writing event to file:', error);
  }
}

scrapeAdidasNetworkData();