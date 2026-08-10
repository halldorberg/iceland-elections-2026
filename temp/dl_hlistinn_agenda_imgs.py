"""Download the May 11 H-listinn Fjallabyggð agenda images."""
import base64, subprocess, sys, io, time
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


IDS = [
    '1298015595799324',
    '1298015602465990',
    '1298015609132656',
    '1298015659132651',
    '1298015669132650',
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
    out = OUT / f'agenda_{fid}.jpg'
    if out.exists() and out.stat().st_size > 1000:
        print(f'  {fid}: cached ({out.stat().st_size//1024} KB)')
        continue
    cdp_nav(f'https://www.facebook.com/photo.php?fbid={fid}&id=100067726875693')
    time.sleep(4)
    b64 = cdp_eval(FETCH)
    if not b64 or len(b64) < 100:
        print(f'  {fid}: empty')
        continue
    raw = base64.b64decode(b64)
    out.write_bytes(raw)
    print(f'  {fid}: {len(raw)//1024} KB')
