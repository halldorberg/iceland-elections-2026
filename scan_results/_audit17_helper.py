import json, os, re, sys, html
MANIFEST_PATH = r"F:\Claude Projects\iceland-elections\scan_results\source_cache\_manifest.json"
CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
RESULTS_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_17.json"
INPUT_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_in_17.json"

_manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))

def cached_path(url):
    meta = _manifest.get(url)
    if meta and meta.get("status") == 200:
        return os.path.join(CACHE_DIR, meta["file"])
    return None

def cached_meta(url):
    return _manifest.get(url)

def strip_html(text):
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def load_text(url):
    p = cached_path(url)
    if not p:
        return None
    raw = open(p, encoding="utf-8", errors="ignore").read()
    return strip_html(raw)

def find_snip(text, needle, window=140):
    if text is None:
        return None
    n = needle.lower()
    t = text.lower()
    i = t.find(n)
    if i < 0:
        return None
    start = max(0, i - window)
    end = min(len(text), i + len(needle) + window)
    return text[start:end]

def find_all_snips(text, needles, window=140):
    out = {}
    for nd in needles:
        out[nd] = find_snip(text, nd, window)
    return out

def init_results():
    if os.path.exists(RESULTS_PATH):
        return json.load(open(RESULTS_PATH, encoding="utf-8"))
    d = {"batch": 17, "results": []}
    json.dump(d, open(RESULTS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return d

def save_result(entry):
    d = init_results()
    # Replace if id exists, else append
    found = False
    for i, r in enumerate(d["results"]):
        if r["id"] == entry["id"]:
            d["results"][i] = entry
            found = True
            break
    if not found:
        d["results"].append(entry)
    json.dump(d, open(RESULTS_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"saved {entry['id']}: {entry['summary']}")

if __name__ == "__main__":
    init_results()
    print("init OK; cache size:", len(_manifest))
