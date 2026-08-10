# -*- coding: utf-8 -*-
"""Helper to add a record (passed as a Python dict literal in argv) to audit_results_14.json."""
import json, sys, io
sys.stdout.reconfigure(encoding='utf-8')

P = r'F:\Claude Projects\iceland-elections\scan_results\audit_results_14.json'

def save(rec):
    data = json.load(open(P, encoding='utf-8'))
    found = False
    for i,r in enumerate(data['results']):
        if r['id'] == rec['id']:
            data['results'][i] = rec; found=True; break
    if not found:
        data['results'].append(rec)
    json.dump(data, open(P,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    print('saved', rec['id'], 'total', len(data['results']))
