import { MUNICIPALITIES } from './data/municipalities.js?v=9';
import { PARTIES } from './data/parties.js?v=9';
import { getMunicipalityPartyData } from './data/candidates.js?v=9';

// ─── Init ──────────────────────────────────────────────────

const params = new URLSearchParams(window.location.search);
const muniId = params.get('id') || 'reykjavik';
const muni = MUNICIPALITIES.find(m => m.id === muniId) || MUNICIPALITIES[0];

document.title = `${muni.name} – Kosningar 2026`;
document.getElementById('muni-name').textContent = muni.name;
document.getElementById('muni-region').textContent = muni.region;
document.getElementById('muni-pop').textContent =
  muni.population.toLocaleString('is-IS') + ' íbúar';

// ─── Election type ─────────────────────────────────────────
const isUnbound   = muni.partyIds.length === 0;
const isSjalkjort = muni.partyIds.length === 1;

// ─── Election type notice card ─────────────────────────────
let noticeEl = document.getElementById('election-type-notice');
if (!noticeEl) {
  noticeEl = document.createElement('div');
  noticeEl.id = 'election-type-notice';
  document.querySelector('.accordion-section')?.before(noticeEl);
}
if (isUnbound) {
  noticeEl.innerHTML = `
    <div class="election-notice election-notice--unbound">
      <div class="en-icon">🗳️</div>
      <div class="en-body">
        <span class="en-badge">Óbundnar kosningar</span>
        <h2 class="en-title">Óbundnar kosningar í ${muni.name}</h2>
        <p class="en-text">Í þessum kosningum eru engar formlegar framboðslistur. Allir kjörgengar einstaklingar í sveitarfélaginu teljast sjálfkrafa frambjóðendur nema þeir afþakki sérstaklega. Kjósendur gefa atkvæði með persónulegri atkvæðagreiðslu fremur en að kjósa eftir listum — það þýðir að hægt er að greiða atkvæði til hvaða kjörgengs einstaklings sem er í sveitarfélaginu.</p>
      </div>
    </div>`;
} else if (isSjalkjort) {
  noticeEl.innerHTML = `
    <div class="election-notice election-notice--sjalkjort">
      <div class="en-icon">✅</div>
      <div class="en-body">
        <span class="en-badge">Sjálfkjörið</span>
        <h2 class="en-title">Sjálfkjörið í ${muni.name}</h2>
        <p class="en-text">Aðeins einn framboðslisti bauð sig fram og var hann samþykktur án kosninga. Þegar fjöldi frambjóðenda á einum lista samsvarar fjölda sæta í sveitarstjórn — eða er færri — er engin ástæða til kosninga og meðlimir listans fara sjálfkrafa inn í sveitarstjórnina. Hægt er að skoða listann hér að neðan.</p>
      </div>
    </div>`;
}

