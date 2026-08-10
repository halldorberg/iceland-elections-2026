#!/usr/bin/env python3
"""
Batch 5 photo harvest - download confirmed photos from session 5.
"""

import json
import os
import hashlib
import urllib.request
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
                print(f"    WARNING: tiny image ({len(raw)} bytes)")
                return None, None
            return raw, ext
    except Exception as e:
        print(f"    ERROR: {e}")
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
        print(f"  SKIP: {candidate_id} {name}")
        return False
    print(f"  Downloading {candidate_id} {name}...")
    img_bytes, img_ext = download_image(photo_url, ext)
    if img_bytes is None:
        print(f"  FAILED: {candidate_id}")
        return False
    filename = save_image(img_bytes, img_ext)
    entry = {
        "id": candidate_id, "muni_slug": muni_slug, "party_code": party_code,
        "ballot": ballot, "name": name, "photo_url": photo_url,
        "photo_local": f"images/candidates/{filename}", "source": source
    }
    data['results'].append(entry)
    found_ids.add(candidate_id)
    print(f"  OK: {candidate_id} -> {filename}")
    return True

data = load_data()
found_ids = set(r['id'] for r in data['results'] if r.get('photo_url'))
print(f"Starting with {len(data['results'])} results, {len(found_ids)} with photos.")

new_count = 0

def check_save():
    global new_count
    if new_count > 0 and new_count % 5 == 0:
        save_data(data)

# ===== SKA.SFL.2 Jóhanna Ey Harðardóttir (feykir.is) =====
# Found at feykir.is/static/news/lg/johanna-ey.jpg (152KB confirmed)
print("\n=== SKA.SFL.2 Jóhanna Ey Harðardóttir ===")
if add_candidate(data, found_ids,
    "SKA.SFL.2", "skagafjordur", "SFL", 2,
    "Jóhanna Ey Harðardóttir",
    "https://www.feykir.is/static/news/lg/johanna-ey.jpg",
    "https://www.feykir.is/is/frettir/johanna-ey-i-efsta-saeti-byggdalistans"):
    new_count += 1
check_save()
time.sleep(0.3)

if new_count % 5 != 0:
    save_data(data)

print(f"\n=== Done. Added {new_count} new photos. Total: {len(data['results'])} ===")
save_data(data)
