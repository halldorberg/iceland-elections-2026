import { MUNICIPALITIES } from './data/municipalities.js?v=15';
import { PARTIES } from './data/parties.js?v=4';
import { getMunicipalityPartyData } from './data/candidates.js?v=96';
import { RESULTS_2022 } from './data/results2022.js?v=7';
import { POLLS }        from './data/polls.js?v=4';
import { EYE_POSITIONS } from './data/eye_positions.js?v=5';
import { CLEAVAGES, STANCE_SMILEYS } from './data/cleavages.js?v=3';
import { RUV_POSITIONS } from './data/ruv_positions.js?v=4';
import { getLang, t, renderLangSwitcher, MUNI_DATIVE_IS } from './i18n.js?v=15';
import { partySlug, partyCodeFromSlug, slugify } from './data/party_slugs.js?v=3';

// ─── i18n ──────────────────────────────────────────────────
const lang = getLang();
const ui   = t();

let TR = {};
if (lang === 'en') {
  const mod = await import('./data/candidates.en.js?v=27');
  TR = mod.TRANSLATIONS_EN;
} else if (lang === 'pl') {
  const mod = await import('./data/candidates.pl.js?v=27');
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
  const setHTML = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };
  set('back-btn-text',            ui.backToMap);
  set('muni-share-text',          ui.share);
  set('modal-share-text',         ui.share);
  set('modal-label-bio',          ui.aboutCandidate);
  set('modal-label-interests',    ui.policyFocus);
  set('modal-label-social',       ui.socialMedia);
  set('modal-label-news',         ui.news);
  set('disclaimer-title',         ui.disclaimerTitle);
  setHTML('disclaimer-body-text', ui.disclaimerText);
  const noInfoEl = document.getElementById('modal-no-info');
  if (noInfoEl) noInfoEl.innerHTML = `<span class="no-info-icon">ℹ️</span> ${ui.noInfo}`;
})();

// ─── Per-muni floating notice ──────────────────────────────
// Shown when the page is for a muni that has a notice defined.
// Dismissal is session-only (sessionStorage) — clicking × hides it for
// this browser session, but it reappears the next time the user opens
// the site so important info doesn't get permanently buried.
(function applyMuniNotice() {
  // The muniId variable is set later in the file — re-derive from URL here so
  // the notice can show before the rest of the page renders.
  const segs = window.location.pathname.replace(/^\/(?:en|pl)\//, '/').replace(/^\/+/, '').split('/');
  const id = segs[0] || (new URLSearchParams(window.location.search).get('id')) || '';

  const NOTICES = {
    mulathing: { titleKey: 'mulathingNoticeTitle', textKey: 'mulathingNoticeText' },
  };
  const notice = NOTICES[id];
  if (!notice) return;
  const sessionKey = 'muni-notice-dismissed:' + id;
  if (sessionStorage.getItem(sessionKey) === '1') return;
  // One-time clean-up of the old localStorage flag from the permanent-dismiss
  // version of this code so users who dismissed earlier see the notice again.
  try { localStorage.removeItem(sessionKey); } catch (e) {}

  const el = document.getElementById('muni-notice');
  if (!el) return;
  document.getElementById('muni-notice-title').textContent = ui[notice.titleKey] || '';
  document.getElementById('muni-notice-text').innerHTML  = ui[notice.textKey] || '';
  el.hidden = false;
  document.getElementById('muni-notice-close').addEventListener('click', () => {
    sessionStorage.setItem(sessionKey, '1');
    el.hidden = true;
  });
})();

// ─── Local avatar generator ────────────────────────────────
function localAvatar(name) {
  const initials = name.trim().split(/\s+/).slice(0, 2).map(w => w[0] || '').join('').toUpperCase();
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"><rect width="300" height="300" fill="#1c2335"/><text x="150" y="155" text-anchor="middle" dominant-baseline="middle" fill="#8892a4" font-family="Arial,sans-serif" font-size="120" font-weight="bold">${initials}</text></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

// ─── Init ──────────────────────────────────────────────────

/**
 * Parse the route from EITHER the path (Phase 2 scheme:
 * /[lang/]<muni>/<party-slug>/<candidate-slug>) OR the legacy query string
 * (?id=X&party=Y&candidate=N). Path takes precedence when present.
 *
 * Returns { muniId, partySlug, partyCode, candidateSlug, candidateBallot, lang }.
 * Candidate fields are resolved at runtime when path-based; the legacy
 * ?candidate=<id> form returns a candidateBallot of the actual ID.
 */
// Special non-party second-segment slugs that open feature panels rather
// than expand a party. Same slug across all locales (matches the existing
// pattern where party slugs are language-agnostic Icelandic strings).
const SPECIAL_FEATURE_SLUGS = new Set(['liklegustu-meirihlutarnir']);

function parseRoute() {
  const pathSegs = window.location.pathname
    .split('/').filter(s => s && !s.endsWith('.html'));
  // /en/gardabaer/samfylkingin/kjartan-atli-kjartansson/
  // ↑      ↑             ↑           ↑
  // lang   muni          party       candidate
  let langSeg = null;
  let segs = pathSegs.slice();
  if (segs.length && (segs[0] === 'en' || segs[0] === 'pl')) {
    langSeg = segs.shift();
  }
  const sp = new URLSearchParams(window.location.search);
  const muniId = segs[0] || sp.get('id') || 'reykjavik';
  const seg1 = segs[1] || null;
  const featureSlug = (seg1 && SPECIAL_FEATURE_SLUGS.has(seg1)) ? seg1 : null;
  const partySlugStr = featureSlug ? null : seg1;
  const candidateSlug = featureSlug ? null : (segs[2] || null);
  const known = MUNICIPALITIES.find(m => m.id === muniId)?.partyIds || [];
  const partyCode = partySlugStr
    ? partyCodeFromSlug(partySlugStr, known)
    : sp.get('party') || null;
  // candidate from legacy ?candidate=ID; for path-based, resolved later.
  const candidateBallot = sp.get('candidate') || null;
  return { muniId, partySlug: partySlugStr, partyCode, candidateSlug, candidateBallot, langOverride: langSeg, featureSlug };
}

const route = parseRoute();
const params = new URLSearchParams(window.location.search);  // kept for backward compat
const muniId = route.muniId;
const muni = MUNICIPALITIES.find(m => m.id === muniId) || MUNICIPALITIES[0];

document.getElementById('muni-name').textContent = muni.name;

// ─── Long-name marquee ─────────────────────────────────────
// If the muni name doesn't fit the centre column (e.g. "Sameinað
// sveitarfélag Borgarbyggðar og Skorradalshrepps"), scroll it like a TV
// news ticker. Otherwise leave it static. Decision is re-evaluated on
// resize so rotating the device works too.
(function setupMuniNameMarquee() {
  const el = document.getElementById('muni-name');
  if (!el) return;
  const name = muni.name;

  function measure() {
    // Reset to static so we measure natural size, not the marquee track.
    el.classList.remove('is-marquee');
    el.textContent = name;
    // Wait one frame for layout to settle before measuring.
    requestAnimationFrame(() => {
      const overflows = el.scrollWidth > el.clientWidth + 1;
      if (!overflows) return;
      // Build a seamlessly-looping ticker: two copies of the name with
      // a gap; outer animates by -50% so the second copy slides in
      // exactly where the first started.
      el.classList.add('is-marquee');
      el.textContent = '';
      const track = document.createElement('span');
      track.className = 'muni-name-track';
      const a = document.createElement('span');  a.textContent = name;
      const b = document.createElement('span');  b.textContent = name;  b.setAttribute('aria-hidden', 'true');
      track.append(a, b);
      el.appendChild(track);
    });
  }

  measure();
  let resizeTimer = null;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(measure, 150);
  });
})();
document.getElementById('muni-region').textContent = muni.region;
document.documentElement.lang = lang;

