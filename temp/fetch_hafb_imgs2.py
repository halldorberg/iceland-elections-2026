"""Fetch HAF.B agenda images one at a time via photo viewer."""
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


FBIDS = [
    965717592777129,
    965717552777133,
    965717489443806,
    965717586110463,
    965717549443800,
    965717486110473,
    965799952768893,
    974266748588880,
]

for fbid in FBIDS:
    out = OUT / f'fbid_{fbid}.jpg'
    if out.exists() and out.stat().st_size > 1000:
        print(f'  {fbid}: cached')
        continue
    url = f'https://www.facebook.com/photo.php?fbid={fbid}&set=pb.100086281493060.-2207520000&type=3'
    cdp_eval(f"location.href={json.dumps(url)}")
    time.sleep(4)
    src_json = cdp_eval(
        "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
        "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,3))"
    )
    try:
        srcs = json.loads(src_json)
    except Exception:
        srcs = []
    if not srcs:
        time.sleep(3)
        srcs = json.loads(cdp_eval(
            "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
            "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,3))"
        ) or '[]')
    if not srcs:
        print(f'  {fbid}: no high-res')
        continue
    src = srcs[0]
    b64 = cdp_eval(
        "(async()=>{const r=await fetch(" + json.dumps(src) + ");"
        "const b=await r.blob();const buf=await b.arrayBuffer();"
        "const arr=new Uint8Array(buf);let s='';"
        "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
        "return btoa(s)})()"
    )
    if not b64:
        print(f'  {fbid}: empty fetch'); continue
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'  {fbid}: decode {e}'); continue
    out.write_bytes(data)
    print(f'  {fbid}: {len(data)} bytes')
