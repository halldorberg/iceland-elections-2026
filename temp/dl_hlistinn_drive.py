"""Download H-listinn Fjallabyggð files from Drive via Edge CDP.

Strategy: navigate the existing Drive tab to /file/d/<id>/view (the
Drive Preview page) for each file, then fetch the embedded
drive-viewer img/embed URL with credentials. Works for everything
shared with the logged-in user without needing the file to be public.
"""
import json, base64, subprocess, sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = 'A3120D1A'
OUT = ROOT / 'temp' / 'hlistinn_fjb'
OUT.mkdir(exist_ok=True, parents=True)


def cdp_eval(expr):
    p = subprocess.run(['python', 'scripts/edge_cdp.py', 'eval', TAB, expr],
                       capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip()


def cdp_nav(url):
    subprocess.run(['python', 'scripts/edge_cdp.py', 'nav', TAB, url],
                   capture_output=True, text=True, encoding='utf-8')


# (seat, name, drive_id)
PHOTOS = [
    (1,  'Helgi',                 '1qYwUm0zvIVaevZkCtQvhqwWAVPndx--1'),
    (2,  'Kristinn',               '1zGwSUmifisn-qmUNG-ReNJzAnwXc0PBS'),
    (3,  'Asgeir_Logi',            '1sQ1qXgacwL20SQa01Bwf-2F63myc9mhi'),
    (4,  'Audur_Osp',              '1XtaOj5CVNSpkfrAHqxGsElf4TL5PGSPS'),
    (5,  'Gudlaugur_Magnus',       '1gL6AZX84rhJXxgwZQYJlItQ0I_e5X3br'),
    (6,  'Thorfinna_Ellen',        '1LCY1I0mezM-0g00qpTc2gy8YuGazAdq0'),
    (7,  'Thorgeir',               '13JuAD8lst387SXzE19YVjXIQEgwRdn3p'),
    (8,  'Klara_Mist',             '103wUvZpuDL6eySenlZGW7XvC53b6Wz1E'),
    (9,  'Jon_Valgeir',            '1r0FHwJenTt8hnKMyHmmglxQubjKAYTrN'),
    (10, 'Andri_Vidar',            '1MVE7IUsZY45ltfw8hM1SMK4LaINDC8wG'),
    (11, 'Adalbjorg',              '1ODp5r5ZMRj7Rsd0FZR7fmtsaPzy6TgC0'),
    (12, 'Aki',                    '1549VNidybV4moTLnTg3GvZPksyBMeVJf'),
    (13, 'Katrin',                 '1piFUeOuXyG3lQ9MoZaQTDv-aN-tGw6rg'),
    (14, 'Arni_Helga',             '141Bm80J3085Ps0CVZpaIM2XFQvhl4gkT'),
]

# Kynning docs (introduction text). The viewer for docx renders text
# pages — we extract textContent rather than the binary.
DOCS = [
    (0,  'H_framboð_texti_1',           '1JmBnZdMgiBEh6OUAk-TxR3DaaTb5LzJR'),
    (1,  'Kynning_1_Helgi',             '1GCg4zg8MJUzedkKijYAmdGJOXu-kZn_z'),
    (2,  'Kynning_2_Kristinn',          '1UzYbUq9eTBjVRD-TVkdJckrkT74jrXrR'),
    (3,  'Kynning_3_Asgeir_Logi',       '1JXCJS0icNMTUGgD5SIFL_jPtPEwa2ML-'),
    (4,  'Kynning_4_Audur_Osp',         '1_xiAMlB41kAeZExJfcwHhN-lxlJcwyUX'),
    (5,  'Kynning_5_Gudlaugur_Magnus',  '1RLjL1QI4cQT2iOqeEh-vj2LSVzZLu3V7'),  # pdf
    (6,  'Kynning_6_Thorfinna_Ellen',   '1CNhhCdo4azN5bQrNL-XsWELP5pV9BKoR'),
    (7,  'Kynning_7_Thorgeir',          '1F55k8km3nagwrvZu2NSIIUbC-_cqYZMh'),
    (8,  'Kynning_8_Klara_Mist',        '1FPovRDtdbm1m3LR2eL2cUZBUpoSThaP1'),
    (9,  'Kynning_9_Jon_Valgeir',       '1pAdANWOJd7gGNWOLfkGcrpnJDTbTOv9K'),
    (10, 'Kynning_10_Andri_Vidar',      '1ebPr1tos70TAaAt71zS9cGOTW-t3y8q9'),
    (11, 'Kynning_11_Adalbjorg',        '1iiETDaWoWmtqKGUY6rknp2Wd_U3YbU-y'),
    (13, 'Kynning_13_Katrin',           '1fN_vT1WxmWRodughuLWxMBM77vxFv9YV'),
    (14, 'Kynning_14_Arni_Helgason',    '10hN5OS9ZKgWtOKlzGcn3V1iIr8ieT1wA'),
]


def fetch_image(file_id, out_path):
    """Navigate to /file/d/ID/view, find the drive-viewer img, fetch it."""
    cdp_nav(f'https://drive.google.com/file/d/{file_id}/view')
    # Poll for image to appear with size > 400
    for _ in range(15):
        time.sleep(1)
        out = cdp_eval(
            "(async()=>{const i=Array.from(document.querySelectorAll('img'))."
            "find(x=>x.src.includes('drive-viewer')&&x.naturalWidth>400);"
            "return i?i.src:''})()"
        )
        if out and out.startswith('http'):
            break
    else:
        return False, 'no img after 15s'
    # Fetch with credentials
    fetch_expr = (
        "(async()=>{const r=await fetch(" + json.dumps(out) +
        ",{credentials:'include'});if(!r.ok)return 'http'+r.status;"
        "const b=await r.blob();const buf=await b.arrayBuffer();"
        "const arr=new Uint8Array(buf);let s='';"
        "for(let i=0;i<arr.length;i++)s+=String.fromCharCode(arr[i]);"
        "return btoa(s)})()"
    )
    b64 = cdp_eval(fetch_expr)
    if not b64 or b64.startswith('http'):
        return False, f'fetch-error: {b64[:60]}'
    try:
        raw = base64.b64decode(b64)
    except Exception as e:
        return False, f'decode: {e}'
    if len(raw) < 1000:
        return False, f'tiny: {len(raw)} bytes'
    out_path.write_bytes(raw)
    return True, f'{len(raw)//1024} KB'


def fetch_doc_text(file_id):
    """For docx/pdf, navigate to viewer and extract document body text."""
    cdp_nav(f'https://drive.google.com/file/d/{file_id}/view')
    # Wait for content to render
    text = ''
    for _ in range(20):
        time.sleep(1.2)
        # Drive previews docx with an embedded viewer; check the
        # whole body innerText after content has loaded.
        t = cdp_eval(
            "(()=>{const f=Array.from(document.querySelectorAll('iframe'));"
            "for(const fr of f){try{const d=fr.contentDocument;if(d){const t=d.body?d.body.innerText:'';if(t.length>120)return t}}catch(e){}}"
            "return document.body.innerText||''})()"
        )
        if t and len(t) > 150 and ('Kynning' in t or 'rambj' in t or 'fram' in t.lower() or seat_search_terms_in(t)):
            text = t
            break
        if t and len(t) > 400:
            text = t
            break
    return text


def seat_search_terms_in(t):
    return any(x in t for x in ['ára', 'starf', 'fædd', 'bý', 'kjör', 'samfél'])


print('=== PHOTOS ===')
results = {}
for seat, name, fid in PHOTOS:
    out = OUT / f'{seat:02d}_{name}.bin'
    if out.exists() and out.stat().st_size > 1000:
        print(f'  {seat:>2}  {name:<20}  cached ({out.stat().st_size//1024} KB)')
        results[seat] = out
        continue
    ok, msg = fetch_image(fid, out)
    print(f'  {seat:>2}  {name:<20}  {"OK" if ok else "FAIL"}  {msg}')
    if ok:
        results[seat] = out

print()
print('=== KYNNING TEXTS ===')
for seat, name, fid in DOCS:
    txt_out = OUT / f'{name}.txt'
    if txt_out.exists() and txt_out.stat().st_size > 100:
        print(f'  {seat:>2}  {name:<35}  cached')
        continue
    text = fetch_doc_text(fid)
    if text and len(text) > 100:
        txt_out.write_text(text, encoding='utf-8')
        print(f'  {seat:>2}  {name:<35}  OK ({len(text)} chars)')
    else:
        print(f'  {seat:>2}  {name:<35}  EMPTY')
