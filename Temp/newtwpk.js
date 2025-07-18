const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function captureNetworkTraffic(url, outputDir) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    const requests = new Map();

    // Create output directory
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    // Capture requests
    page.on('request', (request) => {
        const requestId = request.url() + Date.now();
        requests.set(requestId, {
            url: request.url(),
            method: request.method(),
            headers: request.headers(),
            postData: request.postData(),
            resourceType: request.resourceType(),
            timing: null,
            response: null
        });
    });

    // Capture responses
    page.on('response', async (response) => {
        const request = response.request();
        const timing = response.timing();
        const requestId = [...requests.keys()].find(key => 
            requests.get(key).url === request.url() && 
            requests.get(key).method === request.method()
        );

        if (requestId) {
            const entry = requests.get(requestId);
            entry.timing = timing;
            
            try {
                const buffer = await response.buffer();
                const filename = `response_${Date.now()}_${Math.random().toString(36).slice(2)}`;
                const filePath = path.join(outputDir, filename);
                fs.writeFileSync(filePath, buffer);
                
                entry.response = {
                    status: response.status(),
                    headers: response.headers(),
                    bodyFile: filename,
                    bodySize: buffer.length
                };
            } catch (error) {
                console.error(`Error saving response: ${error}`);
            }
        }
    });

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    await page.waitForTimeout(50000); // Additional wait time

    // Save metadata
    const metadata = Array.from(requests.values());
    fs.writeFileSync(
        path.join(outputDir, 'metadata.json'),
        JSON.stringify(metadata, null, 2)
    );

    await browser.close();
}

// Usage: node capture.js <URL> <output-directory>
const [url, outputDir] = process.argv.slice(2);
if (!url || !outputDir) {
    console.log('Usage: node capture.js <URL> <output-directory>');
    process.exit(1);
}

captureNetworkTraffic(url, outputDir).catch(console.error);



