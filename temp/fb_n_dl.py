import urllib.request, urllib.parse, re, sys, io, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

posts = [
    ('p1', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid0SkfbuKkb1v63yHKpRBSQFGBMJkjN2KSB4AkHqGXwSGaZCYAXRncA5vFf2Sdpokcml'),
    ('p2', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid01LmRa7rDjq8zgzayzvWX8Yumo95KzLAbqreZweDb2nK62qm3MywjAPCNvT8Q6nwUl'),
    ('p3', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid02xu1ZBr3Xh1J9eiVCjodv3knFnvBtXzptmzpuat7SHwgnG8Ddy8FQ677WAD4gaTFzl'),
]
out_dir = r'F:\Claude Projects\iceland-elections\temp\nlist_fb'
os.makedirs(out_dir, exist_ok=True)
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def best_url_for(html, fbid):
    # find all occurrences of fbid (e.g. 691741724_976175858328036) and pick the one
    # with largest size hint or no s/p crop
    candidates = re.findall(r'https://scontent[^"\\\s]*?' + re.escape(fbid) + r'[^"\\\s]*', html)
    if not candidates:
        return None
    candidates = [c.replace('&amp;', '&') for c in candidates]
    # prefer one without "stp=cp0" or s50x50 or s261x260
    def score(u):
        if 'stp=cp' in u: return -10
        if 's50x50' in u: return -5
        m = re.search(r'_p(\d+)x(\d+)_', u) or re.search(r'_s(\d+)x(\d+)_', u)
        if m:
            return int(m.group(1)) * int(m.group(2))
        return 999_999  # no size constraint = original
    candidates.sort(key=score, reverse=True)
    return candidates[0]

for tag, p in posts:
    plug = 'https://www.facebook.com/plugins/post.php?' + urllib.parse.urlencode({'href': p, 'show_text': 'true', 'width': '500'})
    print(f'=== {tag} ===')
    req = urllib.request.Request(plug, headers={'User-Agent': ua})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')
    # find unique fb image ids (skip profile thumb 280523261)
    ids = []
    for m in re.findall(r'/(\d{8,}_\d{8,})_\d+_n', html):
        if m.startswith('280523261'):
            continue
        if m not in ids:
            ids.append(m)
    print(' image ids:', ids)
    for i, fbid in enumerate(ids, 1):
        url = best_url_for(html, fbid)
        if not url:
            print('   no url for', fbid)
            continue
        # truncate after & to base or keep params? use as-is
        print(f'   [{i}] {url[:200]}')
        try:
            r = urllib.request.Request(url, headers={'User-Agent': ua, 'Referer': plug})
            data = urllib.request.urlopen(r, timeout=30).read()
            ext = '.jpg'
            for e in ('.png', '.webp', '.jpeg', '.jpg'):
                if e in url.split('?')[0]:
                    ext = e
                    break
            path = os.path.join(out_dir, f'{tag}_{i:02d}_{fbid[:20]}{ext}')
            open(path, 'wb').write(data)
            print(f'      saved -> {path}  ({len(data):,} bytes)')
        except Exception as e:
            print('      ERR:', e)
