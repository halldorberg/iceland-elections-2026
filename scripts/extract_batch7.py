# -*- coding: utf-8 -*-
"""Extract clean article text from visir_text files for classification."""
import html, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = r"F:\Claude Projects\iceland-elections\scripts\visir_text"

def extract(fn):
    path = os.path.join(BASE, fn)
    with open(path, encoding='utf-8', errors='replace') as f:
        raw = f.read()
    # header
    m_url = re.search(r'^URL: (.+)$', raw, re.M)
    m_date = re.search(r'^DATE: (.+)$', raw, re.M)
    body = raw.split('---', 1)[1] if '---' in raw else raw
    body = html.unescape(body)
    # cut nav: take text after last 'Innskráning'
    idx = body.rfind('Innskráning')
    if idx != -1:
        body = body[idx + len('Innskráning'):]
    # cut tail at 'Viltu birta grein'
    idx2 = body.find('Viltu birta grein')
    if idx2 != -1:
        body = body[:idx2]
    body = re.sub(r'\s+', ' ', body).strip()
    if len(body) > 4200:
        body = body[:3300] + ' [...] ' + body[-900:]
    url = html.unescape(m_url.group(1).strip()) if m_url else ''
    date = m_date.group(1).strip() if m_date else ''
    return url, date, body

if __name__ == '__main__':
    for fn in sys.argv[1:]:
        url, date, body = extract(fn)
        print('=' * 20)
        print('FILE:', fn)
        print('URL:', url)
        print('DATE:', date)
        print('BODY:', body)
        print()
