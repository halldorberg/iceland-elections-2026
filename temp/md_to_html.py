"""Convert audit_2022_full.md → standalone HTML for online browsing."""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
md = (ROOT / 'temp' / 'audit_2022_full.md').read_text(encoding='utf-8')
out = ROOT / 'audit-2022.html'

# Very simple markdown → HTML converter: tables + headings + lists + bold
html_lines = []
in_table = False
for line in md.split('\n'):
    # Heading
    h = re.match(r'^(#{1,6})\s+(.+)$', line)
    if h:
        n = len(h.group(1)); html_lines.append(f'<h{n}>{h.group(2)}</h{n}>'); continue
    # Table row
    if line.startswith('|'):
        cells = [c.strip() for c in line.strip('|').split('|')]
        if all(re.match(r'^-+:?$|^:?-+$', c) for c in cells if c):
            continue  # separator row
        if not in_table:
            html_lines.append('<table class="t">')
            in_table = True
            tag = 'th' if not html_lines[-2:] or '<table' in (html_lines[-2] if len(html_lines)>1 else '') else 'td'
        else:
            tag = 'td'
        # First row after open: th
        if html_lines[-1] == '<table class="t">':
            tag = 'th'
        cell_html = ''.join(f'<{tag}>{c}</{tag}>' for c in cells)
        # Color status column
        if tag == 'td' and cells:
            status = cells[-1]
            cls = ''
            if status.startswith('✅'): cls = ' class="ok"'
            elif status.startswith('❌'): cls = ' class="bad"'
            elif status.startswith('❓'): cls = ' class="unk"'
            elif status.startswith('—'): cls = ' class="ksonly"'
            elif status.startswith('⚠️'): cls = ' class="err"'
            html_lines.append(f'<tr{cls}>{cell_html}</tr>')
        else:
            html_lines.append(f'<tr>{cell_html}</tr>')
        continue
    if in_table and not line.startswith('|'):
        html_lines.append('</table>')
        in_table = False
    # List items
    li = re.match(r'^- (.+)$', line)
    if li:
        html_lines.append(f'<li>{li.group(1)}</li>')
        continue
    # Plain
    if line.strip():
        html_lines.append(f'<p>{line}</p>')
    else:
        html_lines.append('')

if in_table:
    html_lines.append('</table>')

body = '\n'.join(html_lines)

PAGE = (
    '<!DOCTYPE html><html lang="is"><head><meta charset="UTF-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>2022 results audit vs kosningasaga</title>'
    '<style>'
    'body{background:#0d1117;color:#e6edf3;font-family:-apple-system,Segoe UI,sans-serif;font-size:13px;line-height:1.5;max-width:1300px;margin:0 auto;padding:30px 20px;}'
    'h1{font-size:24px;border-bottom:1px solid #30363d;padding-bottom:8px;margin-bottom:14px;}'
    'h2{font-size:18px;margin-top:30px;border-bottom:1px solid #30363d;padding-bottom:6px;}'
    'p{margin:8px 0;}'
    'li{margin:4px 0;color:#8b949e;}'
    '.t{border-collapse:collapse;width:100%;margin:14px 0;font-size:12px;}'
    '.t th{background:#161b22;border:1px solid #30363d;padding:6px 8px;text-align:left;font-weight:600;position:sticky;top:0;}'
    '.t td{border:1px solid #30363d;padding:6px 8px;vertical-align:top;}'
    'tr.ok td{background:rgba(63,185,80,.06);}'
    'tr.bad td{background:rgba(248,81,73,.08);color:#f5d6d6;}'
    'tr.unk td{background:rgba(210,153,34,.07);}'
    'tr.ksonly td{background:rgba(88,166,255,.05);color:#b3cce6;}'
    'tr.err td{background:rgba(188,140,255,.08);}'
    '#filter{margin:10px 0;padding:8px 12px;background:#161b22;border:1px solid #30363d;color:#e6edf3;border-radius:6px;font-size:13px;width:240px;}'
    '</style></head><body>'
    + body +
    '<script>'
    'document.addEventListener("DOMContentLoaded",()=>{'
    'const tbl=document.querySelector(".t");if(!tbl)return;'
    'const inp=document.createElement("input");inp.id="filter";inp.placeholder="Filter (muni, party, status…)";'
    'tbl.parentNode.insertBefore(inp,tbl);'
    'const rows=tbl.querySelectorAll("tr");'
    'inp.addEventListener("input",()=>{const q=inp.value.toLowerCase();rows.forEach((r,i)=>{if(i===0)return;r.style.display=r.textContent.toLowerCase().includes(q)?"":"none";});});'
    '});'
    '</script>'
    '</body></html>'
)

out.write_text(PAGE, encoding='utf-8')
print(f'Wrote {out}')
