# -*- coding: utf-8 -*-
import json, html, re, io, sys

base = r"F:\Claude Projects\iceland-elections\scripts"
files = json.load(open(base + r"\vbatch_2.json", encoding="utf-8"))

out = io.open(base + r"\vbatch_2_digest.txt", "w", encoding="utf-8")
for fn in files:
    raw = io.open(base + r"\visir_text\{}".format(fn), encoding="utf-8", errors="replace").read()
    txt = html.unescape(raw)
    lines = txt.split("\n")
    hdr = {}
    body = ""
    for ln in lines:
        if ln.startswith("URL:"): hdr["url"] = ln[4:].strip()
        elif ln.startswith("TITLE:"): hdr["title"] = ln[6:].strip().replace("­", "")
        elif ln.startswith("AUTHOR:"): hdr["author"] = ln[7:].strip()
        elif ln.startswith("DATE:"): hdr["date"] = ln[5:].strip()
    body = txt.split("---\n", 1)[-1]
    body = body.replace("­", "")
    # cut boilerplate: article starts after last "Innskráning Innskráning"
    m = body.rfind("Innskráning Innskráning")
    if m != -1:
        body = body[m + len("Innskráning Innskráning"):]
    # cut tail
    for marker in ["Viltu birta grein á Vísi?", "Senda grein "]:
        t = body.find(marker)
        if t != -1:
            body = body[:t]
            break
    body = re.sub(r"\s+", " ", body).strip()
    # author from "X skrifar" pattern near start
    am = re.search(r"([A-ZÁÉÍÓÚÝÞÆÖÐ][\w\.\-áéíóúýþæöð ]{2,60}?) skrifar ", body)
    author = hdr.get("author") or (am.group(1).strip() if am else "")
    if len(body) > 4200:
        body = body[:4200] + " [...]"
    out.write("==== FILE: {}\nURL: {}\nTITLE: {}\nAUTHOR: {}\nDATE: {}\nBODY: {}\n\n".format(
        fn, hdr.get("url",""), hdr.get("title",""), author, hdr.get("date",""), body))
out.close()
print("done", len(files))
