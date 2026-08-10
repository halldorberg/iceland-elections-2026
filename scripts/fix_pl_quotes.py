"""
Fix candidates.pl.js: replace curly quotes used as JS string DELIMITERS
with straight quotes, while leaving curly quotes inside string content alone.

A line using curly quotes as delimiters looks like:
  “key”: “value”,

A line using straight quotes as delimiters is already correct:
  "key": "value with ” inside",   <- the ” here is fine, it's content
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

LQ = '“'  # " left double quotation mark (used as opening delimiter)
RQ = '”'  # " right double quotation mark (used as closing delimiter OR in Polish text)

with open('js/data/candidates.pl.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
fixed_count = 0

for i, line in enumerate(lines):
    # Check if this line uses curly quotes as JS object key delimiter
    # Pattern: starts with optional whitespace, then LQ (curly left quote as key start)
    stripped = line.lstrip()
    if stripped.startswith(LQ):
        # This line uses curly quotes as delimiters - replace all delimiter positions
        # The structure is: LQ key RQ : LQ value RQ ,
        # Replace each LQ and RQ with straight " on this line
        new_line = line.replace(LQ, '"').replace(RQ, '"')
        fixed_lines.append(new_line)
        fixed_count += 1
    else:
        # Line uses straight quotes as delimiters - leave as-is
        # Any RQ inside the value is legitimate Polish typography
        fixed_lines.append(line)

print(f'Fixed {fixed_count} lines with curly-quote delimiters')

with open('js/data/candidates.pl.js', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Done.')
