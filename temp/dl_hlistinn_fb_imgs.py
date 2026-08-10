"""Download H-listinn FB photos by fbid via Edge CDP fetch (no creds)."""
import base64, subprocess, sys, io, time, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = 'AAF24D00'
OUT = ROOT / 'temp' / 'hlistinn_fb_agenda'
OUT.mkdir(exist_ok=True, parents=True)


def cdp_eval(expr):
    p = subprocess.run(['python','scripts/edge_cdp.py','eval',TAB,expr],
                       capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip()


def cdp_nav(url):
    subprocess.run(['python','scripts/edge_cdp.py','nav',TAB,url],
                   capture_output=True, text=True, encoding='utf-8')


# All recent text/agenda candidate photos
IDS = [
    '1298022062465344',
    '1298022009132016',
    '1298021965798687',
    '1298021919132025',
    '1298537295747154',
    '1298540269080190',
    '1298540245746859',
    '1299148699019347',
]

FETCH = (
    "(async()=>{const i=Array.from(document.querySelectorAll('img'))."
    "find(x=>x.src.includes('scontent')&&x.naturalWidth>600);"
    "if(!i)return '';const r=await fetch(i.src);"
    "const b=await r.blob();const buf=await b.arrayBuffer();"
    "const arr=new Uint8Array(buf);let s='';"
    "for(let n=0;n<arr.length;n++)s+=String.fromCharCode(arr[n]);"
    "return btoa(s)})()"
)

for fid in IDS:
    out = OUT / f'fbid_{fid}.jpg'
    if out.exists() and out.stat().st_size > 1000:
        print(f'  {fid}: cached ({out.stat().st_size//1024} KB)')
        continue
    cdp_nav(f'https://www.facebook.com/photo.php?fbid={fid}&id=100067726875693')
    time.sleep(4)
    b64 = cdp_eval(FETCH)
    if not b64 or b64 == '""' or len(b64) < 100:
        print(f'  {fid}: empty/short ({len(b64)} b64)')
        continue
    try:
        raw = base64.b64decode(b64)
        out.write_bytes(raw)
        print(f'  {fid}: {len(raw)//1024} KB')
    except Exception as e:
        print(f'  {fid}: decode {e}')
