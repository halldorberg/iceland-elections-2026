/* Generate static argument pages at esbkosningar2026/<key>/index.html */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const dataSrc = fs.readFileSync(path.join(ROOT, 'js', 'esb-data.js'), 'utf8');
const DATA = new Function(dataSrc + '; return DATA;')();
const detailsJa = JSON.parse(fs.readFileSync(path.join(__dirname, 'details_ja.json'), 'utf8'));
const detailsNei = JSON.parse(fs.readFileSync(path.join(__dirname, 'details_nei.json'), 'utf8'));

// Direct mótrök researched from the literature (motrok_*.json); key → [{title,text,source,author,url}]
const MOTROK = {};
for (const f of ['motrok_ja1.json', 'motrok_ja2.json', 'motrok_nei1.json', 'motrok_nei2.json', 'motrok_new.json', 'motrok_new2.json']) {
  const p = path.join(__dirname, f);
  if (fs.existsSync(p)) Object.assign(MOTROK, JSON.parse(fs.readFileSync(p, 'utf8')));
}

const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

// Translations: flat key→string maps produced by esb_translate.py
const TR = {};
for (const lang of ['en', 'pl']) {
  const p = path.join(ROOT, 'translations', `esb_${lang}.json`);
  if (fs.existsSync(p)) TR[lang] = JSON.parse(fs.readFileSync(p, 'utf8'));
}
const tr = (lang, key, fallback) => lang === 'is' ? fallback : ((TR[lang] || {})[key] || fallback);
DATA.articles.forEach((a, i) => { a._i = i; });

const UI = {
  is: {
    sideLabel: s => s === 'ja' ? 'Rök JÁ-hliðar' : 'Rök NEI-hliðar',
    motrokHead: o => `Mótrök — ${o}-hliðin svarar þessum rökum beint`,
    motrokHeadOld: o => `Mótrök — ${o}-hliðin svarar`,
    motrokMore: 'Nánar um þessi mótrök →',
    articlesHead: 'Greinar og umræða um þessi rök',
    backHome: '← Á forsíðu',
    eyebrow: 'Þjóðaratkvæðagreiðsla um ESB 29. ágúst 2026',
    election: 'ESB-kosningin 2026',
    disclaimer: side => `Þessi síða dregur saman málflutning ${side === 'ja' ? 'JÁ' : 'NEI'}-hliðarinnar eins og hann birtist í greinum og umræðu; efnið er samantekt á afstöðu talsmanna, ekki staðreyndayfirlýsing.`,
    ja: 'JÁ', nei: 'NEI',
    infoTitle: 'Fyrirvari',
    infoText: 'Efnið er tekið saman með aðstoð gervigreindar úr opinberum heimildum á netinu. Við getum ekki ábyrgst fulla nákvæmni og mælum með að staðfesta mikilvægar upplýsingar í frumheimildum.',
  },
  en: {
    sideLabel: s => s === 'ja' ? 'YES-side arguments' : 'NO-side arguments',
    motrokHead: o => `Counter-arguments — the ${o} side responds directly`,
    motrokHeadOld: o => `Counter-arguments — the ${o} side responds`,
    motrokMore: 'More about this counter-argument →',
    articlesHead: 'Articles and debate on this argument',
    backHome: '← Home',
    eyebrow: 'EU referendum · 29 August 2026',
    election: 'The 2026 EU referendum',
    disclaimer: side => `This page summarises the ${side === 'ja' ? 'YES' : 'NO'} side's case as it appears in articles and public debate; it is a summary of advocates' positions, not a statement of fact.`,
    ja: 'YES', nei: 'NO',
    infoTitle: 'Disclaimer',
    infoText: 'Content is compiled with AI assistance from public online sources. We cannot guarantee full accuracy and recommend verifying important information in the original sources.',
  },
  pl: {
    sideLabel: s => s === 'ja' ? 'Argumenty strony TAK' : 'Argumenty strony NIE',
    motrokHead: o => `Kontrargumenty — strona ${o} odpowiada bezpośrednio`,
    motrokHeadOld: o => `Kontrargumenty — strona ${o} odpowiada`,
    motrokMore: 'Więcej o tym kontrargumencie →',
    articlesHead: 'Artykuły i debata na ten temat',
    backHome: '← Strona główna',
    eyebrow: 'Referendum ws. UE · 29 sierpnia 2026',
    election: 'Referendum UE 2026',
    disclaimer: side => `Ta strona podsumowuje argumentację strony ${side === 'ja' ? 'TAK' : 'NIE'} tak, jak pojawia się w artykułach i debacie publicznej; jest to podsumowanie stanowisk, a nie stwierdzenie faktów.`,
    ja: 'TAK', nei: 'NIE',
    infoTitle: 'Zastrzeżenie',
    infoText: 'Treści są zestawiane z pomocą AI ze źródeł publicznie dostępnych w internecie. Nie możemy zagwarantować pełnej dokładności i zalecamy weryfikację ważnych informacji w źródłach.',
  },
};

