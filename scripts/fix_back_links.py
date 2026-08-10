"""Fix municipality back buttons: /index.html -> /sveitastjornarkosningar2026/"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'.claude', '.git', 'sveitastjornarkosningar2026', 'node_modules', 'scripts', 'reports', 'raw'}
OLD = 'href="/index.html"'
NEW = 'href="/sveitastjornarkosningar2026/"'

count = 0
errors = []
for dirpath, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP]
    if dirpath == ROOT:
        continue
    for fname in files:
        if fname != 'index.html':
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            if OLD not in content:
                continue
            new_content = content.replace(OLD, NEW)
            with open(fpath, 'w', encoding='utf-8', newline='') as f:
                f.write(new_content)
            count += 1
            if count <= 5:
                print(f'Updated: {fpath}')
        except Exception as e:
            errors.append(f'{fpath}: {e}')

print(f'\nTotal updated: {count} files')
if errors:
    print(f'Errors: {len(errors)}')
    for e in errors[:5]:
        print(e)
