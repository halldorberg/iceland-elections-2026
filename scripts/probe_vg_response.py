"""Parse a single JetEngine AJAX response and dump candidate info."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

d = json.load(open(r"C:/Users/USER/AppData/Local/Temp/vg_akr.json", encoding="utf-8"))
html = d.get("content", "")
print(f"content length: {len(html)}")
print(f"found_posts: {d.get('pagination', {}).get('found_posts')}")

# Find every <img src=...> (note: HTML in the JSON is unescaped already)
imgs = re.findall(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', html)
print(f"\nimage src refs: {len(imgs)}")
seen = set()
for i in imgs:
    if i not in seen:
        seen.add(i)
        print(f"  {i}")

# Find each candidate post block — they're wrapped in jet-listing-dynamic-post-XXXXX
posts = re.split(r'jet-listing-dynamic-post-(\d+)', html)
# posts[0] = preamble, then alternating (post_id, content)
print(f"\nfound {(len(posts)-1)//2} post blocks")
for i in range(1, len(posts), 2):
    pid = posts[i]
    block = posts[i+1] if i+1 < len(posts) else ""
    # Strip CSS/styles — keep only stuff between <h*> or <span> or alt= or img src=
    img_m = re.search(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', block)
    # Headings inside
    h_m = re.findall(r'<h\d[^>]*>([^<]+)</h\d>', block)
    txt = re.sub(r'<style[^>]*>.*?</style>', ' ', block[:2000], flags=re.DOTALL)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt).strip()[:200]
    print(f"\n=== post {pid} ===")
    print(f"  img: {img_m.group(1) if img_m else None}")
    print(f"  h*:  {h_m}")
    print(f"  txt: {txt}")
