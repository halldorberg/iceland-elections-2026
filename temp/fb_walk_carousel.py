"""Walk lightbox carousel of an N-listinn post in Edge, downloading each
1080x1080 image. Uses ArrowRight to advance.

Usage: python fb_walk_carousel.py <tab-id> <tag> <expected-image-count>
"""
import subprocess, json, os, sys, time, urllib.request, re

EDGE_CDP = r'F:\Claude Projects\iceland-elections\scripts\edge_cdp.py'
OUT = r'F:\Claude Projects\iceland-elections\temp\nlist_fb'
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/147.0.0.0'

def cdp(*args):
    r = subprocess.run(['python', EDGE_CDP, *args], capture_output=True, text=True, encoding='utf-8')
    return r.stdout.strip()

def evalj(tab, expr):
    return cdp('eval', tab, expr)

tab = sys.argv[1]
tag = sys.argv[2]
n = int(sys.argv[3])

# Click first carousel image
res = evalj(tab, "(() => { const t = Array.from(document.querySelectorAll('img')).find(i => /t39\\.30808-6\\/\\d{8,}_\\d{8,}/.test(i.src) && i.naturalWidth >= 500); if (!t) return 'no target'; const a = t.closest('a'); (a||t).click(); return 'ok'; })()")
print(' click first:', res)
time.sleep(3)

seen = set()
for step in range(n + 2):
    out = evalj(tab, "JSON.stringify(Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth >= 800 && /t39\\.30808-6\\/\\d{8,}_\\d{8,}/.test(i.src)).map(i => ({w:i.naturalWidth,h:i.naturalHeight,src:i.src})))")
    try:
        imgs = json.loads(out)
    except Exception:
        print(' parse fail:', out[:160])
        imgs = []
    # pick the largest by area not yet seen
    fresh = [im for im in imgs if im['src'] not in seen]
    fresh.sort(key=lambda im: im['w']*im['h'], reverse=True)
    if not fresh:
        print(f' step {step}: no fresh image')
    else:
        im = fresh[0]
        seen.add(im['src'])
        m = re.search(r'/(\d{8,}_\d{8,})_', im['src'])
        fbid = m.group(1) if m else f'unk{step}'
        path = os.path.join(OUT, f'{tag}_full_{step:02d}_{fbid[:20]}_{im["w"]}x{im["h"]}.jpg')
        try:
            req = urllib.request.Request(im['src'], headers={'User-Agent': ua})
            data = urllib.request.urlopen(req, timeout=30).read()
            open(path, 'wb').write(data)
            print(f' step {step}: {im["w"]}x{im["h"]} -> {os.path.basename(path)} ({len(data):,} B)')
        except Exception as e:
            print(' dl err:', e)
    if len(seen) >= n:
        break
    # press ArrowRight on document
    evalj(tab, "(() => { document.body.dispatchEvent(new KeyboardEvent('keydown', {key:'ArrowRight', code:'ArrowRight', keyCode:39, which:39, bubbles:true})); document.body.dispatchEvent(new KeyboardEvent('keyup', {key:'ArrowRight', code:'ArrowRight', keyCode:39, which:39, bubbles:true})); return 'k'; })()")
    time.sleep(2.5)

# close lightbox
evalj(tab, "document.body.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', code:'Escape', keyCode:27, which:27, bubbles:true}))")
print(f' total downloaded: {len(seen)}')
