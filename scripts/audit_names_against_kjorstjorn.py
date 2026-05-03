"""
audit_names_against_kjorstjorn.py
─────────────────────────────────
Full audit: check every candidate in candidates.js against kjörstjórn xlsx.
Reports name mismatches and missing positions.
"""
from __future__ import annotations
import re, sys, unicodedata
from pathlib import Path
import openpyxl

ROOT = Path(__file__).parent.parent
XLSX = ROOT / "BasicData_frambodslistar_sveitarstjornarkosningar_2026.xlsx"
JS = ROOT / "js" / "data" / "candidates.js"

# Map our muni const → xlsx sveitarfélag name
MUNI_NAMES = {
    "RVK": "Reykjavíkurborg", "KOP": "Kópavogsbær", "HAF": "Hafnarfjarðarbær",
    "GAR": "Garðabær", "MOS": "Mosfellsbær", "AKU": "Akureyrarbær",
    "SEL": "Seltjarnarnesbær", "RNB": "Reykjanesbær", "VOG": "Sveitarfélagið Vogar",
    "GRN": "Grindavíkurbær", "SNB": "Suðurnesjabær", "ARB": "Sveitarfélagið Árborg",
    "VME": "Vestmannaeyjabær", "NPG": "Norðurþing", "FJB": "Fjallabyggð",
    "FJD": "Fjarðabyggð", "HFJ": "Sveitarfélagið Hornafjörður", "AKR": "Akraneskaupstaður",
    "BBD": "Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps",
    "ISA": "Ísafjarðarbær", "HVG": "Hveragerðisbær",
    "RTE": "Rangárþing eystra", "RTY": "Rangárþing ytra", "OLF": "Sveitarfélagið Ölfus",
    "SKR": "Skaftárhreppur", "MYR": "Mýrdalshreppur", "BSG": "Bláskógabyggð",
    "FHR": "Flóahreppur", "HMR": "Hrunamannahreppur", "GGR": "Grímsnes- og Grafningshreppur",
    "SGN": "Skeiða- og Gnúpverjahreppur", "DVB": "Dalvíkurbyggð", "EJA": "Eyjafjarðarsveit",
    "HGS": "Hörgársveit", "HNB": "Húnabyggð", "HNT": "Húnaþing vestra",
    "SFJ": "Skagafjörður", "SST": "Sveitarfélagið Skagaströnd",
    "STK": "Sveitarfélagið Stykkishólmur", "GFJ": "Grundarfjarðarbær",
    "BLV": "Bolungarvíkurkaupstaður", "SDV": "Súðavíkurhreppur", "VBG": "Vesturbyggð",
    "STD": "Strandabyggð", "RKH": "Reykhólahreppur", "MUT": "Múlaþing",
    "THV": "Þingeyjarsveit", "HVF": "Hvalfjarðarsveit",
    # uncontested / no-list munis (skip):
    # ASA, DLR, EJM, FLD, GRY, KAL, KJO, LNB, SNF, TJR, VPF
}


