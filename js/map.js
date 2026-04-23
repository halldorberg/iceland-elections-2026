import { MUNICIPALITIES } from './data/municipalities.js?v=2';
import { PARTIES } from './data/parties.js?v=2';

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

// OpenStreetMap tiles — free, no authentication required.
// CSS invert + hue-rotate in map.css gives a dark map appearance.
const tileProviders = [
  {
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    options: {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
      className: 'osm-tile-inverted',
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
    electionBadge = `<span class="tooltip-election-badge tooltip-election-badge--unbound">Óbundnar kosningar</span>`;
    partiesBlock = `<div class="tooltip-unbound-note">Allir kjörgengar einstaklingar geta boðið sig fram — engar formlegar listur.</div>`;
  } else {
    if (isSjalkjort) {
      electionBadge = `<span class="tooltip-election-badge tooltip-election-badge--sjalkjort">Sjálfkjörið</span>`;
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
    <div class="tooltip-region">${muni.region} &nbsp;·&nbsp; ${muni.population.toLocaleString('is-IS')} íbúar</div>
    ${electionBadge}
    ${partiesBlock}
    <div class="tooltip-cta">
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
        <path d="M2 5h6M5 2l3 3-3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      Smelltu til að sjá nánar
    </div>`, {
    className: 'map-tooltip',
    direction: 'right',
    offset: [12, 0],
    opacity: 1,
  });

  marker.on('click', () => {
    window.location.href = `municipality.html?id=${muni.id}`;
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

const statMuni = document.getElementById('stat-municipalities');
const statCandidates = document.getElementById('stat-candidates');
const statParties = document.getElementById('stat-parties');
if (statMuni) statMuni.textContent = MUNICIPALITIES.length;
if (statParties) {
  const uniqueParties = new Set(MUNICIPALITIES.flatMap(m => m.partyIds));
  statParties.textContent = uniqueParties.size;
}
if (statCandidates) {
  // Reykjavík has 46 candidates per list, others average ~12
  const total = MUNICIPALITIES.reduce((sum, m) => {
    const perParty = m.id === 'reykjavik' ? 46 : 12;
    return sum + m.partyIds.length * perParty;
  }, 0);
  statCandidates.textContent = '~' + Math.round(total / 100) * 100 + '+';
}
