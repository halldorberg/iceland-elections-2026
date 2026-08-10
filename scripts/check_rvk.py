#!/usr/bin/env python3
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', encoding='utf-8') as f:
    content = f.read()

# Find the REAL end of RVK const (where depth reaches 0)
muni_start = content.find('\nconst RVK = {')
brace_start = content.index('{', muni_start)
depth = 0
pos = brace_start
in_string = False
string_char = None
BACKSLASH = chr(92)
while pos < len(content):
    c = content[pos]
    if in_string:
        if c == BACKSLASH:
            pos += 1
        elif c == string_char:
            in_string = False
    else:
        if c in ('"', "'", '`'):
            in_string = True
            string_char = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
    pos += 1

line_num = content[:pos].count('\n') + 1
print(f'RVK const ends at line {line_num}, pos {pos}')
print(f'Context around end: {repr(content[pos-30:pos+30])}')

# Also check what's at the second D occurrence
# The second D in RVK appears at RVK offset 145779
rvk_block = content[muni_start:muni_start + pos - brace_start + 200]
d_matches = list(re.finditer(r'\n  D\s*:\s*\{', rvk_block))
print(f'\nD occurrences in RVK block ({len(d_matches)}):')
for i, m in enumerate(d_matches):
    print(f'  {i+1}: offset {m.start()}, line {rvk_block[:m.start()].count(chr(10)) + 1}')
