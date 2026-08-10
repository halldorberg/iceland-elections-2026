const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [];
  page.on('console', msg => { if (msg.type() === 'error') errors.push('[console] ' + msg.text()); });
  page.on('pageerror', err => errors.push('[pageerror] ' + err.message));

  await page.goto('http://localhost:3000/mosfellsbaer/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);

  const muniName = await page.$eval('#muni-name', el => el.textContent).catch(() => '(not found)');
  const body200 = await page.evaluate(() => document.body.innerText.trim().substring(0, 300));

  console.log('muni-name:', muniName);
  console.log('body:', body200);
  if (errors.length) console.log('ERRORS:', errors.slice(0, 10).join('\n'));
  else console.log('No JS errors.');
  await browser.close();
})();