// ─── Coalition strip (líklegustu meirihlutarnir) ──────────────────────────
// Renders an expandable banner directly under the top nav with every
// minimum winning coalition derived from the muni's latest poll, each
// scored on RÚV kosningapróf alignment. Currently gated to Reykjavík for
// the experiment — extend later by removing the muniId check.
(function setupCoalitionStrip() {
  if (muniId !== 'reykjavik') return;
  const pollEntry = (POLLS[muniId] && POLLS[muniId][0]) || null;
  if (!pollEntry || !pollEntry.parties) return;
  const positionsMuni = (RUV_POSITIONS && RUV_POSITIONS[muniId]) || null;

  const totalSeats = pollEntry.totalSeats || 23;
  const majority = Math.floor(totalSeats / 2) + 1;

  // Parties with at least one seat — anything else can't help form a majority.
  const seated = Object.entries(pollEntry.parties)
    .filter(([_, v]) => (v.seats || 0) > 0)
    .map(([code, v]) => ({ code, seats: v.seats }));

  // Enumerate all minimum winning coalitions: subsets summing ≥ majority
  // where removing any single member drops the total below majority.
  const mwcs = [];
  const n = seated.length;
  for (let mask = 1; mask < (1 << n); mask++) {
    let total = 0;
    const members = [];
    for (let i = 0; i < n; i++) {
      if (mask & (1 << i)) { members.push(seated[i]); total += seated[i].seats; }
    }
    if (total < majority) continue;
    const isMin = members.every(p => total - p.seats < majority);
    if (isMin) mwcs.push({ members, total });
  }

  // ─── Coalition scoring on RÚV kosningapróf ─────────────────────────────
  // Uses each party's officially-submitted answer per proposition
  // (ruv_positions.js .value / .mean, 1=mjög ósammála … 4=mjög sammála).
  // Returns the 0-100 score plus enough detail for the breakdown modal.
  function scoreCoalition(memberCodes) {
    if (!positionsMuni) return null;
    const Q = positionsMuni.questions;
    const P = positionsMuni.parties;

    // Walk questions in the RÚV source-document order (captured at build
    // time in ruv_positions.js). Falls back to dict insertion order.
    const qids = positionsMuni.order || Object.keys(Q);
    let spreadSum = 0, spreadCount = 0;
    let impWeightedSpreadSum = 0, impWeightTotal = 0;
    const rows = []; // every per-question row { qid, title, spread, perParty, impW }

    for (const qid of qids) {
      const meta = Q[qid];
      const perParty = {};
      let ok = true;
      for (const code of memberCodes) {
        const entry = P[code] && P[code][qid];
        if (!entry || entry.n === 0) { ok = false; break; }
        perParty[code] = entry.mean;
      }
      if (!ok) continue;
      const vals = Object.values(perParty);
      const spread = Math.max(...vals) - Math.min(...vals);
      spreadSum += spread;
      spreadCount += 1;
      let impW = 0;
      for (const code of memberCodes) impW += (meta.importance && meta.importance[code]) || 0;
      if (impW > 0) {
        impWeightedSpreadSum += spread * impW;
        impWeightTotal += 3 * impW;  // 3 = max possible spread on a 1..4 scale
      }
      rows.push({ qid, title: meta.title, spread, perParty, impW });
    }
    if (spreadCount === 0) return null;

    const avgSpread = spreadSum / spreadCount;
    const spreadScore = 1 - (avgSpread / 3);

    // Pairwise: average per-question distance for every pair of coalition
    // parties. Worst pair drives the weakest-link signal; the whole matrix
    // is exposed for the breakdown modal.
    const pairs = []; // { a, b, dist }
    let worstPairDist = 0;
    let worstPair = null;
    for (let i = 0; i < memberCodes.length; i++) {
      for (let j = i + 1; j < memberCodes.length; j++) {
        const a = memberCodes[i], b = memberCodes[j];
        let sum = 0, n = 0;
        for (const qid of qids) {
          const ea = P[a] && P[a][qid];
          const eb = P[b] && P[b][qid];
          if (!ea || !eb) continue;
          sum += Math.abs(ea.mean - eb.mean);
          n += 1;
        }
        if (n === 0) continue;
        const d = sum / n;
        pairs.push({ a, b, dist: d });
        if (d > worstPairDist) { worstPairDist = d; worstPair = { a, b, dist: d }; }
      }
    }
    const weakestLinkScore = 1 - (worstPairDist / 3);

    const importanceScore = impWeightTotal > 0
      ? 1 - (impWeightedSpreadSum / impWeightTotal)
      : spreadScore;

    const blended = 0.5 * spreadScore + 0.3 * weakestLinkScore + 0.2 * importanceScore;
    const score = Math.round(blended * 100);

    // Top-3 frictions surface in the inline card detail; the full sorted
    // list is kept for the modal.
    const rowsByFriction = rows.slice().sort((a, b) => b.spread - a.spread);
    const frictions = rowsByFriction.slice(0, 3).map(r => ({
      qid: r.qid, title: r.title, spread: r.spread, perParty: r.perParty,
    }));

    return {
      score,
      avgSpread:      +avgSpread.toFixed(3),
      spreadSum:      +spreadSum.toFixed(3),
      worstPairDist:  +worstPairDist.toFixed(3),
      worstPair,                       // {a, b, dist}
      spreadScore:    +spreadScore.toFixed(3),
      weakestLinkScore: +weakestLinkScore.toFixed(3),
      importanceScore: +importanceScore.toFixed(3),
      impWeightedSpreadSum: +impWeightedSpreadSum.toFixed(3),
      impWeightTotal:       +impWeightTotal.toFixed(3),
      frictions,
      rows,                      // full list — source-doc order
      rowsByFriction,            // full list — order = spread desc
      pairs,                     // every coalition party-pair distance
      questionCount: spreadCount,
    };
  }

  // Score every coalition once.
  for (const c of mwcs) {
    c.score = scoreCoalition(c.members.map(m => m.code));
  }

  // Sort: highest samstaða first; tiebreak with fewer parties, then more seats.
  mwcs.sort((a, b) =>
    (b.score?.score ?? -1) - (a.score?.score ?? -1) ||
    a.members.length - b.members.length ||
    b.total - a.total
  );

  const strip   = document.getElementById('coalition-strip');
  const banner  = document.getElementById('coalition-banner');
  const panel   = document.getElementById('coalition-panel');
  const cardsEl = document.getElementById('coalition-cards');
  if (!strip || !banner || !panel || !cardsEl) return;

  // Banner title — translatable.
  const bannerTextEl = banner.querySelector('.coalition-banner-text');
  if (bannerTextEl) bannerTextEl.textContent = ui.coalitionBannerTitle;

  function scoreBand(s) {
    if (s == null) return 'unknown';
    if (s >= 75) return 'high';
    if (s >= 60) return 'mid';
    if (s >= 45) return 'low';
    return 'verylow';
  }

  function meanToLetter(m) {
    if (m == null) return '–';
    if (m < 1.5) return 'A';
    if (m < 2.5) return 'B';
    if (m < 3.5) return 'C';
    return 'D';
  }

  // Local copy — keeps the IIFE independent of helper-hoisting order.
  function escHTML(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function renderFrictions(frictions, memberCodes) {
    if (!frictions || frictions.length === 0) return '';
    const rows = frictions.map(f => {
      const stances = memberCodes.map(code => {
        const m = f.perParty[code];
        const p = PARTIES[code];
        const bg = (p && p.color) || '#555';
        const letter = meanToLetter(m);
        const smiley = STANCE_SMILEYS[letter] || '·';
        return `<span class="friction-stance" style="--chip-bg:${bg}"
                  title="${code}: ${m == null ? '–' : m.toFixed(2)}/4">
                  <span class="friction-stance-code">${code}</span>
                  <span class="friction-stance-smiley">${smiley}</span>
                </span>`;
      }).join('');
      return `
        <li class="friction-row">
          <div class="friction-q">${escHTML(f.title)}</div>
          <div class="friction-stances">${stances}</div>
        </li>`;
    }).join('');
    return `
      <div class="coalition-frictions">
        <div class="coalition-frictions-h">${ui.coalitionFrictionHeader}</div>
        <ul>${rows}</ul>
      </div>`;
  }

  // Build cards once, up front.
  if (mwcs.length === 0) {
    cardsEl.innerHTML = `<div class="coalition-empty">${ui.coalitionEmpty}</div>`;
  } else {
    cardsEl.innerHTML = mwcs.map((c, idx) => {
      const chips = c.members.map(m => {
        const p = PARTIES[m.code];
        const bg = (p && p.color) || '#555';
        return `<span class="coalition-chip" style="--chip-bg:${bg}">${m.code}<span class="coalition-chip-seats">${m.seats}</span></span>`;
      }).join('');
      const partyCount = c.members.length;
      const partyLabel = ui.coalitionPartyCount(partyCount);
      const s = c.score;
      const band = scoreBand(s?.score);
      const scoreHTML = s
        ? `<div class="coalition-score coalition-score--${band}" title="${escHTML(ui.coalitionScoreTooltip)}">
             <span class="coalition-score-num">${s.score}</span>
             <span class="coalition-score-label">${ui.coalitionScoreLabel}</span>
           </div>`
        : `<div class="coalition-score coalition-score--unknown" title="${escHTML(ui.coalitionScoreUnknown)}"><span class="coalition-score-num">–</span><span class="coalition-score-label">${ui.coalitionScoreLabel}</span></div>`;
      const frictionsHTML = s ? renderFrictions(s.frictions, c.members.map(m => m.code)) : '';
      const detailLinkHTML = s
        ? `<button type="button" class="coalition-detail-link" data-idx="${idx}">
             ${ui.coalitionDetailLink || 'Sjá útreikning →'}
           </button>`
        : '';
      return `
        <div class="coalition-card" data-idx="${idx}">
          <button class="coalition-card-head" type="button" aria-expanded="false">
            <div class="coalition-card-main">
              <div class="coalition-card-chips">${chips}</div>
              <div class="coalition-card-meta">
                <span>${partyLabel}</span>
                <span class="coalition-card-total">${c.total}<small>/${totalSeats}</small></span>
              </div>
            </div>
            ${scoreHTML}
          </button>
          <div class="coalition-card-detail">${frictionsHTML}</div>
          ${detailLinkHTML}
        </div>`;
    }).join('');

    // Card expand/collapse + detail-modal opener.
    cardsEl.addEventListener('click', (e) => {
      const linkBtn = e.target.closest('.coalition-detail-link');
      if (linkBtn) {
        const idx = parseInt(linkBtn.dataset.idx, 10);
        const coalition = mwcs[idx];
        if (coalition) openCoalitionDetailModal(coalition);
        return;
      }
      const head = e.target.closest('.coalition-card-head');
      if (!head) return;
      const card = head.closest('.coalition-card');
      const isOpen = card.classList.toggle('is-open');
      head.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // One-liner intro above the grid — same source-of-truth note that
    // used to live in the footer methodology block.
    const intro = document.createElement('div');
    intro.className = 'coalition-intro';
    intro.textContent = ui.coalitionIntro || 'Samstöðueinkunn byggð á svörum úr Kosningaprófi RÚV';
    cardsEl.insertBefore(intro, cardsEl.firstChild);
  }

  // Sync --nav-h (top muni-nav height) and --strip-h (this strip's own
  // height) onto :root so position:fixed offsets, the 50% panel calc,
  // AND the accordion-section padding/top offsets all stay accurate
  // across resizes and the desktop/mobile layout switch.
  function syncDimensions() {
    const nav = document.querySelector('.muni-nav');
    if (!nav) return;
    const nh = nav.getBoundingClientRect().height || 60;
    const sh = banner.getBoundingClientRect().height || 38;
    document.documentElement.style.setProperty('--nav-h', `${nh}px`);
    document.documentElement.style.setProperty('--strip-h', `${sh}px`);
  }

  function setExpanded(expanded) {
    banner.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    panel.setAttribute('aria-hidden', expanded ? 'false' : 'true');
    panel.classList.toggle('is-expanded', expanded);
  }

  banner.addEventListener('click', () => {
    const expanded = banner.getAttribute('aria-expanded') === 'true';
    setExpanded(!expanded);
  });

  // Click anywhere outside the strip → collapse it.
  document.addEventListener('click', (e) => {
    if (banner.getAttribute('aria-expanded') !== 'true') return;
    if (strip.contains(e.target)) return;
    setExpanded(false);
  });
  // Esc also collapses.
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && banner.getAttribute('aria-expanded') === 'true') {
      setExpanded(false);
    }
  });

  // Reveal: drop `hidden`, mark body so the accordion-section CSS bumps
  // its padding-top by --strip-h, then measure nav/strip heights now that
  // they're actually laid out.
  strip.hidden = false;
  document.body.classList.add('has-coalition-strip');
  syncDimensions();
  window.addEventListener('resize', syncDimensions);

  // ─── Coalition-detail modal ────────────────────────────────────────────
  // Lazy-built overlay opened by the "Sjá útreikning" link on each card.
  // Shows the score breakdown, every proposition with each party's stance,
  // and the pairwise distance matrix.
  let _detailEl = null;
  function ensureDetailEl() {
    if (_detailEl) return _detailEl;
    _detailEl = document.createElement('div');
    _detailEl.className = 'coalition-detail-modal';
    _detailEl.setAttribute('role', 'dialog');
    _detailEl.setAttribute('aria-modal', 'true');
    _detailEl.hidden = true;
    _detailEl.innerHTML = `
      <div class="coalition-detail-backdrop"></div>
      <div class="coalition-detail-sheet" role="document">
        <button type="button" class="coalition-detail-x" aria-label="${ui.coalitionDetailClose || 'Loka'}">×</button>
        <div class="coalition-detail-body"></div>
      </div>`;
    document.body.appendChild(_detailEl);
    _detailEl.addEventListener('click', (e) => {
      if (e.target.classList.contains('coalition-detail-backdrop') ||
          e.target.classList.contains('coalition-detail-x')) {
        closeDetailModal();
      }
    });
    return _detailEl;
  }
  function closeDetailModal() {
    if (_detailEl) _detailEl.hidden = true;
    document.body.classList.remove('coalition-detail-open');
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && _detailEl && !_detailEl.hidden) closeDetailModal();
  });

  function openCoalitionDetailModal(coalition) {
    const el = ensureDetailEl();
    const s = coalition.score;
    const codes = coalition.members.map(m => m.code);
    const tCol = ui.coalitionDetailQuestionCol || 'Fullyrðing';
    const spreadCol = ui.coalitionDetailSpreadCol || 'Bil';

    // Header: party chips + total seats + big score.
    const chips = coalition.members.map(m => {
      const p = PARTIES[m.code];
      const bg = (p && p.color) || '#555';
      return `<span class="coalition-chip" style="--chip-bg:${bg}">${m.code}<span class="coalition-chip-seats">${m.seats}</span></span>`;
    }).join('');
    const band = scoreBand(s.score);

    // Score breakdown — three components blended. Each card shows the
    // formula and the actual numbers plugged in beneath the score.
    const pct = (v) => Math.round(v * 100);
    const lang = getLang();
    const f1 = (n) => Number(n).toFixed(2);
    // Localised, terse formulae shown in italics under each component.
    const formulae = {
      is: {
        bil:    `(1 − Σ bil / (N × 3)) × 100 = (1 − ${f1(s.spreadSum)} / (${s.questionCount} × 3)) × 100`,
        link:   s.worstPair
                  ? `(1 − versta-par / 3) × 100 = (1 − ${f1(s.worstPairDist)} / 3) × 100  ·  versta par: ${s.worstPair.a}↔${s.worstPair.b}`
                  : `(1 − versta-par / 3) × 100`,
        imp:    s.impWeightTotal > 0
                  ? `(1 − Σ(bil × vægi) / Σ(3 × vægi)) × 100 = (1 − ${f1(s.impWeightedSpreadSum)} / ${f1(s.impWeightTotal)}) × 100`
                  : `Engin mikilvæg merking — sami mælikvarði og „Bil".`,
        total:  `Samtals = 0,5 × Bil + 0,3 × Versti hlekkur + 0,2 × Áhersluvegið bil = 0,5 × ${pct(s.spreadScore)} + 0,3 × ${pct(s.weakestLinkScore)} + 0,2 × ${pct(s.importanceScore)}`,
      },
      en: {
        bil:    `(1 − Σ spread / (N × 3)) × 100 = (1 − ${f1(s.spreadSum)} / (${s.questionCount} × 3)) × 100`,
        link:   s.worstPair
                  ? `(1 − worst-pair / 3) × 100 = (1 − ${f1(s.worstPairDist)} / 3) × 100  ·  worst pair: ${s.worstPair.a}↔${s.worstPair.b}`
                  : `(1 − worst-pair / 3) × 100`,
        imp:    s.impWeightTotal > 0
                  ? `(1 − Σ(spread × w) / Σ(3 × w)) × 100 = (1 − ${f1(s.impWeightedSpreadSum)} / ${f1(s.impWeightTotal)}) × 100`
                  : `No "important" flags — falls back to the Spread measure.`,
        total:  `Total = 0.5 × Spread + 0.3 × Weakest link + 0.2 × Importance-weighted = 0.5 × ${pct(s.spreadScore)} + 0.3 × ${pct(s.weakestLinkScore)} + 0.2 × ${pct(s.importanceScore)}`,
      },
      pl: {
        bil:    `(1 − Σ rozpiętość / (N × 3)) × 100 = (1 − ${f1(s.spreadSum)} / (${s.questionCount} × 3)) × 100`,
        link:   s.worstPair
                  ? `(1 − najgorsza-para / 3) × 100 = (1 − ${f1(s.worstPairDist)} / 3) × 100  ·  najgorsza para: ${s.worstPair.a}↔${s.worstPair.b}`
                  : `(1 − najgorsza-para / 3) × 100`,
        imp:    s.impWeightTotal > 0
                  ? `(1 − Σ(rozpiętość × w) / Σ(3 × w)) × 100 = (1 − ${f1(s.impWeightedSpreadSum)} / ${f1(s.impWeightTotal)}) × 100`
                  : `Brak ważnych oznaczeń — używamy miary "Rozpiętość".`,
        total:  `Razem = 0,5 × Rozpiętość + 0,3 × Najsłabsze ogniwo + 0,2 × Rozpiętość ważona = 0,5 × ${pct(s.spreadScore)} + 0,3 × ${pct(s.weakestLinkScore)} + 0,2 × ${pct(s.importanceScore)}`,
      },
    };
    const F = formulae[lang] || formulae.is;

    const lbl1 = ui.coalitionDetailBreakdownB1 || 'Bil (50%)';
    const lbl2 = ui.coalitionDetailBreakdownB2 || 'Versti hlekkur (30%)';
    const lbl3 = ui.coalitionDetailBreakdownB3 || 'Áhersluvegið bil (20%)';
    const expl1 = ui.coalitionDetailExplB1 || '';
    const expl2 = ui.coalitionDetailExplB2 || '';
    const expl3 = ui.coalitionDetailExplB3 || '';
    const explT = ui.coalitionDetailExplTotal || '';
    const breakdownHTML = `
      <ul class="coalition-detail-breakdown">
        <li>
          <div class="cdb-row"><span class="cdb-label">${lbl1}</span><span class="cdb-value">${pct(s.spreadScore)}</span></div>
          <p class="cdb-expl">${expl1}</p>
          <div class="cdb-formula">${F.bil}</div>
        </li>
        <li>
          <div class="cdb-row"><span class="cdb-label">${lbl2}</span><span class="cdb-value">${pct(s.weakestLinkScore)}</span></div>
          <p class="cdb-expl">${expl2}</p>
          <div class="cdb-formula">${F.link}</div>
        </li>
        <li>
          <div class="cdb-row"><span class="cdb-label">${lbl3}</span><span class="cdb-value">${pct(s.importanceScore)}</span></div>
          <p class="cdb-expl">${expl3}</p>
          <div class="cdb-formula">${F.imp}</div>
        </li>
        <li class="cdb-total">
          <div class="cdb-row"><span class="cdb-label">${ui.coalitionDetailScoreTotal || 'Samtals'}</span><span class="cdb-value">${s.score}</span></div>
          <p class="cdb-expl">${explT}</p>
          <div class="cdb-formula">${F.total}</div>
        </li>
      </ul>`;

    // Full per-question table.
    const headRow = `
      <tr>
        <th class="cdt-q">${tCol}</th>
        ${codes.map(code => `<th class="cdt-p" style="--chip-bg:${(PARTIES[code]&&PARTIES[code].color)||'#555'}">${code}</th>`).join('')}
        <th class="cdt-s">${spreadCol}</th>
      </tr>`;
    const bodyRows = s.rows.map(r => {
      // Per-question importance map: how many of each coalition party's
      // candidates flagged this proposition as decisive.
      const impByParty = (positionsMuni.questions[r.qid] && positionsMuni.questions[r.qid].importance) || {};
      const stanceCells = codes.map(code => {
        const v = r.perParty[code];
        const letter = meanToLetter(v);
        const smiley = STANCE_SMILEYS[letter] || '·';
        const impN = impByParty[code] || 0;
        const star = impN > 0
          ? `<span class="cdt-p-imp" title="${ui.coalitionDetailImpHint || 'Flokkurinn merkti þessa fullyrðingu sem mikilvæga'}">★</span>`
          : `<span class="cdt-p-imp cdt-p-imp--placeholder" aria-hidden="true">★</span>`;
        return `<td class="cdt-p"><span class="cdt-smiley" title="${code}: ${v != null ? v.toFixed(2) : '–'}/4">${smiley}</span>${star}</td>`;
      }).join('');
      const spreadCls = r.spread >= 2.5 ? 'cdt-s-high'
                      : r.spread >= 1.5 ? 'cdt-s-mid'
                      : r.spread >= 0.5 ? 'cdt-s-low' : 'cdt-s-none';
      return `
        <tr>
          <td class="cdt-q">${escHTML(r.title)}</td>
          ${stanceCells}
          <td class="cdt-s ${spreadCls}">${r.spread.toFixed(2)}</td>
        </tr>`;
    }).join('');

    // Pairwise distance matrix.
    let pairsHTML = '';
    if (s.pairs.length > 0) {
      const pairRows = s.pairs.slice().sort((a, b) => b.dist - a.dist).map(p => {
        const ca = PARTIES[p.a]?.color || '#555';
        const cb = PARTIES[p.b]?.color || '#555';
        return `
          <tr>
            <td class="cdp-pair">
              <span class="coalition-chip" style="--chip-bg:${ca}">${p.a}</span>
              <span class="cdp-vs">↔</span>
              <span class="coalition-chip" style="--chip-bg:${cb}">${p.b}</span>
            </td>
            <td class="cdp-dist">${p.dist.toFixed(2)} / 3</td>
          </tr>`;
      }).join('');
      pairsHTML = `
        <h4>${ui.coalitionDetailPairsH || 'Fjarlægðir milli flokka'}</h4>
        <p class="cd-note">${ui.coalitionDetailPairsHint || 'Meðalfjarlægð á fullyrðingu, 0 = sammála á öllu, 3 = mjög ósammála á öllu.'}</p>
        <table class="coalition-detail-pairs">
          <tbody>${pairRows}</tbody>
        </table>`;
    }

    el.querySelector('.coalition-detail-body').innerHTML = `
      <header class="coalition-detail-header">
        <div class="coalition-detail-chips">${chips}</div>
        <div class="coalition-score coalition-score--${band}">
          <span class="coalition-score-num">${s.score}</span>
          <span class="coalition-score-label">${ui.coalitionScoreLabel}</span>
        </div>
      </header>

      <section>
        <h4>${ui.coalitionDetailBreakdownH || 'Útreikningur (0–100 per hluti)'}</h4>
        ${breakdownHTML}
      </section>

      <section>
        <h4>${ui.coalitionDetailTableH || 'Allar fullyrðingar'}</h4>
        <p class="cd-note">${ui.coalitionDetailTableHint || 'Brosmerki sýna opinbera afstöðu flokksins skv. kosningaprófi RÚV. Bil = munur milli flokks með hæstu og lægstu afstöðu (0–3).'}</p>
        <div class="coalition-detail-table-wrap">
          <table class="coalition-detail-table">
            <thead>${headRow}</thead>
            <tbody>${bodyRows}</tbody>
          </table>
        </div>
      </section>

      <section>${pairsHTML}</section>
    `;
    el.hidden = false;
    document.body.classList.add('coalition-detail-open');
  }

  // Permalink: /reykjavik/liklegustu-meirihlutarnir/ opens the panel
  // on load. Defer so the layout settles and the transition still plays.
  if (route.featureSlug === 'liklegustu-meirihlutarnir') {
    requestAnimationFrame(() => setExpanded(true));
  }
})();

