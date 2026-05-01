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

        # Find the candidate block by name — anchor on the candidate row start
        # ([N, '<name>', '<occ>', ...) so we don't match other occurrences of the
        # name (e.g. inside bios/heimild strings). The lazy match then walks to
        # the candidate's own news: [ ... ] array.
        name_escaped = re.escape(escape_js(name))
        pattern = (
            r"(\[\d+\s*,\s*'(?:" + name_escaped + r")'\s*,[\s\S]*?news\s*:\s*\[)"
            r"([\s\S]*?)"
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

        # Ensure the existing block ends with a comma so appending new items
        # produces valid JS even when the last existing item lacked one.
        existing = m.group(2)
        existing_rstripped = existing.rstrip()
        if existing_rstripped and not existing_rstripped.endswith(","):
            existing = existing_rstripped + ","
        replacement = m.group(1) + existing + "\n" + "\n".join(new_lines) + m.group(3)
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

def _muni_const_range(src: str, muni_slug: str):
    """Return (start, end) byte positions of the `const <CONST_ID> = {...};`
    block whose REAL_DATA mapping says it belongs to muni_slug. Returns
    (None, None) if not found."""
    real_data = re.search(r"const REAL_DATA\s*=\s*\{(.*?)\};", src, re.DOTALL)
    if not real_data:
        return None, None
    slug_to_const = {}
    for m in re.finditer(r"(\w+)\s*:\s*([A-Z_]+)\s*,", real_data.group(1)):
        slug_to_const[m.group(1)] = m.group(2)
    const_id = slug_to_const.get(muni_slug)
    if not const_id:
        return None, None
    open_re = re.compile(r"^const " + re.escape(const_id) + r"\s*=\s*\{", re.MULTILINE)
    om = open_re.search(src)
    if not om:
        return None, None
    # The const block ends at the next `\n};` after a top-level closing brace.
    # All munis use this exact form — `const X = { ... \n};` with no nested
    # const declarations. Search for next `\n};` after open.
    end_idx = src.find("\n};", om.end())
    if end_idx == -1:
        return None, None
    return om.start(), end_idx + 3


def apply_policy(src: str, results: list[dict], dry_run: bool) -> tuple[str, int]:
    """
    For each result entry, add/replace platformUrl and update agenda items.
    Scoped to the municipality's const block — same party_code can appear in
    many munis, so we never search globally.
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

        # Locate the muni's const block first so we never match a same-coded
        # party in another municipality.
        muni_start, muni_end = _muni_const_range(src, muni_slug)
        if muni_start is None:
            print(f"  ⚠ Could not find const block for muni: {muni_slug}")
            continue

        # Within that const block, find the party's `<code>: {` opening.
        # Party openings sit at column 2, e.g. "  M: {".
        party_open_re = re.compile(
            r"\n  " + re.escape(party_code) + r"\s*:\s*\{"
        )
        po = party_open_re.search(src, muni_start, muni_end)
        if not po:
            print(f"  ⚠ Could not find party block for {muni_slug}.{party_code}")
            continue

        # Then find the tagline inside that party block.
        tagline_re = re.compile(
            r"tagline\s*:\s*'(?:[^'\\]|\\.)*',?"
        )
        tag_m = tagline_re.search(src, po.end(), muni_end)
        if not tag_m:
            print(f"  ⚠ {muni_slug}.{party_code}: party block has no tagline")
            continue

        # Build a synthetic match-equivalent: m.start() = po.start, span ends at tag_m.end()
        class _M:
            pass
        m = _M()
        m.start = lambda: po.start()  # type: ignore
        m.end   = lambda: tag_m.end()  # type: ignore

        # Block end is the next "\n  }" after the party opening, but constrained
        # to the muni's const range.
        block_end = src.find("\n  }", po.start(), muni_end)
        if block_end == -1:
            block_end = po.start() + 2000  # safety
        block = src[po.start():block_end]

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


# ── Bios applier ─────────────────────────────────────────────────────────────

def apply_bios(src: str, results: list[dict], dry_run: bool) -> tuple[str, int]:
    """
    For each result entry, update the candidate's extended data block with
    bio, age, interests, and/or social fields (whichever are provided).
    Only works for candidates that already have an extended {age:..., bio:...} block.
    """
    changed = 0
    for entry in results:
        name = entry["name"]
        name_escaped = re.escape(escape_js(name))

        # Find the candidate's extended block, scoped to the muni's const block
        # so we don't update a same-name candidate from another muni.
        muni_slug = entry.get("muni_slug")
        search_start, search_end = 0, len(src)
        if muni_slug:
            ms, me = _muni_const_range(src, muni_slug)
            if ms is not None:
                search_start, search_end = ms, me
        block_re = re.compile(
            r"(\[\d+\s*,\s*'" + name_escaped + r"'.*?\{)(.*?)(\}(?:\]|,\s*\]))",
            re.DOTALL
        )
        m = block_re.search(src, search_start, search_end)
        if not m:
            where = f" in {muni_slug}" if muni_slug else ""
            print(f"  ⚠ Could not find extended block for: {name}{where}")
            continue

        block = m.group(2)

        # Apply bio
        bio = entry.get("bio")
        if bio:
            bio_escaped = escape_js(bio)
            if re.search(r"bio\s*:\s*null", block):
                block = re.sub(r"bio\s*:\s*null", f"bio: '{bio_escaped}'", block, count=1)
            elif re.search(r"bio\s*:\s*'", block):
                block = re.sub(r"bio\s*:\s*'(?:[^'\\]|\\.)*'", f"bio: '{bio_escaped}'", block, count=1)

        # Apply age
        age = entry.get("age")
        if age is not None:
            if re.search(r"age\s*:\s*null", block):
                block = re.sub(r"age\s*:\s*null", f"age: {int(age)}", block, count=1)

        # Apply interests
        interests = entry.get("interests")
        if interests:
            items = ", ".join(f"'{escape_js(i)}'" for i in interests)
            arr = f"[{items}]"
            if re.search(r"interests\s*:\s*null", block):
                block = re.sub(r"interests\s*:\s*null", f"interests: {arr}", block, count=1)

        # Apply social
        social = entry.get("social")
        if social:
            pairs = ", ".join(f"{k}: '{escape_js(v)}'" for k, v in social.items() if v)
            obj = f"{{ {pairs} }}"
            if re.search(r"social\s*:\s*null", block):
                block = re.sub(r"social\s*:\s*null", f"social: {obj}", block, count=1)

        new_segment = m.group(1) + block + m.group(3)
        if new_segment == m.group(0):
            print(f"  ✓ {name}: nothing to update (fields already set or not provided)")
            continue

        if dry_run:
            print(f"  [DRY RUN] {name}: would update bio/age/interests/social")
        else:
            src = src[:m.start()] + new_segment + src[m.end():]
            print(f"  ✓ {name}: bio/age/interests/social updated")
            changed += 1

    return src, changed


# ── Validation ────────────────────────────────────────────────────────────────

def _party_block_range(src: str, muni_slug: str, party_code: str):
    """Return (start, end) byte range of the muni.party block, or (None, None)."""
    muni_start, muni_end = _muni_const_range(src, muni_slug)
    if muni_start is None:
        return None, None
    party_open_re = re.compile(r"\n  " + re.escape(party_code) + r"\s*:\s*\{")
    po = party_open_re.search(src, muni_start, muni_end)
    if not po:
        return None, None
    # End: the line `  },` or `  }` that closes the party object at indent=2.
    block_end = src.find("\n  },", po.start(), muni_end)
    if block_end == -1:
        block_end = src.find("\n  }", po.start(), muni_end)
    if block_end == -1:
        return None, None
    return po.start(), block_end + 4  # include "\n  },"


def verify_policy_apply(before: str, after: str, results: list) -> tuple[bool, list]:
    """Two-layer round-trip check for policy applies.

    Layer 1 — per-entry round-trip:
      For each result entry, the (muni, party) block in `after` must contain
      the expected tagline and platform_url.

    Layer 2 — cross-block leakage:
      Mask out the targeted (muni, party) blocks in both `before` and `after`,
      compare what remains. Any difference outside the targets is leakage —
      the symptom that bit us when the unscoped regex clobbered RVK.D with
      Vogar/D content.

    Returns (ok, errors).
    """
    errors: list[str] = []

    # ── Layer 1 ──
    for entry in results:
        muni  = entry["muni_slug"]
        party = entry["party_code"]
        expected_tagline = entry.get("tagline", "")
        expected_url     = entry.get("platform_url", "")

        ps, pe = _party_block_range(after, muni, party)
        if ps is None:
            errors.append(f"  ✗ {muni}.{party}: party block not found post-apply")
            continue
        block = after[ps:pe]

        if expected_tagline:
            if escape_js(expected_tagline) not in block:
                errors.append(
                    f"  ✗ {muni}.{party}: expected tagline not found in block — "
                    f"either the apply went to the wrong place, or the tagline regex missed."
                )
        if expected_url and expected_url not in block:
            errors.append(
                f"  ✗ {muni}.{party}: expected platform_url not found in block."
            )

    # ── Layer 2 ──
    def collect_ranges(src):
        ranges = []
        for entry in results:
            ps, pe = _party_block_range(src, entry["muni_slug"], entry["party_code"])
            if ps is not None:
                ranges.append((ps, pe))
        return sorted(ranges)

    def mask_canonical(src, ranges):
        out, last = [], 0
        for i, (s, e) in enumerate(ranges):
            out.append(src[last:s])
            out.append(f"<<TARGETED:{i}>>")
            last = e
        out.append(src[last:])
        return "".join(out)

    ranges_before = collect_ranges(before)
    ranges_after  = collect_ranges(after)
    if len(ranges_before) != len(ranges_after):
        errors.append(
            f"  ✗ Targeted-block count differs: {len(ranges_before)} before vs "
            f"{len(ranges_after)} after — apply may have created or destroyed party blocks."
        )

    masked_before = mask_canonical(before, ranges_before)
    masked_after  = mask_canonical(after,  ranges_after)

    if masked_before != masked_after:
        import difflib
        diff = list(difflib.unified_diff(
            masked_before.splitlines(),
            masked_after.splitlines(),
            lineterm="", n=1,
        ))
        errors.append("  ✗ Unexpected changes outside targeted (muni, party) blocks:")
        # First ~20 lines of the unified diff is enough to localise leakage.
        for line in diff[:20]:
            errors.append(f"      {line}")
        if len(diff) > 20:
            errors.append(f"      ... ({len(diff) - 20} more diff lines)")

    return (len(errors) == 0, errors)


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

    if scan_type not in ("news", "photos", "policy", "bios"):
        print(f"ERROR: unknown scan type '{scan_type}'. Use: news, photos, policy, bios")
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
    elif scan_type == "bios":
        new_src, changed = apply_bios(src, results, dry_run)

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
    print("  Syntactic validation passed.")

    # Locality round-trip check (policy only for now — extend per scan_type as
    # the same kind of cross-block leakage is identified for other appliers).
    if scan_type == "policy":
        ok, errors = verify_policy_apply(src, new_src, results)
        if not ok:
            print("\nLOCALITY CHECK FAILED — not writing file:")
            for line in errors:
                print(line)
            print(
                "\nThe in-memory diff shows changes outside the targeted (muni, party) "
                "blocks. This usually means a regex matched the wrong block. Fix the "
                "applier (or the result JSON) before re-running."
            )
            sys.exit(1)
        print("  Locality check passed (no leakage outside targeted blocks).")

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
