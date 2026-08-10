const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-cache', '--disable-application-cache', '--disk-cache-size=0']
  });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: false });
  const page = await ctx.newPage();
  const mimes = {};
  page.on('response', r => {
    if (r.url().includes('.js') && !r.url().includes('gtag') && !r.url().includes('fonts') && !r.url().includes('googletagmanager')) {
      mimes[r.url().split('/').slice(-1)[0].split('?')[0]] = r.headers()['content-type'];
    }
  });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.substring(0,120)));
  await page.goto('https://preview.lydraedisveislan.is/mosfellsbaer/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);
  const name = await page.$eval('#muni-name', el => el.textContent).catch(() => '(blank)');
  console.log('muni-name:', name);
  console.log('MIME types seen:', JSON.stringify(mimes, null, 2));
  if (errors.length) console.log('Errors:', errors.slice(0,3));
  await browser.close();
})();
