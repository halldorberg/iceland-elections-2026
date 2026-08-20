# coding: utf-8
"""Pair JA/NEI campaign videos by argument and generate the vertical feed page
at esbkosningar2026/videos/. Pairs via DATA.counters (arg <-> counter-args)."""
import io, json, subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent

DATA = json.loads(subprocess.run(
    ['node', '-e', "const fs=require('fs');const src=fs.readFileSync('js/esb-data.js','utf8');const DATA=new Function(src+';return DATA;')();process.stdout.write(JSON.stringify({counters:DATA.counters,args:DATA.arguments}))"],
    capture_output=True, text=True, encoding='utf-8', cwd=str(ROOT)).stdout)
COUNTERS = DATA['counters']
ARG_TITLE = {}
ARG_ICON = {}
for side in ('ja', 'nei'):
    for a in DATA['args'][side]:
        ARG_TITLE[a['key']] = a['title'].replace('­', '')
        ARG_ICON[a['key']] = a['icon']

ja = json.load(io.open(ROOT / 'scripts' / 'video_classify_ja.json', encoding='utf-8'))['videos']
nei = json.load(io.open(ROOT / 'scripts' / 'video_classify_nei.json', encoding='utf-8'))['videos']
media = {p.stem for p in (ROOT / 'esb-videos' / 'media').glob('*.mp4')}
ja = [v for v in ja if v['id'] in media and not v.get('flag')]
nei = [v for v in nei if v['id'] in media and not v.get('flag')]

# Pair scoring: ja arg A pairs with nei video whose args intersect COUNTERS.ja[A]
# (the nei args that counter A), and symmetrically nei arg B counters via COUNTERS.nei[B].
def pair_score(jv, nv):
    s = 0
    for a in jv.get('args', []):
        cs = set(COUNTERS.get('ja', {}).get(a, []))
        s += 2 * len(cs & set(nv.get('args', [])))
    for b in nv.get('args', []):
        cs = set(COUNTERS.get('nei', {}).get(b, []))
        s += 2 * len(cs & set(jv.get('args', [])))
    return s

ja_sorted = sorted([v for v in ja if v.get('args')], key=lambda v: -(v.get('views') or 0))
nei_pool = [v for v in nei if v.get('args')]
pairs, used = [], set()
for jv in ja_sorted:
    best, bs = None, 0
    for nv in nei_pool:
        if nv['id'] in used:
            continue
        sc = pair_score(jv, nv)
        if sc > bs:
            best, bs = nv, sc
    if best:
        used.add(best['id'])
        shared_ja = jv['args'][0]
        shared_nei = best['args'][0]
        pairs.append({'ja': jv, 'nei': best, 'argJa': shared_ja, 'argNei': shared_nei})

leftover = [v for v in ja_sorted if all(p['ja']['id'] != v['id'] for p in pairs)] + \
           [v for v in nei_pool if v['id'] not in used] + \
           [v for v in ja + nei if not v.get('args')]

def slide(v, arg):
    t = ARG_TITLE.get(arg, '')
    icon = ARG_ICON.get(arg, '')
    return {'id': v['id'], 'side': v['side'], 'title': v['title'], 'summary': v['summary'],
            'account': v['account'], 'url': v['url'], 'views': v.get('views'),
            'argKey': arg, 'argTitle': t, 'argIcon': icon}

feed = []
for p in pairs:
    feed.append(slide(p['ja'], p['argJa']))
    feed.append(slide(p['nei'], p['argNei']))
for v in leftover:
    feed.append(slide(v, (v.get('args') or [''])[0]))

with io.open(ROOT / 'js' / 'esb-videos.js', 'w', encoding='utf-8', newline='') as f:
    f.write('const VIDEOFEED = ' + json.dumps(feed, ensure_ascii=False, indent=0) + ';\n')

ACC = {'aframisland': 'Áfram Ísland', 'sja': 'SJÁ – Já til að sjá', 'evropuhreyfingin': 'Evrópuhreyfingin', 'heimssyn': 'Heimssýn'}
ACC_URL = {'aframisland': 'https://www.tiktok.com/@afram.island', 'sja': 'https://www.tiktok.com/@jatiladsja',
           'evropuhreyfingin': 'https://www.tiktok.com/@evropuhreyfingin', 'heimssyn': 'https://www.tiktok.com/@heimssyn'}

