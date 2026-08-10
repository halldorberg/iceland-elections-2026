const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const logs = [], errors = [], failed = [];
  page.on('console', m => logs.push(`[${m.type()}] ${m.text().substring(0,150)}`));
  page.on('pageerror', e => errors.push(e.message.substring(0,200)));
  page.on('requestfailed', r => failed.push(`${r.url().split('/').slice(-1)[0]} — ${r.failure()?.errorText}`));
  page.on('response', r => {
    const url = r.url();
    if (url.includes('/js/') && !url.includes('gtag') && !url.includes('unp')) {
      const ct = r.headers()['content-type'] || '';
      if (!ct.includes('javascript')) console.log(`BAD: ${url.split('/').slice(-1)[0]} → ${ct}`);
    }
  });
  await page.goto('https://preview.lydraedisveislan.is/sveitastjornarkosningar2026/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(5000);
  const leaflet = await page.$('.leaflet-container');
  console.log('Leaflet init:', !!leaflet);
  if (errors.length) console.log('PAGE ERRORS:\n' + errors.join('\n'));
  const errLogs = logs.filter(l => l.includes('[error]'));
  if (errLogs.length) console.log('CONSOLE ERRORS:\n' + errLogs.join('\n'));
  if (failed.length) console.log('FAILED REQS:\n' + failed.join('\n'));
  await browser.close();
})();
