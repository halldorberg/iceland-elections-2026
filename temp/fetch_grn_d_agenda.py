"""Walk through the 10 agenda images in the FB photo viewer (one open tab),
   download each via in-browser fetch -> base64, save to disk."""
import json, base64, subprocess, sys, io, time, urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = '89D7410F'
OUT = ROOT / 'temp' / 'grn_d_agenda'
OUT.mkdir(exist_ok=True, parents=True)

FBIDS = [
    122131812399035389, 122131812819035389, 122131812759035389,
    122131812423035389, 122131812507035389, 122131812933035389,
    122131812903035389, 122131812855035389, 122131812735035389,
    122131812681035389,
]

def cdp_eval(expr):
    p = subprocess.run(
        ['python', 'scripts/edge_cdp.py', 'eval', TAB, expr],
        capture_output=True, text=True, encoding='utf-8'
    )
    return p.stdout.strip()

for idx, fbid in enumerate(FBIDS, 1):
    out_fn = OUT / f'page_{idx:02d}_fbid_{fbid}.jpg'
    if out_fn.exists():
        print(f'  {idx:02d}: cached')
        continue

    # Navigate to this photo
    url = f'https://www.facebook.com/photo.php?fbid={fbid}&type=3'
    cdp_eval(f"location.href='{url}'")
    time.sleep(4)

    # Get full-res src
    src_json = cdp_eval(
        "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
        "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,1))"
    )
    try:
        srcs = json.loads(src_json)
    except Exception:
        print(f'  {idx:02d}: bad json: {src_json[:80]}')
        continue
    if not srcs:
        print(f'  {idx:02d}: no high-res src yet, retrying')
        time.sleep(3)
        srcs = json.loads(cdp_eval(
            "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
            "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,1))"
        ) or '[]')
    if not srcs:
        print(f'  {idx:02d}: still no high-res')
        continue
    src = srcs[0]

    # Fetch via in-browser to bypass FB signing rules
    fetch_expr = (
        "(async()=>{const r=await fetch(" + json.dumps(src) + ");"
        "const b=await r.blob();const buf=await b.arrayBuffer();"
        "const arr=new Uint8Array(buf);let s='';"
        "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
        "return btoa(s)})()"
    )
    b64 = cdp_eval(fetch_expr)
    if not b64:
        print(f'  {idx:02d}: fetch returned empty')
        continue
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'  {idx:02d}: b64 decode failed: {e}')
        continue
    out_fn.write_bytes(data)
    print(f'  {idx:02d}: {len(data)} bytes -> {out_fn.name}')

print('\nDone.')
