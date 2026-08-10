#!/usr/bin/env python3
"""
Helper for FB scan via edge_cdp.

Usage:
  python scripts/fb_scan_helper.py search "<query>"
      -> navigates the FB tab to a pages search and prints candidate slugs

  python scripts/fb_scan_helper.py page <slug>
      -> navigates to https://www.facebook.com/<slug>, returns
         {h1, name (best guess from About text), about, links}

  python scripts/fb_scan_helper.py posts <slug>
      -> navigates to https://www.facebook.com/<slug> and returns the
         first ~5 visible post texts and any external links inside them
"""
import json
import sys
import time
import urllib.request
import urllib.parse

import websocket

CDP = "http://localhost:9222"
TAB_PREFIX = "4C25965E"  # the Facebook tab opened earlier
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


def evaluate(ws, expr, await_promise=False):
    res = send(ws, "Runtime.evaluate", {
        "expression": expr,
        "returnByValue": True,
        "awaitPromise": await_promise,
    })
    return res.get("result", {}).get("result", {}).get("value")


def wait_complete(ws, timeout=20):
    end = time.time() + timeout
    while time.time() < end:
        if evaluate(ws, "document.readyState") == "complete":
            return True
        time.sleep(0.5)
    return False


def navigate(url, settle=4):
    t = find_tab(TAB_PREFIX)
    if not t:
        print(json.dumps({"error": f"no tab matching {TAB_PREFIX}"}))
        sys.exit(1)
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
    send(ws, "Page.enable")
    send(ws, "Page.navigate", {"url": url})
    wait_complete(ws, 25)
    time.sleep(settle)
    return ws


SEARCH_JS = r"""
(function(){
  const main = document.querySelector('[role=main]');
  if (!main) return [];
  const seen = new Set();
  const out = [];
  // Get anchor + nearest text label
  for (const a of main.querySelectorAll('a[href*="facebook.com/"]')) {
    const m = a.href.match(/facebook\.com\/([^/?#]+)/);
    if (!m) continue;
    const slug = m[1];
    if (/^(login|search|help|policies|hashtag|profile\.php|pages|groups|events|watch|marketplace|reel|stories|sharer|business|legal|privacy|policy|home\.php|share|gaming|notifications|messages|saved|settings)$/.test(slug)) continue;
    if (seen.has(slug)) continue;
    seen.add(slug);
    // Find nearest plausible label - climb up DOM
    let label = '';
    let el = a;
    for (let i = 0; i < 6 && el; i++) {
      const t = (el.textContent || '').trim();
      if (t && t.length > 2 && t.length < 120) { label = t; break; }
      el = el.parentElement;
    }
    out.push({slug: slug, label: label.replace(/\s+/g,' ').slice(0,140)});
    if (out.length >= 12) break;
  }
  return out;
})()
"""

PAGE_JS = r"""
(function(){
  const main = document.querySelector('[role=main]');
  const tc = (main && main.textContent || '').replace(/\s+/g,' ');
  const h1 = document.querySelector('h1') ? document.querySelector('h1').textContent.trim() : null;
  // Best-guess "page name": often appears at the top of [role=main] textContent
  let pageName = null;
  // first textnode inside main, before "followers"
  const m = tc.match(/^([^•·]{3,120}?)\s*(\d[\d.,K]*\s*followers|·)/);
  if (m) pageName = m[1].trim();
  return {
    h1: h1,
    pageName: pageName,
    about: tc.slice(0, 1500),
    links: Array.from(document.querySelectorAll('a[href]')).map(a=>a.href).filter(h => /^https?:\/\//.test(h) && !/facebook\.com|fbsbx\.com|fbcdn\.net|fb\.watch|messenger\.com|l\.facebook\.com/.test(h)).slice(0, 25)
  };
})()
"""

POSTS_JS = r"""
(function(){
  const main = document.querySelector('[role=main]');
  if (!main) return [];
  const out = [];
  const seen = new Set();
  // Posts often in [role=article]
  for (const art of main.querySelectorAll('[role=article]')) {
    let txt = (art.textContent || '').replace(/\s+/g,' ').trim();
    if (!txt || txt.length < 30) continue;
    const key = txt.slice(0, 120);
    if (seen.has(key)) continue;
    seen.add(key);
    // External links inside the post (FB external link wrappers point to l.facebook.com)
    const ext = Array.from(art.querySelectorAll('a[href]'))
      .map(a => a.href)
      .filter(h => /^https?:\/\//.test(h))
      .map(h => {
        // unwrap l.facebook.com/?u=<encoded>
        const m = h.match(/l\.facebook\.com\/l\.php\?u=([^&]+)/);
        if (m) try { return decodeURIComponent(m[1]); } catch(e){ return h; }
        return h;
      })
      .filter(h => !/facebook\.com|fbsbx\.com|fbcdn\.net|fb\.watch|messenger\.com/.test(h));
    out.push({text: txt.slice(0, 4000), externalLinks: Array.from(new Set(ext))});
    if (out.length >= 6) break;
  }
  // also try with [data-pagelet*=Story]
  if (out.length === 0) {
    for (const el of main.querySelectorAll('div')) {
      const t = (el.textContent || '').replace(/\s+/g,' ').trim();
      if (t.length > 200 && t.length < 5000 && /·|kl\.|\d{4}/.test(t)) {
        const key = t.slice(0, 120);
        if (seen.has(key)) continue;
        seen.add(key);
        out.push({text: t.slice(0,4000), externalLinks: []});
        if (out.length >= 4) break;
      }
    }
  }
  return out;
})()
"""


def cmd_search(query):
    url = "https://www.facebook.com/search/pages/?q=" + urllib.parse.quote(query)
    ws = navigate(url, settle=4)
    val = evaluate(ws, SEARCH_JS)
    ws.close()
    print(json.dumps(val or [], ensure_ascii=False, indent=2))


def cmd_page(slug):
    url = f"https://www.facebook.com/{slug}"
    ws = navigate(url, settle=4)
    val = evaluate(ws, PAGE_JS)
    ws.close()
    print(json.dumps(val or {}, ensure_ascii=False, indent=2))


def cmd_posts(slug):
    url = f"https://www.facebook.com/{slug}"
    ws = navigate(url, settle=5)
    val = evaluate(ws, POSTS_JS)
    ws.close()
    print(json.dumps(val or [], ensure_ascii=False, indent=2))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "search":
        cmd_search(sys.argv[2])
    elif cmd == "page":
        cmd_page(sys.argv[2])
    elif cmd == "posts":
        cmd_posts(sys.argv[2])
    else:
        print(f"unknown command: {cmd}"); sys.exit(1)


if __name__ == "__main__":
    main()