def normalize(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").strip()).lower()


def party_label_match(xlsx_label: str, party_code: str) -> bool:
    """Try to match xlsx framboðslisti to our party_code letter prefix."""
    p = (party_code or "").lower()
    xl = (xlsx_label or "").lower()
    # The xlsx label is like 'B listi - Framsóknarflokkurinn' or 'GB listi - Garðabæjarlistinn'
    # Try first-word/letter match (case-insensitive)
    first = xl.split()[0] if xl else ""
    return first == p or first == p + "-listi"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # 1. Build kjörstjórn lookup: (sveit_n, ballot, party_letter) → name
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.worksheets[0]
    kj_by_pos: dict[tuple[str, int], list[tuple[str, str]]] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] in (None, "Total:"):
            continue
        sveit, listi, num, name = row[0], row[1], row[2], row[3]
        if not sveit or not name or num is None:
            continue
        try:
            num = int(num)
        except (TypeError, ValueError):
            continue
        sveit_n = normalize(sveit)
        kj_by_pos.setdefault((sveit_n, num), []).append((listi or "", name))

    # 2. Walk candidates.js and extract every (const, party, ballot, name)
    src = JS.read_text(encoding="utf-8")
    # First find REAL_DATA mapping const → slug
    rd_match = re.search(r"const REAL_DATA\s*=\s*\{([^}]*)\}", src)
    const_to_slug = {}
    if rd_match:
        for m in re.finditer(r"(\w+)\s*:\s*([A-Z][A-Z0-9_]*)", rd_match.group(1)):
            const_to_slug[m.group(2)] = m.group(1)

    # Extract muni const blocks
    issues = []
    confirmed = 0
    skipped_unknown = 0

    for cm in re.finditer(r"const ([A-Z][A-Z0-9_]+)\s*=\s*\{", src):
        const = cm.group(1)
        if const not in const_to_slug:
            continue
        if const not in MUNI_NAMES:
            continue
        block_start = cm.end()
        # Find matching close `\n};`
        block_end = src.find("\n};", block_start)
        if block_end == -1:
            continue
        muni_block = src[block_start:block_end]
        muni_name = MUNI_NAMES[const]
        sveit_n = normalize(muni_name)

        # Parse party blocks within this muni
        for pm in re.finditer(r"\n  ([A-Z][A-Z0-9]{0,3}):\s*\{", muni_block):
            party = pm.group(1)
            party_start = pm.end()
            # Find party block end (next `\n  ` at indent 2 or `\n}` for muni close)
            next_party = re.search(r"\n  [A-Z][A-Z0-9]{0,3}:\s*\{|\n\};", muni_block[party_start:])
            party_end = party_start + (next_party.start() if next_party else len(muni_block) - party_start)
            party_block = muni_block[party_start:party_end]

            # Find list: [...]
            list_m = re.search(r"list\s*:\s*\[", party_block)
            if not list_m:
                continue
            list_after = party_block[list_m.end():]
            # Walk rows: each starts with [N, '
            for row_m in re.finditer(r"\[(\d+)\s*,\s*'((?:[^'\\]|\\.)*?)'", list_after):
                ballot = int(row_m.group(1))
                our_name = row_m.group(2).replace("\\'", "'")
                # Look up in kjörstjórn
                kj_entries = kj_by_pos.get((sveit_n, ballot), [])
                # Filter by party first-letter match
                kj_match = None
                for li, nm in kj_entries:
                    if party_label_match(li, party):
                        kj_match = (li, nm)
                        break
                if kj_match is None:
                    # No party-letter match; report
                    issues.append({
                        "id": f"{const}.{party}.{ballot}",
                        "muni": muni_name,
                        "our_name": our_name,
                        "kjor_name": None,
                        "kjor_listi": None,
                        "kjor_at_pos": kj_entries,
                        "issue": "party-not-found",
                    })
                    continue
                if normalize(kj_match[1]) != normalize(our_name):
                    issues.append({
                        "id": f"{const}.{party}.{ballot}",
                        "muni": muni_name,
                        "our_name": our_name,
                        "kjor_name": kj_match[1],
                        "kjor_listi": kj_match[0],
                        "issue": "name-mismatch",
                    })
                else:
                    confirmed += 1

    print(f"Audit complete: {confirmed} candidates verified ✓")
    print(f"Issues found: {len(issues)}\n")
    if not issues:
        return

    # Group by issue type
    by_type = {}
    for i in issues:
        by_type.setdefault(i["issue"], []).append(i)

    if "name-mismatch" in by_type:
        print(f"\n=== NAME MISMATCHES ({len(by_type['name-mismatch'])}) ===")
        for i in by_type["name-mismatch"]:
            print(f"  {i['id']:18s} our: '{i['our_name']}'")
            print(f"  {' '*18}  kjör: '{i['kjor_name']}' on '{i['kjor_listi']}'")

    if "party-not-found" in by_type:
        print(f"\n=== PARTY NOT FOUND IN KJÖRSTJÓRN ({len(by_type['party-not-found'])}) ===")
        # Group by id prefix to show only one example per party
        seen_party = set()
        for i in by_type["party-not-found"]:
            const_party = ".".join(i["id"].split(".")[:2])
            if const_party in seen_party:
                continue
            seen_party.add(const_party)
            print(f"  {i['id']:18s} our: '{i['our_name']}'")
            if i["kjor_at_pos"]:
                for li, nm in i["kjor_at_pos"]:
                    print(f"  {' '*18}  kjör pos {i['id'].split('.')[-1]}: '{li}' → '{nm}'")
            else:
                print(f"  {' '*18}  kjör: no candidate at this position in {i['muni']}")


if __name__ == "__main__":
    main()
