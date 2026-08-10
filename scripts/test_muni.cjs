const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const urls = [
    'https://preview.lydraedisveislan.is/reykjavik/',
    'https://preview.lydraedisveislan.is/skaftarhreppur/',
    'https://preview.lydraedisveislan.is/mosfellsbaer/',
  ];
  for (const url of urls) {
    const page = await browser.newPage();
    const errors = [], badMimes = [];
    page.on('pageerror', e => errors.push(e.message.substring(0, 150)));
    page.on('response', r => {
      if (r.url().includes('/js/') && !r.url().includes('gtag') && !r.url().includes('unp')) {
        const ct = r.headers()['content-type'] || '';
        if (!ct.includes('javascript')) badMimes.push(r.url().split('/').slice(-1)[0]);
      }
    });
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    const name = await page.evaluate(() => {
      const el = document.getElementById('municipality-name');
      return el ? el.textContent.trim() : 'NOT FOUND';
    });
    const bodyText = await page.evaluate(() => document.body.innerText.trim().substring(0, 100));
    console.log(`\n--- ${url} ---`);
    console.log('Name el:', name);
    console.log('Body preview:', bodyText);
    if (badMimes.length) console.log('Bad MIMEs:', badMimes);
    if (errors.length) console.log('Errors:', errors.slice(0, 3).join('\n'));
    await page.close();
  }
  await browser.close();
})();
