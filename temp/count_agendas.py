"""Count agenda coverage."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

txt = open('js/data/candidates.js', encoding='utf-8').read()

const_pat = re.compile(r'^const ([A-Z]+)\s*=\s*\{', re.M)
agenda_pat = re.compile(r'agenda:\s*\[(.*?)\]\s*,?\s*(?:platformUrl|list|tagline|//)', re.S)
icon_pat = re.compile(r'\{\s*icon:')


def find_const_block(src, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', src, re.M)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    in_str = None
    while i < len(src):
        c = src[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1


consts = [m.group(1) for m in const_pat.finditer(txt)]
total_lists = 0
with_agenda = 0
total_items = 0
zero_lists = []

for c in consts:
    span = find_const_block(txt, c)
    if not span:
        continue
    bs, be = span
    body = txt[bs:be]
    for pm in re.finditer(r'\n  ([A-Z][A-Za-z0-9]*)\s*:\s*\{', body):
        i = pm.end() - 1
        depth = 0
        in_str = None
        while i < len(body):
            ch = body[i]
            if in_str:
                if ch == '\\':
                    i += 2
                    continue
                if ch == in_str:
                    in_str = None
                i += 1
                continue
            if ch in ("'", '"', '`'):
                in_str = ch
                i += 1
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        ptext = body[pm.end() - 1:i + 1]
        if 'list:' not in ptext:
            continue
        total_lists += 1
        am = agenda_pat.search(ptext)
        n = 0
        if am:
            n = len(icon_pat.findall(am.group(1)))
        total_items += n
        if n > 0:
            with_agenda += 1
        else:
            zero_lists.append((c, pm.group(1)))

print(f'Total lists:            {total_lists}')
print(f'Lists with agenda:      {with_agenda}  ({100*with_agenda/total_lists:.1f}%)')
print(f'Lists without agenda:   {total_lists - with_agenda}')
print(f'Total agenda points:    {total_items}')
print(f'Avg items per list w/ agenda: {total_items/with_agenda:.2f}')
