import re, html, pathlib
outdir = pathlib.Path("tmp_dv/text"); outdir.mkdir(exist_ok=True)
tag_re = re.compile(r'<(/?)div\b', re.I)
idx = []
for f in sorted(pathlib.Path("tmp_dv/articles").glob("*.html")):
    h = f.read_text(encoding="utf-8", errors="replace")
    t = re.search(r"<title>([^<]*)", h)
    title = html.unescape(t.group(1)).split("| DV")[0].strip() if t else ""
    m = re.match(r"(\d{4})_(\d{2})_(\d{2})_(.*)", f.stem)
    date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    start = h.find('field--name-body')
    body = ""
    if start != -1:
        gt = h.find('>', start)
        depth = 1; pos = gt + 1
        for mm in tag_re.finditer(h, gt + 1):
            depth += -1 if mm.group(1) else 1
            if depth == 0:
                body = h[gt+1:mm.start()]; break
    body = re.sub(r'<script.*?</script>', ' ', body, flags=re.S|re.I)
    body = re.sub(r'<style.*?</style>', ' ', body, flags=re.S|re.I)
    body = re.sub(r'<figcaption.*?</figcaption>', ' ', body, flags=re.S|re.I)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = html.unescape(body)
    body = re.sub(r'\s+', ' ', body).strip()
    (outdir / (f.stem + ".txt")).write_text(title + "\n" + date + "\n" + body, encoding="utf-8")
    kw = len(re.findall(r'(?i)\bESB\b|evrópusamband|aðildarviðræð|þjóðaratkvæð|\bevru\b|evran|evrunn|\baðild\b|aðildar\b|Brussel|viðræð', title + " " + body))
    idx.append((f.stem, kw, len(body), title))
idx.sort(key=lambda x: -x[1])
with open("tmp_dv/index.tsv", "w", encoding="utf-8") as out:
    for s, k, l, t in idx:
        out.write(f"{k}\t{l}\t{s}\t{t}\n")