const SIDE = {
  ja:  { label: 'Rök JÁ-hliðar',  color: '#1e88e5', bg: 'rgba(30,136,229,0.08)',  border: 'rgba(30,136,229,0.30)',  other: 'nei', otherLabel: 'Mótrök NEI-hliðar', details: detailsJa },
  nei: { label: 'Rök NEI-hliðar', color: '#e53935', bg: 'rgba(229,57,53,0.08)',   border: 'rgba(229,57,53,0.30)',   other: 'ja',  otherLabel: 'Mótrök JÁ-hliðar',  details: detailsNei },
};

// Info (ℹ) disclaimer widget — bottom-left, minimizes to a badge after 5s
function infoWidget(U) {
  return `<style>
    .dw { position: fixed; bottom: 20px; left: 20px; z-index: 960; display: flex; flex-direction: column; align-items: flex-start; pointer-events: none; }
    .dw-card {
      pointer-events: auto; width: 300px; max-width: calc(100vw - 40px);
      background: rgba(255,255,255,0.97); border: 1px solid rgba(0,0,0,0.12);
      border-radius: 14px; padding: 14px 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.18);
      transition: opacity 0.2s, transform 0.2s; transform-origin: bottom left;
    }
    .dw-card.hid { opacity: 0; pointer-events: none; transform: scale(0.92) translateY(6px); visibility: hidden; }
    .dw-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-weight: 700; font-size: 0.9rem; color: #0f1923; }
    .dw-min { margin-left: auto; background: none; border: none; cursor: pointer; color: #64748b; font-size: 1rem; }
    .dw-text { font-size: 0.78rem; color: #4a5568; line-height: 1.5; }
    .dw-badge {
      pointer-events: auto; display: none; width: 34px; height: 34px; border-radius: 50%;
      background: rgba(255,255,255,0.95); border: 1px solid rgba(0,0,0,0.15);
      color: #1a4fa8; cursor: pointer; align-items: center; justify-content: center; font-size: 0.9rem;
    }
    .dw-badge.vis { display: flex; }
    .dw-badge:hover { background: rgba(26,86,219,0.12); }
    @media (max-width: 1150px) { .dw { bottom: 30px; left: 10px; } }
  </style>
  <div class="dw">
    <div class="dw-card" id="dw-card">
      <div class="dw-head">ℹ️ ${esc(U.infoTitle)}<button class="dw-min" id="dw-min" aria-label="Loka">▾</button></div>
      <div class="dw-text">${esc(U.infoText)}</div>
    </div>
    <button class="dw-badge" id="dw-badge" aria-label="${esc(U.infoTitle)}">ℹ</button>
  </div>
  <script>
    (function () {
      var card = document.getElementById('dw-card'), badge = document.getElementById('dw-badge');
      function min() { card.classList.add('hid'); badge.classList.add('vis'); localStorage.setItem('disclaimer-min', '1'); }
      function exp() { card.classList.remove('hid'); badge.classList.remove('vis'); localStorage.removeItem('disclaimer-min'); }
      if (localStorage.getItem('disclaimer-min') === '1') min(); else setTimeout(min, 5000);
      document.getElementById('dw-min').addEventListener('click', min);
      badge.addEventListener('click', exp);
    })();
  </script>`;
}

function articleCard(art, sideColor, lang) {
  lang = lang || 'is';
  const eng = art.engagement ? ` · ${esc(art.engagement)}` : '';
  return `<div class="art-card" style="border-left:4px solid ${sideColor}">
    <div class="art-meta"><span class="src">${esc(art.source)}</span>${art.author ? '<span>' + esc(art.author) + '</span>' : ''}${art.date ? '<span>' + esc(art.date) + '</span>' : ''}${eng}</div>
    <h3><a href="${esc(art.url)}" target="_blank" rel="noopener">${esc(tr(lang, `art.${art._i}.title`, art.title))}</a></h3>
    <p>${esc(tr(lang, `art.${art._i}.summary`, art.summary))}</p>
  </div>`;
}

