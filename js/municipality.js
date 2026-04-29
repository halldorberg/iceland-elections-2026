import { MUNICIPALITIES } from './data/municipalities.js?v=14';
import { PARTIES } from './data/parties.js?v=4';
import { getMunicipalityPartyData } from './data/candidates.js?v=42';
import { RESULTS_2022 } from './data/results2022.js?v=2';
import { getLang, t, renderLangSwitcher } from './i18n.js?v=3';

// ─── i18n ──────────────────────────────────────────────────
const lang = getLang();
const ui   = t();

let TR = {};
if (lang === 'en') {
  const mod = await import('./data/candidates.en.js?v=2');
  TR = mod.TRANSLATIONS_EN;
} else if (lang === 'pl') {
  const mod = await import('./data/candidates.pl.js?v=2');
  TR = mod.TRANSLATIONS_PL;
}

/** Look up a translated data string; falls back to Icelandic source value. */
function trData(key, fallback) {
  return (lang !== 'is' && TR[key]) ? TR[key] : (fallback ?? '');
}

/** Look up a translated occupation; falls back to the original Icelandic. */
function trOcc(occ) {
  if (lang === 'is' || !occ) return occ || '';
  return TR._occupations?.[occ] || occ;
}

// ─── Lang switcher ─────────────────────────────────────────
renderLangSwitcher(document.getElementById('lang-switcher'));

// ─── Static HTML translations (one-time at init) ───────────
(function applyStaticTranslations() {
  const set = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  set('back-btn-text',         ui.backToMap);
  set('muni-share-text',       ui.share);
  set('modal-share-text',      ui.share);
  set('modal-label-bio',       ui.aboutCandidate);
  set('modal-label-interests', ui.policyFocus);
  set('modal-label-social',    ui.socialMedia);
  set('modal-label-news',      ui.news);
  set('disclaimer-title',      ui.disclaimerTitle);
  set('disclaimer-body-text',  ui.disclaimerText);
  const noInfoEl = document.getElementById('modal-no-info');
  if (noInfoEl) noInfoEl.innerHTML = `<span class="no-info-icon">ℹ️</span> ${ui.noInfo}`;
})();

// ─── Local avatar generator ────────────────────────────────
function localAvatar(name) {
  const initials = name.trim().split(/\s+/).slice(0, 2).map(w => w[0] || '').join('').toUpperCase();
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="300" height="300" fill="#1c2335"/><text x="150" y="155" text-anchor="middle" dominant-baseline="middle" fill="#8892a4" font-family="Arial,sans-serif" font-size="120" font-weight="bold">${initials}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

// ─── Init ──────────────────────────────────────────────────

const params = new URLSearchParams(window.location.search);
const muniId = params.get('id') || 'reykjavik';
const muni = MUNICIPALITIES.find(m => m.id === muniId) || MUNICIPALITIES[0];

document.title = `${muni.name} – Kosningar 2026`;
document.getElementById('muni-name').textContent = muni.name;
document.getElementById('muni-region').textContent = muni.region;

// Municipality share button — clean URL with just ?id=
const muniShareBtn = document.getElementById('muni-share');
if (muniShareBtn) {
  muniShareBtn.addEventListener('click', () => {
    const u = new URL(window.location.href);
    u.search = '';
    u.searchParams.set('id', muniId);
    shareURL(u.toString(), `${muni.name} – Kosningar 2026`);
  });
}
document.getElementById('muni-pop').textContent =
  muni.population.toLocaleString('is-IS') + ' ' + ui.population;

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
        <span class="en-badge">${ui.unboundBadge}</span>
        <h2 class="en-title">${ui.unboundTitle(muni.name)}</h2>
        <p class="en-text">${ui.unboundDesc}</p>
      </div>
    </div>`;
} else if (isSjalkjort) {
  noticeEl.innerHTML = `
    <div class="election-notice election-notice--sjalkjort">
      <div class="en-icon">✅</div>
      <div class="en-body">
        <span class="en-badge">${ui.unopposedBadge}</span>
        <h2 class="en-title">${ui.unopposedTitle(muni.name)}</h2>
        <p class="en-text">${ui.unopposedDesc}</p>
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

  // Honour ?party= deep-link param; otherwise open a random party
  const paramParty     = params.get('party');
  const paramCandidate = params.get('candidate');
  const isDeepLink     = paramParty && muni.partyIds.includes(paramParty);

  const randomIndex = muni.partyIds.length > 1
    ? Math.floor(Math.random() * muni.partyIds.length)
    : 0;
  let activeParty = isDeepLink ? paramParty : muni.partyIds[randomIndex];

  const tip = document.getElementById('random-tooltip');
  if (isDeepLink || muni.partyIds.length <= 1) {
    if (tip) tip.style.display = 'none';
  } else {
    const randomParty = PARTIES[activeParty];
    document.getElementById('random-tooltip-text').textContent =
      ui.randomTooltipOpen(randomParty.name);
    setTimeout(() => { if (tip) tip.style.display = 'none'; }, 5200);
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
    ribbon.style.cssText = `background:${bgStyle};--party-color:${p.color};`;

    ribbon.innerHTML = buildRibbonHTML(p, data);
    container.appendChild(ribbon);
    attachCustomScrollbar(ribbon);
  });
}

