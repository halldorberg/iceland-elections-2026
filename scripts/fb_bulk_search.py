#!/usr/bin/env python3
"""
For a list of (id, queries[], muni_label_substring), do FB pages search,
return top matching slug whose label contains the muni substring (case-insens).
"""
import json
import sys
import time
import urllib.request
import urllib.parse
import websocket

CDP = "http://localhost:9222"
TAB_PREFIX = "4C25965E"
MSG_ID = 0


def list_tabs():
    return json.loads(urllib.request.urlopen(f"{CDP}/json").read())


def find_tab(tab_id):
    for t in list_tabs():
        if t.get("id", "").lower().startswith(tab_id.lower()):
            return t
    return None


def send(ws, method, params=None):
    global MSG_ID
    MSG_ID += 1
    payload = {"id": MSG_ID, "method": method, "params": params or {}}
    ws.send(json.dumps(payload))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == MSG_ID:
            return msg


def evaluate(ws, expr):
    res = send(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return res.get("result", {}).get("result", {}).get("value")


def wait_complete(ws, timeout=12):
    end = time.time() + timeout
    while time.time() < end:
        if evaluate(ws, "document.readyState") == "complete":
            return True
        time.sleep(0.5)
    return False


def navigate(ws, url, settle=2):
    send(ws, "Page.enable")
    send(ws, "Page.navigate", {"url": url})
    wait_complete(ws, 12)
    time.sleep(settle)


SEARCH_JS = r"""
(function(){
  const main = document.querySelector('[role=main]');
  if (!main) return [];
  const seen = new Set();
  const out = [];
  for (const a of main.querySelectorAll('a[href*="facebook.com/"]')) {
    const m = a.href.match(/facebook\.com\/([^/?#]+)/);
    if (!m) continue;
    const slug = m[1];
    if (/^(login|search|help|policies|hashtag|profile\.php|pages|groups|events|watch|marketplace|reel|stories|sharer|business|legal|privacy|policy|home\.php|share|gaming|notifications|messages|saved|settings)$/.test(slug)) continue;
    if (seen.has(slug)) continue;
    seen.add(slug);
    let label = '';
    let el = a;
    for (let i = 0; i < 6 && el; i++) {
      const t = (el.textContent || '').trim();
      if (t && t.length > 2 && t.length < 200) { label = t; break; }
      el = el.parentElement;
    }
    out.push({slug: slug, label: label.replace(/\s+/g,' ').slice(0,200)});
    if (out.length >= 8) break;
  }
  return out;
})()
"""


def search(ws, query):
    url = "https://www.facebook.com/search/pages/?q=" + urllib.parse.quote(query)
    navigate(ws, url, settle=3)
    return evaluate(ws, SEARCH_JS) or []


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) < 3:
        print("Usage: fb_bulk_search.py <input.json> <output.json>"); sys.exit(1)
    inp = json.load(open(sys.argv[1], encoding="utf-8"))
    out_path = sys.argv[2]
    t = find_tab(TAB_PREFIX)
    if not t:
        print(json.dumps({"error": "no tab"})); sys.exit(1)
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
    out = []
    for entry in inp:
        eid = entry["id"]
        muni_substr = entry.get("muni_substr", "").lower()
        result = {"id": eid, "matches": [], "best": None}
        for q in entry["queries"]:
            try:
                hits = search(ws, q)
            except Exception as e:
                hits = []
            for h in hits:
                lab = (h.get("label") or "").lower()
                slug = (h.get("slug") or "").lower()
                if muni_substr and (muni_substr in lab or muni_substr in slug):
                    if h not in result["matches"]:
                        result["matches"].append(h)
                    if not result["best"]:
                        result["best"] = h
            if result["best"]:
                break
        out.append(result)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        sys.stderr.write(f"[{len(out)}/{len(inp)}] {eid} -> {result['best']['slug'] if result['best'] else 'none'}\n")
        sys.stderr.flush()
    ws.close()


if __name__ == "__main__":
    main()