function buildPage(side, arg, lang) {
  lang = lang || 'is';
  const U = UI[lang];
  const prefix = lang === 'is' ? '' : `/${lang}`;
  const S = SIDE[side];
  const O = SIDE[S.other];
  const otherIdx = {};
  DATA.arguments[S.other].forEach(a => otherIdx[a.key] = a);
  const counterKeys = ((DATA.counters || {})[side] || {})[arg.key] || [];
  const counters = counterKeys.map(k => otherIdx[k]).filter(Boolean);
  const articles = DATA.articles
    .filter(a => a.side === side && (a.args || []).includes(arg.key))
    .sort((a, b) => (b.impact || 0) - (a.impact || 0) || (b.date || '').localeCompare(a.date || ''));
  const argTitle = tr(lang, `arg.${arg.key}.title`, arg.title);
  const argText = tr(lang, `arg.${arg.key}.text`, arg.text);
  const paras = (S.details[arg.key] || [arg.text])
    .map((p, i) => `<p>${esc(tr(lang, `detail.${arg.key}.${i}`, p))}</p>`).join('\n      ');
  const otherName = U[S.other];

  const direct = MOTROK[arg.key] || [];
  const countersHtml = direct.length ? `
    <section class="counters-section">
      <h2 class="section-head" style="color:${O.color}">${esc(U.motrokHead(otherName))}</h2>
      ${direct.map((c, i) => `<div class="counter-card" style="border-left:4px solid ${O.color}">
        <div class="counter-head"><h3>${esc(tr(lang, `motrok.${arg.key}.${i}.title`, c.title))}</h3></div>
        <p>${esc(tr(lang, `motrok.${arg.key}.${i}.text`, c.text))}</p>
        <div class="counter-src">${c.url ? `<a href="${esc(c.url)}" target="_blank" rel="noopener" style="color:${O.color}">` : ''}${esc(c.source || '')}${c.author ? ' · ' + esc(c.author) : ''}${c.url ? ' →</a>' : ''}</div>
      </div>`).join('\n      ')}
    </section>` : counters.length ? `
    <section class="counters-section">
      <h2 class="section-head" style="color:${O.color}">${esc(U.motrokHeadOld(otherName))}</h2>
      ${counters.map(c => `<div class="counter-card" style="border-left:4px solid ${O.color}">
        <div class="counter-head"><span class="icon">${c.icon}</span><h3>${esc(tr(lang, `arg.${c.key}.title`, c.title))}</h3></div>
        <p>${esc(tr(lang, `arg.${c.key}.text`, c.text))}</p>
        <a class="more-link" style="color:${O.color}" href="${prefix}/esbkosningar2026/${c.key}/">${esc(U.motrokMore)}</a>
      </div>`).join('\n      ')}
    </section>` : '';

  const articlesHtml = articles.length ? `
    <section class="articles-section">
      <h2 class="section-head">${esc(U.articlesHead)} <span class="count-badge">${articles.length}</span></h2>
      ${articles.map(a => articleCard(a, S.color, lang)).join('\n      ')}
    </section>` : '';

  const title = `${argTitle} — ${U.sideLabel(side)} · ${U.election}`;
  const desc = argText.substring(0, 155);

  return `<!DOCTYPE html>
<html lang="${lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(desc)}" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="canonical" href="https://lydraedisveislan.is${prefix}/esbkosningar2026/${arg.key}/" />
  <link rel="alternate" hreflang="is" href="https://lydraedisveislan.is/esbkosningar2026/${arg.key}/" />
  <link rel="alternate" hreflang="en" href="https://lydraedisveislan.is/en/esbkosningar2026/${arg.key}/" />
  <link rel="alternate" hreflang="pl" href="https://lydraedisveislan.is/pl/esbkosningar2026/${arg.key}/" />
  <link rel="alternate" hreflang="x-default" href="https://lydraedisveislan.is/esbkosningar2026/${arg.key}/" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="Lýðræðisveislan" />
  <meta property="og:url" content="https://lydraedisveislan.is${prefix}/esbkosningar2026/${arg.key}/" />
  <meta property="og:title" content="${esc(title)}" />
  <meta property="og:description" content="${esc(desc)}" />
  <meta property="og:image" content="https://lydraedisveislan.is/images/og-esb.png" />
  <meta property="og:locale" content="is_IS" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="https://lydraedisveislan.is/images/og-esb.png" />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": ${JSON.stringify(argTitle)},
    "description": ${JSON.stringify(desc)},
    "inLanguage": "${lang}",
    "url": "https://lydraedisveislan.is${prefix}/esbkosningar2026/${arg.key}/",
    "isPartOf": { "@type": "WebSite", "name": "Lýðræðisveislan", "url": "https://lydraedisveislan.is/" }
  }
  </script>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-KVRHXCHYLV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-KVRHXCHYLV');
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      color: #0f1923;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.93) 0%, rgba(245,249,255,0.91) 100%),
        url('/images/bg-hero2.jpg') center/cover no-repeat fixed;
      min-height: 100vh;
    }
    a { color: inherit; }
    .site-header {
      position: sticky; top: 0; z-index: 100;
      display: flex; align-items: center; gap: 12px;
      padding: 14px 24px;
      background: rgba(255,255,255,0.95);
      border-bottom: 1px solid rgba(0,0,0,0.07);
      box-shadow: 0 1px 10px rgba(0,0,0,0.06);
      backdrop-filter: blur(12px);
    }
    .back-link {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 0.82rem; font-weight: 600; color: #1a4fa8;
      text-decoration: none; padding: 6px 12px;
      background: rgba(26,86,219,0.07);
      border: 1px solid rgba(26,86,219,0.2); border-radius: 999px;
      white-space: nowrap;
    }
    .back-link:hover { background: rgba(26,86,219,0.14); }
    .site-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1rem; }
    .site-title a { text-decoration: none; }
    main { max-width: 780px; margin: 0 auto; padding: 32px 16px 60px; }
    .side-eyebrow {
      display: inline-block; padding: 5px 14px;
      border-radius: 999px; font-size: 0.72rem; font-weight: 700;
      letter-spacing: 0.08em; text-transform: uppercase;
      background: ${S.bg}; border: 1px solid ${S.border}; color: ${S.color};
      margin-bottom: 14px;
    }
    h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: clamp(1.5rem, 4vw, 2.2rem);
      line-height: 1.2; margin-bottom: 18px;
    }
    h1 .icon { margin-right: 10px; }
    .lead {
      font-size: 1.02rem; line-height: 1.6; color: #334155;
      border-left: 4px solid ${S.color};
      background: #fff; border-radius: 0 10px 10px 0;
      padding: 14px 18px; margin-bottom: 26px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.07);
    }
    .detail p { font-size: 0.95rem; line-height: 1.7; color: #1e293b; margin-bottom: 14px; }
    .section-head {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 1.15rem; margin: 36px 0 16px;
    }
    .count-badge {
      font-size: 0.75rem; background: #eef2fa; color: #4a5568;
      border-radius: 12px; padding: 2px 10px; vertical-align: middle;
    }
    .counter-card, .art-card {
      background: #fff; border-radius: 10px;
      padding: 14px 16px; margin-bottom: 12px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.07);
      overflow-wrap: anywhere;
    }
    .counter-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    .counter-head h3 { font-size: 1rem; }
    .counter-card p { font-size: 0.88rem; color: #4a5568; line-height: 1.55; margin-bottom: 8px; }
    .more-link { font-size: 0.8rem; font-weight: 600; text-decoration: none; }
    .more-link:hover { text-decoration: underline; }
    .counter-src { font-size: 0.74rem; color: #64748b; }
    .counter-src a { font-weight: 600; text-decoration: none; }
    .counter-src a:hover { text-decoration: underline; }
    .art-meta { font-size: 0.76rem; color: #64748b; margin-bottom: 5px; display: flex; gap: 8px; flex-wrap: wrap; }
    .art-meta .src { font-weight: 600; color: #0f1923; }
    .art-card h3 { font-size: 0.98rem; line-height: 1.35; margin-bottom: 5px; }
    .art-card h3 a { text-decoration: none; }
    .art-card h3 a:hover { text-decoration: underline; }
    .art-card p { font-size: 0.86rem; color: #4a5568; line-height: 1.5; }
    .disclaimer {
      margin-top: 40px; padding: 14px 16px;
      background: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.07);
      border-radius: 10px; font-size: 0.76rem; color: #64748b; line-height: 1.5;
    }
  </style>
</head>
<body>
  <header class="site-header">
    <a class="back-link" href="${prefix}/">${esc(U.backHome)}</a>
    <div class="site-title"><a href="${prefix}/">Lýðræðisveislan</a></div>
  </header>
  <main>
    <div class="side-eyebrow">${U.sideLabel(side)} · ${esc(U.eyebrow)}</div>
    <h1><span class="icon">${arg.icon}</span>${esc(argTitle)}</h1>
    <div class="lead">${esc(argText)}</div>
    <div class="detail">
      ${paras}
    </div>
    ${countersHtml}
    ${articlesHtml}
    <div class="disclaimer">${esc(U.disclaimer(side))} ${esc(tr(lang, 'note', DATA.note || ''))}</div>
  </main>
  ${infoWidget(U)}
  <script src="/js/starfandi-banner.js?v=7" defer></script>
</body>
</html>
`;
}

