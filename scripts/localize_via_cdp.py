#!/usr/bin/env python3
"""
Localise the remaining external candidate photos that plain HTTP can't reach
(framsoknrvk.is + images.prismic.io are behind Vercel anti-bot challenges).
Uses CDP-driven Edge to fetch via the page's own fetch() — bypasses anti-bot.

Edge must be running with --remote-debugging-port=9222 --remote-allow-origins=*.
"""
import base64
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
import websocket  # websocket-client

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"
CDP = "http://localhost:9222"


def find_or_open_tab():
    tabs = json.loads(urllib.request.urlopen(f"{CDP}/json").read())
    for t in tabs:
        if t.get("type") == "page" and t.get("url", "").startswith("http"):
            return t
    # Open a new about:blank tab
    req = urllib.request.Request(f"{CDP}/json/new?about:blank", method="PUT")
    return json.loads(urllib.request.urlopen(req).read())


_msg_id = 0
def send(ws, method, params=None):
    global _msg_id
    _msg_id += 1
    ws.send(json.dumps({"id": _msg_id, "method": method, "params": params or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == _msg_id:
            return r


def fetch_via_browser(ws, url):
    """In-page fetch; return bytes or None."""
    js = f"""
    (async () => {{
      try {{
        const r = await fetch({json.dumps(url)}, {{
          credentials: 'include',
          referrer: {json.dumps(url.split('/')[0] + '//' + url.split('/')[2] + '/')},
        }});
        if (!r.ok) return {{ok: false, status: r.status}};
        const buf = await r.arrayBuffer();
        // base64 encode
        const bytes = new Uint8Array(buf);
        let bin = '';
        const chunkSize = 0x8000;
        for (let i = 0; i < bytes.length; i += chunkSize) {{
          bin += String.fromCharCode.apply(null, bytes.slice(i, i + chunkSize));
        }}
        return {{ok: true, b64: btoa(bin), size: bytes.length}};
      }} catch (e) {{ return {{ok: false, err: String(e)}}; }}
    }})()
    """
    res = send(ws, "Runtime.evaluate", {
        "expression": js,
        "awaitPromise": True,
        "returnByValue": True,
    })
    val = res.get("result", {}).get("result", {}).get("value")
    return val


def detect_ext(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff": return "jpg"
    if data[:4] == b"\x89PNG": return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"): return "gif"
    return "jpg"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    pat = re.compile(
        r"(\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*)"
        r"'(https?://[^']+)'"
    )
    url_to_names = {}
    for m in pat.finditer(src):
        name = m.group(2).replace("\\'", "'")
        url = m.group(3)
        url_to_names.setdefault(url, []).append(name)
    print(f"Remaining external URLs: {len(url_to_names)}")

    tab = find_or_open_tab()
    print(f"Using tab: {tab['url'][:80]}")
    ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60)

    # Navigate to each unique host ONCE up front and wait long enough for
    # any Vercel-style anti-bot challenge to clear. After that, in-page
    # fetch() inherits the resolved session.
    hosts_seen = set()
    for url in url_to_names:
        host_root = url.split('/')[0] + '//' + url.split('/')[2] + '/'
        if host_root in hosts_seen:
            continue
        hosts_seen.add(host_root)
        print(f"Warming up {host_root} (10s wait for challenge)...")
        send(ws, "Page.navigate", {"url": host_root})
        time.sleep(10)

    url_to_local = {}
    failed = []
    for i, (url, names) in enumerate(url_to_names.items(), 1):
        print(f"[{i}/{len(url_to_names)}] {names[0][:30]:<32} ← {url[:70]}")
        # Navigate the tab to the URL's host root if we're not already there
        host_root = url.split('/')[0] + '//' + url.split('/')[2] + '/'
        result = fetch_via_browser(ws, url)
        if not result or not result.get("ok"):
            print(f"   ✗ {result}")
            failed.append((url, names))
            continue
        try:
            data = base64.b64decode(result["b64"])
        except Exception as e:
            print(f"   ✗ b64 decode failed: {e}")
            failed.append((url, names))
            continue
        h = hashlib.sha256(data).hexdigest()[:16]
        ext = detect_ext(data)
        out = IMG_DIR / f"{h}.{ext}"
        if not out.exists():
            out.write_bytes(data)
        url_to_local[url] = f"images/candidates/{h}.{ext}"
        print(f"   ✓ {out.name} ({len(data)} bytes)")
    ws.close()

    new_src = src
    for old_url, local_path in url_to_local.items():
        new_src = new_src.replace(f"'{old_url}'", f"'{local_path}'")
    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\n✓ Localised {len(url_to_local)}, failed {len(failed)}")


if __name__ == "__main__":
    main()
