import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('js/data/candidates.js', encoding='utf-8').read()
# RVK from char 303 to 197491+something. Find the '};' ending of RVK
m = re.search(r'^const RVK\s*=\s*\{', src, re.MULTILINE)
start = m.start()
end_pos = src.find('const DEFAULT_AGENDAS')
# back up to find the };
end_brace = src.rfind('};', start, end_pos) + 1
print(f'RVK: {start}-{end_brace}')

depth = 0
i = start
unmatched_opens = []
last_closes_unmatched = []
in_str_count = 0
problem_at = None
while i < end_brace:
    c = src[i]
    if c in ("'", '"'):
        quote = c
        str_start = i
        i += 1
        while i < end_brace:
            if src[i] == "\\":
                i += 2
                continue
            if src[i] == quote:
                i += 1
                break
            i += 1
        else:
            problem_at = ('runaway-string', str_start)
            break
        continue
    if c == '{':
        depth += 1
        unmatched_opens.append(i)
    elif c == '}':
        depth -= 1
        if unmatched_opens:
            unmatched_opens.pop()
        else:
            last_closes_unmatched.append(i)
    i += 1

print(f'final depth: {depth}')
print(f'still-open: {len(unmatched_opens)}')
print(f'extra-close: {len(last_closes_unmatched)}')
print(f'problem: {problem_at}')
for pos in unmatched_opens[-5:]:
    line = src[:pos].count('\n') + 1
    print(f'  unmatched open at line {line}: {src[max(0,pos-60):pos+10].encode("ascii","replace").decode()}')
