"""Walk a fliphtml5 viewer's "Next Page" button and download every unique
large image (the platform pages). Run after the tab is already open at the
flipbook URL.

Usage:  python scripts/fliphtml5_extract.py <tab_id_prefix> [--max=20] [--out=...]
"""
import argparse, sys, io, time, urllib.request, hashlib, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edge_cdp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ap = argparse.ArgumentParser()
ap.add_argument('tab')
ap.add_argument('--max', type=int, default=20)
ap.add_argument('--out', default='temp/flipbook')
args = ap.parse_args()

tab = edge_cdp.find_tab(args.tab)
if not tab:
    print(f'tab {args.tab} not found'); sys.exit(1)
ws = edge_cdp.attach(tab)

out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://online.fliphtml5.com/'}
seen = set()
order = 0

def grab_visible():
    global order
    expr = """
        (() => {
            const imgs = [...document.querySelectorAll('img')]
                .filter(i => i.src && /\\/files\\/large\\//.test(i.src) && i.naturalWidth >= 800);
            return JSON.stringify(imgs.map(i => ({src: i.src.split('?')[0], w: i.naturalWidth, h: i.naturalHeight})));
        })()
    """
    raw = edge_cdp.evaluate(ws, expr)
    return json.loads(raw)

def click_next():
    expr = """
        (() => {
            let btn = document.querySelector('[aria-label="Next Page"]')
                  || document.querySelector('.flip_button_right.button')
                  || document.querySelector('.rightBtn');
            if (!btn) return 'no-next';
            btn.click();
            return 'clicked';
        })()
    """
    return edge_cdp.evaluate(ws, expr)

for step in range(args.max):
    visible = grab_visible()
    new_imgs = [img for img in visible if img['src'] not in seen]
    for img in new_imgs:
        seen.add(img['src'])
        try:
            req = urllib.request.Request(img['src'], headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            order += 1
            h = hashlib.sha256(data).hexdigest()[:10]
            out_path = out_dir / f'page_{order:02d}_{h}.webp'
            out_path.write_bytes(data)
            print(f'  step {step:>2}  page {order}  {img["w"]}x{img["h"]}  {len(data)//1024}KB  →  {out_path.name}')
        except Exception as e:
            print(f'  step {step}  download failed: {e}')
    if step >= 2 and not new_imgs:
        # Two consecutive empty steps → end of book
        print(f'  step {step}: no new pages, stopping')
        break
    r = click_next()
    if r != 'clicked':
        print(f'  step {step}: no next button; stopping')
        break
    time.sleep(1.5)

print(f'\nTotal: {order} unique pages → {out_dir}')
