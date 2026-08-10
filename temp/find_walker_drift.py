"""Walk RVK char-by-char with a paranoid brace tracker, then re-walk with
the same algorithm the apply script uses, and report the FIRST character
position where they disagree."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()
m = re.search(r'^const RVK\s*=\s*\{', src, re.MULTILINE)
start = m.end() - 1  # at the {
end_brace = src.rfind('};', start, src.find('const DEFAULT_AGENDAS')) + 1

def walk(label, escape_skip):
    """Walk and return list of brace events: (pos, char, depth_after)."""
    depth = 0
    i = start
    events = []
    while i < end_brace:
        c = src[i]
        if c in ("'", '"'):
            quote = c
            string_start = i
            i += 1
            while i < end_brace:
                if src[i] == "\\":
                    i += escape_skip
                    continue
                if src[i] == quote:
                    i += 1
                    break
                i += 1
            else:
                events.append((string_start, 'RUNAWAY-' + quote, depth))
                break
            continue
        if c == '{':
            depth += 1
            events.append((i, '{', depth))
        elif c == '}':
            depth -= 1
            events.append((i, '}', depth))
        i += 1
    return events, depth

# Walker the apply script uses (skip 2 chars after backslash)
events_a, depth_a = walk('apply', 2)
# A version that doesn't bend escape rules so wildly (skip 1 to consume the backslash, then continue normally)
events_b, depth_b = walk('paranoid', 1)

print(f'apply-style final depth: {depth_a}, events: {len(events_a)}')
print(f'paranoid    final depth: {depth_b}, events: {len(events_b)}')

# Find first position where they diverge
for j in range(min(len(events_a), len(events_b))):
    if events_a[j] != events_b[j]:
        pa, ca, da = events_a[j]
        pb, cb, db = events_b[j]
        print(f'\nFIRST DIVERGENCE at event {j}:')
        print(f'  apply:    pos {pa} char {ca} depth {da}')
        print(f'  paranoid: pos {pb} char {cb} depth {db}')
        # Show context around earliest pos
        cpos = min(pa, pb)
        line = src[:cpos].count('\n') + 1
        print(f'  approx line {line}')
        print(f'  context: {src[max(0,cpos-120):cpos+30].encode("ascii","replace").decode()!r}')
        break
else:
    print('Walkers agree')
