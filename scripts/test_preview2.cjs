const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const failed = [];
  page.on('requestfailed', r => failed.push(`FAIL: ${r.url()} — ${r.failure()?.errorText}`));
  page.on('response', r => {
    if (r.url().includes('.js') && !r.url().includes('gtag') && !r.url().includes('fonts')) {
      const ct = r.headers()['content-type'] || 'none';
      if (!ct.includes('javascript')) console.log(`BAD MIME: ${r.url().split('/').slice(-1)[0]} → ${ct}`);
    }
  });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('https://preview.lydraedisveislan.is/mosfellsbaer/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);
  const name = await page.$eval('#muni-name', el => el.textContent).catch(() => '(blank)');
  console.log('muni-name:', name);
  if (failed.length) console.log('Failed requests:', failed.slice(0,5));
  if (errors.length) console.log('Page errors:', errors.slice(0,5));
  if (!failed.length && !errors.length) console.log('All OK.');
  await browser.close();
})();
