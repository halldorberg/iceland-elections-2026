import urllib.request, re, hashlib, json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

url = "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=20) as r:
    html = r.read().decode("utf-8", errors="replace")

print(f"HTML size: {len(html)} chars")

# Look for all URLs mentioning drive.google.com
drive_urls = re.findall(r'https?://drive\.google\.com/[^\s\'"<>&\\]+', html)
print(f"\nGoogle Drive URLs: {len(drive_urls)}")
for u in set(drive_urls):
    print(f"  {u}")

# Look for all jpg/png/jpeg/webp URLs
img_urls = re.findall(r'https?://[^\s\'"<>&\\]+\.(?:jpg|jpeg|png|webp|JPG|PNG)', html)
print(f"\nDirect image URLs: {len(img_urls)}")
for u in set(img_urls):
    if "1x1.trans" not in u and "favicon" not in u:
        print(f"  {u}")

# Look for escaped URLs (JSON embedded in page)
escaped = re.findall(r'https?:\\/\\/[^\s\'"<>\\]+\.(?:jpg|jpeg|png|webp)', html)
print(f"\nEscaped image URLs: {len(escaped)}")
for u in set(escaped):
    real_url = u.replace('\\/','/')
    if "1x1.trans" not in real_url and "favicon" not in real_url:
        print(f"  {real_url}")

# Look for data-lazy-src or data-src
lazy = re.findall(r'data-(?:lazy-)?src=["\']([^"\']+)["\']', html)
print(f"\nLazy src attrs: {len(lazy)}")
for u in lazy:
    print(f"  {u}")

# Look for the candidate JS data
# Check if there's a JSON blob with candidate info
json_blobs = re.findall(r'\{[^{}]{100,}photo[^{}]{10,}\}', html, re.IGNORECASE)
print(f"\nJSON blobs with 'photo': {len(json_blobs)}")
for b in json_blobs[:5]:
    print(f"  {b[:200]}")

# Look for "frambjodandi" or candidate-related content
cand = re.findall(r'.{0,100}(?:frambjodandi|candidate|photo|mynd).{0,100}', html, re.IGNORECASE)
print(f"\nCandidate-related content snippets: {len(cand)}")
for c in cand[:10]:
    print(f"  {repr(c)}")
