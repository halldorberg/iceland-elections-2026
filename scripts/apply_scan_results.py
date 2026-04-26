#!/usr/bin/env python3
"""
apply_scan_results.py
─────────────────────
Applies a scan result JSON file back to candidates.js.

Usage:
    python scripts/apply_scan_results.py news   scan_results/news_2026-05-01.json
    python scripts/apply_scan_results.py photos scan_results/photos_2026-05-01.json
    python scripts/apply_scan_results.py policy scan_results/policy_2026-05-01.json

Flags:
    --dry-run    Show what would change without writing anything
    --no-backup  Skip writing a .bak file (not recommended)
"""

import json
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"


# ── Helpers ───────────────────────────────────────────────────────────────────

def escape_js(s: str) -> str:
    """Escape a string for use in a JS single-quoted string."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


def js_news_item(article: dict, indent: int = 10) -> str:
    pad = " " * indent
    title  = escape_js(article["title"])
    url    = article["url"]
    source = escape_js(article.get("source", ""))
    return f"{pad}{{ title: '{title}', url: '{url}', source: '{source}' }},"


def js_agenda_item(item: dict, indent: int = 8) -> str:
    pad = " " * indent
    icon  = item.get("icon", "")
    title = escape_js(item.get("title", ""))
    text  = escape_js(item.get("text", ""))
    return f"{pad}{{ icon: '{icon}', title: '{title}', text: '{text}' }},"


# ── News applier ──────────────────────────────────────────────────────────────

def apply_news(src: str, results: list[dict], dry_run: bool) -> tuple[str, int]:
    """
    For each result entry, find the candidate's news: [] array and
    append any new articles that aren't already present.
    Returns (new_src, count_changed).
    """
    changed = 0
    for entry in results:
        name         = entry["name"]
        new_articles = entry.get("new_articles", [])
        if not new_articles:
            continue

        # Find the candidate block by name — look for the name string near a news: [ array
        # Pattern: find  '<<name>>'  followed (within ~2000 chars) by  news: [
        name_escaped = re.escape(escape_js(name))
        pattern = (
            r"('(?:" + name_escaped + r")'[^}]*?news\s*:\s*\[)"
            r"(.*?)"
            r"(\s*\],)"
        )
        m = re.search(pattern, src, re.DOTALL)
        if not m:
            print(f"  ⚠ Could not find news block for: {name}")
            continue

        existing_block = m.group(2)
        # Collect already-present URLs to avoid duplicates
        existing_urls = set(re.findall(r"url\s*:\s*'([^']*)'", existing_block))

        new_lines = []
        for article in new_articles:
            if article["url"] not in existing_urls:
                new_lines.append(js_news_item(article))
                existing_urls.add(article["url"])

        if not new_lines:
            print(f"  ✓ {name}: no new articles (all already present)")
            continue

        replacement = m.group(1) + m.group(2) + "\n" + "\n".join(new_lines) + m.group(3)
        if dry_run:
            print(f"  [DRY RUN] {name}: would add {len(new_lines)} article(s)")
        else:
            src = src[:m.start()] + replacement + src[m.end():]
            print(f"  ✓ {name}: added {len(new_lines)} article(s)")
            changed += 1

    return src, changed


# ── Photos applier ────────────────────────────────────────────────────────────

def apply_photos(src: str, results: list[dict], dry_run: bool) -> tuple[str, int]:
    """
    For each result entry, replace null (or absent) photo URL with the provided one.
    Assumes photos have been downloaded to images/candidates/ already.
    """
    changed = 0
    for entry in results:
        name        = entry["name"]
        photo_local = entry.get("photo_local", "")
        if not photo_local:
            print(f"  ⚠ {name}: no photo_local path in result entry, skipping")
            continue

        name_escaped = re.escape(escape_js(name))
        # Pattern A: [ballot, 'name', 'occ', null, {  →  [ballot, 'name', 'occ', 'images/...', {
        pattern_null = (
            r"(\[\d+\s*,\s*'" + name_escaped + r"'\s*,\s*'[^']*?'\s*,\s*)null(\s*,\s*\{)"
        )
        # Pattern B: [ballot, 'name', 'occ']  →  [ballot, 'name', 'occ', 'images/...']  (no extended data)
        # (less common, skip for now — these would need a full block addition)

        m = re.search(pattern_null, src)
        if m:
            replacement = m.group(1) + f"'{photo_local}'" + m.group(2)
            if dry_run:
                print(f"  [DRY RUN] {name}: would set photo → {photo_local}")
            else:
                src = src[:m.start()] + replacement + src[m.end():]
                print(f"  ✓ {name}: photo set → {photo_local}")
                changed += 1
        else:
            print(f"  ⚠ Could not find null-photo pattern for: {name}")

    return src, changed


# ── Policy applier ────────────────────────────────────────────────────────────

def apply_policy(src: str, results: list[dict], dry_run: bool) -> tuple[str, int]:
    """
    For each result entry, add/replace platformUrl and update agenda items.
    """
    changed = 0
    for entry in results:
        muni_slug    = entry["muni_slug"]
        party_code   = entry["party_code"]
        platform_url = entry.get("platform_url", "")
        tagline      = entry.get("tagline", "")
        agenda       = entry.get("agenda", [])

        if not platform_url:
            print(f"  ⚠ {muni_slug}.{party_code}: no platform_url, skipping")
            continue

        # Find the party block: look for the party code inside its municipality const
        # This is complex — we find the party's tagline and insert platformUrl after it
        tagline_escaped = re.escape(escape_js(tagline)) if tagline else None

        # Strategy: find  PARTYCODE: {  then the tagline:  line  then insert platformUrl:
        party_block_re = re.compile(
            r"(  " + re.escape(party_code) + r"\s*:\s*\{[^}]*?"
            r"tagline\s*:\s*'(?:[^'\\]|\\.)*',?)",
            re.DOTALL
        )
        m = party_block_re.search(src)
        if not m:
            print(f"  ⚠ Could not find party block for {muni_slug}.{party_code}")
            continue

        # Check if platformUrl already exists in this block
        block_end = src.find("\n  }", m.start())
        if block_end == -1:
            block_end = m.start() + 2000  # safety
        block = src[m.start():block_end]

        url_escaped = escape_js(platform_url)
        new_url_line = f"\n    platformUrl: '{url_escaped}',"

        if "platformUrl:" in block:
            # Replace existing platformUrl
            replacement_block = re.sub(
                r"\n\s*platformUrl\s*:\s*'[^']*',?",
                new_url_line,
                block
            )
        else:
            # Insert platformUrl after tagline line
            replacement_block = re.sub(
                r"(tagline\s*:\s*'(?:[^'\\]|\\.)*',?)",
                r"\1" + new_url_line,
                block,
                count=1
            )

        # Update tagline if provided
        if tagline:
            tl_escaped = escape_js(tagline)
            replacement_block = re.sub(
                r"tagline\s*:\s*'(?:[^'\\]|\\.)*'",
                f"tagline: '{tl_escaped}'",
                replacement_block,
                count=1
            )

        # Update agenda items if provided
        if agenda:
            agenda_lines = "\n".join(js_agenda_item(a) for a in agenda)
            replacement_block = re.sub(
                r"agenda\s*:\s*\[.*?\]",
                f"agenda: [\n{agenda_lines}\n    ]",
                replacement_block,
                flags=re.DOTALL,
                count=1
            )

        if dry_run:
            print(f"  [DRY RUN] {muni_slug}.{party_code}: would add platformUrl + agenda")
        else:
            src = src[:m.start()] + replacement_block + src[m.start() + len(block):]
            print(f"  ✓ {muni_slug}.{party_code}: platformUrl and agenda updated")
            changed += 1

    return src, changed


# ── Validation ────────────────────────────────────────────────────────────────

def quick_validate(src: str) -> bool:
    opens  = src.count("{")
    closes = src.count("}")
    bopen  = src.count("[")
    bclose = src.count("]")
    if opens != closes:
        print(f"  ERROR: brace mismatch {opens} {{ vs {closes} }}")
        return False
    if bopen != bclose:
        print(f"  ERROR: bracket mismatch {bopen} [ vs {bclose} ]")
        return False

    # Check for unescaped single quotes in news/title lines
    bad = 0
    for i, line in enumerate(src.splitlines()):
        stripped = line.strip()
        if stripped.startswith("{ title:") or stripped.startswith("{ source:"):
            count = 0
            j = 0
            while j < len(stripped):
                if stripped[j] == "\\":
                    j += 2
                    continue
                if stripped[j] == "'":
                    count += 1
                j += 1
            if count % 2 != 0:
                print(f"  ERROR: odd quote count at line {i+1}: {stripped[:80]}")
                bad += 1
    if bad:
        return False
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    dry_run   = "--dry-run"   in args
    no_backup = "--no-backup" in args
    args = [a for a in args if not a.startswith("--")]

    if len(args) < 2:
        print("Usage: python scripts/apply_scan_results.py <type> <result_file> [--dry-run] [--no-backup]")
        print("  type: news | photos | policy")
        sys.exit(1)

    scan_type   = args[0].lower()
    result_file = Path(args[1])

    if scan_type not in ("news", "photos", "policy"):
        print(f"ERROR: unknown scan type '{scan_type}'. Use: news, photos, policy")
        sys.exit(1)

    if not result_file.exists():
        print(f"ERROR: result file not found: {result_file}")
        sys.exit(1)

    if not CANDIDATES_JS.exists():
        print(f"ERROR: {CANDIDATES_JS} not found")
        sys.exit(1)

    # Load results
    result_data = json.loads(result_file.read_text(encoding="utf-8"))
    if "_instructions" in result_data:
        print("ERROR: result file still has _instructions key — looks like a template, not real results")
        sys.exit(1)

    results = result_data.get("results", [])
    print(f"Applying {len(results)} {scan_type} result(s) from {result_file.name} ...")
    if dry_run:
        print("  (DRY RUN — no files will be modified)")

    # Read source
    src = CANDIDATES_JS.read_text(encoding="utf-8")

    # Apply
    if scan_type == "news":
        new_src, changed = apply_news(src, results, dry_run)
    elif scan_type == "photos":
        new_src, changed = apply_photos(src, results, dry_run)
    elif scan_type == "policy":
        new_src, changed = apply_policy(src, results, dry_run)

    if dry_run:
        print(f"\nDry run complete. Would have changed {changed} candidate(s)/party(ies).")
        return

    if changed == 0:
        print("Nothing to apply.")
        return

    # Validate before writing
    print("\nValidating output ...")
    if not quick_validate(new_src):
        print("VALIDATION FAILED — not writing file. Check the result JSON for bad characters.")
        sys.exit(1)
    print("  Validation passed.")

    # Backup
    if not no_backup:
        backup = CANDIDATES_JS.with_suffix(f".bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(CANDIDATES_JS, backup)
        print(f"  Backup: {backup.name}")

    # Write
    CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\n✓ Applied {changed} change(s) to {CANDIDATES_JS.name}")
    print("  Remember to bump the ?v= cache-bust in municipality.js")


if __name__ == "__main__":
    main()
