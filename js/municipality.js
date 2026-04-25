import { MUNICIPALITIES } from './data/municipalities.js?v=13';
import { PARTIES } from './data/parties.js?v=4';
import { getMunicipalityPartyData } from './data/candidates.js?v=14';
import { RESULTS_2022 } from './data/results2022.js?v=2';

// ─── Local avatar generator (replaces ui-avatars.com hotlink) ─────────────
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
      `Opnaði ${randomParty.name} af handahófi`;
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

  // Reflect in URL (no new history entry — just update the address bar)
  const u = new URL(window.location.href);
  u.searchParams.set('party', code);
  u.searchParams.delete('candidate');
  history.replaceState(null, '', u);
}

// ─── Splash / Agenda ───────────────────────────────────────

function buildResultsHTML(partyCode, muniId) {
  const muniResults = RESULTS_2022[muniId];
  if (!muniResults) return '';

  // Municipality held unbound/uncontested election in 2022
  if (muniResults.sjalkjorinn) {
    return `
      <div class="results-2022 results-2022--uncontested">
        <div class="results-label">📊 Kosningaúrslit 2022</div>
        <div class="results-uncontested-text">🤝 Óbundnar kosningar — engir listar 2022</div>
      </div>`;
  }

  const r = muniResults.parties?.[partyCode];
  const total = muniResults.totalSeats;

  // Party ran as part of a joint/coalition list in 2022
  if (r?.joint) {
    return `
      <div class="results-2022 results-2022--joint">
        <div class="results-label">📊 Kosningaúrslit 2022</div>
        <div class="results-joint-text">
          Keppti sem hluti af <em>${r.joint}</em>
          &nbsp;·&nbsp; ${r.pct}%&nbsp;&nbsp;${r.seats} sæti af ${total}
        </div>
      </div>`;
  }

  // Party has no 2022 data (new in 2026 or simply absent)
  if (!r) {
    return `
      <div class="results-2022 results-2022--new">
        <div class="results-label">📊 Kosningaúrslit 2022</div>
        <div class="results-new-text">✨ Nýtt framboð — tók ekki þátt árið 2022</div>
      </div>`;
  }

  const barPct = Math.min(r.pct, 100);
  const seatsLabel = r.seats === 0
    ? 'Engin sæti'
    : `af ${total} sætum`;

  return `
    <div class="results-2022">
      <div class="results-label">📊 Kosningaúrslit 2022</div>
      <div class="results-row">
        <div class="results-pct">
          <span class="results-pct-num">${r.pct}<span class="results-pct-sign">%</span></span>
          <span class="results-pct-desc">atkvæða</span>
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

function buildSplashHTML(party, data) {
  const cards = data.agenda.map(item => `
    <div class="agenda-card">
      <div class="agenda-icon">${item.icon}</div>
      <div class="agenda-title">${item.title}</div>
      <div class="agenda-text">${item.text}</div>
    </div>`).join('');

  const resultsHTML = buildResultsHTML(data.partyCode, data.municipalityId);

  return `
    <div class="party-splash">
      <div class="splash-bg"></div>
      <div class="splash-eyebrow">
        <span class="splash-party-badge" style="color:${party.textColor}">
          ${party.code} – ${party.name}
        </span>
        <button class="share-btn share-btn--party"
                data-share-party="${data.partyCode}"
                aria-label="Deila hlekk á þennan flokk">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="11" cy="2.5" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <circle cx="3" cy="7" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <circle cx="11" cy="11.5" r="1.75" stroke="currentColor" stroke-width="1.4"/>
            <line x1="4.6" y1="6.1" x2="9.4" y2="3.4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            <line x1="4.6" y1="7.9" x2="9.4" y2="10.6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          Deila
        </button>
      </div>
      ${resultsHTML}
      <div class="splash-tagline" style="color:${party.textColor}">${data.tagline}</div>
      <div class="agenda-grid">${cards}</div>
    </div>`;
}

// ─── Candidate Gallery ─────────────────────────────────────

function buildCandidatesHTML(data, party) {
  const cards = data.candidates.map(c => {
    const fallback = localAvatar(c.name);
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
    showToast('✓ Hlekkur afritaður!');
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
    if (ok) { showToast('✓ Hlekkur afritaður!'); return; }
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
// Uses the browser's FaceDetector API (Chrome/Edge) to position
// eyes ~33% down in the hero frame. Falls back to object-position
// center 20% on unsupported browsers (good default for headshots).

const faceDetector = ('FaceDetector' in window) ? new FaceDetector({ fastMode: true }) : null;

async function applySmartCrop(img) {
  // Sensible default: show upper portion of image
  img.style.objectPosition = 'center 20%';

  if (!faceDetector) return;

  // Wait for the image to finish loading
  if (!img.complete || !img.naturalWidth) {
    await new Promise(resolve => { img.addEventListener('load', resolve, { once: true }); });
  }

  try {
    const faces = await faceDetector.detect(img);
    if (!faces.length) return;

    // Pick the largest face (most likely the subject)
    const face = faces.reduce((a, b) =>
      b.boundingBox.width * b.boundingBox.height > a.boundingBox.width * a.boundingBox.height ? b : a
    );

    // Eyes sit roughly 35% down inside the face bounding box
    const eyeY = face.boundingBox.top + face.boundingBox.height * 0.35;

    // Calculate object-position Y% that places the eye at ~33% of container height
    const containerH = img.parentElement.offsetHeight;
    const containerW = img.parentElement.offsetWidth;
    const scale = Math.max(containerW / img.naturalWidth, containerH / img.naturalHeight);
    const renderedH = img.naturalHeight * scale;
    const overflow = renderedH - containerH;

    if (overflow <= 0) return; // image fits entirely — no crop needed

    const targetY = containerH * 0.33;           // eyes a third down from top
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

  const fallback = localAvatar(c.name);
  const photo = document.getElementById('modal-photo');
  // Reset position before loading new image
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
  if (c.age) metaParts.push(`<span>${c.age} ára</span><span>·</span>`);
  metaParts.push(`<span>${c.occupation}</span>`);
  document.getElementById('modal-meta').innerHTML = metaParts.join('');

  // Bio section
  const bioSection = document.getElementById('modal-bio-section');
  const bioEl = document.getElementById('modal-bio');
  if (c.bio) {
    bioSection.style.display = '';
    bioEl.textContent = c.bio;
  } else {
    bioSection.style.display = 'none';
  }

  // Interests section
  const interestsSection = document.getElementById('modal-interests-section');
  const interestsEl = document.getElementById('modal-interests');
  if (c.interests && c.interests.length) {
    interestsSection.style.display = '';
    interestsEl.innerHTML = c.interests.map(i => `<span class="interest-chip">${i}</span>`).join('');
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
  const hasAnyInfo = c.bio || (c.interests && c.interests.length) ||
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
