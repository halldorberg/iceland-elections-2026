"""
verify_against_kjorstjorn.py
────────────────────────────
Reads BasicData_frambodslistar_sveitarstjornarkosningar_2026.xlsx (the official
kjörstjórn ballot submission data) and compares each flagged candidate's
name + ballot position against the canonical source.

Usage:
    python scripts/verify_against_kjorstjorn.py
"""
from __future__ import annotations
import sys
import unicodedata
from pathlib import Path

import openpyxl

ROOT = Path(__file__).parent.parent
XLSX = ROOT / "BasicData_frambodslistar_sveitarstjornarkosningar_2026.xlsx"

# Map our muni/party codes to xlsx values for filtering
# Keys are (our_const, our_party_code); values are (xlsx_sveitarfelag, xlsx_framboðslisti substring matcher)
MUNI_NAMES = {
    "RVK": "Reykjavíkurborg",
    "KOP": "Kópavogsbær",
    "HAF": "Hafnarfjarðarbær",
    "GAR": "Garðabær",
    "MOS": "Mosfellsbær",
    "AKU": "Akureyrarbær",
    "SEL": "Seltjarnarnesbær",
    "RNB": "Reykjanesbær",
    "VOG": "Sveitarfélagið Vogar",
    "GRN": "Grindavíkurbær",
    "SNB": "Suðurnesjabær",
    "ARB": "Sveitarfélagið Árborg",
    "VME": "Vestmannaeyjabær",
    "NPG": "Norðurþing",
    "FJB": "Fjallabyggð",
    "FJD": "Fjarðabyggð",
    "HFJ": "Sveitarfélagið Hornafjörður",
    "AKR": "Akraneskaupstaður",
    "BBD": "Sameinað sveitarfélag Borgarbyggðar og Skorradalshrepps",
    "ISA": "Ísafjarðarbær",
    "HVG": "Hveragerðisbær",
    "RTE": "Rangárþing eystra",
    "RTY": "Rangárþing ytra",
    "OLF": "Sveitarfélagið Ölfus",
    "SKR": "Skaftárhreppur",
    "MYR": "Mýrdalshreppur",
    "BSG": "Bláskógabyggð",
    "FHR": "Flóahreppur",
    "HMR": "Hrunamannahreppur",
    "GGR": "Grímsnes- og Grafningshreppur",
    "SGN": "Skeiða- og Gnúpverjahreppur",
    "DVB": "Dalvíkurbyggð",
    "EJA": "Eyjafjarðarsveit",
    "HGS": "Hörgársveit",
    "HNB": "Húnabyggð",
    "HNT": "Húnaþing vestra",
    "SFJ": "Skagafjörður",
    "SST": "Sveitarfélagið Skagaströnd",
    "STK": "Sveitarfélagið Stykkishólmur",
    "GFJ": "Grundarfjarðarbær",
    "BLV": "Bolungarvíkurkaupstaður",
    "SDV": "Súðavíkurhreppur",
    "VBG": "Vesturbyggð",
    "STD": "Strandabyggð",
    "RKH": "Reykhólahreppur",
    "MUT": "Múlaþing",
    "THV": "Þingeyjarsveit",
    "HVF": "Hvalfjarðarsveit",
    "SNF": "Snæfellsbær",
    "SVS": "Svalbarðsstrandarhreppur",
    "KJO": "Kjósarhreppur",
    "VPF": "Vopnafjarðarhreppur",
    "TJR": "Tjörneshreppur",
    "ARN": "Árneshreppur",
    "STR": "Strandabyggð",
}

