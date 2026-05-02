#!/usr/bin/env python3
"""
Download every external photo URL referenced from candidates.js to
/images/candidates/<sha256_first16>.<ext> and rewrite the data file
to point at the local copy.

Stops hotlinking from framerusercontent.com / framsoknrvk.is / etc.
Run once; re-running is idempotent (already-local URLs are skipped).
"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def detect_ext(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:4] == b"\x89PNG":
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"\x00\x00\x00 " and b"avif" in data[:32]:
        return "avif"
    return "jpg"  # best-effort fallback


def download(url: str) -> bytes | None:
    # Encode any non-ASCII characters in the URL path (e.g. Prismic URLs that
    # have Icelandic letters in filenames). urllib doesn't auto-encode.
    from urllib.parse import urlsplit, urlunsplit, quote
    parts = urlsplit(url)
    safe_path = quote(parts.path, safe="/-_.~")
    safe_query = quote(parts.query, safe="=&-_.~")
    encoded = urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment))

    headers = {
        "User-Agent": UA,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "is,en;q=0.9",
        # Some hosts require a same-origin Referer to defeat hotlinking.
        "Referer": f"{parts.scheme}://{parts.netloc}/",
    }
    # framsoknrvk.is redirects 307 to www.framsoknrvk.is then 403 — try the
    # www variant directly as a workaround.
    if parts.netloc == "framsoknrvk.is":
        encoded = encoded.replace("framsoknrvk.is", "www.framsoknrvk.is", 1)
        headers["Referer"] = "https://www.framsoknrvk.is/"

    req = urllib.request.Request(encoded, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception as e:
        print(f"  ✗ download failed: {e}")
        return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Per-row regex matching ballot, name, occupation, photo URL
    pat = re.compile(
        r"(\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*)"
        r"'(https?://[^']+)'"
    )

    # Collect unique (url, [names]) — same URL might (rarely) reference multiple rows
    url_to_names = {}
    for m in pat.finditer(src):
        name = m.group(2).replace("\\'", "'")
        url = m.group(3)
        url_to_names.setdefault(url, []).append(name)

    print(f"Found {len(url_to_names)} unique external photo URLs across "
          f"{sum(len(v) for v in url_to_names.values())} candidate rows.")

    # Download each, compute hash, save locally, build replacement map
    url_to_local = {}
    failed = []
    for i, (url, names) in enumerate(url_to_names.items(), 1):
        sample_name = names[0][:30]
        print(f"[{i}/{len(url_to_names)}] {sample_name:<32} ← {url[:70]}")
        data = download(url)
        if not data:
            failed.append((url, names))
            continue
        h = hashlib.sha256(data).hexdigest()[:16]
        ext = detect_ext(data)
        local_path = f"images/candidates/{h}.{ext}"
        out = IMG_DIR / f"{h}.{ext}"
        if not out.exists():
            out.write_bytes(data)
        url_to_local[url] = local_path

    # Rewrite candidates.js: replace each external URL with its local path.
    # Since URLs are unique strings, we can do simple global replace.
    new_src = src
    for old_url, local_path in url_to_local.items():
        new_src = new_src.replace(f"'{old_url}'", f"'{local_path}'")

    # Sanity: confirm exactly the expected number of replacements happened
    if new_src == src:
        print("\nNothing to write (no external URLs replaced).")
        return
    CANDIDATES_JS.write_text(new_src, encoding="utf-8")

    print(f"\n✓ Localised {len(url_to_local)} URLs.")
    if failed:
        print(f"⚠ {len(failed)} URLs failed to download:")
        for url, names in failed:
            print(f"   {url}  (used by {names[0]})")


if __name__ == "__main__":
    main()
