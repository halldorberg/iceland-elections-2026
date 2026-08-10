"""Use Edge CDP to scrape full-res images from N-listinn FB posts.

For each post URL: open in tab, click into the carousel, walk through each
image, capture the largest <img> visible in the lightbox, save to temp/nlist_fb/.
"""
import subprocess, json, time, os, sys, io, urllib.request, urllib.parse, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

EDGE_CDP = r'F:\Claude Projects\iceland-elections\scripts\edge_cdp.py'
OUT = r'F:\Claude Projects\iceland-elections\temp\nlist_fb'
os.makedirs(OUT, exist_ok=True)

POSTS = [
    ('p1', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid0SkfbuKkb1v63yHKpRBSQFGBMJkjN2KSB4AkHqGXwSGaZCYAXRncA5vFf2Sdpokcml'),
    ('p2', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid01LmRa7rDjq8zgzayzvWX8Yumo95KzLAbqreZweDb2nK62qm3MywjAPCNvT8Q6nwUl'),
    ('p3', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid02xu1ZBr3Xh1J9eiVCjodv3knFnvBtXzptmzpuat7SHwgnG8Ddy8FQ677WAD4gaTFzl'),
]

def cdp(*args):
    r = subprocess.run(['python', EDGE_CDP, *args], capture_output=True, text=True, encoding='utf-8')
    return r.stdout.strip(), r.stderr.strip()

def open_tab(url):
    out, _ = cdp('open', url)
    m = re.search(r'opened tab ([0-9A-F]{8})', out)
    return m.group(1) if m else None

def evalj(tab, expr):
    out, err = cdp('eval', tab, expr)
    return out, err

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0'

# Reuse cookies from Edge CDP via a request to FB; here we assume scontent.xx.fbcdn images are public
# Force cache-buster on URL so we get fresh

for tag, post_url in POSTS:
    print(f'\n=== {tag} {post_url[:80]}... ===')
    tab = open_tab(post_url)
    print(' tab:', tab)
    cdp('wait', tab)
    # extract the carousel image URLs at maximum res visible
    # Click first image to open lightbox
    expr = """
    (() => {
      // gather images from the post body that have fbid in URL and are >= 500px
      const post = document.querySelector('div[role="article"]') || document.body;
      const imgs = Array.from(post.querySelectorAll('img'))
        .filter(i => i.naturalWidth >= 480 && /scontent/.test(i.src))
        .map(i => ({w: i.naturalWidth, h: i.naturalHeight, src: i.src}));
      return JSON.stringify(imgs);
    })()
    """
    out, err = evalj(tab, expr)
    try:
        imgs = json.loads(out)
    except Exception:
        print(' FAIL parse:', out[:200], err)
        continue
    print(f' visible imgs (post body): {len(imgs)}')
    for i, im in enumerate(imgs, 1):
        print(f'   {i}. {im["w"]}x{im["h"]}  {im["src"][:200]}')
    # download
    for i, im in enumerate(imgs, 1):
        url = im['src']
        ext = '.jpg' if '.jpg' in url.split('?')[0] else ('.png' if '.png' in url.split('?')[0] else '.webp')
        path = os.path.join(OUT, f'{tag}_v2_{i:02d}_{im["w"]}x{im["h"]}{ext}')
        if os.path.exists(path):
            print(f'   skip {path}')
            continue
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua, 'Referer': post_url})
            data = urllib.request.urlopen(req, timeout=30).read()
            open(path, 'wb').write(data)
            print(f'   saved -> {os.path.basename(path)} ({len(data):,} bytes)')
        except Exception as e:
            print(f'   ERR: {e}')
