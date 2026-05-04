"""For each entry in fb_platform_scan/worklist.json with a discovered fb_url,
open the page in Edge, scroll through the visible feed + the Featured/About
section, and try to extract a platform/agenda. Writes findings back into
the worklist; entries get scrape_status:
  * scraped       — found a usable platform block
  * no_platform   — page exists but no agenda-style content visible
  * fetch_error   — page wouldn't load

Usage:
    python scripts/fb_scrape_platforms.py --tab 6FDD7D95 --limit 5
"""
from __future__ import annotations
import argparse, json, re, sys, time, urllib.request
from pathlib import Path
import websocket

CDP = "http://localhost:9222"
WL  = Path("fb_platform_scan/worklist.json")

# Words that signal "this post is the platform/agenda" — case-insensitive.
PLATFORM_SIGNALS = [
    "stefnumál", "stefnumáli", "stefnu", "stefnan", "stefna okkar", "okkar áherslur",
    "áherslur", "áherslumál", "okkar helstu", "framtíðarsýn", "stefnuskrá",
    "kosningamál", "okkar markmið", "okkar baráttumál", "ábyrgð – traust",
    "for the upcoming", "main goals", "our policies",
]

def attach(tab_id):
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    tab  = next(t for t in tabs if t["id"].lower().startswith(tab_id.lower()))
    urllib.request.urlopen(f"{CDP}/json/activate/{tab['id']}").read()
    return websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=120)

def make_send(ws):
    mid = [0]
    def send(m, p=None):
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": m, "params": p or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid[0]:
                return msg
    return send

def evalj(send, expr, await_promise=False):
    r = send("Runtime.evaluate",
             {"expression": expr, "returnByValue": True, "awaitPromise": await_promise})
    return r.get("result", {}).get("result", {}).get("value")

CLICK_SEE_MORES = r"""
(()=>{
  const btns = Array.from(document.querySelectorAll('[role="button"]'))
    .filter(b => /^(see more|sjá meira|see all|sjá allt)$/i.test(b.textContent.trim()));
  let clicked = 0;
  btns.forEach(b => { try { b.click(); clicked++; } catch(e){} });
  return clicked;
})()
"""

# Scan every text node for blocks that look like a platform/agenda.
# Filters out text inside <script>/<style> (FB's internal data bundles),
# and walks up to a real post-shaped ancestor (text length 200-8000 chars).
EXTRACT_JS = r"""
(()=>{
  const out = [];
  const seen = new Set();
  const signals = __SIGNALS__;
  // Reject text whose ancestor chain includes <script>, <style>, or noscript
  function inSkippableAncestor(node) {
    let p = node.parentElement;
    while (p) {
      const tn = p.tagName;
      if (tn === 'SCRIPT' || tn === 'STYLE' || tn === 'NOSCRIPT' || tn === 'TEMPLATE') return true;
      p = p.parentElement;
    }
    return false;
  }
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: n => inSkippableAncestor(n) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
  });
  let node;
  while (node = walker.nextNode()) {
    const t = node.textContent;
    if (!t || t.length < 60) continue;
    const tl = t.toLowerCase();
    if (!signals.some(s => tl.includes(s))) continue;
    let p = node.parentElement;
    let prev = p;
    while (p && p.parentElement) {
      const len = (p.innerText || '').length;
      if (len > 8000) break;
      prev = p;
      p = p.parentElement;
    }
    const text = (prev.innerText || '').trim();
    if (text.length < 200) continue;  // too short to be a real platform post
    const sig = text.slice(0, 80);
    if (seen.has(sig)) continue;
    seen.add(sig);
    out.push({ text: text.slice(0, 8000) });
    if (out.length >= 6) break;
  }
  return JSON.stringify(out);
})()
"""