// ─── SEO: dynamic title / meta description / canonical / og per route ────
// Optional explicit candidate override — set by openModal so we can label
// the page with the candidate's actual name without depending on a
// module-level lookup (which has TDZ issues at initial-call time).
let _candidateMetaOverride = null;
function setCandidateMeta(c) { _candidateMetaOverride = c; updatePageMeta(); }
function clearCandidateMeta() { _candidateMetaOverride = null; }

function updatePageMeta() {
  // Re-parse route on every call so URL changes (modal open/close, party
  // expand/collapse) update the head dynamically — works for both path-based
  // (Phase 2) and legacy query-param URLs.
  const r = parseRoute();
  const partyCode = r.partyCode;
  const candidateBallot = r.candidateBallot || (r.candidateSlug ? 'path' : null);
  const muniName = muni.name;
  const electionPhrase = {
    is: 'Kosningar 2026',
    en: '2026 Local Elections',
    pl: 'Wybory samorządowe 2026',
  }[lang] || 'Kosningar 2026';
  // Templates use dashes rather than prepositions because Icelandic muni names
  // are stored in nominative case ("Garðabær"); "í Garðabæ" would require dative
  // and we don't have that field. Dashes sidestep the case issue entirely and
  // also put the most important keyword (muni / party name) first in the SERP.
  const compareLead = {
    is: (m) => `${m} — sjá öll framboð, frambjóðendur og stefnumál fyrir sveitarstjórnarkosningarnar 16. maí 2026. Berðu saman flokka og kjóstu upplýst.`,
    en: (m) => `${m} — see every party, candidate and platform for the May 16, 2026 local elections. Compare them in one place.`,
    pl: (m) => `${m} — zobacz wszystkie partie, kandydatów i programy przed wyborami samorządowymi 16 maja 2026. Porównaj je w jednym miejscu.`,
  }[lang] || ((m) => `${m} — Kosningar 2026`);
  const partyLead = {
    is: (p, m) => `${p} — ${m} — stefnumál og frambjóðendur fyrir sveitarstjórnarkosningar 2026. Berðu listann saman við önnur framboð.`,
    en: (p, m) => `${p} — ${m} — platform and candidates for the 2026 local elections. Compare with other parties on the ballot.`,
    pl: (p, m) => `${p} — ${m} — program i kandydaci w wyborach samorządowych 2026. Porównaj z innymi listami.`,
  }[lang] || ((p, m) => `${p} — ${m} — Kosningar 2026`);
  const candidateLead = {
    is: (n, p, m) => `${n} — ${p} — ${m}. Frambjóðandi í sveitarstjórnarkosningum 2026. Sjá æviágrip, áherslur og fréttir.`,
    en: (n, p, m) => `${n} — ${p} — ${m}. Candidate in the 2026 local elections. See bio, focus areas and news.`,
    pl: (n, p, m) => `${n} — ${p} — ${m}. Kandydat w wyborach samorządowych 2026. Zobacz biografię, priorytety i aktualności.`,
  }[lang] || ((n, p, m) => `${n} — ${p} — ${m}`);

  let title, desc;
  if (candidateBallot && _candidateMetaOverride && partyCode) {
    const party = PARTIES[partyCode] || { name: partyCode };
    const cName = _candidateMetaOverride.name;
    title = `${cName} — ${party.name} — ${muniName}`;
    desc = candidateLead(cName, party.name, muniName);
  } else if (partyCode) {
    const party = PARTIES[partyCode] || { name: partyCode };
    title = `${party.name} — ${muniName} — ${electionPhrase}`;
    desc = partyLead(party.name, muniName);
  } else {
    title = `${muniName} — ${electionPhrase}`;
    desc = compareLead(muniName);
  }
  // Suppress unused-var warnings if no path uses this branch's lead
  void candidateBallot;

  // Trim title to ~60 chars (Google's typical truncation point)
  if (title.length > 60) title = title.slice(0, 57) + '…';

  document.title = title;
  const setMeta = (sel, val) => { const el = document.querySelector(sel); if (el) el.setAttribute('content', val); };
  setMeta('meta[name="description"]', desc);
  setMeta('meta[property="og:title"]', title);
  setMeta('meta[property="og:description"]', desc);
  setMeta('meta[property="og:locale"]', { is: 'is_IS', en: 'en_US', pl: 'pl_PL' }[lang] || 'is_IS');

  // Canonical = current absolute URL
  const canonical = window.location.origin + window.location.pathname + window.location.search;
  const canonicalLink = document.getElementById('canonical-link');
  if (canonicalLink) canonicalLink.setAttribute('href', canonical);
  setMeta('meta[property="og:url"]', canonical);

  // hreflang variants — same path, swap lang param
  const buildHref = (l) => {
    const u = new URL(window.location.href);
    if (l === 'is') u.searchParams.delete('lang');
    else u.searchParams.set('lang', l);
    return u.toString();
  };
  const hl = (id, l) => { const el = document.getElementById(id); if (el) el.setAttribute('href', buildHref(l)); };
  hl('hreflang-is', 'is');
  hl('hreflang-en', 'en');
  hl('hreflang-pl', 'pl');
  hl('hreflang-default', 'is');
}

