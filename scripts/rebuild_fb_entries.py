#!/usr/bin/env python3
"""
Rebuild FB-sourced policy entries with quotes verified against live page text
fetched via the CDP-driven Edge session. urllib can't authenticate to FB so the
standard verify_quotes.py fails for FB URLs — this is the manual workaround.
"""
import json
import sys
import time
import urllib.request
import websocket

CDP = "http://localhost:9222"
TAB_ID_PREFIX = sys.argv[1] if len(sys.argv) > 1 else "4C25965E"


def find_tab():
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    for t in tabs:
        if t.get("id", "").lower().startswith(TAB_ID_PREFIX.lower()):
            return t
    raise RuntimeError("FB tab not found")


def fetch_main_text(url):
    t = find_tab()
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
    msg_id = [0]
    def send(method, params=None):
        msg_id[0] += 1
        ws.send(json.dumps({"id": msg_id[0], "method": method, "params": params or {}}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == msg_id[0]:
                return r
    send("Page.enable")
    send("Page.navigate", {"url": url})
    # Poll readyState
    end = time.time() + 30
    while time.time() < end:
        r = send("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
        if r.get("result", {}).get("result", {}).get("value") == "complete":
            break
        time.sleep(0.5)
    time.sleep(3)  # FB renders posts after readyState=complete
    r = send("Runtime.evaluate", {
        "expression": "(document.querySelector('[role=main]')?.textContent||'').replace(/\\s+/g,' ')",
        "returnByValue": True,
    })
    ws.close()
    return r.get("result", {}).get("result", {}).get("value") or ""


# Two FB-sourced entries with carefully chosen verbatim quotes
ENTRIES = [
    {
        "id": "GAR.B",
        "muni_slug": "gardabaer",
        "party_code": "B",
        "platform_url": "https://www.facebook.com/framsokngardabaer",
        "verified_source_kind": "news-with-rationale",
        "audit_status": "KEPT-WITH-RATIONALE",
        "audit_note": "Framsókn Garðabæ Facebook page. Pinned post (29 April 2026) lists 3 áhersluatriði verbatim; April 22 post adds sumarfrístund detail. No other party-owned site found.",
        "recency_evidence": "FB page header shows post dated 'April 29' and 'April 22' 2026; post text references 'sveitastjórnarkosningum 16. maí'.",
        "fb_page": "https://www.facebook.com/framsokngardabaer",
        "tagline": "Framsókn Garðabæ — lýðheilsa, ábyrgur rekstur og fjölskylduvænt skipulag",
        "agenda": [
            {
                "icon": "💚",
                "title": "Lýðheilsa fyrir alla",
                "text": "Lýðheilsa er ein af höfuðáherslum framboðsins fyrir Garðabæ.",
                "source_quote": "Þetta snýst um: 💚 Lýðheilsu fyrir okkur öll",
            },
            {
                "icon": "📊",
                "title": "Ábyrgur rekstur",
                "text": "Forgangsröðun og ábyrgur rekstur sveitarsjóðs er ein af þremur helstu áherslum listans.",
                "source_quote": "💚 Forgangsröðun og ábyrgan rekstur",
            },
            {
                "icon": "🏗️",
                "title": "Skipulag og samfélag",
                "text": "Skipulag og samfélag sem gott er að búa í er meðal aðaláhersluatriða framboðsins.",
                "source_quote": "💚 Skipulag og samfélag sem gott er að búa í",
            },
            {
                "icon": "👨‍👩‍👧",
                "title": "Sumarfrístund fyrir börn",
                "text": "Sumarfrístund út júní og aftur eftir verslunarmannahelgi til að létta undir með barnafjölskyldum.",
                "source_quote": "Sumarfrístund er hjartans mál Framsóknar í Garðabæ",
            },
        ],
    },
    {
        "id": "BOR.D",
        "muni_slug": "borgarbyggd",
        "party_code": "D",
        "platform_url": "https://www.facebook.com/xdborgarbyggd",
        "verified_source_kind": "news-with-rationale",
        "audit_status": "KEPT-WITH-RATIONALE",
        "audit_note": "Sjálfstæðisflokkurinn Borgarbyggð Facebook page. Featured pinned post (22 April 2026) introduces málefnaskrá listing 6 themes verbatim. Detailed bullets are in carousel images not extractable as text; the intro paragraph is what we quote.",
        "recency_evidence": "FB pinned post dated 'April 22' 2026 explicitly references 'sveitarstjórnarkosningar 2026'.",
        "fb_page": "https://www.facebook.com/xdborgarbyggd",
        "tagline": "Sjálfstæðisflokkurinn í Borgarbyggð — málefnaskrá fyrir 2026",
        "agenda": [
            {
                "icon": "🏛️",
                "title": "Ábyrg stjórnsýsla",
                "text": "Ábyrg stjórnsýsla er meðal helstu áhersluatriða listans fyrir kjörtímabilið.",
                "source_quote": "Við leggjum áherslu á ábyrga stjórnsýslu",
            },
            {
                "icon": "🎒",
                "title": "Skóla- og tómstundastarf",
                "text": "Öflugt skóla- og tómstundastarf á að styrkja samfélagið um allt sveitarfélagið.",
                "source_quote": "öflugt skóla- og tómstundastarf",
            },
            {
                "icon": "🏗️",
                "title": "Innviðir, velferð og atvinnulíf",
                "text": "Sterkir innviðir, velferð, uppbygging og fjölbreytt atvinnulíf um allt sveitarfélagið.",
                "source_quote": "sterka innviði, velferð, uppbyggingu og fjölbreytt atvinnulíf um allt sveitarfélagið",
            },
            {
                "icon": "🤝",
                "title": "Samráð og traust",
                "text": "Listinn vill byggja á samráði, trausti og raunhæfum lausnum fyrir íbúa í þéttbýli og dreifbýli.",
                "source_quote": "Við viljum byggja á samráði, trausti og raunhæfum lausnum fyrir íbúa í þéttbýli jafnt sem dreifbýli",
            },
        ],
    },
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # Verify each entry's quotes against live FB textContent
    verified = []
    for entry in ENTRIES:
        url = entry["platform_url"]
        print(f"\n=== {entry['id']} {url} ===")
        body = fetch_main_text(url)
        print(f"  fetched textContent: {len(body)} chars")
        any_miss = False
        for a in entry["agenda"]:
            q = a["source_quote"]
            present = q in body
            a["quote_verified"] = present
            mark = "✓" if present else "✗"
            print(f"  {mark} {a['title']!r}: {q[:60]!r}")
            if not present:
                any_miss = True
        n_match = sum(1 for a in entry["agenda"] if a["quote_verified"])
        n_total = len(entry["agenda"])
        entry["quote_audit"] = f"{n_match}/{n_total} quotes verified against live FB textContent (via CDP)"
        if n_match >= max(3, int(0.75 * n_total)):
            verified.append(entry)
            print(f"  KEEP ({n_match}/{n_total})")
        else:
            print(f"  DROP ({n_match}/{n_total})")

    # Merge with existing AUDITED file (which has BOL.BBK already)
    audited_path = "scan_results/policy_2026-05-01_FB_AUDITED.json"
    try:
        existing = json.load(open(audited_path, encoding="utf-8"))
    except FileNotFoundError:
        existing = {"scan_type": "policy", "scan_date": "2026-05-01", "agent_note": "FB scan", "results": []}
    # Drop any of our entries already in there (so we replace, not duplicate)
    keep_keys = {(e["muni_slug"], e["party_code"]) for e in verified}
    existing["results"] = [r for r in existing.get("results", []) if (r["muni_slug"], r["party_code"]) not in keep_keys]
    existing["results"].extend(verified)
    existing["agent_note"] = (existing.get("agent_note", "") + " | FB-sourced entries verified via CDP fetch").strip()
    with open(audited_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"\nMerged into {audited_path} — {len(existing['results'])} total entries.")


if __name__ == "__main__":
    main()
