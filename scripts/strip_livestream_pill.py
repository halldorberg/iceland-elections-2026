#!/usr/bin/env python3
"""Excise the self-contained live-stream pill block from every site HTML
file (root index.html, municipality.html template, and all is/en/pl
stubs). The block is invariant in structure across all generated pages:

    <!-- ─── Live-stream pill (bottom-right) ... -->   <- start (this line)
    <div class="ls-pill" ...> ... </div>
    <style> ... </style>
    <script> ... </script>                              <- last </script>
  </body>                                                <- before </body>

So per file: drop every line from the one containing the marker
"Live-stream pill (bottom-right)" up to (not including) the </body>
line — but only if a </script> exists in that span (sanity guard).

  python scripts/strip_livestream_pill.py            # dry run (counts)
  python scripts/strip_livestream_pill.py --apply    # rewrite files
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "Live-stream pill (bottom-right)"
SKIP_PARTS = {".git", ".claude", "node_modules", "scan_results",
              "news_cache", "fb_platform_scan", "source_cache",
              "quarantine", "tmp_candidates", "temp", "temp_xb",
              "__pycache__"}


def strip_one(text: str):
    """Return (new_text, removed_lines) or (None, 0) if no change."""
    if MARKER not in text:
        return None, 0
    keepends = text.splitlines(keepends=True)
    i = next((n for n, ln in enumerate(keepends) if MARKER in ln), None)
    if i is None:
        return None, 0
    b = next((n for n in range(len(keepends) - 1, i, -1)
              if keepends[n].strip() == "</body>"), None)
    if b is None:
        return None, 0
    span = keepends[i:b]
    if not any(ln.strip() == "</script>" for ln in span):
        return None, 0          # guard: no pill script in span → leave it
    new = keepends[:i] + keepends[b:]
    return "".join(new), len(span)


def should_skip(p: Path) -> bool:
    return any(part in SKIP_PARTS for part in p.parts)


def main() -> int:
    apply = "--apply" in sys.argv
    targets = []
    for name in ("index.html", "municipality.html", "404.html"):
        fp = ROOT / name
        if fp.exists():
            targets.append(fp)
    targets += [p for p in ROOT.rglob("index.html") if not should_skip(p)]
    seen, changed, removed_total, samples = set(), 0, 0, []
    for fp in targets:
        rp = fp.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        try:
            txt = fp.read_text(encoding="utf-8")
        except Exception as e:                       # noqa: BLE001
            print(f"  ! read fail {fp}: {e}")
            continue
        new, removed = strip_one(txt)
        if new is None:
            continue
        changed += 1
        removed_total += removed
        if "ls-pill" in new or "YT_CHANNEL" in new:
            print(f"  !! residue left in {fp} — NOT writing")
            continue
        if not new.rstrip().endswith("</html>"):
            print(f"  !! {fp} no longer ends with </html> — NOT writing")
            continue
        if len(samples) < 4:
            tail = "".join(new.splitlines(keepends=True)[-3:])
            samples.append((str(fp.relative_to(ROOT)), removed, tail))
        if apply:
            fp.write_text(new, encoding="utf-8")
    mode = "APPLIED" if apply else "DRY RUN"
    print(f"[{mode}] {changed} file(s) "
          f"{'rewritten' if apply else 'would change'}, "
          f"{removed_total} pill lines total, {len(seen)} scanned")
    for rel, rm, tail in samples:
        print(f"\n  • {rel}  (-{rm} lines)  tail:")
        for ln in tail.splitlines():
            print(f"      {ln}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
