import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.load(open('scan_results/ruv_bios.json', encoding='utf-8'))
for e in data:
    if e.get('muni_const') == 'HAF' and e.get('party_code') == 'B' and e.get('ballot') == 3:
        bio = e.get('new_bio', '')
        print('Length:', len(bio))
        print('Has apostrophe count:', bio.count("'"))
        if "'" in bio:
            idx = bio.find("'")
            print('First apostrophe context:', repr(bio[max(0, idx - 30):idx + 50]))
        # Look for "mála stjórnun"
        if 'mála stjórnun' in bio:
            idx = bio.find('mála stjórnun')
            print('Found mála stjórnun at:', idx)
            print('Context:', repr(bio[max(0, idx - 100):idx + 100]))
        break
