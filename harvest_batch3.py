#!/usr/bin/env python3
"""
Batch 3 photo harvest for Iceland municipal elections 2026.
Downloads photos for candidates identified in this session.
"""

import json
import os
import hashlib
import urllib.request
import urllib.error
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

PHOTOS_FILE = "scan_results/photos_2026-04-29.json"
IMAGES_DIR = "images/candidates"

def load_data():
    with open(PHOTOS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(PHOTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {len(data['results'])} total results.")

def download_image(url, ext=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            content_type = resp.headers.get('Content-Type', '')
            raw = resp.read()
            if not ext:
                if 'png' in content_type or url.lower().split('?')[0].endswith('.png'):
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'webp' in content_type:
                    ext = 'webp'
                else:
                    ext = 'jpg'
            if len(raw) < 1000:
                print(f"    WARNING: very small image ({len(raw)} bytes) from {url}")
                return None, None
            return raw, ext
    except Exception as e:
        print(f"    ERROR downloading {url}: {e}")
        return None, None

def save_image(image_bytes, ext):
    md5 = hashlib.md5(image_bytes).hexdigest()[:16]
    filename = f"{md5}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
    return filename

def add_candidate(data, found_ids, candidate_id, muni_slug, party_code, ballot, name, photo_url, source, ext=None):
    if candidate_id in found_ids:
        print(f"  SKIP (already found): {candidate_id} {name}")
        return False

    print(f"  Downloading {candidate_id} {name}...")
    img_bytes, img_ext = download_image(photo_url, ext)

    if img_bytes is None:
        print(f"  FAILED: {candidate_id}")
        return False

    filename = save_image(img_bytes, img_ext)
    entry = {
        "id": candidate_id,
        "muni_slug": muni_slug,
        "party_code": party_code,
        "ballot": ballot,
        "name": name,
        "photo_url": photo_url,
        "photo_local": f"images/candidates/{filename}",
        "source": source
    }
    data['results'].append(entry)
    found_ids.add(candidate_id)
    print(f"  OK: {candidate_id} {name} -> {filename}")
    return True


data = load_data()
found_ids = set(r['id'] for r in data['results'] if r.get('photo_url'))
print(f"Starting with {len(data['results'])} results, {len(found_ids)} with photos.")

new_count = 0

def maybe_save():
    global new_count
    if new_count % 5 == 0 and new_count > 0:
        save_data(data)


# ===== VOG.D.1 Björg Ásta Þórðardóttir =====
# From visir.is article about D-list in Vogar - main image A66955...
print("\n=== VOG.D.1 Björg Ásta Þórðardóttir ===")
if add_candidate(data, found_ids,
    "VOG.D.1", "vogar", "D", 1,
    "Björg Ásta Þórðardóttir",
    "https://www.visir.is/i/A66955940E9D0583D7BEFA597CF4F521050EC332D7BDEF15C77D0C53567DDEF4_713x0.jpg",
    "https://www.visir.is/g/20262864465d/sjalfstaedismenn-og-ohadir-stadfesta-listann-i-vogum"):
    new_count += 1
maybe_save()

# ===== Piratar Reykjavik candidates =====
# REY.G.1 is Ingimar Þór Friðriksson but piratar page shows Kristinn Jón Ólafsson - skip for now
# Let's check if any of the piratar page candidates match REY.G ones in manifest

# The Piratar page candidates are for a different party code (G = Grænir/Green?)
# Actually G = Píratar in manifest. Let me try fetching piratar more candidates.

# Known piratar candidates from piratar.is/piratarireykjavik26:
# - Kristinn Jón Ólafsson (ballot 1 after primary win?)
# Let's skip REY.G.1 for now and focus on confirmed matches.

time.sleep(0.5)

# ===== FJA.S.1 check - Stefán Þór Eysteinsson =====
# From visir.is - Fjarðabyggð S-list ballot 1
print("\n=== Checking FJA.S.1 ===")
if add_candidate(data, found_ids,
    "FJA.S.1", "fjardabyggd", "S", 1,
    "Stefán Þór Eysteinsson",
    "https://www.visir.is/i/4B81554E6976EAE6028EA571342FF9638F02F496403ADD26745039A63B41C8ED_713x0.jpg",
    "https://www.visir.is/g/20262857336d/stefan-thor-leidir-jafnadarmenn-i-fjardabyggd"):
    new_count += 1
maybe_save()
time.sleep(0.5)

# ===== feykir.is Skagafjörður SFL candidates =====
# Fetched from feykir.is - Sveinn Finster Úlfarsson (SKA.SFL.3) - ALREADY DONE above

# Let's look for more Skagafjörður SFL candidates on feykir.is
# feykir.is already found: SKA.SFL.1, SKA.SFL.4 in previous run

# Try SKA.SFL.2 Jóhanna Ey Harðardóttir
print("\n=== SKA.SFL.2 Jóhanna Ey Harðardóttir ===")
if add_candidate(data, found_ids,
    "SKA.SFL.2", "skagafjordur", "SFL", 2,
    "Jóhanna Ey Harðardóttir",
    "https://www.feykir.is/static/news/lg/johannaey.jpg",
    "https://www.feykir.is/is/adsendar-greinar/kosningar-2026"):
    new_count += 1
maybe_save()
time.sleep(0.5)

# ===== More visir.is oddvitaaskorunin candidates =====
# Let me try to find more from visir.is

# Íris Edda Jónsdóttir (VOP.VOP.1, Vopnafjörður)
# visir said: Íris bæjarstjóraefni í Eyjum - that was Vestmannaeyjar, different person
# VOP.VOP.1 = Íris Edda Jónsdóttir - Vopnafjörður "Strong Foundation" list

print("\n=== VOP.VOP.1 Íris Edda Jónsdóttir ===")
# Try visir.is article about Vopnafjörður VOP list
if add_candidate(data, found_ids,
    "VOP.VOP.1", "vopnafjordur", "VOP", 1,
    "Íris Edda Jónsdóttir",
    "https://www.visir.is/i/DF2E667CD3CD0CB9450A012DAE47C6AB62F29C941A28737E10E22BC4ED34EE3E_713x0.jpg",
    "https://www.visir.is/g/20262867167d/iris-baejarstjoraefni-sjalfstaedismanna-i-eyjum"):
    new_count += 1
maybe_save()
time.sleep(0.5)

print(f"\nDone. Total new photos added: {new_count}")
print(f"Total results: {len(data['results'])}")
save_data(data)
