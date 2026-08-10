"""Walk the Framsókn í Grindavík agenda post images."""
import json, base64, subprocess, sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = '03977ADE'
OUT = ROOT / 'temp' / 'grn_b_agenda'
OUT.mkdir(exist_ok=True, parents=True)

FBIDS = [
    122112743655257707,
    122112743607257707,
    122112743571257707,
    122112743499257707,
    122112743469257707,
    122112743445257707,
    122112743379257707,
]


def cdp_eval(expr):
    p = subprocess.run(['python','scripts/edge_cdp.py','eval',TAB,expr],
                       capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip()


for idx, fbid in enumerate(FBIDS, 1):
    out_fn = OUT / f'page_{idx:02d}_fbid_{fbid}.jpg'
    if out_fn.exists():
        print(f'  {idx:02d}: cached')
        continue
    cdp_eval(f"location.href='https://www.facebook.com/photo.php?fbid={fbid}&type=3'")
    time.sleep(4)
    src_json = cdp_eval(
        "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
        "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,1))"
    )
    try:
        srcs = json.loads(src_json)
    except Exception:
        srcs = []
    if not srcs:
        time.sleep(3)
        srcs = json.loads(cdp_eval(
            "JSON.stringify(Array.from(document.querySelectorAll('img')).filter("
            "i=>i.src.includes('scontent')&&i.naturalWidth>=600).map(i=>i.src).slice(0,1))"
        ) or '[]')
    if not srcs:
        print(f'  {idx:02d}: no img'); continue
    src = srcs[0]
    fetch_expr = (
        "(async()=>{const r=await fetch(" + json.dumps(src) + ");"
        "const b=await r.blob();const buf=await b.arrayBuffer();"
        "const arr=new Uint8Array(buf);let s='';"
        "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
        "return btoa(s)})()"
    )
    b64 = cdp_eval(fetch_expr)
    if not b64:
        print(f'  {idx:02d}: empty fetch'); continue
    try:
        data = base64.b64decode(b64)
    except Exception as e:
        print(f'  {idx:02d}: decode fail {e}'); continue
    out_fn.write_bytes(data)
    print(f'  {idx:02d}: {len(data)} bytes')

print('\nDone.')
