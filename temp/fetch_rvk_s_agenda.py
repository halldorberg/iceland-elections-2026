"""Fetch all 5 RVK.S agenda sub-pages via Edge CDP with scroll."""
import json, subprocess, sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
TAB = '9301EC24'
OUT = ROOT / 'temp' / 'rvk_s_agenda'
OUT.mkdir(exist_ok=True, parents=True)

URLS = [
    (1, 'Setjum börnin í fyrsta sæti',     'https://xs.is/setjum-bornin-i-fyrsta-saeti'),
    (2, 'Slagkraftur í húsnæðisuppbyggingu', 'https://xs.is/slagkraftur-i-husnaedisuppbyggingu'),
    (3, 'Fulla ferð áfram í samgöngumálum',  'https://xs.is/fulla-ferd-afram-i-samgongumalum'),
    (4, 'Rúllum út rauða dreglinum',         'https://xs.is/rullum-ut-rauda-dreglinum-fyrir-folk-og-atvinnulif'),
    (5, 'Gott og gaman að búa í borginni',   'https://xs.is/gott-og-gaman-ad-bua-i-borginni'),
]


def cdp_nav(url):
    subprocess.run(['python','scripts/edge_cdp.py','nav',TAB,url],
                   capture_output=True, text=True, encoding='utf-8')


def cdp_eval(expr):
    p = subprocess.run(['python','scripts/edge_cdp.py','eval',TAB,expr],
                       capture_output=True, text=True, encoding='utf-8')
    return p.stdout.strip()


for seat, title, url in URLS:
    out = OUT / f'{seat}_{title.replace(" ", "_")[:60]}.txt'
    if out.exists() and out.stat().st_size > 500:
        print(f'  {seat}  cached')
        continue
    cdp_nav(url)
    time.sleep(3)
    # Scroll all the way down — slow, repeated, to trigger lazy loads
    cdp_eval(
        "(async()=>{const h=document.body.scrollHeight;"
        "for(let s=0;s<25;s++){window.scrollTo(0,s*700);"
        "await new Promise(r=>setTimeout(r,500))}"
        "window.scrollTo(0,document.body.scrollHeight);"
        "await new Promise(r=>setTimeout(r,1500));"
        "return 'done'})()"
    )
    time.sleep(1)
    # Pull all main-content text
    txt = cdp_eval(
        "(()=>{const main=document.querySelector('main')||document.querySelector('article')||document.body;"
        "return main.innerText})()"
    )
    out.write_text(txt, encoding='utf-8')
    print(f'  {seat}  {title[:40]}  ({len(txt)} chars)')
