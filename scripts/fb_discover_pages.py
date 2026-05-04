"""Discover Facebook pages for small-town election lists by driving Edge
through the existing CDP debug port. For each entry in
fb_platform_scan/worklist.json, opens https://www.facebook.com/search/pages/
with a query built from (tagline + muni label), captures the top result(s),
and writes them back into the worklist as candidate fb_urls.

Usage:
    python scripts/fb_discover_pages.py --tab 6FDD7D95 --limit 5

Run without --limit to process every pending entry.

Note: relies on Edge being launched with --remote-debugging-port=9222 and
the user being logged in to facebook.com (so search results render).
"""
from __future__ import annotations
import argparse, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
import websocket

CDP = "http://localhost:9222"
WL  = Path("fb_platform_scan/worklist.json")

def attach(tab_id):
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    tab  = next(t for t in tabs if t["id"].lower().startswith(tab_id.lower()))
    urllib.request.urlopen(f"{CDP}/json/activate/{tab['id']}").read()
    return websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=120)

def make_send(ws):
    mid = [0]
    def send(method, params=None):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid[0]:
                return msg
    return send

def evalj(send, expr, await_promise=False):
    r = send("Runtime.evaluate",
             {"expression": expr, "returnByValue": True, "awaitPromise": await_promise})
    return r.get("result", {}).get("result", {}).get("value")

# The 7 nationally-recognised parties — when the entry uses one of these
# ballot codes, the official party name is the most reliable search query.
NATIONAL_PARTIES = {
    "B": "Framsókn",
    "D": "Sjálfstæðisflokkurinn",
    "S": "Samfylkingin",
    "M": "Miðflokkurinn",
    "V": "Vinstri Græn",
    "C": "Viðreisn",
    "P": "Píratar",
}

POLITICAL_TOKENS = {
    "flokk", "listi", "list-", "framboð", "framsókn", "sjálfstæð",
    "samfylking", "miðflokk", "vinstri", "píratar", "viðreisn",
    "vg", "vg-", "kex", "almannahagur",
}

NEGATIVE_TOKENS = {
    "slysavarn", "kvenfélag", "verslun", "veitingastaður", "kaffihús",
    "líkamsrækt", "skóli", "leikskóli", "sundlaug", "íþróttafélag",
    "kórinn", "tónlistarskól", "matvöruverslun", "söfnuður", "kirkja",
    "barnshafandi",  # "Tvö Líf" type pages
}

def build_queries(entry: dict) -> list[str]:
    """Best-effort search queries, most-specific first."""
    qs = []
    code  = entry.get("party_code") or ""
    label = entry.get("party_label") or ""
    muni  = entry.get("muni_label") or ""
    tag   = entry.get("tagline") or ""

    short = tag.split(" — ")[0].split(" – ")[0].strip() if tag else ""

    # National-party lists: the most reliable query is the party name + muni.
    if code in NATIONAL_PARTIES:
        qs.append(f"{NATIONAL_PARTIES[code]} {muni}")
        if label and label != NATIONAL_PARTIES[code]:
            qs.append(f"{label} {muni}")
        # Only fall back to the slogan-short if it actually contains a
        # political token — otherwise it picks up generic words like "Líf".
        if short and any(t in short.lower() for t in POLITICAL_TOKENS):
            qs.append(f"{short} {muni}")
    else:
        # Local lists: the canonical short name from the tagline is usually
        # the literal page name (e.g. "L-listinn", "Vegvísir", "Þ-listinn").
        if short and len(short) >= 4 and short.lower() != muni.lower():
            qs.append(f"{short} {muni}")
        if label and muni and label not in qs:
            qs.append(f"{label} {muni}")
        if tag and len(tag) < 80 and tag not in qs:
            qs.append(tag)
        if short and short not in qs:
            qs.append(short)
    return [q for q in qs if q.strip()]

