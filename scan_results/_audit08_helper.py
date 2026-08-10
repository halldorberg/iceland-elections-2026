import re, json, sys, io
from html import unescape
if __name__ == '__main__':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

BASE = r'F:\Claude Projects\iceland-elections\scan_results\source_cache' + '\\'

def text(p):
    with open(BASE + p, 'rb') as f:
        raw = f.read()
    # try utf-8 first then cp1252/iso-8859-1
    try:
        h = raw.decode('utf-8')
    except UnicodeDecodeError:
        try:
            h = raw.decode('iso-8859-1')
        except UnicodeDecodeError:
            h = raw.decode('cp1252', errors='replace')
    # detect mojibake/other charset by looking at meta charset
    m = re.search(rb'charset=["\']?([\w\-]+)', raw[:2048], re.I)
    if m:
        cs = m.group(1).decode('ascii', errors='ignore').lower()
        if cs not in ('utf-8','utf8') and cs:
            try:
                h = raw.decode(cs, errors='replace')
            except LookupError:
                pass
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S|re.I)
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S|re.I)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = unescape(h)
    h = re.sub(r'\s+', ' ', h)
    return h

def search(p, term, ctx=200):
    t = text(p)
    out = []
    for m in re.finditer(re.escape(term), t, re.I):
        s = max(0, m.start()-ctx); e = min(len(t), m.end()+ctx)
        out.append(t[s:e])
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'text':
        print(text(sys.argv[2])[:int(sys.argv[3]) if len(sys.argv)>3 else 8000])
    elif cmd == 'search':
        for h in search(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv)>4 else 200):
            print('---'); print(h)
