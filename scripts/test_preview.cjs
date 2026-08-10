const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', err => errors.push('PAGE: ' + err.message));
  await page.goto('https://preview.lydraedisveislan.is/mosfellsbaer/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(4000);
  const muniName = await page.$eval('#muni-name', el => el.textContent).catch(() => '(not found)');
  const body100 = await page.evaluate(() => document.body.innerText.trim().substring(0, 150));
  console.log('muni-name:', muniName);
  console.log('body:', body100);
  if (errors.length) console.log('ERRORS:', errors.slice(0,5).join('\n'));
  else console.log('No JS errors.');
  await browser.close();
})();
