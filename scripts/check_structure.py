#!/usr/bin/env python3
import re

with open('../js/data/candidates.js', encoding='utf-8') as f:
    src = f.read()

opens = src.count('{')
closes = src.count('}')
print('Braces: { =', opens, '} =', closes, 'balance =', opens - closes)

opens2 = src.count('[')
closes2 = src.count(']')
print('Brackets: [ =', opens2, '] =', closes2, 'balance =', opens2 - closes2)

for var in ['KJO', 'SNF', 'TJR', 'VPF']:
    m = re.search(r'const ' + var + r'\s*=', src)
    status = 'found' if m else 'MISSING'
    print('const ' + var + ': ' + status)

# Check that REAL_DATA references them
real_data = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', src, re.DOTALL)
if real_data:
    block = real_data.group(1)
    for muni, var in [('snaefellsbaer', 'SNF'), ('kjosarhreppur', 'KJO'), ('tjornes', 'TJR'), ('vopnafjordur', 'VPF')]:
        found = var in block
        print('REAL_DATA ' + muni + ' -> ' + var + ': ' + ('ok' if found else 'MISSING'))

# Count candidates in KJO, SNF, TJR
for var in ['KJO', 'SNF', 'TJR', 'VPF']:
    m = re.search(r'const ' + var + r'\s*=\s*\{', src)
    if m:
        start = m.end() - 1
        depth = 0
        pos = start
        while pos < len(src):
            if src[pos] == '{': depth += 1
            elif src[pos] == '}':
                depth -= 1
                if depth == 0: break
            pos += 1
        block = src[start:pos+1]
        names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', block)
        print(var + ' candidates: ' + str(len(names)))
