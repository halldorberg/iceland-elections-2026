import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const errors = [];
page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
page.on('pageerror', err => errors.push('PAGE ERROR: ' + err.message));

await page.goto('http://localhost:3000/mosfellsbaer/', { waitUntil: 'networkidle', timeout: 30000 });

// Wait a moment for JS to render
await page.waitForTimeout(3000);

const muniName = await page.$eval('#muni-name', el => el.textContent).catch(() => 'NOT FOUND');
const bodyText = await page.evaluate(() => document.body.innerText.trim().substring(0, 200));

console.log('muni-name:', muniName);
console.log('body preview:', bodyText);
console.log('JS errors:', errors.slice(0, 10));

await browser.close();
