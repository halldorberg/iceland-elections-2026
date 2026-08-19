import json, html, re, os

base = r"F:\Claude Projects\iceland-elections\scripts"
files = json.load(open(os.path.join(base, "vbatch_1.json"), encoding="utf-8"))
outdir = os.path.join(base, "visir_clean_1")
os.makedirs(outdir, exist_ok=True)

for fn in files:
    raw = open(os.path.join(base, "visir_text", fn), encoding="utf-8", errors="replace").read()
    lines = raw.split("\n")
    hdr = {}
    for l in lines[:4]:
        if ":" in l:
            k, v = l.split(":", 1)
            hdr[k.strip()] = html.unescape(v.strip())
    body = "\n".join(lines[5:])
    body = html.unescape(body)
    # article body starts after last "Innskráning Innskráning Skoðun"
    m = re.search(r"Innskráning\s+Innskráning\s+Skoðun", body)
    if m:
        body = body[m.end():]
    # cut at end marker
    for marker in ["Viltu birta grein á Vísi?", "Senda grein "]:
        idx = body.find(marker)
        if idx > 0:
            body = body[:idx]
            break
    body = re.sub(r"\s+", " ", body).strip()
    out = f"URL: {hdr.get('URL','')}\nTITLE: {hdr.get('TITLE','')}\nAUTHOR: {hdr.get('AUTHOR','')}\nDATE: {hdr.get('DATE','')}\nLEN: {len(body)}\n---\n"
    # wrap body at ~120 chars per line for readability
    words = body.split(" ")
    line = []
    ll = 0
    wrapped = []
    for w in words:
        line.append(w)
        ll += len(w) + 1
        if ll > 110:
            wrapped.append(" ".join(line))
            line = []
            ll = 0
    if line:
        wrapped.append(" ".join(line))
    out += "\n".join(wrapped) + "\n"
    open(os.path.join(outdir, fn), "w", encoding="utf-8").write(out)

print("done", len(files))
