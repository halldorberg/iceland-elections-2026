"""Helper for R04 audit. Loads cached HTML and extracts text per URL."""
import json
import re
import os
from html import unescape

CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
MANIFEST = json.load(open(os.path.join(CACHE_DIR, "_manifest.json"), encoding="utf-8"))


def cached_text(url):
    meta = MANIFEST.get(url)
    if not meta:
        return None, "NOT_CACHED"
    p = os.path.join(CACHE_DIR, meta["file"])
    if not os.path.exists(p):
        return None, "FILE_MISSING"
    try:
        with open(p, "rb") as fh:
            data = fh.read()
        # Try utf-8 first; fall back to latin-1
        for enc in ("utf-8", "windows-1252", "latin-1"):
            try:
                raw = data.decode(enc)
                # Heuristic: if utf-8 has many replacement chars, try next
                if enc == "utf-8" and raw.count("�") > 50:
                    continue
                # if mojibake from utf-8 read as latin-1 (Ã° etc), fix
                if enc != "utf-8" and "Ã" in raw[:3000]:
                    try:
                        raw = data.decode("utf-8", errors="replace")
                    except Exception:
                        pass
                break
            except UnicodeDecodeError:
                continue
        else:
            raw = data.decode("utf-8", errors="replace")
    except Exception as e:
        return None, f"ERROR:{e}"
    # Strip script, style
    raw = re.sub(r"<script[\s\S]*?</script>", " ", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", " ", raw, flags=re.I)
    raw = re.sub(r"<!--[\s\S]*?-->", " ", raw)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text, meta.get("status")


def find(url, needle, window=200):
    text, status = cached_text(url)
    if text is None:
        return f"[{status}]"
    if not isinstance(needle, list):
        needle = [needle]
    out = []
    for n in needle:
        i = text.lower().find(n.lower())
        if i >= 0:
            s = max(0, i - window // 2)
            e = min(len(text), i + len(n) + window // 2)
            out.append(text[s:e])
        else:
            out.append(f"NOT_FOUND:{n}")
    return out


if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    needles = sys.argv[2:]
    res = find(url, needles, 300)
    for r in res:
        print("---")
        print(r)
