"""Helper for batch 10 audit. Run: python -i _audit10_helper.py"""
import re, json, os, sys

CACHE = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
RESULT_PATH = r"F:\Claude Projects\iceland-elections\scan_results\audit_results_10.json"
MANIFEST = json.load(open(os.path.join(CACHE, "_manifest.json"), encoding="utf-8"))


def text_of(url):
    meta = MANIFEST.get(url)
    if not meta:
        return None, None
    if meta.get("status") != 200:
        return None, meta
    p = os.path.join(CACHE, meta["file"])
    if not os.path.exists(p):
        return None, meta
    h = open(p, encoding="utf-8", errors="replace").read()
    h = re.sub(r"<script[^>]*>.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", h)
    # decode common entities
    t = (t
         .replace("&aacute;", "á").replace("&Aacute;", "Á")
         .replace("&eacute;", "é").replace("&Eacute;", "É")
         .replace("&iacute;", "í").replace("&Iacute;", "Í")
         .replace("&oacute;", "ó").replace("&Oacute;", "Ó")
         .replace("&uacute;", "ú").replace("&Uacute;", "Ú")
         .replace("&yacute;", "ý").replace("&Yacute;", "Ý")
         .replace("&aelig;", "æ").replace("&AElig;", "Æ")
         .replace("&oslash;", "ø").replace("&Oslash;", "Ø")
         .replace("&aring;", "å").replace("&Aring;", "Å")
         .replace("&thorn;", "þ").replace("&THORN;", "Þ")
         .replace("&eth;", "ð").replace("&ETH;", "Ð")
         .replace("&ouml;", "ö").replace("&Ouml;", "Ö")
         .replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
         .replace("&nbsp;", " "))
    t = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), t)
    t = re.sub(r"\s+", " ", t).strip()
    return t, meta


def find(url, name, window=300):
    t, _ = text_of(url)
    if not t:
        return None
    # try various forms (drop accents)
    needles = [name, name.split()[0]]
    for n in needles:
        i = t.lower().find(n.lower())
        if i >= 0:
            return t[max(0, i - window):i + window + len(n)]
    return None


def save(result):
    data = json.load(open(RESULT_PATH, encoding="utf-8"))
    # replace if already present
    data["results"] = [r for r in data["results"] if r["id"] != result["id"]]
    data["results"].append(result)
    json.dump(data, open(RESULT_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("saved", result["id"], "->", result["summary"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        win = int(sys.argv[3]) if len(sys.argv) > 3 else 400
        if name:
            print(find(url, name, win))
        else:
            t, _ = text_of(url)
            print(t[:5000] if t else "no cache")
