"""R07 helpers: cache lookup + text extraction + incremental writer."""
import json, os, re, sys, io
from html import unescape

# Force UTF-8 stdout on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
MANIFEST = os.path.join(CACHE_DIR, "_manifest.json")
RESULT_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_R07.json"
INPUT_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_in_R07.json"

with open(MANIFEST, encoding="utf-8") as f:
    MAN = json.load(f)


def cached_meta(url):
    return MAN.get(url)


def cached_text(url, max_len=200000):
    meta = MAN.get(url)
    if not meta:
        return None, "missing"
    status = meta.get("status")
    fp = os.path.join(CACHE_DIR, meta.get("file", ""))
    if not os.path.exists(fp):
        return None, f"file_missing(status={status})"
    # try utf-8 first, fall back to windows-1252
    with open(fp, "rb") as f:
        rb = f.read()
    enc = meta.get("encoding") or ""
    raw = None
    for try_enc in ([enc] if enc else []) + ["utf-8", "cp1252", "latin-1"]:
        try:
            raw = rb.decode(try_enc, errors="strict")
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if raw is None:
        raw = rb.decode("utf-8", errors="ignore")
    # detect mojibake: lots of unicode replacement or "Ã" chars
    # heuristic: if "ð" appears, ok; if "�" cluster, retry cp1252
    if raw.count("�") > 30:
        try:
            raw = rb.decode("cp1252", errors="replace")
        except Exception:
            pass
    # strip script/style
    raw = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style[^>]*>.*?</style>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_len], f"ok(status={status})"


def search(text, needle, window=120):
    if not text:
        return []
    out = []
    idx = 0
    nl = needle.lower()
    tl = text.lower()
    while True:
        i = tl.find(nl, idx)
        if i < 0:
            break
        s = max(0, i - window)
        e = min(len(text), i + len(needle) + window)
        out.append(text[s:e])
        idx = i + len(needle)
        if len(out) >= 5:
            break
    return out


def load_results():
    if os.path.exists(RESULT_PATH):
        with open(RESULT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"batch": "R07", "results": []}


def save_result(entry):
    data = load_results()
    # remove existing entry with same id
    data["results"] = [r for r in data["results"] if r.get("id") != entry["id"]]
    data["results"].append(entry)
    with open(RESULT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"saved {entry['id']} (total={len(data['results'])})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        with open(INPUT_PATH, encoding="utf-8") as f:
            d = json.load(f)
        for c in d["candidates"]:
            print(c["id"], c["name"])
    elif cmd == "text":
        url = sys.argv[2]
        t, status = cached_text(url)
        print(status)
        if t:
            print(t[:5000])
    elif cmd == "find":
        url = sys.argv[2]
        needle = sys.argv[3]
        t, status = cached_text(url)
        print(status)
        if t:
            for s in search(t, needle, int(sys.argv[4]) if len(sys.argv) > 4 else 200):
                print("---")
                print(s)
