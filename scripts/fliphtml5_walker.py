"""Walk a fliphtml5 flipbook via Edge CDP, collect every unique large-image
URL, download each, and downscale to ≤1800 px on the long edge for safe
visual reading. Saves originals + downscaled copies side by side.

Usage:
  python scripts/fliphtml5_walker.py <tab_id_prefix> <total_pages> [--out=temp/flip]
"""
import argparse, json, sys, io, time, urllib.request, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edge_cdp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ap = argparse.ArgumentParser()
ap.add_argument('tab')
ap.add_argument('total', type=int)
ap.add_argument('--out', default='temp/flip')
args = ap.parse_args()

tab = edge_cdp.find_tab(args.tab)
if not tab:
    print(f'tab {args.tab} not found'); sys.exit(1)
ws = edge_cdp.attach(tab)
out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://online.fliphtml5.com/'}

seen = set()

def grab_visible_pages():
    expr = """
        (() => {
            const imgs = [...document.querySelectorAll('img')]
                .filter(i => i.src && /fliphtml5.*files\\/large\\//.test(i.src))
                .map(i => i.src.split('?')[0]);
            return JSON.stringify([...new Set(imgs)]);
        })()
    """
    return json.loads(edge_cdp.evaluate(ws, expr))

def click_next():
    expr = """
        (() => {
            const inp = [...document.querySelectorAll('input')]
                .find(i => /^\\d+\\/\\d+$/.test(i.value));
            if (inp) {
                const m = inp.value.match(/^(\\d+)\\/(\\d+)$/);
                if (+m[1] >= +m[2]) return 'at-end';
            }
            const next = document.querySelector('.flip_button_right')
                || document.querySelector('.rightBtn');
            if (!next) return 'no-button';
            // Full mouse-event sequence; bare click() can fail if the
            // handler listens for mousedown/mouseup specifically.
            const r = next.getBoundingClientRect();
            const opts = { bubbles: true, cancelable: true, view: window,
                           clientX: r.left + r.width/2, clientY: r.top + r.height/2 };
            next.dispatchEvent(new MouseEvent('mousedown', opts));
            next.dispatchEvent(new MouseEvent('mouseup', opts));
            next.dispatchEvent(new MouseEvent('click', opts));
            return 'clicked';
        })()
    """
    return edge_cdp.evaluate(ws, expr)

# Walk
for step in range(args.total + 2):
    new_urls = [u for u in grab_visible_pages() if u not in seen]
    for u in new_urls:
        seen.add(u)
        # Filename from hash in URL
        name = u.rsplit('/', 1)[-1]
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            (out_dir / name).write_bytes(data)
            print(f'  page {step:>2}: {name}  ({len(data)//1024} KB)')
        except Exception as e:
            print(f'  page {step:>2}: {name} fail: {e}')
    r = click_next()
    if r not in ('clicked', 'advanced'):
        print(f'  next-fn returned {r!r} at step {step}; stopping'); break
    time.sleep(1.2)

print(f'\nUnique pages downloaded: {len(seen)}')

# Downscale every webp/jpg in out_dir to ≤1800px on long edge, save .small.jpg
try:
    from PIL import Image
except ImportError:
    print('Pillow not installed — skipping downscale.')
    sys.exit(0)

print('Downscaling to ≤1800 px long edge…')
for p in sorted(out_dir.glob('*')):
    if p.suffix.lower() not in ('.webp', '.jpg', '.jpeg', '.png'): continue
    try:
        im = Image.open(p).convert('RGB')
        im.thumbnail((1800, 1800))
        small = p.with_name(p.stem + '.small.jpg')
        im.save(small, 'JPEG', quality=85)
        print(f'  {p.name} → {small.name} ({im.size[0]}x{im.size[1]})')
    except Exception as e:
        print(f'  {p.name}: ERR {e}')
