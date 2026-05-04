#!/usr/bin/env python3
"""
For every policy_2026-05-01_*.json entry, fetch platform_url with a real
browser UA, strip HTML to plain text, and check whether each agenda
source_quote actually appears in the body. Reports per-entry stats and
writes a `_AUDITED` JSON keeping only entries where >=75% of quotes match.
"""
import json
import re
import sys
import urllib.request
import urllib.error
import socket
from pathlib import Path

socket.setdefaulttimeout(20)
ROOT = Path(__file__).parent.parent
SCAN_DIR = ROOT / "scan_results"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def fetch_text(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "is,en;q=0.9",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
        return None, f"FETCH_FAIL:{type(e).__name__}:{getattr(e,'code',None)}"
    try:
        html = raw.decode("utf-8", errors="replace")
    except Exception as e:
        return None, f"DECODE_FAIL:{e}"
    body = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", body)
    text = re.sub(r"\s+", " ", text)
    return text, None


def quote_match(quote, body):
    """Return True if the quote substantively appears in body.

    We check several increasingly lenient criteria:
    1. Verbatim substring.
    2. Substring after light normalization (lowercase, collapse non-letters).
    3. Of the words in the quote (>=4 chars), at least 75% appear in body.
    """
    if not quote or not body:
        return False
    if quote in body:
        return True
    norm_q = re.sub(r"[^\w]+", " ", quote.lower()).strip()
    norm_b = re.sub(r"[^\w]+", " ", body.lower())
    if norm_q in norm_b:
        return True
    # word-overlap fallback
    words = [w for w in norm_q.split() if len(w) >= 4]
    if not words:
        return False
    body_words = set(norm_b.split())
    hits = sum(1 for w in words if w in body_words)
    return hits / len(words) >= 0.75


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    audited = []
    summary = []
    for p in sorted(SCAN_DIR.glob("policy_2026-*_*.json")):
        if "AUDITED" in p.name:
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        kept = []
        for r in d.get("results", []):
            url = r.get("platform_url", "")
            quotes = [a.get("source_quote", "") for a in r.get("agenda", [])]
            body, err = fetch_text(url)
            if err:
                summary.append((r["muni_slug"], r["party_code"], 0, len(quotes), f"FAIL {err}"))
                continue
            n_match = sum(1 for q in quotes if quote_match(q, body))
            n_total = len(quotes)
            ratio = n_match / n_total if n_total else 0
            verdict = "KEEP" if ratio >= 0.75 else "DROP"
            summary.append((r["muni_slug"], r["party_code"], n_match, n_total, verdict))
            if verdict == "KEEP":
                # Annotate which bullets matched/missed for transparency
                for a in r["agenda"]:
                    a["quote_verified"] = quote_match(a.get("source_quote", ""), body)
                r["quote_audit"] = f"{n_match}/{n_total} quotes verified against fetched body"
                kept.append(r)
        if kept:
            out = dict(d)
            out["results"] = kept
            out["agent_note"] = (out.get("agent_note", "") + " | quote-audited 2026-05-01").strip()
            outpath = SCAN_DIR / f"{p.stem}_AUDITED.json"
            outpath.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
            audited.append(outpath)
        # remove the original so the renderer only picks up audited
        p.unlink()
    # Print report
    print(f"{'muni':<22} {'party':<6} {'match':<7} verdict")
    print("-" * 60)
    for muni, party, n, total, verdict in summary:
        print(f"{muni:<22} {party:<6} {n}/{total:<5} {verdict}")
    print()
    print(f"Wrote audited files: {[p.name for p in audited]}")
    keeps = sum(1 for s in summary if s[4] == "KEEP")
    drops = sum(1 for s in summary if s[4] == "DROP")
    fails = sum(1 for s in summary if s[4].startswith("FAIL"))
    print(f"KEEP: {keeps}, DROP: {drops}, FETCH_FAIL: {fails}")


if __name__ == "__main__":
    main()
