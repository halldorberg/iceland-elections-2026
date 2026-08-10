"""Fetch HAF.B agenda images via Edge CDP in-browser fetch."""
import json, base64, subprocess, sys, io, time
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = '3E4FF37F'
OUT = ROOT / 'temp' / 'haf_b_agenda'
OUT.mkdir(exist_ok=True, parents=True)


def cdp_eval(expr):
    p = subprocess.run(['python', 'scripts/edge_cdp.py', 'eval', TAB, expr],
                       capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip()


# fbids of suspected agenda graphics in the "Málefnaskrá" post
FBIDS = [
    965717592777129,  # Mennta-/íþrótta-/lýðheilsumál
    965717552777133,  # Velferðamál
    965717489443806,  # unknown topic
    965717586110463,
    965717549443800,
    965717486110473,
    965799952768893,
    974266748588880,
]

# Get full image URLs by re-reading the page
src_json = cdp_eval(
    "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
    "i=>i.src.includes('scontent')).map(i=>i.src))"
)
all_imgs = json.loads(src_json)

import re
fbid_to_url = {}
for url in all_imgs:
    for fbid in FBIDS:
        if str(fbid) in url:
            # prefer 960x960 over 206x206
            if fbid in fbid_to_url and '_s960x960' in fbid_to_url[fbid]:
                continue
            fbid_to_url[fbid] = url

for fbid in FBIDS:
    url = fbid_to_url.get(fbid)
    if not url:
        print(f'  {fbid}: NO URL FOUND')
        continue
    # Force 960x960
    url = re.sub(r'_s\d+x\d+', '_s960x960', url)

    fetch_expr = (
        "(async()=>{const r=await fetch(" + json.dumps(url) + ");"
        "const b=await r.blob();const buf=await b.arrayBuffer();"
        "const arr=new Uint8Array(buf);let s='';"
        "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
        "return btoa(s)})()"
    )
    b64 = cdp_eval(fetch_expr)
    if not b64:
        print(f'  {fbid}: empty fetch')
        continue
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'  {fbid}: decode error {e}')
        continue
    out = OUT / f'fbid_{fbid}.jpg'
    out.write_bytes(data)
    print(f'  {fbid}: {len(data)} bytes')
