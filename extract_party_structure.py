"""
Extract the complete party/list structure from xd.is pages including party codes.
Download candidate photos to tmp folder for visual identification.
"""
import urllib.request, re, hashlib, json, ssl, time, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

xd_pages = {
    "skagafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "borgarbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "dalvikurbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "hunabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "rangarthing-eystra": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "hunathing-vestra": "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
}

all_data = {}

for muni_slug, page_url in xd_pages.items():
    print(f"\n=== {muni_slug} ===")
    html = fetch_html(page_url)

    # Find the JS data section
    # Look for the xdm data structure with parties
    # The structure appears to be:
    # parties: [
    #   { partyCode: "...", partyName: "...", candidates: [...] },
    #   ...
    # ]

    # Let's extract the full JS block containing parties data
    parties_idx = html.find("parties:")
    if parties_idx == -1:
        parties_idx = html.find('"parties"')
    if parties_idx == -1:
        print("  No parties data found")
        continue

    # Get a large chunk of text around this
    # Find the enclosing JS object by tracking brackets
    data_start = max(0, parties_idx - 200)
    chunk = html[data_start:data_start + 50000]

    print(f"  Found parties data at index {parties_idx}")
    # Print first 2000 chars to understand structure
    print(chunk[:3000])
    print("...")
