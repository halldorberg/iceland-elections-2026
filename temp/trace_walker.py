import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('js/data/candidates.js', encoding='utf-8').read()
m = re.search(r'^const RVK\s*=\s*\{', src, re.MULTILINE)
open_pos = m.end() - 1
print('open_pos:', open_pos, 'char:', repr(src[open_pos]))
depth = 0
i = open_pos
iterations = 0
in_string_at = None
while i < len(src):
    iterations += 1
    c = src[i]
    if c in ("'", '"'):
        quote = c
        in_string_at = i
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
            print(f'CLOSED at {i}, line ~{src[:i].count(chr(10))}')
            print('preview:', repr(src[max(0,i-80):i+10]))
            sys.exit(0)
    i += 1
print(f'WALKED OFF END at i={i}, depth still {depth}, last_string_at={in_string_at}')
print(f'iters: {iterations}')