function attachCustomScrollbar(ribbon) {
  const content = ribbon.querySelector('.ribbon-content');
  if (!content) return;

  const bar = document.createElement('div');
  bar.className = 'custom-scrollbar';
  bar.innerHTML = '<div class="custom-scrollbar-thumb"></div>';
  ribbon.appendChild(bar);

  const thumb = bar.querySelector('.custom-scrollbar-thumb');
  let hideTimer = null;

  function updateThumb() {
    const { scrollTop, scrollHeight, clientHeight } = content;
    if (scrollHeight <= clientHeight + 1) { bar.style.opacity = '0'; return; }
    const trackH = bar.clientHeight;
    const ratio = clientHeight / scrollHeight;
    const thumbH = Math.max(32, ratio * trackH);
    const maxThumbTop = trackH - thumbH;
    const maxScroll = scrollHeight - clientHeight;
    thumb.style.height = thumbH + 'px';
    thumb.style.top = ((scrollTop / maxScroll) * maxThumbTop) + 'px';
  }

  function show() {
    const { scrollHeight, clientHeight } = content;
    if (scrollHeight <= clientHeight + 1) return;
    clearTimeout(hideTimer);
    updateThumb();
    bar.style.opacity = '1';
  }

  function scheduleHide() {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { bar.style.opacity = '0'; }, 800);
  }

  content.addEventListener('scroll', () => { updateThumb(); show(); scheduleHide(); });
  content.addEventListener('mouseenter', show);
  content.addEventListener('mouseleave', scheduleHide);

  // Draggable thumb
  let drag = null;
  thumb.addEventListener('mousedown', e => {
    e.preventDefault();
    drag = { startY: e.clientY, startScroll: content.scrollTop };
    document.body.style.userSelect = 'none';
  });
  window.addEventListener('mousemove', e => {
    if (!drag) return;
    const { scrollHeight, clientHeight } = content;
    const trackH = bar.clientHeight;
    const thumbH = thumb.offsetHeight;
    const maxThumbTop = trackH - thumbH;
    const maxScroll = scrollHeight - clientHeight;
    const dy = e.clientY - drag.startY;
    content.scrollTop = drag.startScroll + (dy / maxThumbTop) * maxScroll;
    updateThumb();
  });
  window.addEventListener('mouseup', () => {
    if (!drag) return;
    drag = null;
    document.body.style.userSelect = '';
    scheduleHide();
  });
}

