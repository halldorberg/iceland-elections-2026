#!/usr/bin/env python
"""
Scrape all candidate data from xd.is via Chrome DevTools Protocol (synchronous).
Requires Edge running with --remote-debugging-port=9222
"""
import json, time, urllib.request
import websocket

CDP_HOST = 'http://localhost:9222'

def get_ws_url():
    tabs = json.loads(urllib.request.urlopen(CDP_HOST + '/json').read())
    for t in tabs:
        if 'xd.is' in t.get('url', '') and t['type'] == 'page':
            return t['webSocketDebuggerUrl']
    for t in tabs:
        if t['type'] == 'page' and t['url'].startswith('http'):
            return t['webSocketDebuggerUrl']
    raise Exception("No usable tab found")

class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=30)
        self._id = 0

    def send(self, method, params=None):
        self._id += 1
        msg = json.dumps({'id': self._id, 'method': method, 'params': params or {}})
        self.ws.send(msg)
        # Read messages until we get the response for this id
        target_id = self._id
        while True:
            raw = self.ws.recv()
            data = json.loads(raw)
            if data.get('id') == target_id:
                return data
            # ignore events

    def navigate_and_wait(self, url, settle=1.5):
        self.send('Page.enable')
        self.send('Page.navigate', {'url': url})
        # Drain messages until loadEventFired
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                self.ws.settimeout(2)
                raw = self.ws.recv()
                data = json.loads(raw)
                if data.get('method') == 'Page.loadEventFired':
                    break
            except Exception:
                break
        self.ws.settimeout(30)
        time.sleep(settle)

    def evaluate(self, expression):
        result = self.send('Runtime.evaluate', {
            'expression': expression,
            'returnByValue': True,
        })
        try:
            return result['result']['result'].get('value')
        except Exception:
            return None

    def close(self):
        self.ws.close()


def scrape_all():
    ws_url = get_ws_url()
    print(f"Connecting to: {ws_url}")
    client = CDP(ws_url)

    # Navigate to main listing page and collect list URLs
    print("Loading main listing page...")
    client.navigate_and_wait('https://xd.is/sveitarstjornarkosningar-2026-2/')

    list_urls_raw = client.evaluate("""
        JSON.stringify(
            [...document.querySelectorAll('a')]
            .filter(a => a.textContent.trim().toLowerCase().includes('skoða'))
            .map(a => a.href)
            .filter((v,i,arr) => arr.indexOf(v) === i)
        )
    """)
    list_urls = json.loads(list_urls_raw) if list_urls_raw else []
    print(f"Found {len(list_urls)} list pages")

    all_candidates = []

    for i, url in enumerate(list_urls):
        print(f"  [{i+1}/{len(list_urls)}] {url}")
        try:
            client.navigate_and_wait(url, settle=2.0)

            raw = client.evaluate("""
                (function() {
                    if (typeof XDM_DATA !== 'undefined') return JSON.stringify(XDM_DATA);
                    return null;
                })()
            """)

            if not raw:
                print(f"    -> No XDM_DATA")
                continue

            data = json.loads(raw)
            candidates = data.get('candidates', [])
            muni = data.get('name', '')
            lst  = data.get('listName', '')
            print(f"    -> {muni} / {lst}: {len(candidates)} candidates")

            for c in candidates:
                photo_id = c.get('photoId') or c.get('photoID') or c.get('photo_id')
                all_candidates.append({
                    'municipality': muni,
                    'list': lst,
                    'seat': c.get('seat'),
                    'name': c.get('name', ''),
                    'title': c.get('title', ''),
                    'photoId': photo_id,
                    'objectPosition': c.get('objectPosition', ''),
                    'photoScale': c.get('photoScale', ''),
                    '_keys': sorted(c.keys())
                })

        except Exception as e:
            print(f"    ERROR: {e}")

    client.close()

    out_path = r'F:\Claude Projects\iceland-elections\scan_results\xd_candidates_cdp.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=2)

    total = len(all_candidates)
    with_photo = sum(1 for c in all_candidates if c.get('photo'))
    key_sets = list({str(c['_keys']) for c in all_candidates})

    print(f"\nDone! {total} candidates saved to xd_candidates_cdp.json")
    print(f"With photos: {with_photo}/{total}")
    print(f"Field variations: {key_sets}")
    if with_photo:
        sample = next(c for c in all_candidates if c.get('photo'))
        print(f"Sample photo: {sample['photo']}")

if __name__ == '__main__':
    scrape_all()
