"""Walk through each Miðflokkurinn í Grindavík candidate FB post, expand,
   extract the structured bio (Nafn/Atvinna/Fjölskylduhagir/...) + photo URL.
   Download cropped 400x400 candidate photo."""
import json, base64, subprocess, sys, io, time, re, hashlib
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = 'FF342017'
OUT = ROOT / 'temp' / 'grn_m_bios'
OUT.mkdir(exist_ok=True, parents=True)

# fbids of candidate intro post photos (cards), from photo album scan
POSTS = [
    # (ballot, expected_name, fbid)
    (2,  'Björn Steinar Brynjólfsson', '1295036816144875'),
    (3,  'Gunnar Már Gunnarsson',      '1294207819561108'),
    (4,  'Signý Lind Elíasdóttir',     '1293508779631012'),
    (5,  'Eydís Ármannsdóttir',        '1292549489726941'),
    (6,  'Aníta Sif Kristjánsdóttir',  '1291754473139776'),
    (7,  'Páll Gíslason',              '1291227473192476'),
    (8,  'Páll Árni Pétursson',        '1290914969890393'),
    (9,  'Hajie Flores Sicat',         '1289477556700801'),
    (10, 'Andri Hrafn Vilhelmsson',    '1288598036788753'),
    (11, 'Ragna Fossádal',             '1287929383522285'),
]


def cdp_eval(expr):
    p = subprocess.run(
        ['python', 'scripts/edge_cdp.py', 'eval', TAB, expr],
        capture_output=True, text=True, encoding='utf-8'
    )
    return p.stdout.strip()


results = []
for ballot, name, fbid in POSTS:
    url = f'https://www.facebook.com/photo.php?fbid={fbid}&type=3'
    cdp_eval(f"location.href='{url}'")
    time.sleep(4)

    # Click "See more" anywhere on the page
    cdp_eval(
        "Array.from(document.querySelectorAll('div[role=button]')).filter("
        "b=>(b.innerText||'').match(/See more|Sjá meira/)).forEach(b=>b.click()); 1"
    )
    time.sleep(2)

    body = cdp_eval("document.body.innerText")
    # edge_cdp.py returns the raw string for type:string Runtime.evaluate
    txt_fn = OUT / f'ballot_{ballot:02d}_{fbid}.txt'
    txt_fn.write_text(body, encoding='utf-8')

    # Get full-res image URL
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
    img_src = srcs[0] if srcs else None
    if img_src:
        b64 = cdp_eval(
            "(async()=>{const r=await fetch(" + json.dumps(img_src) + ");"
            "const b=await r.blob();const buf=await b.arrayBuffer();"
            "const arr=new Uint8Array(buf);let s='';"
            "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
            "return btoa(s)})()"
        )
        try:
            data = base64.b64decode(b64)
            raw_fn = OUT / f'ballot_{ballot:02d}_{fbid}_raw.jpg'
            raw_fn.write_bytes(data)
            print(f'  {ballot:02d} {name}: post {len(body)} chars, img {len(data)} bytes')
            results.append({'ballot': ballot, 'name': name, 'fbid': fbid, 'txt': str(txt_fn), 'img_raw': str(raw_fn)})
        except Exception as e:
            print(f'  {ballot:02d} {name}: img decode failed: {e}')
    else:
        print(f'  {ballot:02d} {name}: no img')

json.dump(results, open(OUT / 'index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\nDone. {len(results)} candidates scraped.')