function buildRibbonHTML(party, data) {
  return `
    <div class="ribbon-strip" aria-hidden="true">
      <div class="ribbon-label" style="color:${party.textColor}">
        <span class="ribbon-code">${party.code}</span>
        <span class="ribbon-party-name">${party.shortName}</span>
      </div>
      <div class="ribbon-hover-text" style="color:${party.textColor}">${ui.openParty}</div>
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

function trackEvent(name, params) {
  if (typeof gtag === 'function') gtag('event', name, params);
}

function switchParty(code) {
  activeParty = code;

  trackEvent('party_open', {
    municipality_id:   muni.id,
    municipality_name: muni.name,
    party_code:        code,
    party_name:        PARTIES[code]?.name ?? code,
  });

  let expandedEl = null;
  container.querySelectorAll('.party-ribbon').forEach(r => {
    const rCode = r.dataset.code;
    const p = PARTIES[rCode];
    const isNowExpanded = rCode === code;

    r.classList.toggle('is-expanded', isNowExpanded);
    r.style.background = isNowExpanded
      ? `linear-gradient(160deg, ${p.accentColor || p.color} 0%, ${p.color} 100%)`
      : p.color;

    if (isNowExpanded) expandedEl = r;
  });

  // On mobile the container is a fixed-height scroll zone — bring the
  // newly expanded ribbon to the top so the user sees its content AND
  // can still scroll down to reach the collapsed ribbons below it.
  if (expandedEl && window.innerWidth <= 768) {
    requestAnimationFrame(() => {
      expandedEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // Reflect in URL (no new history entry — just update the address bar)
  const u = new URL(window.location.href);
  u.searchParams.set('party', code);
  u.searchParams.delete('candidate');
  history.replaceState(null, '', u);
}

// ─── Results 2022 ──────────────────────────────────────────

function buildResultsHTML(partyCode, municipalityId) {
  const muniResults = RESULTS_2022[municipalityId];
  if (!muniResults) return '';

  // Municipality held unbound/uncontested election in 2022
  if (muniResults.sjalkjorinn) {
    return `
      <div class="results-2022 results-2022--uncontested">
        <div class="results-label">${ui.results2022Label}</div>
        <div class="results-uncontested-text">${ui.resultsUncontested2022}</div>
      </div>`;
  }

  const r = muniResults.parties?.[partyCode];
  const total = muniResults.totalSeats;

  // Party ran as part of a joint/coalition list in 2022
  if (r?.joint) {
    return `
      <div class="results-2022 results-2022--joint">
        <div class="results-label">${ui.results2022Label}</div>
        <div class="results-joint-text">
          ${ui.resultsJoint(`<em>${r.joint}</em>`)}
          &nbsp;·&nbsp; ${r.pct}%&nbsp;&nbsp;${r.seats} ${ui.ofSeats(total)}
        </div>
      </div>`;
  }

  // Party has no 2022 data (new in 2026 or simply absent)
  if (!r) {
    return `
      <div class="results-2022 results-2022--new">
        <div class="results-label">${ui.results2022Label}</div>
        <div class="results-new-text">${ui.resultsNew}</div>
      </div>`;
  }

  const barPct = Math.min(r.pct, 100);
  const seatsLabel = r.seats === 0
    ? ui.noSeats
    : ui.ofSeats(total);

  return `
    <div class="results-2022">
      <div class="results-label">${ui.results2022Label}</div>
      <div class="results-row">
        <div class="results-pct">
          <span class="results-pct-num">${r.pct}<span class="results-pct-sign">%</span></span>
          <span class="results-pct-desc">${ui.votes}</span>
        </div>
        <div class="results-bar-wrap">
          <div class="results-bar-track">
            <div class="results-bar-fill" style="width:${barPct}%"></div>
          </div>
          ${r.note ? `<div class="results-note">${r.note}</div>` : ''}
        </div>
        <div class="results-seats">
          <span class="results-seats-num">${r.seats === 0 ? '–' : r.seats}</span>
          <span class="results-seats-desc">${seatsLabel}</span>
        </div>
      </div>
    </div>`;
}

// ─── Splash / Agenda ───────────────────────────────────────

function buildSplashHTML(party, data) {
  const muniKey = data.municipalityId;
  const partyKey = data.partyCode;

  const cards = data.agenda.map((item, i) => {
    const title = trData(`${muniKey}.${partyKey}.agenda.${i}.title`, item.title);
    const text  = trData(`${muniKey}.${partyKey}.agenda.${i}.text`,  item.text);
    return `
      <div class="agenda-card">
        <div class="agenda-icon">${item.icon}</div>
        <div class="agenda-title">${title}</div>
        <div class="agenda-text">${text}</div>
      </div>`;
  }).join('');

  const resultsHTML = buildResultsHTML(data.partyCode, data.municipalityId);

  const sourceHTML = data.platformUrl
    ? `<div class="agenda-source">
        <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
          <path d="M5 2H2a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1V7M8 1h3m0 0v3m0-3L5 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <a href="${data.platformUrl}" target="_blank" rel="noopener noreferrer">${ui.platformSource(new URL(data.platformUrl).hostname.replace('www.',''))}</a>
       </div>`
    : '';

  const disclaimerHTML = data.isPlaceholder
    ? `<div class="agenda-disclaimer">
        <span class="agenda-disclaimer-icon">⚠️</span>
        <div class="agenda-disclaimer-body">
          <strong>${ui.noPlatformTitle}</strong>
          <span>${ui.noPlatformDesc}</span>
          <a href="mailto:halldor.berg@inno.link" class="agenda-disclaimer-cta">${ui.noPlatformCTA}</a>
        </div>
       </div>`
    : '';

  const tagline = trData(`${muniKey}.${partyKey}.tagline`, data.tagline);

  return `
    <div class="party-splash">
      <div class="splash-bg"></div>
      <div class="splash-eyebrow">
        <span class="splash-party-badge" style="color:${party.textColor}">
          ${party.code} – ${party.name}
        </span>
        <button class="share-btn share-btn--party"
                data-share-party="${data.partyCode}"
                aria-label="${ui.share}">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="11" cy="2.5" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <circle cx="3" cy="7" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <circle cx="11" cy="11.5" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <line x1="4.6" y1="6.1" x2="9.4" y2="3.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            <line x1="4.6" y1="7.9" x2="9.4" y2="10.6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          ${ui.share}
        </button>
      </div>
      ${resultsHTML}
      <div class="splash-tagline" style="color:${party.textColor}">${tagline}</div>
      ${disclaimerHTML}
      ${data.isPlaceholder ? '' : `<div class="agenda-grid">${cards}</div>`}
      ${sourceHTML}
    </div>`;
}

// ─── Candidate Gallery ─────────────────────────────────────

function buildCandidatesHTML(data, party) {
  const cards = data.candidates.map(c => {
    const fallback = localAvatar(c.name);
    const occupation = trOcc(c.occupation);
    return `
      <div class="candidate-card"
           data-candidate-id="${c.id}"
           data-party-code="${data.partyCode}"
           role="button" tabindex="0"
           aria-label="${ui.seeMore} ${c.name}">
        <div class="candidate-photo-wrap">
          <img src="${c.imageUrl}"
               alt="${c.name}"
               loading="lazy"
               onerror="this.onerror=null;this.src='${fallback}'" />
          <div class="candidate-ballot">${c.ballotOrder}</div>
        </div>
        <div class="candidate-info">
          <div class="candidate-name">${c.name}</div>
          <div class="candidate-occupation">${occupation}</div>
        </div>
        <div class="candidate-card-hover-overlay">
          <span>${ui.seeMore}</span>
        </div>
      </div>`;
  }).join('');

  return `
    <div class="candidates-section">
      <div class="candidates-section-title">
        <span style="color:${party.color}">${party.name}</span>
        &nbsp;– ${ui.candidates}
      </div>
      <div class="candidates-grid">${cards}</div>
    </div>`;
}

// ─── Share / deep-link helpers ────────────────────────────

function partyURL(partyCode) {
  const u = new URL(window.location.href);
  u.searchParams.set('party', partyCode);
  u.searchParams.delete('candidate');
  return u.toString();
}

function candidateURL(candidateId, partyCode) {
  const u = new URL(window.location.href);
  u.searchParams.set('party', partyCode);
  u.searchParams.set('candidate', candidateId);
  return u.toString();
}

let toastTimer = null;
function showToast(msg) {
  const el = document.getElementById('share-toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('is-visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('is-visible'), 3000);
}

async function shareURL(url, title) {
  // 1 — Native share sheet (mobile / supported browsers)
  if (navigator.share) {
    try { await navigator.share({ title, url }); return; } catch (err) {
      if (err.name === 'AbortError') return; // user dismissed — do nothing
    }
  }

  // 2 — Clipboard API (requires secure context; works on localhost & HTTPS)
  try {
    await navigator.clipboard.writeText(url);
    showToast(ui.shareToastCopied);
    return;
  } catch {}

  // 3 — execCommand fallback (works in iframes, HTTP, legacy browsers)
  try {
    const ta = Object.assign(document.createElement('textarea'), {
      value: url,
      style: 'position:fixed;left:-9999px;top:-9999px;opacity:0;',
    });
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (ok) { showToast(ui.shareToastCopied); return; }
  } catch {}

  // 4 — Last resort: show URL in the toast so user can copy manually
  showToast(url);
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

// ─── Smart face crop ───────────────────────────────────────
const faceDetector = ('FaceDetector' in window) ? new FaceDetector({ fastMode: true }) : null;

async function applySmartCrop(img) {
  img.style.objectPosition = 'center 20%';
  if (!faceDetector) return;
  if (!img.complete || !img.naturalWidth) {
    await new Promise(resolve => { img.addEventListener('load', resolve, { once: true }); });
  }
  try {
    const faces = await faceDetector.detect(img);
    if (!faces.length) return;
    const face = faces.reduce((a, b) =>
      b.boundingBox.width * b.boundingBox.height > a.boundingBox.width * a.boundingBox.height ? b : a
    );
    const eyeY = face.boundingBox.top + face.boundingBox.height * 0.35;
    const containerH = img.parentElement.offsetHeight;
    const containerW = img.parentElement.offsetWidth;
    const scale = Math.max(containerW / img.naturalWidth, containerH / img.naturalHeight);
    const renderedH = img.naturalHeight * scale;
    const overflow = renderedH - containerH;
    if (overflow <= 0) return;
    const targetY = containerH * 0.33;
    const eyeRendered = eyeY * scale;
    const P = Math.max(0, Math.min(100, (eyeRendered - targetY) / overflow * 100));
    img.style.transition = 'object-position 0.35s ease';
    img.style.objectPosition = `center ${P}%`;
  } catch {
    // FaceDetector rejected (CORS image, security, etc.) — keep default
  }
}

function openModal(id) {
  const c = allCandidates[id];
  if (!c) return;
  const party = PARTIES[c.partyCode];

  trackEvent('candidate_open', {
    municipality_id:   muni.id,
    municipality_name: muni.name,
    party_code:        c.partyCode,
    party_name:        party?.name ?? c.partyCode,
    candidate_name:    c.name,
    ballot_order:      c.ballotOrder,
  });

  const fallback = localAvatar(c.name);
  const photo = document.getElementById('modal-photo');
  photo.style.objectPosition = 'center 20%';
  photo.style.transition = '';
  photo.src = c.imageUrl;
  photo.alt = c.name;
  photo.onerror = () => { photo.onerror = null; photo.src = fallback; };
  applySmartCrop(photo);

  document.getElementById('modal-name').textContent = c.name;

  const badge = document.getElementById('modal-badge');
  badge.textContent = `#${c.ballotOrder} · ${party.name}`;
  badge.style.cssText = `background:${party.color}22;border:1px solid ${party.color}55;color:${party.color};`;

  // Meta: show age only if real data is available
  const metaParts = [];
  if (c.age) metaParts.push(`<span>${c.age} ${ui.ageLabel}</span><span>·</span>`);
  metaParts.push(`<span>${trOcc(c.occupation)}</span>`);
  document.getElementById('modal-meta').innerHTML = metaParts.join('');

  // Bio section
  const bioSection  = document.getElementById('modal-bio-section');
  const bioEl       = document.getElementById('modal-bio');
  const heimildEl   = document.getElementById('modal-heimild');
  const bio = trData(`${muni.id}.${c.partyCode}.list.${c.ballotOrder}.bio`, c.bio);
  if (bio) {
    bioSection.style.display = '';
    bioEl.textContent = bio;
    if (c.heimild && c.heimild.length) {
      heimildEl.style.display = '';
      heimildEl.innerHTML = ui.source + ': ' + c.heimild.map(h =>
        `<a class="heimild-link" href="${h.url}" target="_blank" rel="noopener">${h.label}</a>`
      ).join(', ');
    } else {
      heimildEl.style.display = 'none';
    }
  } else {
    bioSection.style.display = 'none';
    heimildEl.style.display = 'none';
  }

  // Interests section
  const interestsSection = document.getElementById('modal-interests-section');
  const interestsEl = document.getElementById('modal-interests');
  if (c.interests && c.interests.length) {
    interestsSection.style.display = '';
    const chips = c.interests.map((interest, j) => {
      const translated = trData(`${muni.id}.${c.partyCode}.list.${c.ballotOrder}.interests.${j}`, interest);
      return `<span class="interest-chip">${translated}</span>`;
    }).join('');
    interestsEl.innerHTML = chips;
  } else {
    interestsSection.style.display = 'none';
  }

  // Social links section
  const socialSection = document.getElementById('modal-social-section');
  const socialEl = document.getElementById('modal-social');
  if (c.social && c.social.length) {
    socialSection.style.display = '';
    socialEl.innerHTML = c.social.map(s => {
      const icons = { facebook: '📘', twitter: '🐦', x: '𝕏', instagram: '📸', linkedin: '💼', web: '🌐', tiktok: '🎵' };
      const icon = icons[s.type] || '🔗';
      return `<a class="social-link" href="${s.url}" target="_blank" rel="noopener">${icon} ${s.label}</a>`;
    }).join('');
  } else {
    socialSection.style.display = 'none';
  }

  // News section
  const newsSection = document.getElementById('modal-news-section');
  const newsEl = document.getElementById('modal-news');
  if (c.news && c.news.length) {
    newsSection.style.display = '';
    newsEl.innerHTML = c.news.map(n =>
      `<a class="news-link" href="${n.url}" target="_blank" rel="noopener">
        <span class="news-title">${n.title}</span>
        <span class="news-source">${n.source}</span>
      </a>`
    ).join('');
  } else {
    newsSection.style.display = 'none';
  }

  // "No info" notice — show if none of bio/interests/social/news
  const noInfo = document.getElementById('modal-no-info');
  const hasAnyInfo = bio || (c.interests && c.interests.length) ||
                     (c.social && c.social.length) || (c.news && c.news.length);
  noInfo.style.display = hasAnyInfo ? 'none' : '';

  overlay.classList.add('is-open');
  document.body.style.overflow = 'hidden';

  // Push URL so the back button closes the modal
  const u = new URL(window.location.href);
  u.searchParams.set('party', c.partyCode);
  u.searchParams.set('candidate', id);
  history.pushState({ candidate: id }, '', u);

  // Wire share button for this candidate
  const shareBtn = document.getElementById('modal-share');
  if (shareBtn) {
    shareBtn.onclick = () => shareURL(
      candidateURL(id, c.partyCode),
      `${c.name} – ${PARTIES[c.partyCode].name} – Kosningar 2026`
    );
  }
}