# A representative cross-section of Iceland's munis whose names commonly
# show up in FB pages we DON'T want — used to detect "wrong muni" hits
# (e.g. "Sjálfstæðisflokkurinn Borgarbyggð" when we're searching Skaftárhreppur).
KNOWN_MUNI_TOKENS = [
    "reykjavík", "kópavog", "hafnarfj", "garðabæ", "mosfellsbæ", "akureyri",
    "seltjarnar", "reykjanes", "suðurnes", "árborg", "vestmannaey",
    "fjarðabyg", "akranes", "borgarby", "ísafjarð", "vog", "skaftárh",
    "hrunamann", "skeiða", "hörgárs", "húnaþing", "húnavatns", "húnabyg",
    "skagafj", "hornafj", "norðurþ", "rangárþ", "dalvíkur", "hvalfj",
    "svalbarðs", "skagaströ", "hveragerð", "grindav", "mýrdal", "bláskóga",
    "flóahrep", "grímsne", "skeiða", "eyjafj", "stykkishó", "grundarfj",
    "bolungarv", "súðavík", "vesturby", "strandaby", "reykhóla", "múlaþ",
    "þingeyj", "fjallaby", "snæfellsbæ", "kjósarh", "vopnafj", "tjörnes",
    "árnesh", "ölfus", "norðvesturkj",  # kjördæmi (region — not a muni)
]

def muni_token(muni_label: str) -> str:
    """4–5 char lowercase prefix of the muni used for substring matching.
    Handles Icelandic case-endings: 'Akranes' is contained in 'Akranesi'."""
    return (muni_label or "").lower()[:5]

def label_contains_muni(label: str, muni_label: str) -> bool:
    if not muni_label:
        return False
    lab = label.lower()
    # try several candidate stems for tougher names
    stems = {
        muni_label.lower(),
        muni_label.lower().rstrip("ur"),
        muni_label.lower()[:4],
        muni_label.lower()[:5],
        muni_label.lower()[:6],
    }
    return any(s and s in lab for s in stems)

def label_has_other_muni(label: str, our_muni: str) -> bool:
    """True iff the label name-drops a *different* muni than ours."""
    lab = label.lower()
    our = (our_muni or "").lower()
    for tok in KNOWN_MUNI_TOKENS:
        if tok in lab and tok not in our:
            return True
    return False

def label_has_other_party(label: str, our_code: str) -> bool:
    """True iff the label name-drops a national party that ISN'T ours."""
    lab = label.lower()
    for code, name in NATIONAL_PARTIES.items():
        if code == our_code:
            continue
        # 7-char prefix to match inflected forms (Sjálfstæð, Framsókn, Miðflokk…)
        stem = name.lower()[:7]
        if stem in lab:
            return True
    return False

def score_hit(label: str, query: str, muni: str, party_label: str, code: str) -> int:
    """Cheap relevance score — higher is better; <1 is rejected."""
    lab = label.lower()
    if any(t in lab for t in NEGATIVE_TOKENS):
        return -1
    # Hard requirement: label must contain our muni's stem.
    if not label_contains_muni(label, muni):
        return -1
    # Hard reject: label name-drops a different muni than ours.
    if label_has_other_muni(label, muni):
        return -1
    # Hard reject: label name-drops a different national party than ours.
    if label_has_other_party(label, code):
        return -1
    # Hard reject: label is JUST the muni name (likely the muni's own page).
    label_words = [w for w in re.split(r"\s+", label.strip()) if w]
    muni_words  = [w for w in re.split(r"\s+", (muni or "").strip()) if w]
    if [w.lower() for w in label_words] == [w.lower() for w in muni_words]:
        return -1
    # For NATIONAL_PARTIES we additionally require the party-name signal in the
    # label (so we don't end up matching a similarly-spelled list of the wrong
    # party that happens to be in the same muni).
    if code in NATIONAL_PARTIES and NATIONAL_PARTIES[code].lower() not in lab:
        return -1
    score = 2  # passed all hard checks — base score
    if code in NATIONAL_PARTIES and NATIONAL_PARTIES[code].lower() in lab:
        score += 3
    elif party_label and any(w.lower() in lab for w in party_label.split() if len(w) >= 4):
        score += 2
    if any(t in lab for t in POLITICAL_TOKENS):
        score += 1
    qtoks = [t.lower() for t in query.split() if len(t) >= 3]
    overlap = sum(1 for t in qtoks if t in lab)
    score += min(2, overlap)
    return score

