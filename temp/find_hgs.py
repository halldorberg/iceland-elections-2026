import re
src = open(r'F:\Claude Projects\iceland-elections\js\data\candidates.js', encoding='utf-8').read()
m = re.search(r'^const HGS = \{', src, re.M)
print('HGS const at line', src[:m.start()].count('\n') + 1)
i = m.end() - 1
depth = 0
in_str = None
brace_open = False
while i < len(src):
    c = src[i]
    if in_str:
        prev = src[i-1] if i > 0 else ''
        if c == in_str and prev != '\\':
            in_str = None
    elif c == '"' or c == "'":
        in_str = c
    elif c == '{':
        depth += 1
        brace_open = True
    elif c == '}':
        depth -= 1
        if brace_open and depth == 0:
            break
    i += 1
end_line = src[:i].count('\n') + 1
print('HGS ends at line', end_line)
# print top section to see codes
print(src[m.start():m.start()+800])