function buildArticlesPage() {
  const argIdx = { ja: {}, nei: {} };
  DATA.arguments.ja.forEach(a => argIdx.ja[a.key] = a);
  DATA.arguments.nei.forEach(a => argIdx.nei[a.key] = a);

  const col = side => DATA.articles
    .filter(a => a.side === side)
    .sort((a, b) => (b.impact || 0) - (a.impact || 0) || (b.date || '').localeCompare(a.date || ''))
    .map(art => {
      const S = SIDE[side];
      const pills = (art.args || []).map(k => argIdx[side][k]
        ? `<a class="pill" style="background:${S.bg};border-color:${S.border};color:${S.color}" href="/esbkosningar2026/${k}/" title="${esc(argIdx[side][k].title)}">${argIdx[side][k].icon}<span class="lbl">&nbsp;${esc(argIdx[side][k].title)}</span></a>`
        : '').join('');
      const eng = art.engagement ? ` · ${esc(art.engagement)}` : '';
      return `<div class="art-card">
        <div class="art-meta"><span class="src">${esc(art.source)}</span>${art.author ? '<span>' + esc(art.author) + '</span>' : ''}${art.date ? '<span>' + esc(art.date) + '</span>' : ''}${eng}</div>
        <h3><a href="${esc(art.url)}" target="_blank" rel="noopener">${esc(art.title)}</a></h3>
        <p>${esc(art.summary)}</p>
        <div class="pills">${pills}</div>
      </div>`;
    }).join('\n      ');

  const jaCount = DATA.articles.filter(a => a.side === 'ja').length;
  const neiCount = DATA.articles.filter(a => a.side === 'nei').length;

  return `<!DOCTYPE html>
<html lang="is">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Allar greinar og umræða — ESB-kosningin 2026 · Lýðræðisveislan</title>
  <meta name="description" content="Allar ${jaCount + neiCount} greindar greinar og umræða um þjóðaratkvæðagreiðsluna um ESB-aðildarviðræður 29. ágúst 2026 — JÁ- og NEI-hlið hlið við hlið." />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="canonical" href="https://lydraedisveislan.is/esbkosningar2026/greinar/" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Lýðræðisveislan" />
  <meta property="og:url" content="https://lydraedisveislan.is/esbkosningar2026/greinar/" />
  <meta property="og:title" content="Allar greinar og umræða — ESB-kosningin 2026" />
  <meta property="og:image" content="https://lydraedisveislan.is/images/og-esb.png" />
  <meta property="og:locale" content="is_IS" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="https://lydraedisveislan.is/images/og-esb.png" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-KVRHXCHYLV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-KVRHXCHYLV');
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      color: #0f1923;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.93) 0%, rgba(245,249,255,0.91) 100%),
        url('/images/bg-hero2.jpg') center/cover no-repeat fixed;
      min-height: 100vh;
    }
    a { color: inherit; }
    .site-header {
      position: sticky; top: 0; z-index: 100;
      display: flex; align-items: center; gap: 12px;
      padding: 14px 24px;
      background: rgba(255,255,255,0.95);
      border-bottom: 1px solid rgba(0,0,0,0.07);
      box-shadow: 0 1px 10px rgba(0,0,0,0.06);
      backdrop-filter: blur(12px);
    }
    .back-link {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 0.82rem; font-weight: 600; color: #1a4fa8;
      text-decoration: none; padding: 6px 12px;
      background: rgba(26,86,219,0.07);
      border: 1px solid rgba(26,86,219,0.2); border-radius: 999px;
      white-space: nowrap;
    }
    .back-link:hover { background: rgba(26,86,219,0.14); }
    .site-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1rem; }
    .site-title a { text-decoration: none; }
    main { max-width: 1000px; margin: 0 auto; padding: 32px 16px 60px; }
    h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: clamp(1.4rem, 4vw, 2rem);
      text-align: center; margin-bottom: 6px;
    }
    .sub { text-align: center; color: #64748b; font-size: 0.85rem; margin-bottom: 28px; }
    .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
    .col-head {
      position: sticky; top: 66px; z-index: 5;
      text-align: center; font-family: 'Space Grotesk', sans-serif;
      font-size: 1.05rem; font-weight: 700; color: #fff;
      padding: 10px; border-radius: 10px; margin-bottom: 12px;
    }
    .col-head.ja { background: #1e88e5; }
    .col-head.nei { background: #e53935; }
    .art-card {
      background: #fff; border-radius: 10px;
      padding: 13px 15px; margin-bottom: 10px;
      box-shadow: 0 1px 5px rgba(0,0,0,0.07);
      border: 1px solid rgba(0,0,0,0.07);
      overflow-wrap: anywhere;
    }
    .art-meta { font-size: 0.76rem; color: #64748b; margin-bottom: 5px; display: flex; gap: 8px; flex-wrap: wrap; }
    .art-meta .src { font-weight: 600; color: #0f1923; }
    .art-card h3 { font-size: 0.96rem; line-height: 1.35; margin-bottom: 5px; }
    .art-card h3 a { text-decoration: none; }
    .art-card h3 a:hover { text-decoration: underline; }
    .art-card p { font-size: 0.85rem; color: #4a5568; line-height: 1.5; margin-bottom: 8px; }
    .pills { display: flex; flex-wrap: wrap; gap: 5px; }
    .pill {
      font-size: 0.72rem; border-radius: 12px; padding: 2px 9px;
      display: inline-flex; align-items: center; gap: 4px;
      border: 1px solid; text-decoration: none;
    }
    .pill:hover { filter: brightness(0.92); }
    @media (max-width: 700px) {
      .cols { gap: 8px; }
      .art-card p { display: none; }
      .art-card.open p { display: block; }
      .art-card { cursor: pointer; }
      .pill .lbl { display: none; }
      .col-head { font-size: 0.85rem; padding: 8px; }
    }
  </style>
</head>
<body>
  <header class="site-header">
    <a class="back-link" href="/">← Á forsíðu</a>
    <div class="site-title"><a href="/">Lýðræðisveislan</a></div>
  </header>
  <main>
    <h1>Allar greinar og umræða</h1>
    <div class="sub">${jaCount + neiCount} greind atriði um þjóðaratkvæðagreiðsluna 29. ágúst 2026 — ${jaCount} JÁ-megin · ${neiCount} NEI-megin</div>
    <div class="cols">
      <div>
        <div class="col-head ja">JÁ — Halda viðræðum áfram</div>
        ${col('ja')}
      </div>
      <div>
        <div class="col-head nei">NEI — Ekki halda viðræðum áfram</div>
        ${col('nei')}
      </div>
    </div>
  </main>
  <script>
    document.querySelector('.cols').addEventListener('click', e => {
      if (e.target.closest('a')) return;
      const card = e.target.closest('.art-card');
      if (card) card.classList.toggle('open');
    });
  </script>
  ${infoWidget(UI.is)}
  <script src="/js/starfandi-banner.js?v=7" defer></script>
</body>
</html>
`;
}

let count = 0;
const langs = ['is', ...Object.keys(TR)];
for (const lang of langs) {
  const base = lang === 'is' ? ROOT : path.join(ROOT, lang);
  for (const side of ['ja', 'nei']) {
    for (const arg of DATA.arguments[side]) {
      const dir = path.join(base, 'esbkosningar2026', arg.key);
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(path.join(dir, 'index.html'), buildPage(side, arg, lang), 'utf8');
      count++;
    }
  }
}
const greinarDir = path.join(ROOT, 'esbkosningar2026', 'greinar');
fs.mkdirSync(greinarDir, { recursive: true });
fs.writeFileSync(path.join(greinarDir, 'index.html'), buildArticlesPage(), 'utf8');
console.log(`Built ${count} argument pages (${langs.join(', ')}) + greinar page`);
