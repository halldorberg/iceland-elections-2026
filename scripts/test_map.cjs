const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [], mimes = {};
  page.on('pageerror', e => errors.push(e.message.substring(0,200)));
  page.on('response', r => {
    if (r.url().includes('.js') && !r.url().includes('gtag') && !r.url().includes('fonts') && !r.url().includes('googletagmanager') && !r.url().includes('unpkg')) {
      const ct = r.headers()['content-type'] || 'none';
      const name = r.url().split('/').slice(-1)[0].split('?')[0];
      mimes[name] = ct;
    }
  });
  await page.goto('https://preview.lydraedisveislan.is/sveitastjornarkosningar2026/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(4000);
  const mapEl = await page.$('#map');
  const mapHeight = mapEl ? await mapEl.evaluate(el => el.offsetHeight) : 0;
  const hasCanvas = await page.$('.leaflet-canvas-layer, .leaflet-tile') !== null;
  console.log('Map div height:', mapHeight);
  console.log('Leaflet tiles present:', hasCanvas);
  if (errors.length) console.log('ERRORS:', errors.slice(0,5).join('\n'));
  console.log('Bad MIMEs:', Object.entries(mimes).filter(([k,v])=>!v.includes('javascript')).map(([k,v])=>`${k}:${v}`));
})().catch(console.error).finally(() => process.exit(0));
