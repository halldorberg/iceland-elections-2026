"""Validate EN and PL overlays for JS syntax issues (unescaped newlines, brackets)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for fn in ('js/data/candidates.en.js', 'js/data/candidates.pl.js'):
    print(f'=== {fn} ===')
    src = open(fn, encoding='utf-8').read()
    n = len(src)
    i = 0
    in_str = None
    str_start = None
    broken = []
    depth_c = 0
    depth_s = 0
    while i < n:
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
                str_start = None
            elif c == '\n':
                broken.append((str_start, i))
            i += 1
            continue
        if c == '/' and i + 1 < n and src[i + 1] == '/':
            j = src.find('\n', i + 2)
            i = (j + 1) if j != -1 else n
            continue
        if c == '"':
            in_str = '"'; str_start = i; i += 1; continue
        if c == "'":
            in_str = "'"; str_start = i; i += 1; continue
        if c == '`':
            i += 1
            while i < n and src[i] != '`':
                if src[i] == '\\':
                    i += 2
                    continue
                i += 1
            i += 1
            continue
        if c == '{': depth_c += 1
        elif c == '}': depth_c -= 1
        elif c == '[': depth_s += 1
        elif c == ']': depth_s -= 1
        i += 1
    print(f'  In-string newlines: {len(broken)}')
    print(f'  Final brackets {{}}: {depth_c}   []: {depth_s}')
    for s, n2 in broken[:3]:
        line = src[:s].count('\n') + 1
        print(f'  line {line}: {src[s:n2+30][:200]!r}')
