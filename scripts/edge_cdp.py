#!/usr/bin/env python3
"""
Tiny Chrome DevTools Protocol helper for driving Edge launched with
--remote-debugging-port=9222.

Usage:
  python scripts/edge_cdp.py tabs                     # list tabs
  python scripts/edge_cdp.py open <url>               # open new tab, print id
  python scripts/edge_cdp.py nav <tabId> <url>        # navigate tab
  python scripts/edge_cdp.py text <tabId>             # body innerText
  python scripts/edge_cdp.py html <tabId>             # outerHTML (truncated)
  python scripts/edge_cdp.py eval <tabId> <expr>      # evaluate JS, print result
  python scripts/edge_cdp.py wait <tabId>             # wait until document.readyState=='complete'
"""
import json
import sys
import time
import urllib.request

import websocket  # websocket-client

CDP = "http://localhost:9222"
MSG_ID = 0


def list_tabs():
    return json.loads(urllib.request.urlopen(f"{CDP}/json").read())


def find_tab(tab_id):
    for t in list_tabs():
        if t.get("id", "").lower().startswith(tab_id.lower()):
            return t
    return None


def open_new_tab(url):
    # PUT /json/new?<url>
    req = urllib.request.Request(f"{CDP}/json/new?{url}", method="PUT")
    return json.loads(urllib.request.urlopen(req).read())


def send(ws, method, params=None):
    global MSG_ID
    MSG_ID += 1
    payload = {"id": MSG_ID, "method": method, "params": params or {}}
    ws.send(json.dumps(payload))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == MSG_ID:
            return msg


def attach(tab, timeout=30):
    ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=timeout)
    return ws


def evaluate(ws, expr, await_promise=False):
    res = send(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": await_promise,
    })
    result = res.get("result", {}).get("result", {})
    if result.get("type") == "string":
        return result.get("value", "")
    return result.get("value")


def wait_complete(ws, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        state = evaluate(ws, "document.readyState")
        if state == "complete":
            return True
        time.sleep(0.5)
    return False


def cmd_tabs():
    for t in list_tabs():
        if t.get("type") not in ("page", "iframe"):
            continue
        print(f"  [{t.get('id','')[:8]}] {t.get('title','')[:50]:<52} {t.get('url','')[:90]}")


def cmd_open(url):
    if "://" not in url:
        url = "https://" + url
    t = open_new_tab(url)
    print(f"opened tab {t['id'][:8]} -> {t['url']}")


def cmd_nav(tab_id, url):
    t = find_tab(tab_id)
    if not t:
        print(f"no tab matching {tab_id}"); sys.exit(1)
    if "://" not in url:
        url = "https://" + url
    ws = attach(t)
    send(ws, "Page.enable")
    send(ws, "Page.navigate", {"url": url})
    wait_complete(ws, 30)
    ws.close()
    print(f"navigated [{t['id'][:8]}] -> {url}")


def cmd_text(tab_id):
    t = find_tab(tab_id)
    if not t:
        print(f"no tab matching {tab_id}"); sys.exit(1)
    ws = attach(t)
    txt = evaluate(ws, "document.body && document.body.innerText")
    ws.close()
    print(txt or "")


def cmd_html(tab_id):
    t = find_tab(tab_id)
    if not t:
        print(f"no tab matching {tab_id}"); sys.exit(1)
    ws = attach(t)
    html = evaluate(ws, "document.documentElement.outerHTML")
    ws.close()
    print((html or "")[:30000])


def cmd_eval(tab_id, expr):
    t = find_tab(tab_id)
    if not t:
        print(f"no tab matching {tab_id}"); sys.exit(1)
    ws = attach(t)
    # Always await promises — safe, returns plain values unchanged
    val = evaluate(ws, expr, await_promise=True)
    ws.close()
    print(json.dumps(val, ensure_ascii=False, indent=2) if not isinstance(val, str) else val)


def cmd_wait(tab_id):
    t = find_tab(tab_id)
    if not t:
        print(f"no tab matching {tab_id}"); sys.exit(1)
    ws = attach(t)
    print("complete" if wait_complete(ws, 30) else "timeout")
    ws.close()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "tabs":
        cmd_tabs()
    elif cmd == "open":
        cmd_open(sys.argv[2])
    elif cmd == "nav":
        cmd_nav(sys.argv[2], sys.argv[3])
    elif cmd == "text":
        cmd_text(sys.argv[2])
    elif cmd == "html":
        cmd_html(sys.argv[2])
    elif cmd == "eval":
        cmd_eval(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "wait":
        cmd_wait(sys.argv[2])
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