html = """<!DOCTYPE html>
<html lang="is">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Myndbandaveislan — JÁ og NEI hlið við hlið · ESB 2026</title>
  <meta name="description" content="Stutt myndbönd JÁ- og NEI-hreyfinganna fyrir þjóðaratkvæðagreiðsluna 29. ágúst 2026 — pöruð saman: rök og mótsvar, eitt af hvoru í einu." />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="canonical" href="https://lydraedisveislan.is/esbkosningar2026/videos/" />
  <meta property="og:title" content="Myndbandaveislan — rök og mótsvar á víxl" />
  <meta property="og:image" content="https://lydraedisveislan.is/images/og-esb.png" />
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-KVRHXCHYLV"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-KVRHXCHYLV');</script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { height: 100%; background: #0a0e1a; font-family: 'Inter', system-ui, sans-serif; }
    .feed { height: 100dvh; overflow-y: auto; scroll-snap-type: y mandatory; }
    .slide {
      position: relative; height: 100dvh; scroll-snap-align: start;
      display: flex; align-items: center; justify-content: center; overflow: hidden;
    }
    .slide video { height: 100%; max-width: 100vw; object-fit: contain; }
    .badge {
      position: absolute; top: max(14px, env(safe-area-inset-top)); left: 14px; z-index: 5;
      padding: 6px 16px; border-radius: 999px; color: #fff; font-weight: 800; font-size: 0.95rem;
      box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    }
    .badge.ja { background: #1e88e5; }
    .badge.nei { background: #e53935; }
    .counter-tag {
      position: absolute; top: max(14px, env(safe-area-inset-top)); left: 90px; z-index: 5;
      padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,0.92); color: #0f1923;
      font-weight: 600; font-size: 0.72rem;
    }
    .back {
      position: absolute; top: max(14px, env(safe-area-inset-top)); right: 14px; z-index: 5;
      padding: 6px 14px; border-radius: 999px; background: rgba(0,0,0,0.55); color: #fff;
      text-decoration: none; font-size: 0.8rem; font-weight: 600;
    }
    .meta {
      position: absolute; left: 0; right: 0; bottom: 0; z-index: 4;
      padding: 18px 16px calc(18px + env(safe-area-inset-bottom));
      background: linear-gradient(to top, rgba(0,0,0,0.75), transparent);
      color: #fff;
    }
    .meta .arg { font-size: 0.74rem; opacity: 0.95; margin-bottom: 5px; font-weight: 600; }
    .meta h2 { font-size: 1.05rem; margin-bottom: 4px; }
    .meta p { font-size: 0.8rem; opacity: 0.85; line-height: 1.4; max-width: 640px; }
    .meta .credit { margin-top: 7px; font-size: 0.72rem; opacity: 0.75; }
    .meta .credit a { color: #9ecbff; text-decoration: none; }
    .mute-hint {
      position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); z-index: 6;
      background: rgba(0,0,0,0.55); color: #fff; padding: 10px 20px; border-radius: 999px;
      font-size: 0.85rem; pointer-events: none; opacity: 0; transition: opacity 0.3s;
    }
    .slide.show-hint .mute-hint { opacity: 1; }
    .progress {
      position: absolute; left: 0; right: 0; bottom: 0; z-index: 7;
      height: 18px; display: flex; align-items: flex-end;
      touch-action: none; cursor: pointer;
    }
    .progress .track {
      width: 100%; height: 2px; background: rgba(255,255,255,0.25);
      transition: height 0.15s;
    }
    .progress .fill { height: 100%; width: 0%; background: rgba(255,255,255,0.85); }
    .progress.active .track { height: 10px; }
    .progress.active .fill { background: #fff; }
    .progress .time {
      position: absolute; bottom: 22px; left: 50%; transform: translateX(-50%);
      background: rgba(0,0,0,0.65); color: #fff; padding: 3px 10px; border-radius: 8px;
      font-size: 0.75rem; opacity: 0; transition: opacity 0.15s; pointer-events: none;
    }
    .progress.active .time { opacity: 1; }
  </style>
</head>
<body>
  <div class="feed" id="feed"></div>
  <script src="/js/esb-videos.js?v=1"></script>
  <script>
    const ACC = __ACC__;
    const ACCURL = __ACCURL__;
    const feedEl = document.getElementById('feed');
    const esc = s => (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    feedEl.innerHTML = VIDEOFEED.map((v, i) => `
      <div class="slide" data-i="${i}">
        <video src="https://d2phchlsyto3ho.cloudfront.net/media/${v.id}.mp4" loop muted playsinline preload="${i < 3 ? 'auto' : 'none'}"></video>
        <div class="badge ${v.side}">${v.side === 'ja' ? 'JÁ' : 'NEI'}</div>
        ${v.argTitle ? `<div class="counter-tag">${v.argIcon} ${esc(v.argTitle)}</div>` : ''}
        <a class="back" href="/">← lýðræðisveislan.is</a>
        <div class="meta">
          ${v.argTitle ? `<div class="arg">${v.argIcon} ${esc(v.argTitle)}</div>` : ''}
          <h2>${esc(v.title)}</h2>
          <p>${esc(v.summary)}</p>
          <div class="credit">Myndband: <a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(ACC[v.account] || v.account)} á TikTok →</a></div>
        </div>
        <div class="mute-hint">🔊 Smelltu til að heyra hljóð</div>
        <div class="progress"><div class="track"><div class="fill"></div></div><div class="time"></div></div>
      </div>`).join('');

    // Thin TikTok-style progress line: always 2px, grows and scrubs on touch/drag
    document.querySelectorAll('.slide').forEach(slide => {
      const video = slide.querySelector('video');
      const prog = slide.querySelector('.progress');
      const fill = slide.querySelector('.fill');
      const time = slide.querySelector('.time');
      const fmt = s => Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0');
      video.addEventListener('timeupdate', () => {
        if (video.duration) fill.style.width = (100 * video.currentTime / video.duration) + '%';
      });
      let scrubbing = false;
      const seekTo = x => {
        const r = prog.getBoundingClientRect();
        const frac = Math.min(1, Math.max(0, (x - r.left) / r.width));
        if (video.duration) {
          video.currentTime = frac * video.duration;
          fill.style.width = (100 * frac) + '%';
          time.textContent = fmt(frac * video.duration) + ' / ' + fmt(video.duration);
        }
      };
      prog.addEventListener('pointerdown', e => {
        e.stopPropagation(); scrubbing = true;
        prog.classList.add('active'); prog.setPointerCapture(e.pointerId); seekTo(e.clientX);
      });
      prog.addEventListener('pointermove', e => { if (scrubbing) seekTo(e.clientX); });
      prog.addEventListener('pointerup', e => {
        scrubbing = false; prog.classList.remove('active'); e.stopPropagation();
      });
      prog.addEventListener('click', e => e.stopPropagation());
    });

    let sound = false;
    const vids = Array.from(document.querySelectorAll('.slide video'));
    const io = new IntersectionObserver(es => {
      es.forEach(e => {
        const v = e.target.querySelector('video');
        if (e.isIntersecting) {
          v.preload = 'auto';
          v.muted = !sound;
          v.play().catch(() => {});
          if (!sound) { e.target.classList.add('show-hint'); setTimeout(() => e.target.classList.remove('show-hint'), 2500); }
          // Remember position (by video id, survives feed reordering)
          const i = +e.target.dataset.i;
          if (VIDEOFEED[i]) localStorage.setItem('videofeed-pos', VIDEOFEED[i].id);
        } else { v.pause(); v.currentTime = 0; }
      });
    }, { threshold: 0.6 });

    // Resume where the visitor left off
    const savedId = localStorage.getItem('videofeed-pos');
    if (savedId) {
      const idx = VIDEOFEED.findIndex(v => v.id === savedId);
      if (idx > 0) document.querySelector(`.slide[data-i="${idx}"]`).scrollIntoView({ behavior: 'instant', block: 'start' });
    }
    document.querySelectorAll('.slide').forEach(s => io.observe(s));
    document.addEventListener('click', e => {
      if (e.target.closest('a')) return;
      sound = !sound;
      vids.forEach(v => v.muted = !sound);
    });
  </script>
</body>
</html>
"""
html = html.replace('__ACC__', json.dumps(ACC, ensure_ascii=False)).replace('__ACCURL__', json.dumps(ACC_URL, ensure_ascii=False))
out = ROOT / 'esbkosningar2026' / 'videos'
out.mkdir(parents=True, exist_ok=True)
with io.open(out / 'index.html', 'w', encoding='utf-8', newline='') as f:
    f.write(html)
print(f'{len(pairs)} pairs + {len(leftover)} extras = {len(feed)} slides; feed page written')
