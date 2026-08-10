#!/usr/bin/env python3
"""
Batch 2 photo harvest for Iceland municipal elections 2026.
Downloads photos and updates photos_2026-04-29.json.
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
    """Download image, return (bytes, ext) or (None, None) on failure."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get('Content-Type', '')
            data = resp.read()
            if not ext:
                if 'png' in content_type or url.lower().endswith('.png'):
                    ext = 'png'
                elif 'gif' in content_type:
                    ext = 'gif'
                elif 'webp' in content_type:
                    ext = 'webp'
                else:
                    ext = 'jpg'
            return data, ext
    except Exception as e:
        print(f"    ERROR downloading {url}: {e}")
        return None, None

def save_image(image_bytes, ext):
    """Save image to images/candidates dir, return filename."""
    md5 = hashlib.md5(image_bytes).hexdigest()[:16]
    filename = f"{md5}.{ext}"
    filepath = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
    return filename

def add_candidate(data, found_ids, candidate_id, muni_slug, party_code, ballot, name, photo_url, source, ext=None):
    """Download photo and add candidate to results. Returns True if added."""
    if candidate_id in found_ids:
        print(f"  SKIP (already found): {candidate_id} {name}")
        return False

    print(f"  Downloading photo for {candidate_id} {name}...")
    img_bytes, img_ext = download_image(photo_url, ext)

    if img_bytes is None:
        print(f"  FAILED to download photo for {candidate_id}")
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

# ============================================================
# Main harvest
# ============================================================

data = load_data()
found_ids = set(r['id'] for r in data['results'] if r.get('photo_url'))
print(f"Starting with {len(data['results'])} results, {len(found_ids)} with photos.")

new_count = 0

# Helper to save every 5 new photos
def maybe_save(force=False):
    global new_count
    if force or new_count % 5 == 0:
        save_data(data)

# ============================================================
# BATCH A: bb.is Víkuviðtal - already processed in previous run
# SKA.SFL.3 - Sveinn Úlfarsson - feykir.is
# ============================================================

print("\n=== SKA.SFL.3 Sveinn Úlfarsson (feykir.is) ===")
if add_candidate(data, found_ids,
    "SKA.SFL.3", "skagafjordur", "SFL", 3,
    "Sveinn Úlfarsson",
    "https://www.feykir.is/static/news/lg/sveinnfinster2.jpg",
    "https://www.feykir.is/is/frettir/hvernig-ma-efla-thjonustu-og-umhverfi-sveitarfelagsins-sveinn-finster-ulfarsson"):
    new_count += 1

maybe_save()

print(f"\nDone. Total new photos added: {new_count}")
print(f"Total results: {len(data['results'])}")
save_data(data)
