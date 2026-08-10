"""Find all agendas that look like placeholders (thin text, no source_quote)
and tag with the date of last git modification."""
import re, subprocess, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
JS = ROOT / 'js' / 'data' / 'candidates.js'

src = JS.read_text(encoding='utf-8')

# Map muni constants → muni IDs
m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
muni_const_to_id = {}
for pm in re.finditer(r"(\w+):\s*([A-Z][A-Z0-9_]*)", m.group(1)):
    muni_const_to_id[pm.group(2)] = pm.group(1)


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m: return None
    op = m.end() - 1
    depth = 0; i = op; in_str = None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\': i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c in ("'", '"', '`'): in_str = c; i += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return op + 1, i
        i += 1


def find_agenda_range(text, base_offset):
    """Return absolute (start, end) of `agenda: [...]` inside the text."""
    am = re.search(r'agenda:\s*\[', text)
    if not am:
        return None
    open_idx = am.end() - 1
    depth = 0
    i = open_idx
    while i < len(text):
        c = text[i]
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return base_offset + am.start(), base_offset + i + 1
        i += 1
    return None


def line_of(offset):
    return src[:offset].count('\n') + 1


def git_last_modified(start_line, end_line):
    """Find the most recent commit that touched any line in [start_line, end_line]."""
    try:
        p = subprocess.run(
            ['git', 'log', '-1', '--format=%ai|%h|%s',
             f'-L{start_line},{end_line}:js/data/candidates.js'],
            cwd=str(ROOT), capture_output=True, text=True, encoding='utf-8',
            timeout=30,
        )
        out = p.stdout.split('\n')[0] if p.stdout else ''
        return out
    except Exception as e:
        return f'err: {e}'


results = []

for const, muni_id in muni_const_to_id.items():
    rng = find_const_block(src, const)
    if not rng: continue
    cs, ce = rng
    body = src[cs:ce]
    # Each party in this muni
    for pm in re.finditer(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', body):
        party = pm.group(1)
        # Walk party block to find its end
        i = pm.end() - 1
        depth = 0; in_str = None
        while i < len(body):
            c = body[i]
            if in_str:
                if c == '\\': i += 2; continue
                if c == in_str: in_str = None
                i += 1; continue
            if c in ("'", '"', '`'): in_str = c; i += 1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        ptext = body[pm.end() - 1:i + 1]
        ag_range = find_agenda_range(ptext, cs + pm.end() - 1)
        if not ag_range:
            continue
        ag_text = src[ag_range[0]:ag_range[1]]
        # Stats
        items = []
        depth2 = 0
        in_str2 = None
        cur_start = None
        for k, c in enumerate(ag_text):
            if in_str2:
                if c == '\\':
                    continue
                if c == in_str2:
                    in_str2 = None
                continue
            if c in ("'", '"', '`'):
                in_str2 = c
                continue
            if c == '{':
                if depth2 == 0: cur_start = k
                depth2 += 1
            elif c == '}':
                depth2 -= 1
                if depth2 == 0 and cur_start is not None:
                    items.append(ag_text[cur_start:k+1])
                    cur_start = None
        # Per-item text length + source_quote count
        text_lens = []
        has_sq = 0
        for it in items:
            tm = re.search(r"text:\s*'((?:[^'\\]|\\.)+)'", it)
            if tm:
                text_lens.append(len(tm.group(1)))
            if "source_quote" in it:
                has_sq += 1
        if not items:
            continue
        avg = sum(text_lens) / len(text_lens) if text_lens else 0
        sq_pct = has_sq / len(items) * 100
        # Git modification
        start_line = line_of(ag_range[0])
        end_line = line_of(ag_range[1])
        gitinfo = git_last_modified(start_line, end_line)
        results.append({
            'muni': muni_id,
            'party': party,
            'items': len(items),
            'avg_text': avg,
            'src_quote_pct': sq_pct,
            'lines': f'{start_line}-{end_line}',
            'git': gitinfo,
        })

# Print as a sortable table
print(f'{"muni":<18s} {"party":<5s} {"items":>5s} {"avg_text":>9s} {"sq%":>5s}  {"last touched":<60s}')
print('─' * 110)

# Sort: thinnest (lowest avg_text, no source_quote, oldest commit) first
def sort_key(r):
    # Primary: 0 if no source_quotes, 1 otherwise. Secondary: avg_text ascending.
    has_sq = r['src_quote_pct'] > 0
    return (has_sq, r['avg_text'])

for r in sorted(results, key=sort_key):
    git = r['git'] or '(could not determine)'
    # Truncate git message
    if '|' in git:
        date, sha, msg = git.split('|', 2)
        date = date.split(' ')[0]
        git_short = f'{date} {sha} {msg[:50]}'
    else:
        git_short = git[:60]
    print(f'{r["muni"]:<18s} {r["party"]:<5s} {r["items"]:>5d} {r["avg_text"]:>9.0f} {r["src_quote_pct"]:>4.0f}%  {git_short:<60s}')
