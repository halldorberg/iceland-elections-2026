"""Inspect each approved ID against audit_results files."""
import json, re, sys, io, os, glob
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')

approved_str = """AKR.D.10, AKR.D.7, AKR.D.8, AKR.D.9, AKR.S.10, AKR.S.6, AKR.S.7, AKR.S.8, AKR.S.9, ARB.D.10, ARB.D.9, BBD.D.8, BBD.D.9, BBD.M.10, BBD.M.8, BBD.M.9, FJD.D.10, FJD.D.6, FJD.D.7, FJD.D.8, FJD.D.9, FJD.S.10, FJD.S.6, FJD.S.7, FJD.S.8, FJD.S.9, GFJ.GFD.11, GFJ.GFD.12, GFJ.GFD.14, HNB.D.11, HNB.D.12, HNB.D.13, HNB.D.14, HNB.D.15, HNT.D.11, HNT.D.12, HVF.HVA.13, ISF.M.2, ISF.S.2, KOP.B.3, KOP.D.5, KOP.J.4, KOP.J.5, KOP.V.5, MUT.B.2, MUT.B.4, MUT.B.5, MUT.B.6, MUT.D.10, MUT.D.2, MUT.D.3, MUT.D.4, MUT.D.5, MUT.D.6, MUT.D.7, MUT.D.8, MUT.D.9, MUT.L.2, MUT.L.3, MUT.L.4, MUT.L.5, MUT.M.2, MUT.M.4, MUT.M.6, MUT.M.8, MUT.V.2, MUT.V.4, MUT.V.5, MYR.MYA.2, MYR.MYZ.2, NPG.B.2, NPG.D.2, NPG.NBO.2, NPG.NPM.2, NPG.NPV.2, OLF.D.2, OLF.S.2, RTE.B.2, RTY.D.12, RTY.D.13, RTY.D.14, RTY.RYA.11, RTY.RYA.12, RTY.RYA.13, RVK.B.20, RVK.B.21, RVK.B.22, RVK.B.26, RVK.B.35, RVK.B.41, RVK.B.42, RVK.B.43, RVK.B.44, RVK.B.45, RVK.C.22, RVK.C.44, RVK.C.45, RVK.F.4, RVK.P.4, RVK.R.17, RVK.R.18, RVK.R.19, RVK.R.21, RVK.R.4, RVK.S.19, RVK.S.20, RVK.S.21, RVK.S.40, RVK.S.41, RVK.S.42, RVK.S.43, RVK.S.44, RVK.S.45, SEL.D.6, SEL.M.2, SEL.SCS.2, SFJ.B.1, SFJ.B.2, SFJ.M.1, SFJ.M.2, SFJ.SFL.1, SFJ.SFL.2, SGN.SGE.1, SGN.SGE.2, SGN.SGL.1, SGN.SGL.2, SKR.D.1, SKR.D.2, SKR.SKO.1, SKR.SKO.2, SNB.B.6, SNB.D.2, SNB.D.6, SNB.D.7, SNB.D.8, SNB.D.9, SNB.M.1, SNB.M.2, SNB.M.8, SNB.M.9, SNB.S.1, SNB.S.2, SNB.S.6, SNB.S.7, SNB.S.8, SNF.D.1, SST.B.2, SST.S.2, STK.FLS.2, THV.THVA.12, THV.THVA.2, THV.THVL.2, THV.THVN.2, VBG.STV.14, VME.D.2, VME.E.2, VME.M.2, VOG.D.11, VOG.D.2, VOG.FYRS.2, VOG.VOE.2, VOG.VOL.2, VPF.VOP.1"""
approved = [x.strip() for x in approved_str.split(',') if x.strip()]
print(f'approved count: {len(approved)}')

audit_index = {}

def add_entry(fp, k, v):
    if not k or not isinstance(v, dict):
        return
    if k in audit_index:
        return
    audit_index[k] = (fp, v)

def visit(fp, obj):
    if isinstance(obj, dict):
        # If it has 'id' key, treat as entry
        if 'id' in obj and isinstance(obj.get('id'), str):
            add_entry(fp, obj['id'], obj)
            return
        # Otherwise iterate
        for k, v in obj.items():
            if isinstance(v, dict) and ('rescue' in v or 'rewrite' in v or 'flags' in v or 'bio' in v or 'new_bio' in v):
                add_entry(fp, k, v)
            elif isinstance(v, (dict, list)):
                visit(fp, v)
    elif isinstance(obj, list):
        for it in obj:
            visit(fp, it)

for fp in sorted(glob.glob(str(ROOT / 'scan_results' / 'audit_results*.json')) +
                 glob.glob(str(ROOT / 'scan_results' / 'bios_*.json'))):
    if 'bak_' in fp or fp.endswith('.bak'):
        continue
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        continue
    visit(fp, d)

print(f'audit index size: {len(audit_index)}')

missing = []
have_rewrite = 0
applied_already = 0
for aid in approved:
    if aid not in audit_index:
        missing.append(aid)
        continue
    fp, entry = audit_index[aid]
    if entry.get('applied'):
        applied_already += 1
    rescue = entry.get('rescue') or entry.get('rewrite_payload') or {}
    rw = rescue.get('rewrite') or entry.get('rewrite') or entry.get('new_bio') or entry.get('bio')
    if rw:
        have_rewrite += 1

print(f'\napproved: {len(approved)}  found: {len(approved)-len(missing)}  missing: {len(missing)}')
print(f'have rewrite: {have_rewrite}  already applied: {applied_already}')
if missing:
    print('\nMISSING IDs:')
    for m in missing:
        print(f'  {m}')

# Save the index
out = {}
for aid in approved:
    if aid in audit_index:
        fp, entry = audit_index[aid]
        out[aid] = {'source_file': fp, 'entry': entry}
json.dump(out, open(ROOT / 'temp' / 'approved_resolved.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print(f'\nWrote temp/approved_resolved.json with {len(out)} entries')
