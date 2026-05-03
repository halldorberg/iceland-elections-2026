"""Patch KÓP.S candidate occupations to match xs.is canonical list.

Our scraped occupations were stale/jumbled — e.g. our #11 had "Fyrrum ráðherra"
which actually belongs to xs.is #22 Rannveig. Names are mostly correct; only
occupations need fixing.

For #6 Hildur María, xs.is doesn't list an occupation; we use the value confirmed
by visir.is via agent O ("sérfræðingur á Veðurstofu Íslands").
"""
from __future__ import annotations
import re
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
PATH = ROOT / "js" / "data" / "candidates.js"

# (ballot, expected_name, new_occupation_from_xs.is)
PATCHES = [
    (1,  "Jónas Már Torfason",                    "Lögfræðingur"),
    (2,  "Eydís Inga Valsdóttir",                 "Sérfræðingur hjá Rannís"),
    (3,  "Hákon Gunnarsson",                      "Sérfræðingur í stefnumótun"),
    (4,  "Sólveig Skaftadóttir",                  "Verkefnastjóri stjórnsýslu hjá Reykjavíkurborg"),
    (5,  "Orri Thor Eggertsson",                  "Nemi í rekstrarverkfræði"),
    (6,  "Hildur María Friðriksdóttir",           "Sérfræðingur hjá Veðurstofu Íslands"),
    (7,  "Örn Arnarson",                          "Kennari og formaður Samleiks"),
    (8,  "Mirabela Blaga",                        "Fasteignasali"),
    (9,  "Björn Þór Rögnvaldsson",                "Lögfræðingur"),
    (10, "Sólveig Jóhannesdóttir Larsen",         "Nemi í stjórnmálafræði"),
    (11, "Sigurður Kári Harðarson",               "Nemi við lýðháskóla"),
    (12, "Friðmey Jónsdóttir",                    "Deildarstjóri félagsmiðstöðva, fyrrv. framkvæmdastjóri Samfés"),
    (13, "Kristján Bjarnar Ólafsson",             "Hagfræðingur hjá FSRE"),
    (14, "Margrét Tryggvadóttir",                 "Formaður Rithöfundasambands Íslands"),
    (15, "Jón Júlíusson",                         "Formaður GKG, fv. bæjarfulltrúi"),
    (16, "Ingunn S. Unnsteinsdóttir Kristensen",  "Dr. í sálfræði, Opni háskólinn HR"),
    (17, "Ingi Hafliði Guðjónsson",               "Matvinnslumaður og viðskiptafræðingur"),
    (18, "Heiða Björk Þórbergsdóttir",            "Framkvæmdastjóri"),
    (19, "Erlendur Geirdal",                      "Tæknifræðingur"),
    (20, "Sigurlaug Kristín Sævarsdóttir",        "Vörustjóri"),
    (21, "Bergljót Kristinsdóttir",               "Bæjarfulltrúi"),
    (22, "Rannveig Guðmundsdóttir",               "Fyrrum ráðherra og bæjarfulltrúi"),
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    src = PATH.read_text(encoding="utf-8")

    # Locate the KOP const block
    m = re.search(r"const KOP\s*=\s*\{", src)
    if not m:
        print("ERROR: KOP const not found")
        return 1
    kop_start = m.end()
    # Find the matching close `\n};`
    kop_end = src.find("\n};", kop_start)
    if kop_end == -1:
        print("ERROR: KOP block end not found")
        return 1

    # Within KOP, locate `S: { ... }` party block. Indent 2 spaces.
    party_re = re.compile(r"\n  S:\s*\{")
    pm = party_re.search(src, kop_start, kop_end)
    if not pm:
        print("ERROR: KOP.S not found")
        return 1
    s_start = pm.start()
    # Walk to find matching `\n  },`
    s_end = src.find("\n  },", s_start, kop_end)
    if s_end == -1:
        s_end = src.find("\n  }", s_start, kop_end)
    if s_end == -1:
        print("ERROR: KOP.S close not found")
        return 1

    s_block = src[s_start:s_end]

    # Apply patches in REVERSE order so offsets don't drift
    new_block = s_block
    changes = []
    for ballot, name, new_occ in PATCHES:
        # Match: `[N, 'name', 'occ', ...`
        name_esc = re.escape(name).replace("\\'", "\\\\'")
        # Use a flexible regex that handles either order
        pat = re.compile(
            r"(\[" + str(ballot) + r"\s*,\s*'" + name_esc + r"'\s*,\s*)'([^']*)'(\s*[,\]])"
        )
        m2 = pat.search(new_block)
        if not m2:
            print(f"  WARN: could not find #{ballot} {name}")
            continue
        old_occ = m2.group(2)
        if old_occ == new_occ:
            continue  # already correct
        new_block = new_block[:m2.start()] + m2.group(1) + f"'{new_occ}'" + m2.group(3) + new_block[m2.end():]
        changes.append((ballot, name, old_occ, new_occ))

    new_src = src[:s_start] + new_block + src[s_end:]
    if changes:
        PATH.write_text(new_src, encoding="utf-8")
        print(f"  Applied {len(changes)} occupation fixes:")
        for ballot, name, old_occ, new_occ in changes:
            print(f"    #{ballot:2d} {name}")
            print(f"        was: {old_occ}")
            print(f"        now: {new_occ}")
    else:
        print("  No changes needed.")

    # Validate balance
    if new_src.count("{") != new_src.count("}"):
        print("ERROR: brace imbalance after edit!")
        return 1
    if new_src.count("[") != new_src.count("]"):
        print("ERROR: bracket imbalance after edit!")
        return 1
    print("  Brace/bracket balance OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
