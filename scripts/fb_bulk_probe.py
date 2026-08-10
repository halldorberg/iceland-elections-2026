#!/usr/bin/env python3
"""
Bulk probe FB slugs for a list of parties. For each tuple (id, candidate_slugs[]),
navigate to each slug and report whether it's a real page.
Output JSON to stdout.
"""
import json
import sys
import time
import urllib.request
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


def wait_complete(ws, timeout=15):
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


def probe_slug(ws, slug):
    navigate(ws, f"https://www.facebook.com/{slug}", settle=2)
    js = r"""
    (function(){
      const main = document.querySelector('[role=main]');
      const tc = (main && main.textContent || '').replace(/\s+/g,' ');
      const isUnavailable = /This content isn't available/i.test(tc);
      const isPersonal = /Add friend/i.test(tc) && /\d+ friends?/.test(tc) && !/followers/.test(tc);
      // get the page-name-ish prefix
      let pname = null;
      const m = tc.match(/^([^•·]{3,140}?)\s*(\d[\d.,K]* followers|\d+ friends|·)/);
      if (m) pname = m[1].trim();
      return {
        unavailable: isUnavailable,
        personal: isPersonal,
        pageName: pname,
        sample: tc.slice(0, 250)
      };
    })()
    """
    return evaluate(ws, js)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) < 2:
        print("Usage: fb_bulk_probe.py <input.json>"); sys.exit(1)
    inp = json.load(open(sys.argv[1], encoding="utf-8"))
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    t = find_tab(TAB_PREFIX)
    if not t:
        print(json.dumps({"error": "no tab"})); sys.exit(1)
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
    out = []
    for entry in inp:
        eid = entry.get("id")
        slugs = entry.get("slugs", [])
        result = {"id": eid, "found": None, "tries": []}
        for slug in slugs:
            try:
                r = probe_slug(ws, slug)
            except Exception as e:
                r = {"error": str(e)}
            r["slug"] = slug
            result["tries"].append(r)
            if r and not r.get("unavailable") and not r.get("personal") and r.get("pageName"):
                result["found"] = {
                    "slug": slug,
                    "pageName": r.get("pageName"),
                    "sample": r.get("sample"),
                }
                break
        out.append(result)
        # incremental write & status
        if out_path:
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(out, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        sys.stderr.write(f"[{len(out)}/{len(inp)}] {eid} -> {('FOUND ' + result['found']['slug']) if result['found'] else 'none'}\n")
        sys.stderr.flush()
    ws.close()
    if not out_path:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
