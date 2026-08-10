import openpyxl, json, re

wb = openpyxl.load_workbook('F:/Claude Projects/iceland-elections/BasicData_frambodslistar_sveitarstjornarkosningar_2026.xlsx', data_only=True)
ws = wb.worksheets[1]
all_excel = [row[0] for row in ws.iter_rows(values_only=True) if row[0] and row[0] != 'Total:']
obundnar = [m for m in all_excel if 'bundnar' in m]
print('7 obundnar municipalities:')
for m in obundnar:
    print(' ', m)

print()
with open('F:/Claude Projects/iceland-elections/js/data/municipalities.js', encoding='utf-8') as f:
    js_text = f.read()

pattern = r"id:\s*'([^']+)'[^}]*?name:\s*'([^']+)'"
js_munis = re.findall(pattern, js_text)
print(f'JS has {len(js_munis)} municipalities')

print()
print('Mapping obundnar -> JS:')
for m in obundnar:
    base = m.split(' - ')[0].strip()
    matches = [(mid, name) for mid, name in js_munis
               if name.lower() == base.lower()
               or base.lower() in name.lower()
               or name.lower() in base.lower()]
    print(f'  {base!r} -> {matches if matches else "NOT FOUND"}')

print()
print('JS entries with empty partyIds:')
empty = re.findall(r"id:\s*'([^']+)'[^}]*?name:\s*'([^']+)'[^}]*?partyIds:\s*\[\s*\]", js_text)
for mid, name in empty:
    print(f'  {mid}: {name}')