# Flags to verify — (id, our_name, claimed_correct_name_or_position)
FLAGS = [
    # (id, our_name, kind, expected_or_query)
    ("F-list RVK #6", "Lilja Sigríður Steingrímsdóttir", "name+pos", ("RVK", "F", 6)),
    ("F-list RVK #7", "Sigurður Rúnarsson", "name+pos", ("RVK", "F", 7)),
    ("RTY.RYA #4", "Viðar M. Þorsteinsson", "name+pos", ("RTY", "RYA", 4)),
    ("RTY.RYA #5", "Eiríkur Vilhelm Sigurðsson", "name+pos", ("RTY", "RYA", 5)),
    ("RTE.D #5", "Bjarki Freyr Sigurjónsson", "name+pos", ("RTE", "D", 5)),
    ("RTE.D #9", "<who is here?>", "name+pos", ("RTE", "D", 9)),
    ("VME.M #8", "<missing>", "name+pos", ("VME", "M", 8)),
    ("VME.M #9", "Emma Karína Jakobsen", "name+pos", ("VME", "M", 9)),
    ("VME.M #10", "Sveinn Hjalti Guðmundsson", "name+pos", ("VME", "M", 10)),
    ("SNB.M #4", "Sigríður Rós Jónatansdóttir", "name+pos", ("SNB", "M", 4)),
    ("SNB.M #5", "Ólafur Fannar Þórhallsson", "name+pos", ("SNB", "M", 5)),
    # Name spellings
    ("SFJ.D.4", "Rósanna Valdimársdóttir", "name+pos", ("SFJ", "D", 4)),
    ("RNB.D.6", "Guðlaug Sunna Gunnarsdóttir", "name+pos", ("RNB", "D", 6)),
    ("SFJ.B.6", "Atli Már Trautason", "name+pos", ("SFJ", "B", 6)),
    ("SFJ.M.7", "Valdimár Á. Þorbergsson", "name+pos", ("SFJ", "M", 7)),
    ("SFJ.M.8", "Hólmsteinn Orri Þorleifssson", "name+pos", ("SFJ", "M", 8)),
    ("BBD.M.13", "Snorri Jóhannsson", "name+pos", ("BBD", "M", 13)),
    ("HVG.OKH.7", "Eyþór Atli Olsen Finnsson", "name+pos", ("HVG", "OKH", 7)),
    ("HAF.S.17", "Valdimár Aðalsteinsson", "name+pos", ("HAF", "S", 17)),
    ("RNB.D.15", "Guðmundur Steinársson", "name+pos", ("RNB", "D", 15)),
    ("ARB.D.22", "Ari Thorarensen", "name+pos", ("ARB", "D", 22)),
    ("ARB.D.15", "Alexander Egan", "name+pos", ("ARB", "D", 15)),
    ("ARB.B.6", "Kristín J. Hannesdóttir", "name+pos", ("ARB", "B", 6)),
    ("KOP.S.20", "Sigurlaug Kristín Sævarsdóttir", "name+pos", ("KOP", "S", 20)),
    # Single weird occupations need separate check (xlsx has no occupation)
]


def normalize(s: str) -> str:
    """Normalize for comparison: lowercase + strip + NFC."""
    if not s:
        return ""
    return unicodedata.normalize("NFC", s).strip().lower()


def party_label_match(xlsx_label: str, our_party: str) -> bool:
    """Loose match: 'X listi' or 'X-listi' inside xlsx framboðslisti string."""
    xlsx_lower = xlsx_label.lower()
    p = our_party.lower()
    return (
        f"{p} listi" in xlsx_lower or f"{p}-listi" in xlsx_lower or
        f" {p} " in xlsx_lower or xlsx_lower.startswith(f"{p} ") or
        xlsx_lower.startswith(f"{p}-")
    )


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.worksheets[0]

    # Build lookup: (sveitarfélag, ballot_num) → list of (framboðslisti, name)
    # Plus: (sveitarfélag, framboðslisti, ballot_num) → name
    by_sveit_pos: dict[tuple[str, int], list[tuple[str, str]]] = {}
    by_full_key: dict[tuple[str, str, int], str] = {}
    by_name: dict[str, list[tuple[str, str, int]]] = {}

    rows_iter = ws.iter_rows(min_row=2, values_only=True)
    for row in rows_iter:
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
        by_sveit_pos.setdefault((sveit_n, num), []).append((listi or "", name))
        if listi:
            by_full_key[(sveit_n, listi, num)] = name
        by_name.setdefault(normalize(name), []).append((sveit, listi or "", num))

    print(f"Loaded {len(by_full_key)} candidates from kjörstjórn xlsx\n")

    print("=" * 90)
    print("VERIFICATION REPORT")
    print("=" * 90)

    for label, our_name, kind, params in FLAGS:
        const, party, ballot = params
        muni_name = MUNI_NAMES.get(const)
        if not muni_name:
            print(f"\n[{label}] ❓ Unknown muni const: {const}")
            continue
        sveit_n = normalize(muni_name)
        candidates_at_pos = by_sveit_pos.get((sveit_n, ballot), [])
        # Filter by party-letter match
        matches = [(li, nm) for li, nm in candidates_at_pos if party_label_match(li, party)]

        # Lookup: where does our claimed name actually appear (any position)?
        our_name_normalized = normalize(our_name)
        our_name_locations = by_name.get(our_name_normalized, [])

        print(f"\n[{label}] our data: '{our_name}'")
        if matches:
            for li, nm in matches:
                same = normalize(nm) == our_name_normalized
                marker = "✓ MATCH" if same else "❌ DIFFERENT"
                print(f"    kjörstjórn at #{ballot} on '{li}': '{nm}'  {marker}")
        else:
            print(f"    kjörstjórn at #{ballot} for {muni_name} party '{party}': NO MATCH")
            if candidates_at_pos:
                print(f"    All at #{ballot} in {muni_name}:")
                for li, nm in candidates_at_pos:
                    print(f"      '{li}': '{nm}'")
        if our_name_locations:
            for s, l, p in our_name_locations:
                if normalize(s) != sveit_n or p != ballot:
                    print(f"    NOTE: '{our_name}' actually at {s} '{l}' #{p}")


if __name__ == "__main__":
    main()
