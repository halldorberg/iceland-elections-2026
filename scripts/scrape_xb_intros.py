"""Scrape all "Kynning á frambjóðanda - N sæti." posts from the Strandabyggð
Framsókn FB page (id=61585879199774). Uses the existing Edge CDP tab
6FDD7D95. Scrolls in small steps so posts stay in DOM long enough to
capture, and writes a single JSON dump.

Each captured entry: { n, name, bio_is, bio_en, photo_url, permalink }.
"""
from __future__ import annotations
import base64, json, re, sys, time, urllib.request
import websocket

CDP   = "http://localhost:9222"
TAB   = "6FDD7D95"
OUT   = "C:/Windows/Temp/xb_intros.json"

def attach():
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    tab  = next(t for t in tabs if t["id"].lower().startswith(TAB.lower()))
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

# JS that finds every "Kynning á frambjóðanda - N sæti." block currently
# in the DOM and returns the post's own text + photo URL + permalink.
# Tight regex so we only match the literal intro marker (not "1. Ábyrg…").
CAPTURE_JS = r"""
(()=>{
  const out = [];
  const seen = new Set();
  // Walk every text node that contains the intro marker
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
  let node;
  while (node = walker.nextNode()) {
    const m = node.textContent.match(/Kynning\s+á\s+frambjóðanda\s*-\s*(\d{1,2})[.\s]*sæti/i);
    if (!m) continue;
    const n = parseInt(m[1], 10);
    if (seen.has(n)) continue;
    seen.add(n);

    // Walk up to a sensible post container — stop when the ancestor's
    // text length grows past ~6000 chars (likely we've hit the whole page).
    let root = node.parentElement;
    let prev = root;
    while (root && root.parentElement) {
      const tlen = root.textContent.length;
      if (tlen > 6000) break;
      prev = root;
      root = root.parentElement;
    }
    root = prev; // last good ancestor
    const text = root.textContent || '';
    const img = root.querySelector('img[src*="fbcdn"]:not([src*="static"])');
    const link = root.querySelector('a[href*="/permalink/"], a[href*="story_fbid"], a[href*="/posts/"]');

    out.push({
      n, text: text.slice(0, 5000),
      photo_url: img ? img.src : null,
      permalink: link ? link.href : null,
    });
  }
  return JSON.stringify(out);
})()
"""

def main():
    ws   = attach()
    send = make_send(ws)
    send("Page.enable")

    # Reset to top
    send("Runtime.evaluate", {"expression": "window.scrollTo(0, 0)"})
    time.sleep(2)

    found: dict[int, dict] = {}
    last_height = 0
    no_growth_iters = 0
    max_iters = 100

    for it in range(max_iters):
        # Click any "See more" buttons inside intro posts so we capture
        # the full text instead of the truncated preview.
        send("Runtime.evaluate", {"expression": r"""
(()=>{
  const btns = Array.from(document.querySelectorAll('[role="button"]'))
    .filter(b => /^see more$|^sjá meira$/i.test(b.textContent.trim()));
  let clicked = 0;
  btns.forEach(b => { try { b.click(); clicked++; } catch(e){} });
  return clicked;
})()
"""})
        time.sleep(0.8)

        # Capture currently-visible intro posts
        res = send("Runtime.evaluate", {"expression": CAPTURE_JS, "returnByValue": True})
        try:
            captured = json.loads(res["result"]["result"]["value"])
        except Exception:
            captured = []
        for entry in captured:
            n = entry["n"]
            # Update if we found one with more text or a photo we didn't have
            existing = found.get(n)
            if not existing \
               or len(entry["text"]) > len(existing.get("text") or "") \
               or (entry["photo_url"] and not existing.get("photo_url")) \
               or (entry["permalink"] and not existing.get("permalink")):
                found[n] = entry

        # scrollHeight + scrollY
        res = send("Runtime.evaluate", {"expression":
            "JSON.stringify({h: document.body.scrollHeight, sy: window.scrollY, vh: window.innerHeight})",
            "returnByValue": True})
        s = json.loads(res["result"]["result"]["value"])

        print(f"  iter {it+1}: y={s['sy']}/{s['h']} captured n={sorted(found.keys())}", flush=True)

        if len(found) >= 10:
            print("  all 10 captured, stop")
            break

        # Did the page grow?
        if s["h"] == last_height:
            no_growth_iters += 1
            if no_growth_iters >= 8 and s["sy"] + s["vh"] >= s["h"] - 100:
                print("  bottom reached and no growth, stop")
                break
        else:
            no_growth_iters = 0
        last_height = s["h"]

        # Scroll down ~30% viewport — small steps so each post overlaps
        # multiple iterations and can't slip past the lazy-render window.
        send("Runtime.evaluate", {"expression": "window.scrollBy({top: window.innerHeight * 0.3, behavior: 'instant'})"})
        time.sleep(2.5)  # let posts render

    ws.close()

    # Save
    out = {"count": len(found), "candidates": [found[k] for k in sorted(found)]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  saved {len(found)} entries -> {OUT}")
    for c in out["candidates"]:
        print(f"  {c['n']}: text={len(c['text'])} chars, photo={'yes' if c['photo_url'] else 'no'}, link={'yes' if c['permalink'] else 'no'}")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
