import json, sys, io, os
sys.stdout.reconfigure(encoding='utf-8')
P = r'F:\Claude Projects\iceland-elections\scan_results\audit_results_14.json'
def append(rec):
    data = json.load(open(P, encoding='utf-8'))
    # If the id exists, replace
    found = False
    for i,r in enumerate(data['results']):
        if r['id'] == rec['id']:
            data['results'][i] = rec; found=True; break
    if not found:
        data['results'].append(rec)
    json.dump(data, open(P,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print('saved', rec['id'])

if __name__ == '__main__':
    rec = json.loads(sys.stdin.read())
    append(rec)
