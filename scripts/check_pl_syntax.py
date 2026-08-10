import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('js/data/candidates.pl.js', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f'Total lines: {len(lines)}')

# Look for unescaped backslash problems
# A backslash inside a JS string that's not a valid escape char can break things
problems = []
for i, line in enumerate(lines):
    stripped = line.rstrip('\r\n')
    # Check for bare backslash at end of line (not inside comment)
    if stripped.endswith('\\') and not stripped.strip().startswith('//'):
        problems.append(f'Line {i+1}: trailing backslash: {repr(stripped[:120])}')
    # Check for \' or other odd escapes in double-quoted strings
    if "\\'" in stripped:
        problems.append(f'Line {i+1}: has backslash-apostrophe: {repr(stripped[:120])}')
    # Check for unescaped double quote inside string value
    # Pattern: starts with spaces, quote, key, quote, colon, space, quote, ...value with unescaped quote..., quote, comma?
    # Simple heuristic: count bare (non-escaped) double quotes on this line
    # Remove escaped quotes first
    no_escaped = stripped.replace('\\"', '').replace("\\'", '')
    dq_count = no_escaped.count('"')
    if dq_count % 2 != 0 and not stripped.strip().startswith('//'):
        problems.append(f'Line {i+1}: odd quote count ({dq_count}): {repr(stripped[:120])}')

print(f'Problems found: {len(problems)}')
for p in problems[:30]:
    print(p)
