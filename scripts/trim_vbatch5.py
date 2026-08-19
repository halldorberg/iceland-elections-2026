# -*- coding: utf-8 -*-
import json, html, os, re, sys

base = r"F:\Claude Projects\iceland-elections\scripts"
files = json.load(open(os.path.join(base, "vbatch_5.json"), encoding="utf-8"))
outdir = os.path.join(base, "visir_trim_5")
os.makedirs(outdir, exist_ok=True)

for fn in files:
    p = os.path.join(base, "visir_text", fn)
    raw = open(p, encoding="utf-8", errors="replace").read()
    lines = raw.split("\n")
    url = lines[0].replace("URL: ", "").strip()
    title = html.unescape(lines[1].replace("TITLE: ", "")).replace("\xad", "").strip()
    date = lines[3].replace("DATE: ", "").strip()
    body = html.unescape("\n".join(lines[5:])).replace("\xad", "")
    # find article start: after last "Innskráning Skoðun <title>"
    author = ""
    idx = body.rfind("Innskráning Skoðun ")
    if idx >= 0:
        seg = body[idx + len("Innskráning Skoðun "):]
    else:
        seg = body
    # author = text between title and " skrifar"
    m = re.match(re.escape(title) + r"\s+(.{2,60}?)\s+skrifar", seg, re.DOTALL)
    if m:
        author = m.group(1).strip()
        seg = seg[m.end():]
    else:
        m2 = re.search(r"([A-ZÁÐÉÍÓÚÝÞÆÖ][^\n]{2,60}?)\s+skrifar\s+\d+\.", seg)
        if m2:
            author = m2.group(1).strip()
            seg = seg[m2.end():]
    # strip leading date/time like "4. júlí 2026 10:57"
    seg = re.sub(r"^\s*\d+\.?\s*\S+\s+2026\s+\d\d:\d\d\s*", "", seg)
    # cut tail
    for marker in ["Athugið. Vísir hvetur", "Skoðun Mest lesið", "Tengdar fréttir", "Höfundur er"]:
        i = seg.find(marker)
        if i > 0 and marker == "Höfundur er":
            # keep the author-description sentence (next ~200 chars)
            seg = seg[: i + 250]
            break
        if i > 0:
            seg = seg[:i]
            break
    seg = seg.strip()
    if len(seg) > 3300:
        seg = seg[:2800] + "\n[...]\n" + seg[-450:]
    import textwrap
    seg = "\n".join(textwrap.fill(l, 160) for l in seg.split("\n"))
    out = "URL: %s\nTITLE: %s\nAUTHOR: %s\nDATE: %s\n---\n%s\n" % (url, title, author, date, seg)
    open(os.path.join(outdir, fn), "w", encoding="utf-8").write(out)
    print(fn, "|", author, "|", title[:60])
