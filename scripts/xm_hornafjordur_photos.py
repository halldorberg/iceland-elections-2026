"""Download the 14 Miðflokkurinn-Hornafjörður candidate photos from
xmhornafjordur.is, hash them, and copy into images/candidates/.
"""
import hashlib, urllib.request, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
DST = ROOT / 'images' / 'candidates'
DST.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    (1,  'Reynir Ásgeirsson',          '14be7dd4-534f-40b5-a469-0278c6c87a63', '8'),
    (2,  'Stefán Freyr Jónsson',       '178f98d9-233b-469b-ac9a-c87498207adc', '9'),
    (3,  'Herdís I. Waage',            '8031325c-a6be-4a0a-aa6b-61bc50ffa994', '10'),
    (4,  'Erlingur Ingi Brynjólfsson', 'c512439d-05b0-445d-aa36-34d9a35d56cc', '11'),
    (5,  'Valur Pálsson',              '50032818-7146-4c5d-bccd-e463c9215d65', '22'),
    (6,  'Hilmar Þór Sigurjónsson',    '22277965-8512-4138-9bde-5a6d0db5611e', '13'),
    (7,  'Hjörvar Hauksson',           'b826813d-161e-44e0-b15d-e623d58c8a13', '12'),
    (8,  'Amor Joy Pepito Mantilla',   'a048515f-84db-44fd-86d4-0ebb8629acae', '16'),
    (9,  'Atli Þór Arnarson',          'f95b163e-774c-4193-a3d5-53f937c3eca8', '15'),
    (10, 'Pálmi Freyr Gunnarsson',     'd6e7939a-9a18-44a8-9145-207c8ed04e64', '17'),
    (11, 'Antonía Malmquist',          '9dabcaf7-d226-4bea-890a-b79161a5b718', '19'),
    (12, 'Magdalena Anna Zazulak',     'f576f467-eb06-4f3e-8953-c109d6c7dec4', '18'),
    (13, 'Ágúst Már Ágústsson',        '83ded578-be77-4f48-b3fa-cbaedf1886b6', '20'),
    (14, 'Ómar Antonsson',             'a22d7773-0752-4ed0-a3d7-de9f899d79f9', '29'),
]

mapping = {}
for seat, name, guid, num in CANDIDATES:
    url = (
        f'https://images.squarespace-cdn.com/content/v1/'
        f'69d2615d67c55e680263fc55/{guid}/Untitled+design+%28{num}%29.jpg'
        '?format=1500w'
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    h = hashlib.sha256(data).hexdigest()[:16]
    out = DST / f'{h}.jpg'
    if not out.exists():
        out.write_bytes(data)
    mapping[seat] = f'images/candidates/{out.name}'
    print(f'  seat {seat:2d}  {name:35s} -> {out.name}  ({len(data):,} bytes)')

(ROOT / 'temp' / 'xm_hornafjordur_photo_map.json').write_text(
    json.dumps(mapping, indent=2), encoding='utf-8'
)
print(f'\nMapping written to temp/xm_hornafjordur_photo_map.json')
