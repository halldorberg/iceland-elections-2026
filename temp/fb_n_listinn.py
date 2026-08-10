import urllib.request, urllib.parse, re, sys, io, json, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

posts = [
    ('p1', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid0SkfbuKkb1v63yHKpRBSQFGBMJkjN2KSB4AkHqGXwSGaZCYAXRncA5vFf2Sdpokcml'),
    ('p2', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid01LmRa7rDjq8zgzayzvWX8Yumo95KzLAbqreZweDb2nK62qm3MywjAPCNvT8Q6nwUl'),
    ('p3', 'https://www.facebook.com/nyi.ohadi.listinn/posts/pfbid02xu1ZBr3Xh1J9eiVCjodv3knFnvBtXzptmzpuat7SHwgnG8Ddy8FQ677WAD4gaTFzl'),
]
out_dir = r'F:\Claude Projects\iceland-elections\temp\nlist_fb'
os.makedirs(out_dir, exist_ok=True)

for tag, p in posts:
    plug = 'https://www.facebook.com/plugins/post.php?' + urllib.parse.urlencode({'href': p, 'show_text': 'true', 'width': '500'})
    print(f'=== {tag} ===')
    req = urllib.request.Request(plug, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')
    open(os.path.join(out_dir, f'{tag}.html'), 'w', encoding='utf-8').write(html)
    # find caption — multiple patterns
    text_chunks = []
    for pat in [r'data-testid="post_message"[^>]*>([\s\S]*?)</div>',
                r'class="[^"]*userContent[^"]*"[^>]*>([\s\S]*?)</div>']:
        for m in re.finditer(pat, html):
            t = re.sub(r'<[^>]+>', '\n', m.group(1))
            t = re.sub(r'\n+', '\n', t).strip()
            if t:
                text_chunks.append(t)
    if text_chunks:
        print(' TEXT:')
        print(text_chunks[0][:1500])
    seen = {}
    for m in re.findall(r'https://scontent[^"\s]*?\.(?:jpg|jpeg|png|webp)', html):
        if '_nc_sid=f907e8' in m or 's50x50' in m:
            continue
        idm = re.search(r'/(\d{8,})_(\d{8,})_', m)
        key = idm.group(0) if idm else m[:80]
        if key in seen:
            continue
        seen[key] = m.replace('&amp;', '&')
    print(' IMG candidates:')
    for k, u in seen.items():
        print(' ', k, '->', u[:200])
PY = ''
