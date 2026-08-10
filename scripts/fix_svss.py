#!/usr/bin/env python3
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BACKSLASH = chr(92)

with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', encoding='utf-8') as f:
    content = f.read()

# Fix SVS.SVSS #10: Waldemar Sienda -> Helena Valdís Bergland Traustadóttir
svs_start = content.find('\nconst SVS = {')
svs_end = content.find('\nconst ', svs_start + 1)

# Find SVSS list start
party_pat = re.compile(r'\n  SVSS\s*:\s*\{')
pm = party_pat.search(content, svs_start, svs_end)
list_pat = re.compile(r'\blist\s*:\s*\[')
lm = list_pat.search(content, pm.end(), svs_end)
bracket = lm.end() - 1
depth = 0
pos = bracket
in_string = False
string_char = None
while pos < len(content):
    c = content[pos]
    if in_string:
        if c == BACKSLASH: pos += 1
        elif c == string_char: in_string = False
    else:
        if c in ('"', "'", '`'): in_string = True; string_char = c
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    pos += 1

list_end = pos
list_text = content[bracket:list_end+1]

# Replace [10, 'Waldemar Sienda', 'Frambjóðandi'] with Helena...
old_entry = "[10, 'Waldemar Sienda', 'Frambjóðandi']"
new_entry = "[10, 'Helena Valdís Bergland Traustadóttir', 'Frambjóðandi']"

if old_entry in list_text:
    new_list = list_text.replace(old_entry, new_entry, 1)
    content = content[:bracket] + new_list + content[list_end+1:]
    print("Fixed SVS.SVSS #10: 'Waldemar Sienda' -> 'Helena Valdís Bergland Traustadóttir'")
else:
    print("ERROR: Could not find entry to fix")

# Also fix SVS.SVSH which has Waldemar Sienda at #10 - that's correct for H listi
# Let's verify SVSH is correct
svsh_pm = re.search(r'\n  SVSH\s*:\s*\{', content[svs_start:svs_end])
if svsh_pm:
    print("SVSH found (H listi - correct)")

with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Saved!")
