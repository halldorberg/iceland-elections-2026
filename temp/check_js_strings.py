"""Detect literal newlines inside JS single/double quoted strings.
   Properly skips //... and /* ... */ comments and template literals."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()
i = 0
in_str = None
str_start = None
broken = []
n = len(src)
while i < n:
    c = src[i]
    # Inside a string
    if in_str:
        if c == '\\':
            i += 2
            continue
        if c == in_str:
            in_str = None
            str_start = None
            i += 1
            continue
        if c == '\n':
            broken.append((str_start, i))
            i += 1
            continue
        i += 1
        continue
    # Line comment //
    if c == '/' and i + 1 < n and src[i + 1] == '/':
        # skip until newline
        j = src.find('\n', i + 2)
        if j == -1:
            break
        i = j + 1
        continue
    # Block comment /* ... */
    if c == '/' and i + 1 < n and src[i + 1] == '*':
        j = src.find('*/', i + 2)
        if j == -1:
            break
        i = j + 2
        continue
    if c == "'":
        in_str = "'"; str_start = i; i += 1; continue
    if c == '"':
        in_str = '"'; str_start = i; i += 1; continue
    if c == '`':
        i += 1
        while i < n and src[i] != '`':
            if src[i] == '\\':
                i += 2
                continue
            i += 1
        i += 1
        continue
    i += 1

print(f'Broken: {len(broken)}')
for s, n in broken[:5]:
    line = src[:s].count('\n') + 1
    snippet = src[s:n + 30]
    print(f'  line {line}: {snippet[:200]!r}')