function closeModal(updateHistory = true) {
  overlay.classList.remove('is-open');
  document.body.style.overflow = '';
  if (updateHistory) {
    const u = new URL(window.location.href);
    u.searchParams.delete('candidate');
    history.replaceState(null, '', u);
  }
}

document.getElementById('modal-close').addEventListener('click', () => closeModal());
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// Back button closes the modal without double-popping history
window.addEventListener('popstate', e => {
  if (overlay.classList.contains('is-open')) {
    closeModal(false);
  }
});

// ─── Party share button delegation ────────────────────────

container.addEventListener('click', e => {
  const btn = e.target.closest('.share-btn--party');
  if (!btn) return;
  e.stopPropagation();
  const code = btn.dataset.shareParty;
  const party = PARTIES[code];
  shareURL(partyURL(code), `${party.name} – ${muni.name} – Kosningar 2026`);
});

// ─── Boot ──────────────────────────────────────────────────

  renderAccordion();

  // Track the initially displayed party
  trackEvent('party_open', {
    municipality_id:   muni.id,
    municipality_name: muni.name,
    party_code:        activeParty,
    party_name:        PARTIES[activeParty]?.name ?? activeParty,
  });

  // ─── Mobile scroll-fade indicators ────────────────────────
  (function initScrollFades() {
    if (window.innerWidth > 768) return;
    const section = document.querySelector('.accordion-section');
    if (!section) return;
    function update() {
      const atTop    = container.scrollTop < 8;
      const atBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 8;
      section.classList.toggle('is-scrolled-down', !atTop);
      section.classList.toggle('is-at-bottom',     atBottom);
    }
    container.addEventListener('scroll', update, { passive: true });
    update();
  })();

  // Set initial URL to reflect the active party (no history entry)
  const initURL = new URL(window.location.href);
  initURL.searchParams.set('party', activeParty);
  if (!paramCandidate) initURL.searchParams.delete('candidate');
  history.replaceState(null, '', initURL);

  // Open candidate from deep link (after DOM is ready)
  if (paramCandidate && allCandidates[paramCandidate]) {
    requestAnimationFrame(() => openModal(paramCandidate));
  }

} // end else (not isUnbound)
