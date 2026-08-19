# coding: utf-8
"""Fetch all to-classify Visir articles to scripts/visir_raw/ (resumable).
Extracts main text into scripts/visir_text/<id>.txt with a header block."""
import io, json, os, re, time, urllib.request, hashlib
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / 'visir_raw'
TXT = ROOT / 'visir_text'
RAW.mkdir(exist_ok=True)
TXT.mkdir(exist_ok=True)

todo = json.load(io.open(ROOT / 'visir_todo.json', encoding='utf-8'))

def article_id(url):
    m = re.search(r'/g/(\d+)', url)
    return m.group(1) if m else hashlib.md5(url.encode()).hexdigest()[:12]

def strip_tags(html):
    html = re.sub(r'<script.*?</script>', ' ', html, flags=re.S)
    html = re.sub(r'<style.*?</style>', ' ', html, flags=re.S)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    return re.sub(r'\s+', ' ', html).strip()

done = fails = 0
for url, title in todo.items():
    aid = article_id(url)
    out = TXT / f'{aid}.txt'
    if out.exists():
        done += 1
        continue
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'replace')
    except Exception as e:
        print(f'FAIL {aid} {e}', flush=True)
        fails += 1
        continue
    # author: visir puts author in meta or byline
    author = ''
    m = re.search(r'"author"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', html)
    if m:
        author = m.group(1)
    date = ''
    m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
    if m:
        date = m.group(1)
    # main body: visir article body div
    body = html
    m = re.search(r'<div[^>]+class="[^"]*article-body[^"]*"[^>]*>(.*?)</div>\s*<div', html, flags=re.S)
    if m:
        body = m.group(1)
    text = strip_tags(body)[:6000]
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write(f'URL: {url}\nTITLE: {title}\nAUTHOR: {author}\nDATE: {date}\n---\n{text}\n')
    done += 1
    if done % 25 == 0:
        print(f'{done}/{len(todo)}', flush=True)
    time.sleep(0.4)
print(f'DONE {done} ok, {fails} failed', flush=True)