def scrape_one(send, url: str, slow_scroll=True) -> dict:
    """Open the page, scroll, click see-mores, return any platform-like text blocks."""
    send("Page.navigate", {"url": url})
    time.sleep(6)
    # Wait for page render
    for _ in range(8):
        time.sleep(1)
        try:
            ln = evalj(send, "document.body.innerText.length") or 0
            if ln > 1500:
                break
        except Exception:
            pass
    # Scroll thoroughly — small overlapping steps so each post stays in DOM
    # long enough to be captured, with see-more clicks on every step to
    # expand truncated platform posts (same pattern as the XB scrape).
    if slow_scroll:
        captures = []
        for step in range(0, 12000, 400):
            evalj(send, f"window.scrollTo(0, {step})")
            time.sleep(1.8)
            evalj(send, CLICK_SEE_MORES)
            time.sleep(0.6)
            # Capture what's currently visible — accumulate across iterations
            try:
                expr = EXTRACT_JS.replace("__SIGNALS__", json.dumps(PLATFORM_SIGNALS))
                raw = evalj(send, expr) or "[]"
                blocks = json.loads(raw)
                for b in blocks:
                    sig = b["text"][:80]
                    if not any(c["text"].startswith(b["text"][:80]) for c in captures):
                        captures.append(b)
            except Exception:
                pass
            # Stop early if we've hit the bottom
            sh = evalj(send, "JSON.stringify({h:document.body.scrollHeight, sy:window.scrollY, vh:window.innerHeight})")
            try:
                s = json.loads(sh)
                if s["sy"] + s["vh"] >= s["h"] - 100 and step >= 2000:
                    break
            except Exception:
                pass
        intro = evalj(send, "document.querySelector('[role=\"main\"]')?.innerText?.slice(0, 800) || ''") or ""
        return { "blocks": captures, "intro": intro[:800] }
    # Capture
    expr = EXTRACT_JS.replace("__SIGNALS__", json.dumps(PLATFORM_SIGNALS))
    raw = evalj(send, expr) or "[]"
    try:
        blocks = json.loads(raw)
    except Exception:
        blocks = []
    # Also capture page intro text
    intro = evalj(send, "document.querySelector('[role=\"main\"]')?.innerText?.slice(0, 800) || ''") or ""
    return { "blocks": blocks, "intro": intro[:800] }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tab", default="6FDD7D95")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--id", help="single entry id to scrape")
    args = ap.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    wl = json.loads(WL.read_text(encoding="utf-8"))
    pending = [e for e in wl["entries"]
               if (args.id and e["id"] == args.id)
               or (not args.id and e.get("fb_url") and e.get("scrape_status") == "fb_found")]
    if args.limit:
        pending = pending[:args.limit]
    print(f"scraping platform from {len(pending)} pages")

    ws   = attach(args.tab)
    send = make_send(ws)
    send("Page.enable")

    found = 0
    for i, entry in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {entry['id']}  {entry['fb_url']}")
        try:
            res = scrape_one(send, entry["fb_url"])
        except Exception as e:
            entry["scrape_status"] = "fetch_error"
            entry["scrape_error"]  = str(e)
            print(f"   ! error: {e}")
            WL.write_text(json.dumps(wl, ensure_ascii=False, indent=2), encoding="utf-8")
            continue
        if res["blocks"]:
            entry["platform_text"] = res["blocks"][0]["text"]
            entry["platform_text_more"] = [b["text"] for b in res["blocks"][1:]] or None
            entry["scrape_status"] = "scraped"
            entry["intro"] = res.get("intro")
            found += 1
            print(f"   ✓ found {len(res['blocks'])} platform-like block(s) ({len(res['blocks'][0]['text'])} chars)")
        else:
            entry["scrape_status"] = "no_platform"
            entry["intro"] = res.get("intro")
            print(f"   – no platform-like text found")
        WL.write_text(json.dumps(wl, ensure_ascii=False, indent=2), encoding="utf-8")

    ws.close()
    print(f"\nDone — {found}/{len(pending)} pages yielded a platform block")

if __name__ == "__main__":
    main()
