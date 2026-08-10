"""
Find candidates that are in the manifest (missing photos) but NOT yet in the results file.
Focus on candidates from the source pages being scraped.
Cross-reference with the bb.is vikuvidtal coverage area (Vestfirðir municipalities).
"""
import json

# Load manifest
with open(r"F:\Claude Projects\iceland-elections\scan_manifest.json", "r", encoding="utf-8") as f:
    manifest = json.load(f)

# Load results
with open(r"F:\Claude Projects\iceland-elections\scan_results\photos_2026-04-29.json", "r", encoding="utf-8") as f:
    results = json.load(f)

# Get all candidate IDs that already have photos
already_found = {r["id"] for r in results["results"]}
print(f"Already found: {len(already_found)} candidates")

# Get all missing photo candidates
missing = manifest["missing_photos"]
print(f"Total missing: {len(missing)}")

# Focus on municipalities covered by source pages
# bb.is covers Vestfirðir municipalities
vestfirdir_slugs = ["isafjordur", "bolungarvik", "strandabyggd", "vesturbyggd", "reykholar", "hnjotur", "baejarsveit"]
# xd.is pages being scraped
xd_slugs = ["skagafjordur", "borgarbyggd", "dalvikurbyggd", "hunabyggd", "rangarthing-eystra", "rangarthingeystra", "hunathing-vestra", "hunathing"]
# other source pages
other_slugs = ["akranes", "hvalfjardarsveit", "vogar", "grundarfjordur"]

all_target_slugs = vestfirdir_slugs + xd_slugs + other_slugs

print("\n=== Candidates NOT yet in results file (relevant municipalities) ===")
for cand in missing:
    if cand["id"] not in already_found:
        # Check if it's from a relevant municipality
        slug = cand["muni_slug"]
        relevant = any(s in slug for s in all_target_slugs)
        if relevant:
            print(f"  {cand['id']} {cand['name']} ({slug}, {cand['party_code']}, ballot={cand['ballot']})")

print("\n=== Candidates in results file from bb.is ===")
bb_results = [r for r in results["results"] if r.get("source", "").startswith("https://bb.is")]
for r in bb_results:
    print(f"  {r['id']} {r['name']} -> {r.get('photo_local', '?')}")

print("\n=== Candidates in results file from xd.is ===")
xd_results = [r for r in results["results"] if "xd.is" in r.get("source", "")]
for r in xd_results:
    print(f"  {r['id']} {r['name']} -> {r.get('photo_local', '?')}")
