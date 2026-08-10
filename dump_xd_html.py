"""Find the JS data structure in xd.is HTML"""
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

req = urllib.request.Request("https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/", headers=headers)
with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
    html = r.read().decode("utf-8", errors="replace")

# Find "candidates" keyword
for term in ["candidates", "listCode", "partyCode", "listName", "xdmData", "xdm_data", "listSlug"]:
    idx = html.find(term)
    if idx != -1:
        print(f"\n=== Found '{term}' at idx {idx} ===")
        print(html[max(0,idx-100):idx+300])
        print("...")

# Find all strings that look like party/list codes
# These would be short 1-5 char uppercase strings
codes = re.findall(r'"([A-Z]{1,5})"\s*:', html)
print(f"\nShort uppercase key patterns: {set(codes)}")

# Find script tags with data
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f"\nNumber of script tags: {len(scripts)}")
for i, s in enumerate(scripts):
    if 'photoId' in s or 'candidate' in s.lower() or 'seat' in s:
        print(f"\n=== Script {i} (contains photo/candidate data) ===")
        print(s[:3000])
        print("---")
