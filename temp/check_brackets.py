"""Check bracket balance in candidates.js."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()
depth_curly = 0
depth_sq = 0
depth_paren = 0
in_str = None
in_comment = None
i = 0
n = len(src)
while i < n:
    c = src[i]
    if in_comment == 'line':
        if c == '\n':
            in_comment = None
        i += 1
        continue
    if in_comment == 'block':
        if c == '*' and i + 1 < n and src[i + 1] == '/':
            in_comment = None
            i += 2
            continue
        i += 1
        continue
    if in_str:
        if c == '\\':
            i += 2
            continue
        if c == in_str:
            in_str = None
        i += 1
        continue
    if c == "'":
        in_str = "'"
        i += 1
        continue
    if c == '"':
        in_str = '"'
        i += 1
        continue
    if c == '`':
        in_str = '`'
        i += 1
        continue
    if c == '/' and i + 1 < n:
        if src[i + 1] == '/':
            in_comment = 'line'
            i += 2
            continue
        if src[i + 1] == '*':
            in_comment = 'block'
            i += 2
            continue
    if c == '{':
        depth_curly += 1
    elif c == '}':
        depth_curly -= 1
    elif c == '[':
        depth_sq += 1
    elif c == ']':
        depth_sq -= 1
    elif c == '(':
        depth_paren += 1
    elif c == ')':
        depth_paren -= 1
    i += 1

print(f'Final {{}}: {depth_curly}')
print(f'Final []: {depth_sq}')
print(f'Final (): {depth_paren}')
print(f'In string: {in_str!r}')
print(f'In comment: {in_comment!r}')
