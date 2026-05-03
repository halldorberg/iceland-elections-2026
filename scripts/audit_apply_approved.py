"""Apply user-approved bios from audit_results.json into candidates.js.

For each approved candidate ID:
  - If audit_results[id] has a rescue.rewrite → replace bio + heimild
    in candidates.js with the rewrite + rescue.new_heimild.
  - If no rewrite (clean as-is approval) → no candidates.js change.
  - Mark audit_results[id].applied = true on success.

Validates JS syntax (brace/bracket balance) after edits.
Backs up candidates.js before editing.

Usage:
    python scripts/audit_apply_approved.py "ID1, ID2, ID3"
"""
from __future__ import annotations
import json, re, sys, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
AUDIT_JSON = ROOT / "scan_results" / "audit_results.json"


def escape_js(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def _find_const_block(src: str, const_name: str) -> tuple[int, int] | None:
    """Return (start, end) of the body of `const X = { ... };` matching const_name.
    start = position right after the opening `{`, end = position of the closing `}`."""
    m = re.search(r"^const " + re.escape(const_name) + r"\s*=\s*\{", src, re.MULTILINE)
    if not m:
        return None
    open_pos = m.end() - 1
    # walk to find matching close, respecting strings + brackets
    depth = 0
    i = open_pos
    while i < len(src):
        c = src[i]
        if c in ("'", '"'):
            # skip string
            quote = c
            i += 1
            while i < len(src):
                ch = src[i]
                if ch == "\\":
                    i += 2
                    continue
                if ch == quote:
                    i += 1
                    break
                i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1
    return None


def _find_party_row(src: str, const_name: str, party_code: str, ballot: int) -> re.Match | None:
    """Find the candidate row in the candidates.js source.
    Returns a regex match against the entire row from the leading `[` to its
    matching `]`, scoped within the muni's const block.
    """
    span = _find_const_block(src, const_name)
    if not span:
        return None
    body_start, body_end = span

    # Find the party block within this muni
    # Indent is 2 spaces and the party code is followed by `:`
    party_re = re.compile(r"\n  " + re.escape(party_code) + r"\s*:\s*\{")
    pm = party_re.search(src, body_start, body_end)
    if not pm:
        return None

    # The party block ends at the next "\n  }" or "\n  }," at indent 2
    party_close = src.find("\n  }", pm.end(), body_end)
    if party_close == -1:
        return None

    # Now find the row whose first integer is `ballot`
    # Pattern: `[<ballot>, 'name', 'occupation', ...`
    row_re = re.compile(r"\[\s*" + str(ballot) + r"\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*?)'", re.DOTALL)
    return row_re.search(src, pm.end(), party_close)


def _row_extent(src: str, row_start: int) -> int:
    """Given the position of `[` opening a row, return the position just past
    the matching `]`. Respects strings and nested brackets."""
    if src[row_start] != "[":
        # Walk back; row_re matched at \[ already
        pass
    depth = 0
    i = row_start
    while i < len(src):
        c = src[i]
        if c in ("'", '"'):
            quote = c
            i += 1
            while i < len(src):
                ch = src[i]
                if ch == "\\":
                    i += 2
                    continue
                if ch == quote:
                    i += 1
                    break
                i += 1
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _build_heimild_js(new_heimild: list[dict]) -> str:
    if new_heimild:
        items = ", ".join(
            "{ url: '" + escape_js(h.get("url", "")) + "', label: '" + escape_js(h.get("label", "")) + "' }"
            for h in new_heimild if h.get("url")
        )
        return "[" + items + "]"
    return "null"


def _replace_bio_and_heimild(row_text: str, new_bio: str, new_heimild: list[dict]) -> str:
    """Within a single candidate row text, do one of:
      - extended block exists (`{ ... bio: ... ... }`): replace bio + heimild
      - plain row (`[N, 'name', 'occ', 'image']` or `[N, 'name', 'occ']`):
        extend with fresh `{ age: null, bio: '...', interests: null,
        social: null, heimild: [...], news: [] }` block.
    """
    bio_escaped = "'" + escape_js(new_bio) + "'"
    heimild_js = _build_heimild_js(new_heimild)

    # Path 1: extended block already exists
    bio_pattern = re.compile(r"bio\s*:\s*(?:null|'(?:[^'\\]|\\.)*')")
    if bio_pattern.search(row_text):
        row_text = bio_pattern.sub("bio: " + bio_escaped, row_text, count=1)
        heimild_pattern = re.compile(r"heimild\s*:\s*(?:null|\[[^\]]*\])(?=\s*,|\s*\})", re.DOTALL)
        if heimild_pattern.search(row_text):
            row_text = heimild_pattern.sub("heimild: " + heimild_js, row_text, count=1)
        else:
            # Inject after bio
            row_text = re.sub(
                r"(bio\s*:\s*'(?:[^'\\]|\\.)*',)",
                r"\1 heimild: " + heimild_js + ",",
                row_text, count=1
            )
        return row_text

    # Path 2: plain row → add an extended block
    new_block = (
        "{ age: null, bio: " + bio_escaped + ", interests: null, "
        "social: null, heimild: " + heimild_js + ", news: [] }"
    )
    # Match `[N, 'name', 'occ'(, 'images/...')?]` and inject the block before `]`
    plain_re = re.compile(
        r"^\[(\s*\d+\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*'(?:[^'\\]|\\.)*'(?:\s*,\s*'images/[^']+')?)\s*\](.*)$",
        re.DOTALL,
    )
    m = plain_re.match(row_text)
    if not m:
        raise ValueError("row not in plain or extended format")
    return "[" + m.group(1) + ", " + new_block + "]" + (m.group(2) or "")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2:
        print("Usage: python audit_apply_approved.py 'ID1, ID2, ...'", file=sys.stderr)
        return 1

    raw_ids = sys.argv[1]
    ids = [i.strip() for i in re.split(r"[,\s]+", raw_ids) if i.strip()]
    print(f"Approved IDs to apply: {len(ids)}")

    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    src = CANDIDATES_JS.read_text(encoding="utf-8")
    # Backup
    bak = CANDIDATES_JS.with_name("candidates.js.bak_apply_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    bak.write_text(src, encoding="utf-8")
    print(f"  Backup: {bak.name}")

    # Stats
    rewrite_count = 0
    asis_count = 0
    skip_count = 0
    skipped = []
    not_found = []

    new_src = src
    for cid in ids:
        if cid not in audit:
            # Likely a skipped bio (bio: null in candidates.js — user is
            # approving "leave the skip as-is"). Record a stub entry so the
            # UI shows it as applied next render.
            audit[cid] = {
                "applied": True,
                "applied_as": "skip",
                "stats": {"verified": 0, "flagged": 0, "unreachable": 0},
                "statements": [],
                "summary": "User approved skip (no bio researched).",
            }
            skip_count += 1
            continue
        entry = audit[cid]
        if entry.get("applied"):
            skipped.append((cid, "already applied"))
            continue

        rescue = entry.get("rescue") or {}
        rewrite = rescue.get("rewrite")

        # Choose what to apply:
        #   - rewrite-approval: rescue.rewrite + rescue.new_heimild
        #   - as-is approval:   entry.bio (original) + entry.sources
        if rewrite:
            apply_bio = rewrite
            apply_heimild = rescue.get("new_heimild") or []
            apply_kind = "rewrite"
        else:
            apply_bio = entry.get("bio")
            if not apply_bio:
                # No bio at all — treat as skip (shouldn't happen for as-is path)
                entry["applied"] = True
                entry["applied_as"] = "skip"
                skip_count += 1
                continue
            # Convert plain-string sources to {url, label} dicts if needed
            raw_sources = entry.get("sources", [])
            apply_heimild = []
            for s in raw_sources:
                if isinstance(s, dict):
                    apply_heimild.append(s)
                elif isinstance(s, str) and s.startswith("http"):
                    label = s.split("/")[2] if s.count("/") >= 2 else s
                    apply_heimild.append({"url": s, "label": label})
            apply_kind = "as-is"

        # Need to find the row in candidates.js
        parts = cid.split(".")
        if len(parts) != 3:
            not_found.append((cid, "id format"))
            continue
        const_name, party_code, ballot_s = parts
        try:
            ballot = int(ballot_s)
        except ValueError:
            not_found.append((cid, "bad ballot"))
            continue

        m = _find_party_row(new_src, const_name, party_code, ballot)
        if not m:
            not_found.append((cid, "row not found"))
            continue

        # row starts at the `[`
        row_start = m.start()
        row_end = _row_extent(new_src, row_start)
        if row_end < 0:
            not_found.append((cid, "row close not found"))
            continue
        row_text = new_src[row_start:row_end]

        try:
            new_row_text = _replace_bio_and_heimild(row_text, apply_bio, apply_heimild)
        except ValueError as e:
            not_found.append((cid, f"replace failed: {e}"))
            continue

        new_src = new_src[:row_start] + new_row_text + new_src[row_end:]
        entry["applied"] = True
        entry["applied_as"] = apply_kind
        if apply_kind == "rewrite":
            rewrite_count += 1
        else:
            asis_count += 1

    # Validate
    if new_src.count("{") != new_src.count("}"):
        print(f"  ERROR: brace imbalance after edits ({new_src.count('{')} vs {new_src.count('}')})", file=sys.stderr)
        return 1
    if new_src.count("[") != new_src.count("]"):
        print(f"  ERROR: bracket imbalance after edits ({new_src.count('[')} vs {new_src.count(']')})", file=sys.stderr)
        return 1
    print(f"  Brace/bracket balance OK")

    # Write
    CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n  Rewrites applied (bio + heimild changed in candidates.js): {rewrite_count}")
    print(f"  As-is sign-offs   (no JS change):                          {asis_count}")
    print(f"  Skip approvals    (no JS change, was bio: null):           {skip_count}")
    if skipped:
        print(f"  Skipped: {len(skipped)}")
        for cid, why in skipped[:10]:
            print(f"    {cid}: {why}")
    if not_found:
        print(f"  NOT FOUND ({len(not_found)}):")
        for cid, why in not_found:
            print(f"    {cid}: {why}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