if (isUnbound) {
  const tip = document.getElementById('random-tooltip');
  if (tip) tip.style.display = 'none';
  // Nothing else to render — skip accordion entirely
} else {
  // Precompute all party data
  const partyDataMap = {};
  muni.partyIds.forEach(code => {
    partyDataMap[code] = getMunicipalityPartyData(muni.id, code);
  });

  // Random opening party (skip random tooltip for single-list)
  const randomIndex = muni.partyIds.length > 1
    ? Math.floor(Math.random() * muni.partyIds.length)
    : 0;
  let activeParty = muni.partyIds[randomIndex];

  if (muni.partyIds.length > 1) {
    const randomParty = PARTIES[activeParty];
    document.getElementById('random-tooltip-text').textContent =
      `Opnaði ${randomParty.name} af handahófi`;
    setTimeout(() => {
      const tip = document.getElementById('random-tooltip');
      if (tip) tip.style.display = 'none';
    }, 5200);
  } else {
    const tip = document.getElementById('random-tooltip');
    if (tip) tip.style.display = 'none';
  }

// ─── Render Ribbons ────────────────────────────────────────

const container = document.getElementById('accordion-container');

function renderAccordion() {
  container.innerHTML = '';

  muni.partyIds.forEach(code => {
    const p = PARTIES[code];
    const data = partyDataMap[code];
    const isExpanded = code === activeParty;

    const ribbon = document.createElement('div');
    ribbon.className = `party-ribbon${isExpanded ? ' is-expanded' : ''}`;
    ribbon.dataset.code = code;

    const bgStyle = isExpanded
      ? `linear-gradient(160deg, ${p.accentColor || p.color} 0%, ${p.color} 100%)`
      : p.color;
    ribbon.style.cssText = `background:${bgStyle};`;

    ribbon.innerHTML = buildRibbonHTML(p, data);
    container.appendChild(ribbon);
  });
}

function buildRibbonHTML(party, data) {
  return `
    <div class="ribbon-strip" aria-hidden="true">
      <div class="ribbon-label" style="color:${party.textColor}">
        <span class="ribbon-code">${party.code}</span>
        <span class="ribbon-party-name">${party.shortName}</span>
      </div>
      <div class="ribbon-hover-text" style="color:${party.textColor}">Opna</div>
    </div>

    <div class="ribbon-content">
      ${buildSplashHTML(party, data)}
      ${buildCandidatesHTML(data, party)}
    </div>`;
}

// ─── Open/Close Ribbons ────────────────────────────────────

// Event delegation — one listener on container for ribbon clicks
container.addEventListener('click', e => {
  // Don't intercept candidate card clicks
  if (e.target.closest('.candidate-card')) return;

  const ribbon = e.target.closest('.party-ribbon');
  if (!ribbon) return;

  const code = ribbon.dataset.code;
  if (code === activeParty) return;

  switchParty(code);
});

function switchParty(code) {
  activeParty = code;

  container.querySelectorAll('.party-ribbon').forEach(r => {
    const rCode = r.dataset.code;
    const p = PARTIES[rCode];
    const isNowExpanded = rCode === code;

    r.classList.toggle('is-expanded', isNowExpanded);
    r.style.background = isNowExpanded
      ? `linear-gradient(160deg, ${p.accentColor || p.color} 0%, ${p.color} 100%)`
      : p.color;
  });
}

// ─── Splash / Agenda ───────────────────────────────────────

function buildSplashHTML(party, data) {
  const cards = data.agenda.map(item => `
    <div class="agenda-card">
      <div class="agenda-icon">${item.icon}</div>
      <div class="agenda-title">${item.title}</div>
      <div class="agenda-text">${item.text}</div>
    </div>`).join('');

  return `
    <div class="party-splash">
      <div class="splash-bg"></div>
      <div class="splash-eyebrow">
        <span class="splash-party-badge" style="color:${party.textColor}">
          ${party.code} – ${party.name}
        </span>
      </div>
      <div class="splash-tagline" style="color:${party.textColor}">${data.tagline}</div>
      <div class="agenda-grid">${cards}</div>
    </div>`;
}

// ─── Candidate Gallery ─────────────────────────────────────

function buildCandidatesHTML(data, party) {
  const cards = data.candidates.map(c => {
    const fallback = `https://ui-avatars.com/api/?name=${encodeURIComponent(c.name)}&size=300&background=1c2335&color=8892a4&bold=true`;
    return `
      <div class="candidate-card"
           data-candidate-id="${c.id}"
           data-party-code="${data.partyCode}"
           role="button" tabindex="0"
           aria-label="Sjá nánar um ${c.name}">
        <div class="candidate-photo-wrap">
          <img src="${c.imageUrl}"
               alt="${c.name}"
               loading="lazy"
               onerror="this.onerror=null;this.src='${fallback}'" />
          <div class="candidate-ballot">${c.ballotOrder}</div>
        </div>
        <div class="candidate-info">
          <div class="candidate-name">${c.name}</div>
          <div class="candidate-occupation">${c.occupation}</div>
        </div>
        <div class="candidate-card-hover-overlay">
          <span>Sjá nánar →</span>
        </div>
      </div>`;
  }).join('');

  return `
    <div class="candidates-section">
      <div class="candidates-section-title">
        <span style="color:${party.color}">${party.name}</span>
        &nbsp;– Frambjóðendur
      </div>
      <div class="candidates-grid">${cards}</div>
    </div>`;
}

// ─── Modal ─────────────────────────────────────────────────

const overlay = document.getElementById('modal-overlay');

// Build flat candidate lookup
const allCandidates = {};
muni.partyIds.forEach(code => {
  partyDataMap[code].candidates.forEach(c => {
    allCandidates[c.id] = { ...c, partyCode: code };
  });
});

// Delegate candidate card clicks
container.addEventListener('click', e => {
  const card = e.target.closest('.candidate-card');
  if (!card) return;
  e.stopPropagation();
  openModal(card.dataset.candidateId);
});

container.addEventListener('keydown', e => {
  if (e.key !== 'Enter' && e.key !== ' ') return;
  const card = e.target.closest('.candidate-card');
  if (card) { e.preventDefault(); openModal(card.dataset.candidateId); }
});

function openModal(id) {
  const c = allCandidates[id];
  if (!c) return;
  const party = PARTIES[c.partyCode];

  const fallback = `https://ui-avatars.com/api/?name=${encodeURIComponent(c.name)}&size=400&background=1c2335&color=8892a4&bold=true`;
  const photo = document.getElementById('modal-photo');
  photo.src = c.imageUrl;
  photo.alt = c.name;
  photo.onerror = () => { photo.onerror = null; photo.src = fallback; };

  document.getElementById('modal-name').textContent = c.name;

  const badge = document.getElementById('modal-badge');
  badge.textContent = `#${c.ballotOrder} · ${party.name}`;
  badge.style.cssText = `background:${party.color}22;border:1px solid ${party.color}55;color:${party.color};`;

  document.getElementById('modal-meta').innerHTML =
    `<span>${c.age} ára</span><span>·</span><span>${c.occupation}</span>`;

  document.getElementById('modal-bio').textContent = c.bio;

  document.getElementById('modal-interests').innerHTML =
    c.interests.map(i => `<span class="interest-chip">${i}</span>`).join('');

  overlay.classList.add('is-open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  overlay.classList.remove('is-open');
  document.body.style.overflow = '';
}

document.getElementById('modal-close').addEventListener('click', closeModal);
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// ─── Boot ──────────────────────────────────────────────────

  renderAccordion();
} // end else (not isUnbound)
