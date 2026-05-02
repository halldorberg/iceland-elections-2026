import { MUNICIPALITIES } from './data/municipalities.js?v=13';
import { PARTIES } from './data/parties.js?v=4';
import { getLang, t, renderLangSwitcher } from './i18n.js?v=2';

// ─── i18n ──────────────────────────────────────────────────
const lang = getLang();
const ui   = t();

// Inject language switcher
renderLangSwitcher(document.getElementById('lang-switcher'));

// Update static page text for current language
(function applyStaticTranslations() {
  const set = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  const setHTML = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

  // Hero
  setHTML('hero-title',     ui.heroTitle);
  set('hero-intro',          ui.heroIntro);
  set('hero-intro-emphasis', ui.heroIntroEmphasis);

  // Dynamic <title> and <meta name="description"> per language (SEO)
  if (ui.pageTitleHome) document.title = ui.pageTitleHome;
  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc && ui.pageDescHome) metaDesc.setAttribute('content', ui.pageDescHome);
  const ogTitle = document.querySelector('meta[property="og:title"]');
  if (ogTitle && ui.pageTitleHome) ogTitle.setAttribute('content', ui.pageTitleHome);
  const ogDesc = document.querySelector('meta[property="og:description"]');
  if (ogDesc && ui.pageDescHome) ogDesc.setAttribute('content', ui.pageDescHome);
  const ogLocale = document.querySelector('meta[property="og:locale"]');
  if (ogLocale) ogLocale.setAttribute('content', { is: 'is_IS', en: 'en_US', pl: 'pl_PL' }[lang] || 'is_IS');
  // Set <html lang="..."> so browser/Google know the page language
  document.documentElement.lang = lang;

  // Stats
  set('stat-label-municipalities', ui.statMunicipalities);
  set('stat-label-parties',        ui.statParties);
  set('stat-label-candidates',     ui.statCandidates);

  // Map overlay
  set('map-overlay-title', ui.mapOverlayTitle);
  set('map-overlay-desc',  ui.mapOverlayDesc);

  // Legend
  set('legend-title', ui.legendTitle);

  // Instructions
  set('instr-hover', ui.instrHover);
  set('instr-click', ui.instrClick);
  set('instr-zoom',  ui.instrZoom);

  // Disclaimer
  set('disclaimer-title',     ui.disclaimerTitle);
  set('disclaimer-body-text', ui.disclaimerText);
})();

// ─── Map init ──────────────────────────────────────────────

const map = L.map('map', {
  center: [64.9, -19.0],
  zoom: 6,
  zoomControl: true,
  scrollWheelZoom: true,
  attributionControl: true,
  minZoom: 5,
  maxZoom: 13,
});

// Stadia Maps — Alidade Smooth Dark (natively dark, no CSS filter needed)
const STADIA_KEY = '7380e2ba-69c3-4dce-a6ba-354145bbfe61';
const tileProviders = [
  {
    url: `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=${STADIA_KEY}`,
    options: {
      attribution: '© <a href="https://stadiamaps.com/" target="_blank">Stadia Maps</a> © <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors',
      maxZoom: 20,
      minZoom: 0,
    },
  },
];

let currentProviderIndex = 0;
let tileLayer = null;

function loadTileProvider(index) {
  if (index >= tileProviders.length) return; // all failed

  if (tileLayer) map.removeLayer(tileLayer);

  const { url, options } = tileProviders[index];
  tileLayer = L.tileLayer(url, options);

  // If this provider fails, try the next
  tileLayer.on('tileerror', () => {
    if (currentProviderIndex === index) {
      currentProviderIndex = index + 1;
      loadTileProvider(currentProviderIndex);
    }
  });

  tileLayer.addTo(map);
}

loadTileProvider(0);

// ─── Markers ───────────────────────────────────────────────

MUNICIPALITIES.forEach(muni => {
  const icon = L.divIcon({
    className: '',
    html: `<div class="municipality-marker">
             <div class="marker-dot"></div>
             <div class="marker-ring"></div>
           </div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    tooltipAnchor: [12, 0],
  });

  const marker = L.marker([muni.coords.lat, muni.coords.lng], { icon });

  const listCount = muni.partyIds.length;
  const isUnbound = listCount === 0;
  const isSjalkjort = listCount === 1;

  let electionBadge = '';
  let partiesBlock;

  if (isUnbound) {
    electionBadge = `<span class="tooltip-election-badge tooltip-election-badge--unbound">${ui.unboundBadge}</span>`;
    partiesBlock = `<div class="tooltip-unbound-note">${ui.unboundNote}</div>`;
  } else {
    if (isSjalkjort) {
      electionBadge = `<span class="tooltip-election-badge tooltip-election-badge--sjalkjort">${ui.unopposedBadge}</span>`;
    }
    partiesBlock = `<div class="tooltip-parties">${muni.partyIds.map(code => {
      const p = PARTIES[code];
      return `<span class="tooltip-party-chip"
                style="background:${p.color}22;color:${p.color};border-color:${p.color}55">
                <strong>${p.code}</strong> ${p.shortName}
              </span>`;
    }).join('')}</div>`;
  }

  marker.bindTooltip(`
    <div class="tooltip-name">${muni.name}</div>
    <div class="tooltip-region">${muni.region} &nbsp;·&nbsp; ${muni.population.toLocaleString('is-IS')} ${ui.population}</div>
    ${electionBadge}
    ${partiesBlock}
    <div class="tooltip-cta">
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
        <path d="M2 5h6M5 2l3 3-3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      ${ui.mapTooltipCTA}</div>`, {
    className: 'map-tooltip',
    direction: 'right',
    offset: [12, 0],
    opacity: 1,
  });

  marker.on('click', () => {
    const params = lang !== 'is' ? `&lang=${lang}` : '';
    window.location.href = `municipality.html?id=${muni.id}${params}`;
  });

  marker.addTo(map);
});

// ─── Party legend ──────────────────────────────────────────

const legendItems = document.getElementById('legend-items');
if (legendItems) {
  Object.values(PARTIES).forEach(party => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = `<div class="legend-color" style="background:${party.color}"></div>
                      <span><strong>${party.code}</strong> – ${party.shortName}</span>`;
    legendItems.appendChild(item);
  });
}

// ─── Stats ─────────────────────────────────────────────────

// Stats are hardcoded in index.html with accurate counts from the data.
