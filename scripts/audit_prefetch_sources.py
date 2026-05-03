"""Phase 0 of the bio-audit pipeline: pre-fetch every cited source URL into
a local HTML cache so the audit agents don't have to re-fetch them.

Skips LinkedIn (always 403'd / auth wall). Uses curl with an Edge UA which
worked reliably for mbl.is + kosningasaga in the pilot.
"""
from __future__ import annotations
import concurrent.futures as cf
import hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).parent.parent
BIOS_GLOB = "scan_results/bios_2026-05-02_*.json"
CACHE_DIR = ROOT / "scan_results" / "source_cache"
MANIFEST_FILE = CACHE_DIR / "_manifest.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/138.0.0.0"
WORKERS = 8
SKIP_HOSTS = ("linkedin.com", "www.linkedin.com")


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def fetch_one(url: str, dest: Path) -> dict:
    """Fetch one URL. Returns metadata."""
    out_file = dest / (url_hash(url) + ".html")
    cmd = [
        "curl", "-sL",
        "--max-time", "20",
        "-A", UA,
        "-o", str(out_file),
        "-w", "%{http_code}",
        url,
    ]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        status = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    except Exception as e:
        status = -1
    elapsed = round(time.time() - t0, 2)
    size = out_file.stat().st_size if out_file.exists() else 0
    return {
        "url": url,
        "file": out_file.name,
        "status": status,
        "size": size,
        "elapsed_s": elapsed,
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Collect every unique URL from bios_*.json files
    urls: set[str] = set()
    for f in sorted(ROOT.glob(BIOS_GLOB)):
        if "to_research" in f.name or "audit" in f.name:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ⚠ {f.name}: {e}")
            continue
        for r in data.get("results", []):
            for src in (r.get("sources") or r.get("heimild") or []):
                if isinstance(src, dict):
                    u = (src.get("url") or "").strip()
                else:
                    u = str(src).strip()
                if u and u.startswith(("http://", "https://")):
                    if any(h in u for h in SKIP_HOSTS):
                        continue
                    urls.add(u)
    print(f"  Unique non-LinkedIn URLs to fetch: {len(urls)}")

    # 2. Load existing manifest
    manifest: dict[str, dict] = {}
    if MANIFEST_FILE.exists():
        try:
            manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}

    # Skip already-fetched (status 200 only — re-fetch errors)
    todo: list[str] = []
    for u in sorted(urls):
        meta = manifest.get(u)
        if meta and meta.get("status") == 200 and meta.get("size", 0) > 0:
            continue
        todo.append(u)
    print(f"  Already cached (200 OK): {len(urls) - len(todo)}")
    print(f"  To fetch:                {len(todo)}")

    if not todo:
        print("  Nothing to do.")
        return

    # 3. Fetch with thread pool
    t0 = time.time()
    done = 0
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(fetch_one, u, CACHE_DIR): u for u in todo}
        for fut in cf.as_completed(futures):
            meta = fut.result()
            manifest[meta["url"]] = meta
            done += 1
            if done % 25 == 0 or done == len(todo):
                # Periodic flush
                MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
                elapsed = round(time.time() - t0, 1)
                rate = round(done / max(elapsed, 1), 2)
                print(f"  [{done:4d}/{len(todo)}] last: HTTP {meta['status']:>3d} {meta['size']:>7d}B {meta['url'][:80]}  ({rate}/s)")

    # Final flush
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. Summary
    by_status: dict = {}
    for m in manifest.values():
        by_status[m["status"]] = by_status.get(m["status"], 0) + 1
    print(f"\n  Done in {round(time.time()-t0,1)}s.")
    print(f"  Cache: {CACHE_DIR}")
    print(f"  Status breakdown:")
    for s in sorted(by_status):
        print(f"    HTTP {s:>4}: {by_status[s]}")


if __name__ == "__main__":
    main()