CAPTURE_JS = r"""
(()=>{
  // FB search pages are SPA — find every link to a profile/page that has a
  // visible image + text label.
  const out = [];
  const seen = new Set();
  const links = document.querySelectorAll('a[href*="/profile.php?id="], a[href^="https://www.facebook.com/"]');
  for (const a of links) {
    const href = a.href.split('?')[0] + (a.href.includes('?id=') ? '?' + a.href.split('?')[1].split('&')[0] : '');
    if (seen.has(href)) continue;
    if (!/facebook\.com\/(profile\.php\?id=\d+|[^\/]+\/?$)/.test(href)) continue;
    if (/\/search\/|\/groups\/|\/photo\/|\/posts\//.test(href)) continue;
    if (/messages|notifications|marketplace|events|reels/.test(href)) continue;
    const txt = (a.innerText || a.textContent || '').trim();
    if (!txt || txt.length < 3 || txt.length > 200) continue;
    // Skip nav links
    if (/^(Home|See all|More|Friends|Photos|Videos|See more|Like|Following)$/i.test(txt)) continue;
    seen.add(href);
    out.push({ url: href, label: txt.slice(0, 120) });
    if (out.length >= 8) break;
  }
  return JSON.stringify(out);
})()
"""

def discover_one(send, entry: dict, debug=False) -> tuple[str, str] | None:
    """Try each search query in turn; return (url, label) of best hit or None."""
    queries = build_queries(entry)
    for q in queries:
        url = f"https://www.facebook.com/search/pages/?q={urllib.parse.quote(q)}"
        send("Page.navigate", {"url": url})
        time.sleep(4)
        # Wait for results to render
        for _ in range(5):
            time.sleep(1)
            try:
                txt = evalj(send, "document.body.innerText.length") or 0
                if txt > 1000:
                    break
            except Exception:
                pass
        # Capture
        try:
            raw = evalj(send, CAPTURE_JS) or "[]"
            results = json.loads(raw)
        except Exception:
            results = []
        if debug:
            print(f"      query={q!r}  hits={len(results)}", file=sys.stderr)
            for r in results[:3]:
                print(f"        - {r['label']!r}  {r['url']}", file=sys.stderr)
        if not results:
            continue
        scored = []
        for r in results:
            s = score_hit(r['label'], q, entry.get("muni_label",""),
                          entry.get("party_label",""), entry.get("party_code",""))
            scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        best_score, best = scored[0]
        if debug:
            print(f"      best score={best_score}  hit={best['label']!r}", file=sys.stderr)
        # Require a meaningful score — at least muni + party signal
        if best_score >= 4:
            return best['url'], best['label']
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tab", default="6FDD7D95")
    ap.add_argument("--limit", type=int, default=0,
                    help="process at most N pending entries (0 = all)")
    ap.add_argument("--id", help="only process this single entry id")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--retry-failed", action="store_true",
                    help="re-discover entries previously marked no_fb_page")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    wl = json.loads(WL.read_text(encoding="utf-8"))
    pending = [e for e in wl["entries"]
               if (args.id and e["id"] == args.id)
               or (not args.id and not e.get("fb_url")
                   and (args.retry_failed or e.get("scrape_status") == "pending"))]
    if args.limit:
        pending = pending[:args.limit]
    print(f"discovering FB pages for {len(pending)} entries (of {len(wl['entries'])})")

    ws   = attach(args.tab)
    send = make_send(ws)
    send("Page.enable")

    found_count = 0
    for i, entry in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {entry['id']}  {entry['muni_label']}  {entry['party_label']}")
        try:
            hit = discover_one(send, entry, debug=args.debug)
        except Exception as e:
            print(f"   ! error: {e}")
            hit = None
        if hit:
            url, label = hit
            entry["fb_url"]       = url
            entry["fb_page_name"] = label
            entry["scrape_status"] = "fb_found"
            found_count += 1
            print(f"   ✓ {label}  →  {url}")
        else:
            entry["scrape_status"] = "no_fb_page"
            print(f"   – no FB page found")
        # Persist after each entry — long runs survive interruptions
        WL.write_text(json.dumps(wl, ensure_ascii=False, indent=2), encoding="utf-8")

    ws.close()
    print(f"\nDone — {found_count}/{len(pending)} pages found and saved")

if __name__ == "__main__":
    main()
