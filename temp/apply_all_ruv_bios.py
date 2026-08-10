"""Apply all RUV draft bios from scan_results/ruv_bios.json into candidates.js.
   Targets only entries with a ruv_id (skips fb_only ones — already applied).
   Updates the bio field within the matching candidate object."""
import json, re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = ROOT / 'js' / 'data' / 'candidates.js'
RUV = ROOT / 'scan_results' / 'ruv_bios.json'


def escape_js(s):
    return (s.replace('\\', '\\\\')
             .replace("'", "\\'")
             .replace('\n', '\\n')
             .replace('\r', '\\r'))


def find_const_block(src, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', src, re.M)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    in_str = None
    while i < len(src):
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1


def find_party_block(src, const_start, const_end, party_code):
    """Find the start and end of a party object inside the const block."""
    pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    m = pat.search(src, const_start, const_end)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    in_str = None
    while i < const_end:
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1


def find_candidate_row(src, party_start, party_end, ballot):
    """Find the candidate row [N, ...] within a party's list array.
       Returns (row_start, row_end) where row_end points past the closing ]."""
    # Pattern: line starting with "      [N," or similar at proper indent
    pat = re.compile(r'\n\s+\[\s*' + str(ballot) + r'\s*,')
    m = pat.search(src, party_start, party_end)
    if not m:
        return None
    bracket_pos = src.find('[', m.start())
    i = bracket_pos
    depth = 0
    in_str = None
    while i < party_end:
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return bracket_pos, i + 1
        i += 1


def update_bio_in_row(row_text, new_bio, ruv_sources=None):
    """Replace bio: 'old' or bio: null inside a candidate row.
       Also merge ruv_sources into the existing heimild (deduplicating by URL).
       If the row has no extended object yet, return None (caller will extend)."""
    bio_escaped = escape_js(new_bio)
    replacement = f"bio: '{bio_escaped}'"
    repl_fn = lambda m: replacement
    new_row = None
    if re.search(r"bio\s*:\s*null", row_text):
        new_row = re.sub(r"bio\s*:\s*null", repl_fn, row_text, count=1)
    elif re.search(r"bio\s*:\s*'(?:[^'\\]|\\.)*'", row_text):
        new_row = re.sub(r"bio\s*:\s*'(?:[^'\\]|\\.)*'", repl_fn, row_text, count=1)
    else:
        return None

    # Merge ruv_sources into existing heimild
    if ruv_sources:
        # Extract existing heimild URLs
        existing_urls = set(re.findall(r"\{\s*url:\s*'((?:[^'\\]|\\.)+)'", new_row))
        new_src_items = []
        for s in ruv_sources:
            if not isinstance(s, dict):
                continue
            url = s.get('url', '')
            label = s.get('label', '')
            if not url or url in existing_urls:
                continue
            new_src_items.append(
                "{ url: '" + escape_js(url) + "', label: '" + escape_js(label) + "' }"
            )
            existing_urls.add(url)
        if new_src_items:
            extra = ', '.join(new_src_items)
            # Try several patterns for the existing heimild field
            if re.search(r"heimild:\s*null", new_row):
                new_row = re.sub(
                    r"heimild:\s*null",
                    lambda m: f"heimild: [{extra}]",
                    new_row, count=1
                )
            elif re.search(r"heimild:\s*\[\s*\]", new_row):
                new_row = re.sub(
                    r"heimild:\s*\[\s*\]",
                    lambda m: f"heimild: [{extra}]",
                    new_row, count=1
                )
            else:
                # Insert before the closing ] of the existing heimild array.
                # Find the heimild array and append items.
                hm = re.search(r"heimild:\s*\[", new_row)
                if hm:
                    # Walk to the matching closing ]
                    i = hm.end() - 1
                    depth = 0
                    in_str = None
                    while i < len(new_row):
                        c = new_row[i]
                        if in_str:
                            if c == '\\':
                                i += 2
                                continue
                            if c == in_str:
                                in_str = None
                            i += 1
                            continue
                        if c in ("'", '"', '`'):
                            in_str = c
                            i += 1
                            continue
                        if c == '[':
                            depth += 1
                        elif c == ']':
                            depth -= 1
                            if depth == 0:
                                break
                        i += 1
                    # Insert before closing ]
                    insertion = ', ' + extra
                    new_row = new_row[:i] + insertion + new_row[i:]
    return new_row


def extend_plain_row(row_text, new_bio, sources):
    """Take a plain row like `[N, 'name', 'occ']` or `[N, 'name', 'occ', 'images/...']`
       and add an extended block with the bio. Return new row text or None if the
       row format isn't recognized."""
    bio_escaped = escape_js(new_bio)
    src_items = ''
    if sources:
        parts = []
        for s in sources:
            if not isinstance(s, dict): continue
            url = s.get('url', '')
            label = s.get('label', '')
            if not url: continue
            parts.append("{ url: '" + escape_js(url) + "', label: '" + escape_js(label) + "' }")
        if parts:
            src_items = ', '.join(parts)
    heimild_js = f"[{src_items}]" if src_items else 'null'
    ext = f"{{ age: null, bio: '{bio_escaped}', interests: null, social: null, heimild: {heimild_js}, news: [] }}"

    # Plain row WITH photo: [N, 'name', 'occ', 'images/...']
    m = re.match(r"^(\[\d+\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*'images/[^']+')\s*\]$", row_text)
    if m:
        return m.group(1) + ', ' + ext + ']'
    # Plain row WITHOUT photo: [N, 'name', 'occ']
    m = re.match(r"^(\[\d+\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*'(?:[^'\\]|\\.)*')\s*\]$", row_text)
    if m:
        return m.group(1) + ', null, ' + ext + ']'
    return None


# Build muni_const → const var mapping (e.g. 'RVK' → 'RVK')
# In candidates.js, const names match muni_const for most munis.
# But some have differing const names. Let me build mapping from REAL_DATA.
def build_muni_to_const(src):
    m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
    if not m:
        raise RuntimeError('REAL_DATA not found')
    mapping = {}
    for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', m.group(1)):
        muni_id, var_name = pm.group(1), pm.group(2)
        mapping[var_name.lower()] = var_name  # const var name
    # Also map muni_const → const_var via slug? In ruv_bios.json muni_const IS the const var name.
    # Just return identity mapping of const var names.
    return {v: v for v in mapping.values()}


def main(dry_run=False):
    src = CJS.read_text(encoding='utf-8')
    ruv = json.load(open(RUV, encoding='utf-8'))

    # Filter: only entries with ruv_id (skip fb_only) and with new_bio
    target = [e for e in ruv if e.get('ruv_id') and e.get('new_bio')]
    print(f'Targeting {len(target)} of {len(ruv)} entries')

    # Pre-compute const block positions for each muni_const we'll touch
    munis_used = sorted({e['muni_const'] for e in target})
    const_ranges = {}
    for m in munis_used:
        r = find_const_block(src, m)
        if r is None:
            print(f'  WARN: const {m} not found')
            continue
        const_ranges[m] = r

    # Build cache of party block ranges (per (muni, party))
    party_ranges = {}

    # We'll batch updates: collect (start, end, new_text) tuples, then apply
    # in reverse order so positions remain valid.
    edits = []
    not_found = 0
    extended = 0          # path 1: existing extended block updated
    extended_added = 0    # path 2/3: extended block added to plain row
    no_change = 0
    bad_format = 0

    for e in target:
        muni = e['muni_const']
        party = e['party_code']
        ballot = e['ballot']
        new_bio = e['new_bio']
        sources = e.get('sources') or []

        if muni not in const_ranges:
            not_found += 1
            continue

        cs, ce = const_ranges[muni]
        key = (muni, party)
        if key not in party_ranges:
            party_ranges[key] = find_party_block(src, cs, ce, party)
        pr = party_ranges[key]
        if pr is None:
            not_found += 1
            continue
        ps, pe = pr

        cand = find_candidate_row(src, ps, pe, ballot)
        if cand is None:
            not_found += 1
            continue
        rs, re_pos = cand
        row_text = src[rs:re_pos]

        new_row = update_bio_in_row(row_text, new_bio, sources)
        if new_row is not None:
            if new_row == row_text:
                no_change += 1
            else:
                edits.append((rs, re_pos, new_row))
                extended += 1
            continue

        # Plain row → extend it
        new_row = extend_plain_row(row_text, new_bio, sources)
        if new_row is None:
            bad_format += 1
            continue
        edits.append((rs, re_pos, new_row))
        extended_added += 1

    will_update = extended + extended_added
    print(f'\nWill update existing extended: {extended}')
    print(f'Will extend plain rows:        {extended_added}')
    print(f'No change (already same):      {no_change}')
    print(f'Not found:                     {not_found}')
    print(f'Bad row format:                {bad_format}')
    print(f'TOTAL edits:                   {will_update}')

    if dry_run:
        print('\nDRY RUN — not writing.')
        return

    # Apply edits in reverse order
    edits.sort(key=lambda x: x[0], reverse=True)
    for rs, re_pos, new_row in edits:
        src = src[:rs] + new_row + src[re_pos:]

    CJS.write_text(src, encoding='utf-8')
    print(f'\nWrote candidates.js')


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    main(dry_run=dry)
