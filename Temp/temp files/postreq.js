const puppeteer = require('puppeteer');

async function sendPostRequest() {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();

    // Set cookies from the headers
    const cookies = [
        {
            name: 'session-id',
            value: '259-9356352-5887904',
            domain: '.amazon.in',
            path: '/',
            secure: true
        },
        {
            name: 'i18n-prefs',
            value: 'INR',
            domain: '.amazon.in',
            path: '/',
            secure: true
        },
        {
            name: 'ubid-acbin',
            value: '259-3849922-8806565',
            domain: '.amazon.in',
            path: '/',
            secure: true
        },
        {
            name: 'session-token',
            value: '74lb3uYwiENc+tO+RwNxOQZq39EedQvTz1qvu8kvugC8AmNTBaFmaXPySA80l8daWbafrgEdwEuGeSXclm6pL2Xb61Gz9PidGkOE3IdkJCORTw5xdWy/qSbXRnODlbCWWGpFuVWZ3PQSVx0toYJ6jRWywLAyL+qTh56la7bym8LEi2C0ExWV4D+OmX47RVCDtkMu+sBu2iS3kjcXJpxJqGtoEhTTHhGJUEvxF6HBKuzQ8bEnipTBxxL/s5RnWG5wTIoJAeMrKowiXV9d+Eouw1RrtRCciDddh4yg827NgfLHGpU/pS2886j0XQJFF8OH/5Gwd3qi4sIkfPe1xG4yv5X4K4MH3KSG',
            domain: '.amazon.in',
            path: '/',
            secure: true
        }
    ];
    await page.setCookie(...cookies);

    // Navigate to referer first to establish context
    await page.goto('https://www.amazon.in/s?k=torch&s=exact-aware-popularity-rank&crid=3ETNR5JWU4W61&qid=1741272443&sprefix=torch%2Caps%2C347&ref=sr_st_exact-aware-popularity-rank&ds=v1%3ADFWZY1x9V2HRQvEkyPVgZ0pvtc02lAk5TH%2F6TMeDINA', {
        waitUntil: 'networkidle2'
    });

    // Send POST request using fetch
    const response = await page.evaluate(async () => {
        const url = 'https://www.amazon.in/s/query?crid=3ETNR5JWU4W61&k=torch&page=2&qid=1741272497&ref=sr_pg_1&s=exact-aware-popularity-rank&sprefix=torch%2Caps%2C347&xpid=jLUztdZElCudH';
        
        // YOU NEED TO REPLACE THIS WITH THE ACTUAL REQUEST BODY
        const body = JSON.stringify({ 
            // Example structure - this is just a placeholder
            page: 2,
            query: 'torch'
        });

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'accept': 'text/html,image/webp,*/*',
                    'content-type': 'application/json',
                    'x-requested-with': 'XMLHttpRequest',
                    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'priority': 'u=1, i'
                },
                body: body
            });
            return response.text();
        } catch (error) {
            return error.toString();
        }
    });

    console.log('Response:', response);
    await browser.close();
}

sendPostRequest();