// Initial call (partyDataMap is populated below; run again after that's ready)
updatePageMeta();

// Hook into history changes so candidate modal open/close updates title
function _onUrlChange() { updatePageMeta(); }
const _origReplace = window.history.replaceState.bind(window.history);
window.history.replaceState = function (...args) {
  const r = _origReplace(...args);
  setTimeout(_onUrlChange, 0);
  return r;
};
const _origPush = window.history.pushState.bind(window.history);
window.history.pushState = function (...args) {
  const r = _origPush(...args);
  setTimeout(_onUrlChange, 0);
  return r;
};
window.addEventListener('popstate', () => setTimeout(_onUrlChange, 0));

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

  // Honour deep-link party — from path (/<muni>/<party-slug>/) or legacy ?party=
  const paramParty     = route.partyCode || params.get('party');
  const paramCandidate = params.get('candidate');  // legacy id-based; path-based handled below
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
    const p = withMuniNameOverride(PARTIES[code], partyDataMap[code]);
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
    activatePollCarousels(ribbon);
    activateCleavageTracks(ribbon);
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

// Per-muni party-name override: if the muni's data block sets `partyName`
// (e.g. X-B in Strandabyggð is "Framsókn og óháðir" not "Framsóknarflokkurinn"),
// shallow-copy the global PARTIES entry and replace name + shortName.
function withMuniNameOverride(party, data) {
  if (!party || !data || !data.partyName) return party;
  return { ...party, name: data.partyName, shortName: data.partyShortName || data.partyName };
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

// When there are few parties the default 66vh cap leaves dead space at the
// bottom on mobile. Give the expanded panel the full remaining viewport height
// so the screen is always filled. Falls back to CSS defaults for busy layouts.
function applyMobileExpandedHeight(expandedEl) {
  if (!expandedEl || window.innerWidth > 768) return;
  const navH       = 72;                               // .accordion-section { top: 72px }
  const collapsedH = (muni.partyIds.length - 1) * 56; // 56px per collapsed ribbon
  const available  = window.innerHeight - navH - collapsedH;
  const cssDefault = Math.round(0.66 * window.innerHeight);
  if (available > cssDefault) {
    expandedEl.style.maxHeight = available + 'px';
    expandedEl.style.minHeight = available + 'px';
  }
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

    // Clear any previously-set inline height overrides on collapsed ribbons
    if (!isNowExpanded) {
      r.style.maxHeight = '';
      r.style.minHeight = '';
    }

    if (isNowExpanded) expandedEl = r;
  });

  // On mobile the container is a fixed-height scroll zone.
  if (expandedEl && window.innerWidth <= 768) {
    applyMobileExpandedHeight(expandedEl);

    // Bring the newly expanded ribbon to the top so the user sees its
    // content AND can still scroll down to reach the collapsed ribbons.
    requestAnimationFrame(() => {
      expandedEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // Reflect in URL (no new history entry — just update the address bar)
  history.replaceState(null, '', buildRouteURL(code));
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

// ─── Recent poll (same shape as Results 2022) ──────────────

function buildPollHTML(partyCode, municipalityId) {
  const muniEntry = POLLS[municipalityId];
  if (!muniEntry) return '';

  // Backwards-compat: accept either an array of polls (newest first) or a
  // single poll object.
  const polls = Array.isArray(muniEntry) ? muniEntry : [muniEntry];
  // Filter to polls that include this party.
  const slides = polls
    .map(p => ({ poll: p, r: p.parties?.[partyCode] }))
    .filter(s => s.r);
  if (!slides.length) return '';

  const renderSlide = ({ poll, r }, idx) => {
    const total = poll.totalSeats;
    const src   = poll.source || {};
    const barPct = Math.min(r.pct, 100);
    const seatsLabel = r.seats === 0 ? ui.noSeats : ui.ofSeats(total);
    const url    = src['url_'    + lang] || src.url    || '';
    const period = src['period_' + lang] || src.period || '';
    const sourceLink = url
      ? `<a href="${url}" target="_blank" rel="noopener noreferrer">${ui.pollSource(src.pollster, period, src.sample)}</a>`
      : ui.pollSource(src.pollster, period, src.sample);
    const olderTag = idx > 0
      ? `<span class="results-poll-older-tag">${ui.olderPollTag}</span>`
      : '';
    return `
      <div class="results-poll-slide" data-slide="${idx}">
        <div class="results-2022 results-poll">
          <div class="results-label">
            ${ui.pollLabel(src.pollster, src.pollsterGen)}
            ${olderTag}
          </div>
          <div class="results-row">
            <div class="results-pct">
              <span class="results-pct-num">${r.pct}<span class="results-pct-sign">%</span></span>
              <span class="results-pct-desc">${ui.votes}</span>
            </div>
            <div class="results-bar-wrap">
              <div class="results-bar-track">
                <div class="results-bar-fill" style="width:${barPct}%"></div>
              </div>
            </div>
            <div class="results-seats">
              <span class="results-seats-num">${r.seats === 0 ? '–' : r.seats}</span>
              <span class="results-seats-desc">${seatsLabel}</span>
            </div>
          </div>
          <div class="results-poll-source">
            ${sourceLink}
            <span class="results-poll-hint">· ${ui.pollSeatsHint}</span>
          </div>
        </div>
      </div>`;
  };

  if (slides.length === 1) {
    return renderSlide(slides[0], 0);
  }

  // Carousel: newest visible by default, older slides live "in the past" to
  // the LEFT. Click ‹ to scroll backwards in time (older slides come in from
  // the left); click › to scroll forwards (newer slides come from the right).
  // To make that physical metaphor work we render slides in chronological
  // order (oldest → newest, left → right) and start the track shifted all
  // the way to the right so the rightmost slide (newest) is in view.
  const count = slides.length;
  const newestIdx = count - 1;  // displayed index of the newest slide
  const slidesHTML = slides
    .map((s, originalIdx) => ({ ...s, originalIdx }))
    .reverse()  // oldest first in DOM, newest last
    .map((s, displayIdx) => renderSlide(s, s.originalIdx, displayIdx))
    .join('');
  return `
    <div class="results-poll-carousel" data-current="${newestIdx}" data-count="${count}">
      <button type="button" class="results-poll-nav results-poll-nav-prev"
              data-dir="-1" aria-label="${ui.olderPollNav}" title="${ui.olderPollNav}">‹</button>
      <div class="results-poll-viewport">
        <div class="results-poll-track">${slidesHTML}</div>
      </div>
      <button type="button" class="results-poll-nav results-poll-nav-next"
              data-dir="1" aria-label="${ui.newerPollNav}" title="${ui.newerPollNav}" disabled>›</button>
      <div class="results-poll-pager"><span class="results-poll-pager-current">${count}</span> / ${count}</div>
      <div class="results-poll-mobile-hint">${ui.pollCarouselHint}</div>
    </div>`;
}

// Hook up carousel navigation after the splash is inserted into the DOM.
// `current` is the *display index* (0 = leftmost = oldest, count-1 = newest).
function activatePollCarousels(root) {
  root.querySelectorAll('.results-poll-carousel').forEach(carousel => {
    const track   = carousel.querySelector('.results-poll-track');
    const slides  = carousel.querySelectorAll('.results-poll-slide');
    const prevBtn = carousel.querySelector('.results-poll-nav-prev');
    const nextBtn = carousel.querySelector('.results-poll-nav-next');
    const pager   = carousel.querySelector('.results-poll-pager-current');
    const count   = slides.length;
    let current   = count - 1;   // start at newest (rightmost)
    const setCurrent = i => {
      current = Math.max(0, Math.min(count - 1, i));
      track.style.transform = `translateX(-${current * 100}%)`;
      carousel.dataset.current = current;
      if (pager) pager.textContent = current + 1;
      if (prevBtn) prevBtn.disabled = current <= 0;          // can't go older
      if (nextBtn) nextBtn.disabled = current >= count - 1;  // can't go newer
    };
    carousel.querySelectorAll('.results-poll-nav').forEach(btn => {
      btn.addEventListener('click', () => setCurrent(current + Number(btn.dataset.dir)));
    });
    setCurrent(count - 1);
  });
}

// ─── Cleavages carousel (RÚV kosningapróf) ─────────────────
// Horizontal scroll of "where do parties disagree?" topics. The party
// being viewed gets a smiley showing its stance; the icon on top is a
// click/hover tooltip with the full Icelandic question text.

function buildCleavagesHTML(data) {
  const list = CLEAVAGES[data.municipalityId];
  if (!list || !list.length) return '';
  const partyCode = data.partyCode;

  const stanceLabels = {
    A: ui.stanceA, B: ui.stanceB, C: ui.stanceC, D: ui.stanceD,
  };
  const cards = list.map(topic => {
    const stance = topic.stances[partyCode];
    const smiley = stance ? STANCE_SMILEYS[stance] : '—';
    const stanceLabel = stance ? stanceLabels[stance] : ui.cleavagesNoStance;
    return `
      <div class="cleavage-card" tabindex="0">
        <button class="cleavage-icon" type="button"
                aria-label="${escapeHtml(topic.title)}"
                data-tooltip="${escapeHtml(topic.title)}"
                data-tooltip-stance="${escapeHtml(stanceLabel)}"
                data-tooltip-stance-key="${escapeHtml(stance || '')}">
          <span class="cleavage-icon-emoji" aria-hidden="true">${topic.icon}</span>
        </button>
        <div class="cleavage-stance" title="${escapeHtml(stanceLabel)}">
          <span class="cleavage-smiley" aria-hidden="true">${smiley}</span>
        </div>
      </div>`;
  }).join('');

  return `
    <div class="cleavages-section" data-cleavage-count="${list.length}">
      <div class="cleavages-header">${escapeHtml(ui.cleavagesHeader)}</div>
      <div class="cleavages-track-wrap">
        <button type="button" class="cleavages-arrow cleavages-arrow-left"
                aria-label="${escapeHtml(ui.cleavagesScrollL)}" tabindex="-1">‹</button>
        <div class="cleavages-track">${cards}</div>
        <button type="button" class="cleavages-arrow cleavages-arrow-right"
                aria-label="${escapeHtml(ui.cleavagesScrollR)}" tabindex="-1">›</button>
      </div>
    </div>`;
}

// Lazy single-instance body-level tooltip. Putting it inside the track
// causes clipping (overflow-x:auto creates a clip context on the y-axis
// too), so we render it as a body child positioned via getBoundingClientRect.
let _cleavageTooltipEl = null;
function _getCleavageTooltipEl() {
  if (_cleavageTooltipEl) return _cleavageTooltipEl;
  const el = document.createElement('div');
  el.className = 'cleavage-tooltip';
  el.setAttribute('role', 'tooltip');
  document.body.appendChild(el);
  _cleavageTooltipEl = el;
  // Hide on outside tap (mobile). A click anywhere inside a cleavage card
  // is treated as "still in interaction" — the click handler will replace
  // the tooltip with that card's content.
  document.addEventListener('pointerdown', (ev) => {
    if (ev.target.closest('.cleavage-card')) return;
    el.classList.remove('show');
  });
  return el;
}
function _showCleavageTooltip(target) {
  const text = target.dataset.tooltip;
  if (!text) return;
  const el = _getCleavageTooltipEl();
  const stance    = target.dataset.tooltipStance || '';
  const stanceKey = target.dataset.tooltipStanceKey || '';
  // Two-line content: question above, stance label below in a coloured pill.
  el.innerHTML = ''; // wipe and rebuild structurally
  const titleDiv = document.createElement('div');
  titleDiv.className = 'cleavage-tooltip-title';
  titleDiv.textContent = text;
  el.appendChild(titleDiv);
  if (stance) {
    const stanceDiv = document.createElement('div');
    stanceDiv.className = 'cleavage-tooltip-stance';
    stanceDiv.dataset.stance = stanceKey;
    stanceDiv.textContent = stance;
    el.appendChild(stanceDiv);
  }
  el.classList.add('show');
  // Default position above the icon, centered.
  const r = target.getBoundingClientRect();
  // First render to measure
  el.style.maxWidth = `${Math.min(280, window.innerWidth - 24)}px`;
  el.style.left = '0px';
  el.style.top  = '0px';
  const tw = el.offsetWidth, th = el.offsetHeight;
  let cx = r.left + r.width / 2;
  let top = r.top - th - 8;
  // Flip below if it'd go off-screen at top
  let placement = 'top';
  if (top < 8) {
    top = r.bottom + 8;
    placement = 'bottom';
  }
  // Clamp horizontally
  let left = cx - tw / 2;
  if (left < 8) left = 8;
  if (left + tw > window.innerWidth - 8) left = window.innerWidth - tw - 8;
  el.style.left = `${left}px`;
  el.style.top  = `${top}px`;
  el.dataset.placement = placement;
  // Position arrow caret to point at the icon
  const arrowOffset = Math.max(8, Math.min(tw - 8, cx - left));
  el.style.setProperty('--arrow-x', `${arrowOffset}px`);
}
function _hideCleavageTooltip() {
  if (_cleavageTooltipEl) _cleavageTooltipEl.classList.remove('show');
}

// Apply transparency-fade + arrow visibility based on scroll position.
// At scroll-start: only right side fades + only right arrow visible.
// After any scroll: both fade and both arrows. At end: only left.
function activateCleavageTracks(root) {
  root.querySelectorAll('.cleavages-track').forEach(track => {
    const wrap = track.parentElement;
    const leftBtn  = wrap?.querySelector('.cleavages-arrow-left');
    const rightBtn = wrap?.querySelector('.cleavages-arrow-right');
    const update = () => {
      const max = track.scrollWidth - track.clientWidth;
      if (max <= 1) {
        track.classList.remove('at-end', 'in-middle');
        track.style.maskImage = 'none';
        track.style.webkitMaskImage = 'none';
        if (leftBtn)  leftBtn.hidden = true;
        if (rightBtn) rightBtn.hidden = true;
        return;
      }
      track.style.maskImage = '';
      track.style.webkitMaskImage = '';
      const left = track.scrollLeft;
      const atStart = left <= 1;
      const atEnd   = left >= max - 1;
      track.classList.toggle('at-end',   atEnd && !atStart);
      track.classList.toggle('in-middle', !atStart && !atEnd);
      if (leftBtn)  leftBtn.hidden  = atStart;
      if (rightBtn) rightBtn.hidden = atEnd;
    };
    track.addEventListener('scroll', update, { passive: true });
    update();
    if ('ResizeObserver' in window) {
      new ResizeObserver(update).observe(track);
    }
    if (leftBtn)  leftBtn.addEventListener('click', () => track.scrollBy({ left: -track.clientWidth * 0.8, behavior: 'smooth' }));
    if (rightBtn) rightBtn.addEventListener('click', () => track.scrollBy({ left:  track.clientWidth * 0.8, behavior: 'smooth' }));

    // Tooltip handlers — fire from anywhere on the card (click, tap, hover,
    // keyboard focus). The tooltip anchors to the icon so its position is
    // consistent regardless of where on the card the user clicked.
    // Always SHOW on click — never toggle. The body-level pointerdown
    // handler installed in _getCleavageTooltipEl handles dismissal when
    // the user clicks outside any card. (Toggling here was racing with
    // the focus event on the inner button, which fired show first and
    // then click toggled it back off.)
    track.querySelectorAll('.cleavage-card').forEach(card => {
      const btn = card.querySelector('.cleavage-icon');
      if (!btn) return;
      card.addEventListener('mouseenter', () => _showCleavageTooltip(btn));
      card.addEventListener('mouseleave', _hideCleavageTooltip);
      card.addEventListener('focusin',    () => _showCleavageTooltip(btn));
      card.addEventListener('focusout',   _hideCleavageTooltip);
      card.addEventListener('click', () => _showCleavageTooltip(btn));
    });
    // Hide tooltip while scrolling the strip.
    track.addEventListener('scroll', _hideCleavageTooltip, { passive: true });
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
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
  const pollHTML    = buildPollHTML(data.partyCode, data.municipalityId);

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
      ${pollHTML}
      <div class="splash-tagline" style="color:${party.textColor}">${tagline}</div>
      ${disclaimerHTML}
      ${data.isPlaceholder ? '' : `<div class="agenda-grid">${cards}</div>`}
      ${sourceHTML}
      ${buildCleavagesHTML(data)}
      ${buildCleavagesSourceHTML(data)}
    </div>`;
}

// Localised muni name for natural-language titles. Icelandic uses the
// dative form after "í"; English/Polish leave the name as-is.
function _muniLocative(m) {
  if (lang === 'is') return MUNI_DATIVE_IS[m.id] || m.name;
  return m.name;
}

// ─── Cleavage compare modal — open/close wiring ────────────
// Build the modal lazily on click, append it to <body> so it escapes
// any stacking contexts created by .party-ribbon / .ribbon-content,
// then remove it on close. Avoids duplicate-overlay issues when the
// user switches parties (each party-splash re-render).
function _openCleavageCompare(partyCode) {
  _closeCleavageCompare(); // wipe any prior instance
  const fakeData = { municipalityId: muni.id, partyCode };
  const html = buildCleavageCompareModalHTML(fakeData);
  if (!html) return;
  const wrap = document.createElement('div');
  wrap.innerHTML = html;
  const ov = wrap.firstElementChild;
  document.body.appendChild(ov);
  requestAnimationFrame(() => {
    ov.classList.add('is-open');
    _bindCompareScrollState(ov);
  });
  document.body.style.overflow = 'hidden';
}

// Edge-fade gradients + sticky-column shadow are toggled via a
// data-scroll-state attribute that reflects whether the user is at the
// start, middle, or end of horizontal scroll. Three states avoid
// flashing transitions when the table fits without scrolling.
function _bindCompareScrollState(ov) {
  const scroller = ov.querySelector('.cleavage-compare-scroll');
  if (!scroller) return;
  const update = () => {
    const max = scroller.scrollWidth - scroller.clientWidth;
    if (max <= 1) { scroller.dataset.scrollState = 'none'; return; }
    if (scroller.scrollLeft <= 1) scroller.dataset.scrollState = 'start';
    else if (scroller.scrollLeft >= max - 1) scroller.dataset.scrollState = 'end';
    else scroller.dataset.scrollState = 'mid';
  };
  scroller.addEventListener('scroll', update, { passive: true });
  // Initial state: defer one frame so layout has settled
  requestAnimationFrame(update);
}
function _closeCleavageCompare() {
  const ov = document.getElementById('cleavage-compare-overlay');
  if (ov) ov.remove();
  document.body.style.overflow = '';
}
document.addEventListener('click', (ev) => {
  const btn = ev.target.closest('[data-cleavages-compare]');
  if (btn) {
    ev.preventDefault();
    _openCleavageCompare(btn.dataset.partyCode);
    return;
  }
  if (ev.target.closest('#cleavage-compare-close')) {
    _closeCleavageCompare();
    return;
  }
  const ov = ev.target.closest('#cleavage-compare-overlay');
  if (ov && ev.target === ov) _closeCleavageCompare();
});
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') _closeCleavageCompare();
});

// Source link rendered below the cleavages carousel — points readers at
// the upstream RÚV kosningapróf so they can verify the party stances.
// The "compare all parties" button sits next to it because that's the
// natural place: same data, same source.
function buildCleavagesSourceHTML(data) {
  if (!CLEAVAGES[data.municipalityId]) return '';
  return `<div class="agenda-source cleavages-source">
    <svg width="11" height="11" viewBox="0 0 12 12" fill="none">
      <path d="M5 2H2a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1V7M8 1h3m0 0v3m0-3L5 7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <a href="https://kosningaprof.ruv.is/" target="_blank" rel="noopener noreferrer">${ui.platformSource('kosningaprof.ruv.is')}</a>
    <button type="button" class="cleavages-compare-btn"
            data-cleavages-compare data-party-code="${escapeHtml(data.partyCode)}"
            aria-label="${escapeHtml(ui.cleavagesCompareCTA)}">
      <svg width="11" height="11" viewBox="0 0 12 12" fill="none" aria-hidden="true">
        <rect x="1.5" y="1.5" width="9" height="9" rx="1" stroke="currentColor" stroke-width="1.2"/>
        <path d="M6 1.5v9M1.5 6h9" stroke="currentColor" stroke-width="1.2"/>
      </svg>
      <span>${escapeHtml(ui.cleavagesCompareCTA)}</span>
    </button>
  </div>`;
}

// Comparison table modal — shows every party in this muni × every
// cleavage topic, as a sticky-first-column / horizontal-scroll table.
// Data source is identical to the carousel: CLEAVAGES[muniId].
function buildCleavageCompareModalHTML(data) {
  const list = CLEAVAGES[data.municipalityId];
  if (!list || !list.length) return '';
  const currentCode = data.partyCode;

  // Party codes that actually appear in this muni's cleavages (intersect
  // with PARTIES so we have colours + names). Order: current party first,
  // then by ballot letter.
  const stanceCodes = new Set();
  list.forEach(t => Object.keys(t.stances).forEach(c => stanceCodes.add(c)));
  const codes = [...stanceCodes]
    .filter(c => PARTIES[c] || muni.partyIds.includes(c))
    .sort();
  if (currentCode && codes.includes(currentCode)) {
    codes.splice(codes.indexOf(currentCode), 1);
    codes.unshift(currentCode);
  }

  const stanceLabels = { A: ui.stanceA, B: ui.stanceB, C: ui.stanceC, D: ui.stanceD };

  // Header row
  const headerCells = codes.map(code => {
    const p = PARTIES[code] || { name: code, color: '#666' };
    const isCurrent = code === currentCode ? ' is-current' : '';
    return `<th class="compare-party-th${isCurrent}" title="${escapeHtml(p.shortName || p.name || code)}">
      <span class="compare-party-pill" style="background:${p.color || '#666'}">${escapeHtml(code)}</span>
    </th>`;
  }).join('');

  // Body rows
  const bodyRows = list.map(topic => {
    const cells = codes.map(code => {
      const stance = topic.stances[code];
      const smiley = stance ? STANCE_SMILEYS[stance] : '—';
      const stanceLabel = stance ? stanceLabels[stance] : ui.cleavagesNoStance;
      const isCurrent = code === currentCode ? ' is-current' : '';
      const stanceKey = stance || '';
      const tooltip = `${topic.title} — ${stanceLabel}`;
      return `<td class="compare-cell${isCurrent}" data-stance="${escapeHtml(stanceKey)}"
                  title="${escapeHtml(tooltip)}">
        <span class="compare-smiley">${smiley}</span>
      </td>`;
    }).join('');
    return `<tr>
      <th class="compare-topic-th" scope="row">
        <span class="compare-topic-title">${escapeHtml(topic.title)}</span>
      </th>${cells}
    </tr>`;
  }).join('');

  return `<div class="cleavage-compare-overlay" id="cleavage-compare-overlay"
                role="dialog" aria-modal="true" aria-labelledby="cleavage-compare-title">
    <div class="cleavage-compare-card">
      <button class="cleavage-compare-close" id="cleavage-compare-close"
              type="button" aria-label="${escapeHtml(ui.cleavagesCompareClose)}">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M3 3L13 13M13 3L3 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
      <div class="cleavage-compare-header">
        <h3 id="cleavage-compare-title">${escapeHtml(ui.cleavagesCompareTitle(_muniLocative(muni)))}</h3>
        <p class="cleavage-compare-sub">${escapeHtml(ui.cleavagesCompareSub)}</p>
      </div>
      <div class="cleavage-compare-scroll-wrap">
        <div class="cleavage-compare-scroll" data-scroll-state="start">
          <table class="cleavage-compare-table">
            <thead><tr><th class="compare-topic-th compare-topic-th--header">${escapeHtml(ui.cleavagesCompareTopicCol)}</th>${headerCells}</tr></thead>
            <tbody>${bodyRows}</tbody>
          </table>
        </div>
        <div class="cleavage-compare-fade cleavage-compare-fade--left" aria-hidden="true"></div>
        <div class="cleavage-compare-fade cleavage-compare-fade--right" aria-hidden="true"></div>
      </div>
      <div class="cleavage-compare-footer">
        <a href="https://kosningaprof.ruv.is/" target="_blank" rel="noopener noreferrer">
          ${escapeHtml(ui.platformSource('kosningaprof.ruv.is'))} ↗
        </a>
      </div>
    </div>
  </div>`;
}

// ─── Candidate Gallery ─────────────────────────────────────

function buildCandidatesHTML(data, party) {
  const partyName = PARTIES[data.partyCode]?.name || data.partyCode;
  // Per-poll seat projection — candidates with ballotOrder <= pollSeats get
  // their own party-coloured frame.
  // Per-card elected frame uses the newest poll (index 0 in the per-muni
  // array). Backwards-compat: if POLLS[muni] is still a single object, use it.
  const _pollEntry = POLLS[data.municipalityId];
  const _newestPoll = Array.isArray(_pollEntry) ? _pollEntry[0] : _pollEntry;
  const pollSeats = _newestPoll?.parties?.[data.partyCode]?.seats || 0;

  const renderCard = c => {
    const fallback = localAvatar(c.name);
    const occupation = trOcc(c.occupation);
    // SEO + a11y: descriptive alt ("<Name> — <Party> í <Muni>") + explicit
    // dimensions to prevent layout shift (Cumulative Layout Shift, a Google
    // Core Web Vitals ranking factor).
    const altText = `${c.name} — ${partyName}, ${muni.name}`;
    const elected = pollSeats > 0 && c.ballotOrder <= pollSeats;
    const cardClass = elected ? 'candidate-card is-elected-poll' : 'candidate-card';
    return `
      <div class="${cardClass}"
           data-candidate-id="${c.id}"
           data-party-code="${data.partyCode}"
           role="button" tabindex="0"
           aria-label="${ui.seeMore} ${c.name}">
        <div class="candidate-photo-wrap">
          <img src="${c.imageUrl}"
               alt="${altText}"
               width="240" height="240"
               loading="lazy" decoding="async"
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
  };

  const legend = pollSeats > 0
    ? `<div class="candidates-elected-legend" style="--party-color:${party.color}">
         <span class="candidates-elected-legend-swatch"></span>
         <span class="candidates-elected-legend-text">${ui.electedFrameLabel}</span>
       </div>`
    : '';

  return `
    <div class="candidates-section" style="--party-color:${party.color}">
      <div class="candidates-section-title">
        <span style="color:${party.color}">${party.name}</span>
        &nbsp;– ${ui.candidates}
      </div>
      ${legend}
      <div class="candidates-grid">${data.candidates.map(renderCard).join('')}</div>
    </div>`;
}

// ─── Share / deep-link helpers ────────────────────────────

/**
 * Build a path-based URL for the given route.
 *   buildRouteURL('S')                       → /<lang>/<muni>/samfylkingin/
 *   buildRouteURL('S', 'Kjartan Atli ...')   → /<lang>/<muni>/samfylkingin/kjartan-atli-.../
 * Lang prefix is read from current URL.
 */
function buildRouteURL(partyCode, candidateName) {
  const r = parseRoute();
  const langPrefix = r.langOverride ? `/${r.langOverride}` : '';
  let path = `${langPrefix}/${muniId}/`;
  if (partyCode) {
    path += partySlug(partyCode) + '/';
    if (candidateName) {
      path += slugify(candidateName) + '/';
    }
  }
  return window.location.origin + path;
}

function partyURL(partyCode) {
  return buildRouteURL(partyCode);
}

function candidateURL(candidateId, partyCode) {
  // Look up candidate name from allCandidates (populated after data load)
  const c = allCandidates[candidateId];
  return buildRouteURL(partyCode, c?.name);
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

let modalNavList = [];
let modalNavIdx  = -1;

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
// Eye position is computed two ways:
//   1. Pre-baked map EYE_POSITIONS (OpenCV face detection, build-time)
//      — covers all locally-hosted candidate images.
//   2. Browser FaceDetector API as runtime fallback for remote images
//      (mostly only available on Android Chromium).
// If neither is available, the CSS default `object-position: center 25%`
// kicks in (sensible for typical headshots).

const faceDetector = ('FaceDetector' in window) ? new FaceDetector({ fastMode: true }) : null;

/** Look up pre-computed entry { eyeY, w, h } for an image URL or null. */
function lookupPrecomputedEntry(imgSrc) {
  const match = imgSrc.match(/images\/candidates\/[^?#]+/);
  if (!match) return null;
  return EYE_POSITIONS[match[0]] || null;
}

/** Position image so eyes land at ~1/3 from top of visible area, given explicit dimensions. */
function applyObjectPosition(img, eyeYFrac, naturalW, naturalH) {
  const containerH = img.parentElement.offsetHeight;
  const containerW = img.parentElement.offsetWidth;
  if (!containerH || !containerW || !naturalH) return;
  const scale = Math.max(containerW / naturalW, containerH / naturalH);
  const renderedH = naturalH * scale;
  const overflow = renderedH - containerH;
  if (overflow <= 0) return; // image not vertically cropped — leave default
  const targetY = containerH * 0.33; // eyes at 1/3 from container top
  const eyeRendered = eyeYFrac * naturalH * scale;
  const P = Math.max(0, Math.min(100, (eyeRendered - targetY) / overflow * 100));
  img.style.objectPosition = `center ${P}%`;
}

/**
 * Position the modal hero photo so the subject's eyes land at ~1/3 from the top.
 * Pass `nextSrc` (the URL we're about to assign) to get a synchronous, flash-free
 * position whenever the image is in the pre-baked map.
 */
async function applySmartCrop(img, nextSrc) {
  // 1. Pre-baked map (sync, no wait) — covers local /images/candidates/*
  const entry = lookupPrecomputedEntry(nextSrc || img.src);
  if (entry) {
    img.style.transition = ''; // position correct from frame 1, no animation needed
    applyObjectPosition(img, entry.eyeY, entry.w, entry.h);
    return;
  }

  // 2. Remote / unmapped — wait for load, then try browser FaceDetector
  img.style.objectPosition = ''; // CSS default while we figure it out
  if (!img.complete || !img.naturalWidth) {
    await new Promise(resolve => { img.addEventListener('load', resolve, { once: true }); });
  }
  if (!faceDetector) return;
  try {
    const faces = await faceDetector.detect(img);
    if (!faces.length) return;
    const face = faces.reduce((a, b) =>
      b.boundingBox.width * b.boundingBox.height > a.boundingBox.width * a.boundingBox.height ? b : a
    );
    const eyeYPx = face.boundingBox.top + face.boundingBox.height * 0.38;
    img.style.transition = 'object-position 0.35s ease';
    applyObjectPosition(img, eyeYPx / img.naturalHeight, img.naturalWidth, img.naturalHeight);
  } catch {
    // FaceDetector rejected (CORS image, security, etc.) — leave CSS default
  }
}

function openModal(id) {
  const c = allCandidates[id];
  if (!c) return;
  const party = PARTIES[c.partyCode];

  document.getElementById('modal-card').scrollTop = 0;

  // Navigation state for this party list
  modalNavList = Object.values(allCandidates)
    .filter(x => x.partyCode === c.partyCode)
    .sort((a, b) => a.ballotOrder - b.ballotOrder);
  modalNavIdx = modalNavList.findIndex(x => x.id === id);
  const navEl   = document.getElementById('modal-nav');
  const prevBtn = document.getElementById('modal-prev');
  const nextBtn = document.getElementById('modal-next');
  if (modalNavList.length > 1) {
    navEl.style.display = '';
    prevBtn.disabled = modalNavIdx === 0;
    nextBtn.disabled = modalNavIdx === modalNavList.length - 1;
    document.getElementById('modal-nav-pos').textContent =
      `${modalNavIdx + 1} / ${modalNavList.length}`;
  } else {
    navEl.style.display = 'none';
  }

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
  // Apply the precomputed eye-Y crop BEFORE setting src so the new image
  // appears at the correct position immediately — no flash, no transition.
  applySmartCrop(photo, c.imageUrl);
  photo.src = c.imageUrl;
  photo.alt = `${c.name} — ${party?.name || ''}, ${muni.name}`;
  photo.onerror = () => { photo.onerror = null; photo.src = fallback; };

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
  setCandidateMeta(c);  // tell updatePageMeta before pushState fires the hook
  history.pushState({ candidate: id }, '', buildRouteURL(c.partyCode, c.name));

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
  clearCandidateMeta();
  if (updateHistory) {
    // Revert URL to party-level (drop candidate slug); preserves muni + party
    const r = parseRoute();
    history.replaceState(null, '', buildRouteURL(r.partyCode));
  }
}

document.getElementById('modal-close').addEventListener('click', () => closeModal());
overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeModal(); return; }
  if (!overlay.classList.contains('is-open')) return;
  if (e.key === 'ArrowLeft'  && modalNavIdx > 0)
    openModal(modalNavList[modalNavIdx - 1].id);
  if (e.key === 'ArrowRight' && modalNavIdx < modalNavList.length - 1)
    openModal(modalNavList[modalNavIdx + 1].id);
});

document.getElementById('modal-prev').addEventListener('click', () => {
  if (modalNavIdx > 0) openModal(modalNavList[modalNavIdx - 1].id);
});
document.getElementById('modal-next').addEventListener('click', () => {
  if (modalNavIdx < modalNavList.length - 1) openModal(modalNavList[modalNavIdx + 1].id);
});

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

  // On mobile, fix the initial expanded panel height for sparse party lists
  if (window.innerWidth <= 768) {
    const initExpanded = container.querySelector('.party-ribbon.is-expanded');
    applyMobileExpandedHeight(initExpanded);
  }

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

  // Set initial URL to reflect the active party (no history entry).
  // Skip if the active party WASN'T deep-linked — leave the URL clean at the
  // muni level so /gardabaer/ doesn't auto-rewrite to /gardabaer/<random>/.
  if (isDeepLink) {
    history.replaceState(null, '', buildRouteURL(activeParty));
  }

  // Open candidate from deep link (after DOM is ready). Either:
  //   - legacy ?candidate=<id>          → direct id lookup
  //   - new path /<muni>/<party>/<slug>/ → resolve slug → id by name match
  let toOpen = paramCandidate;
  if (!toOpen && route.candidateSlug) {
    const matched = Object.values(allCandidates).find(c =>
      slugify(c.name) === route.candidateSlug
    );
    if (matched) toOpen = matched.id;
  }
  if (toOpen && allCandidates[toOpen]) {
    requestAnimationFrame(() => openModal(toOpen));
  }

} // end else (not isUnbound)
