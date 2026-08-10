const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message.substring(0,200)));
  await page.goto('https://preview.lydraedisveislan.is/sveitastjornarkosningar2026/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(6000);
  const leafletContainer = await page.$('.leaflet-container');
  const markerCount = (await page.$$('.municipality-marker')).length;
  const mapHeight = await page.$eval('#map', el => el.offsetHeight).catch(() => 0);
  const mapWidth  = await page.$eval('#map', el => el.offsetWidth).catch(() => 0);
  const leafletState = await page.evaluate(() => {
    const m = document.getElementById('map');
    return m ? { scroll: m.scrollHeight, classes: m.className, childCount: m.children.length } : null;
  });
  console.log('Map size:', mapWidth, 'x', mapHeight);
  console.log('Leaflet container:', !!leafletContainer);
  console.log('Municipality markers:', markerCount);
  console.log('Map state:', JSON.stringify(leafletState));
  if (errors.length) console.log('Errors:', errors.slice(0,5));
  await browser.close();
})();
