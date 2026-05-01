#!/usr/bin/env python3
"""
generate_manifest.py
────────────────────
Reads candidates.js and produces scan_manifest.json — a lightweight
work-list for AI scan agents. Run this before every scan session.

Usage:
    python scripts/generate_manifest.py

Output:
    scan_manifest.json  (root of project)
"""

import re
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
MANIFEST_OUT  = ROOT / "scan_manifest.json"

# Human-readable municipality labels (id → display name)
MUNI_LABELS = {
    "reykjavik":         "Reykjavík",
    "kopavogur":         "Kópavogur",
    "hafnarfjordur":     "Hafnarfjörður",
    "gardabaer":         "Garðabær",
    "mosfellsbaer":      "Mosfellsbær",
    "akureyri":          "Akureyri",
    "seltjarnarnes":     "Seltjarnarnes",
    "reykjanesbaer":     "Reykjanesbær",
    "vogar":             "Vogar",
    "grindavik":         "Grindavík",
    "sudurnesjabaer":    "Suðurnesjabær",
    "arborg":            "Árborg",
    "vestmannaeyjar":    "Vestmannaeyjar",
    "nordurping":        "Norðurþing",
    "fjallabyggd":       "Fjallabyggð",
    "fjardabyggd":       "Fjarðabyggð",
    "hornafjordur":      "Hornafjarðarsveit",
    "akranes":           "Akranes",
    "borgarbyggd":       "Borgarbyggð",
    "isafjordur":        "Ísafjarðarbær",
    "hveragerdi":        "Hveragerði",
    "rangarthingeystra": "Rangárþing eystra",
    "rangarthingytra":   "Rangárþing ytra",
    "olfus":             "Ölfus",
    "skaftarhreppur":    "Skaftárhreppur",
    "myrdalshr":         "Mýrdalshreppur",
    "blaskogabyggd":     "Bláskógabyggð",
    "floahreppur":       "Flóahreppur",
    "hrunamannahreppur": "Hrunamannahreppur",
    "grimsnesgrafningur":"Grímsnes- og Grafningshreppur",
    "skeidagnup":        "Skeiða- og Gnúpverjahreppur",
    "dalvikurbyggd":     "Dalvíkurbyggð",
    "eyjafjardarsveit":  "Eyjafjarðarsveit",
    "horgarsv":          "Hörgársveit",
    "hunabyggd":         "Húnabyggð",
    "hunathing":         "Húnavatnshreppur",
    "skagafjordur":      "Skagafjörður",
    "skagastrond":       "Skagaströnd",
    "stykkisholmur":     "Stykkishólmur",
    "grundarfjordur":    "Grundarfjörður",
    "bolungarvik":       "Bolungarvík",
    "sudavik":           "Suðavík",
    "vesturbyggd":       "Vesturbyggð",
    "strandabyggd":      "Strandabyggð",
    "reykholar":         "Reykhólar",
    "mulathing":         "Múlaþing",
    "thingeyjarsveit":   "Þingeyjarsveit",
    "hvalfjardarsveit":  "Hvalfjarðarsveit",
    "snaefellsbaer":     "Snæfellsbær",
    "svalbardsstrond":   "Svalbards- og Langadalshr.",
    "kjosarhreppur":     "Kjósarhreppur",
    "vopnafjordur":      "Vopnafjörður",
    "tjornes":           "Þórshafnarhreppur",
    "arneshr":           "Árneshr.",
}

PARTY_LABELS = {
    "D": "Sjálfstæðisflokkurinn",
    "B": "Framsóknarflokkurinn",
    "S": "Samfylkingin",
    "V": "Vinstri Græn",
    "A": "Vinstrið – grænt og framsækt",
    "P": "Píratar",
    "M": "Miðflokkurinn",
    "F": "Flokkur fólksins",
    "C": "Viðreisn",
    "J": "Sósíalistar",
    "GB": "Garðabæjarlisti",
    "AL": "Akureyrarlistinn",
    "L":  "L-listinn",
    "K":  "Kex framboð",
    "E":  "Eyjalisti",
    "H":  "H-listinn",
    "VM": "Vinir Mosfellsbæjar",
    "OKH":"Okkar Hveragerði",
    "SCS":"Seltjarnarneslistinn",
    "BBL":"Borgarbyggðarlisti",
    "G":  "Góðir Reykjavík",
    "R":  "Röðull",
}

# ── Parser ────────────────────────────────────────────────────────────────────

def parse_candidates_js(path: Path):
    """
    Returns (municipalities, parties, candidates) where:
      municipalities: {const_id: muni_slug}
      parties:  list of {muni_slug, muni_label, party_code, party_label,
                         has_platform_url, tagline}
      candidates: list of {muni_slug, muni_label, party_code, ballot_order,
                            name, occupation, has_photo, news_urls, news_count}
    """
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()

    # ── Step 1: build const-id → muni-slug map from REAL_DATA block ──────────
    real_data_block = re.search(
        r"const REAL_DATA\s*=\s*\{(.*?)\};",
        src, re.DOTALL
    )
    const_to_slug: dict[str, str] = {}
    if real_data_block:
        for m in re.finditer(r"(\w+)\s*:\s*([A-Z_]+)\s*,", real_data_block.group(1)):
            slug, const = m.group(1), m.group(2)
            const_to_slug[const] = slug

    # ── Step 2: walk line by line with a state machine ────────────────────────
    parties    = []
    candidates = []

    current_const    = None   # e.g. "RVK"
    current_slug     = None   # e.g. "reykjavik"
    current_party    = None   # e.g. "D"
    in_list          = False
    has_platform_url = False
    current_tagline  = ""
    brace_depth      = 0      # depth since party block opened
    list_brace_depth = 0      # depth when 'list: [' was encountered
    list_indent      = -1     # column of the opening 'list: [' line; only ']' at this indent ends the list

    # Regex patterns
    re_const_start   = re.compile(r"^const ([A-Z][A-Z0-9_]+)\s*=\s*\{")
    re_party_start   = re.compile(r"^\s{2}([A-Z][A-Z0-9]{0,3})\s*:\s*\{")
    re_tagline       = re.compile(r"tagline\s*:\s*'((?:[^'\\]|\\.)*)'")
    re_platform_url  = re.compile(r"platformUrl\s*:")
    re_list_start    = re.compile(r"list\s*:\s*\[")
    re_candidate     = re.compile(
        r"\[(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'(.*)"
    )

    for line in lines:
        stripped = line.strip()

        # Track current const (municipality)
        m = re_const_start.match(line)
        if m:
            const_id = m.group(1)
            if const_id in const_to_slug:
                current_const = const_id
                current_slug  = const_to_slug[const_id]
            else:
                current_const = None
                current_slug  = None
            current_party    = None
            in_list          = False
            continue

        if current_const is None:
            continue

        # Track party start
        if not in_list:
            m = re_party_start.match(line)
            if m:
                # Save previous party if any
                if current_party:
                    parties.append({
                        "muni_slug":        current_slug,
                        "muni_label":       MUNI_LABELS.get(current_slug, current_slug),
                        "party_code":       current_party,
                        "party_label":      PARTY_LABELS.get(current_party, current_party),
                        "has_platform_url": has_platform_url,
                        "tagline":          current_tagline,
                    })
                current_party    = m.group(1)
                has_platform_url = False
                current_tagline  = ""
                in_list          = False
                continue

        # Track tagline
        if not in_list and current_party:
            mt = re_tagline.search(line)
            if mt:
                current_tagline = mt.group(1)

        # Track platform URL
        if not in_list and current_party and re_platform_url.search(line):
            has_platform_url = True

        # Track list start
        if current_party and not in_list and re_list_start.search(line):
            in_list          = True
            list_brace_depth = 0
            list_indent      = len(line) - len(line.lstrip(" "))
            continue

        # Inside list: parse candidate rows
        if in_list:
            # End of list — closing ']' must be at exactly the same indent as 'list: ['.
            # Inner brackets (social: [], news: [], candidate-row [...]) are deeper.
            this_indent = len(line) - len(line.lstrip(" "))
            if stripped in ("],", "]") and this_indent == list_indent:
                in_list = False
                # Save party
                if current_party:
                    parties.append({
                        "muni_slug":        current_slug,
                        "muni_label":       MUNI_LABELS.get(current_slug, current_slug),
                        "party_code":       current_party,
                        "party_label":      PARTY_LABELS.get(current_party, current_party),
                        "has_platform_url": has_platform_url,
                        "tagline":          current_tagline,
                    })
                    current_party = None
                continue

            # Candidate row: starts with [ and has ballot number + name + occupation
            m = re_candidate.match(stripped)
            if m:
                ballot = int(m.group(1))
                name   = m.group(2).replace("\\'", "'")
                occ    = m.group(3).replace("\\'", "'")
                rest   = m.group(4)  # everything after the occupation

                # Determine if photo is present
                # rest looks like: , 'images/...' or , null or empty
                has_photo = bool(re.search(r"'images/candidates/", rest))

                candidates.append({
                    "muni_slug":   current_slug,
                    "muni_label":  MUNI_LABELS.get(current_slug, current_slug),
                    "party_code":  current_party,
                    "ballot":      ballot,
                    "name":        name,
                    "occupation":  occ,
                    "has_photo":   has_photo,
                    # news is extracted in step 3
                    "news_urls":   [],
                    "news_count":  0,
                })

    # Save last party if file ends mid-parse
    if current_party and current_slug:
        parties.append({
            "muni_slug":        current_slug,
            "muni_label":       MUNI_LABELS.get(current_slug, current_slug),
            "party_code":       current_party,
            "party_label":      PARTY_LABELS.get(current_party, current_party),
            "has_platform_url": has_platform_url,
            "tagline":          current_tagline,
        })

    # ── Step 3a: detect which candidates already have a bio ──────────────────
    # Look for bio: 'non-empty text' and find the name that precedes it
    has_bio_names: set[str] = set()
    for m in re.finditer(r"bio\s*:\s*'([^']{1,})'", src):
        prefix = src[max(0, m.start() - 600):m.start()]
        name_matches = re.findall(r"\[\d+\s*,\s*'((?:[^'\\]|\\.)*?)'", prefix)
        if name_matches:
            has_bio_names.add(name_matches[-1].replace("\\'", "'"))

    # Detect candidates that have an extended data block {age:..., bio:...}
    has_extended_names: set[str] = set()
    for m in re.finditer(r"bio\s*:\s*(?:null|')", src):
        prefix = src[max(0, m.start() - 600):m.start()]
        name_matches = re.findall(r"\[\d+\s*,\s*'((?:[^'\\]|\\.)*?)'", prefix)
        if name_matches:
            has_extended_names.add(name_matches[-1].replace("\\'", "'"))

    for c in candidates:
        c['has_bio']      = c['name'] in has_bio_names
        c['has_extended'] = c['name'] in has_extended_names

    # ── Step 3: extract news URLs per candidate via regex ─────────────────────
    # Build a lookup by name for the news extraction pass
    cand_index: dict[str, list] = {}
    for c in candidates:
        key = (c["muni_slug"], c["party_code"], c["name"])
        cand_index.setdefault(key, []).append(c)

    # Find all news arrays: look for sequences of { title:..., url:... }
    news_re = re.compile(
        r"\{\s*title\s*:\s*'((?:[^'\\]|\\.)*)'\s*,\s*url\s*:\s*'((?:[^'\\]|\\.)*)'\s*,"
        r"\s*source\s*:\s*'((?:[^'\\]|\\.)*)'",
        re.DOTALL
    )

    # We need to associate news blocks with candidates
    # Strategy: find each candidate's extended data block and extract its news
    # Pattern: after the occupation (3rd element), find the {age:..., news:[...]} block
    cand_block_re = re.compile(
        r"\[\d+\s*,\s*'(?:[^'\\]|\\.)*'\s*,\s*'(?:[^'\\]|\\.)*'(?:\s*,\s*(?:'[^']*'|null))?\s*,\s*\{[^}]*?news\s*:\s*\[(.*?)\]\s*,?\s*\}",
        re.DOTALL
    )

    # Simpler approach: for each candidate, scan a window around their line for news
    # Since candidates.js is structured with one candidate per block,
    # we use a two-pass approach: find 'news:' arrays and their preceding name

    name_news_re = re.compile(
        r"'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*(?:,\s*(?:'[^']*'|null))?\s*,\s*\{"
        r".*?news\s*:\s*\[(.*?)\]\s*,?\s*\}",
        re.DOTALL
    )

    for m in name_news_re.finditer(src):
        name = m.group(1).replace("\\'", "'")
        news_block = m.group(2)
        urls = [nm.group(2) for nm in news_re.finditer(news_block)]
        # Find matching candidates by name (may match across munis — that's ok, all get same count hint)
        for key, cands in cand_index.items():
            if key[2] == name:
                for c in cands:
                    c["news_urls"]  = urls
                    c["news_count"] = len(urls)

    return parties, candidates


# ── Manifest builder ──────────────────────────────────────────────────────────

def build_manifest(parties, candidates):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Missing photos
    missing_photos = [
        {
            "id":          f"{c['muni_slug'][:3].upper()}.{c['party_code']}.{c['ballot']}",
            "muni_slug":   c["muni_slug"],
            "muni_label":  c["muni_label"],
            "party_code":  c["party_code"],
            "ballot":      c["ballot"],
            "name":        c["name"],
            "occupation":  c["occupation"],
        }
        for c in candidates if not c["has_photo"]
    ]

    # Missing policy (no platformUrl)
    missing_policy = [
        {
            "id":           f"{p['muni_slug'][:3].upper()}.{p['party_code']}",
            "muni_slug":    p["muni_slug"],
            "muni_label":   p["muni_label"],
            "party_code":   p["party_code"],
            "party_label":  p["party_label"],
            "tagline":      p["tagline"],
        }
        for p in parties if not p["has_platform_url"]
    ]

    # Missing bios — top 6 per list, candidates with extended block but no bio
    # (ballot > 6 are skipped — writing bios for every candidate is not realistic)
    missing_bios = [
        {
            "id":           f"{c['muni_slug'][:3].upper()}.{c['party_code']}.{c['ballot']}",
            "muni_slug":    c["muni_slug"],
            "muni_label":   c["muni_label"],
            "party_code":   c["party_code"],
            "ballot":       c["ballot"],
            "name":         c["name"],
            "occupation":   c["occupation"],
            "has_extended": c["has_extended"],
        }
        for c in candidates
        if not c["has_bio"] and c["ballot"] <= 6
    ]

    # All candidates for news refresh, sorted: fewest news first (highest priority)
    news_candidates = sorted(
        [
            {
                "id":          f"{c['muni_slug'][:3].upper()}.{c['party_code']}.{c['ballot']}",
                "muni_slug":   c["muni_slug"],
                "muni_label":  c["muni_label"],
                "party_code":  c["party_code"],
                "ballot":      c["ballot"],
                "name":        c["name"],
                "occupation":  c["occupation"],
                "news_count":  c["news_count"],
                "news_urls":   c["news_urls"],
            }
            for c in candidates
        ],
        key=lambda x: x["news_count"]
    )

    return {
        "generated":   now,
        "source_file": "js/data/candidates.js",
        "summary": {
            "total_candidates":  len(candidates),
            "total_parties":     len(parties),
            "missing_photos":    len(missing_photos),
            "missing_policy":    len(missing_policy),
            "missing_bios":      len(missing_bios),
            "zero_news":         sum(1 for c in candidates if c["news_count"] == 0),
            "low_news_1_3":      sum(1 for c in candidates if 1 <= c["news_count"] <= 3),
            "good_news_4_plus":  sum(1 for c in candidates if c["news_count"] >= 4),
        },
        "missing_photos":   missing_photos,
        "missing_policy":   missing_policy,
        "missing_bios":     missing_bios,
        "news_candidates":  news_candidates,
    }


# ── Result-file templates ─────────────────────────────────────────────────────

PHOTO_RESULT_TEMPLATE = {
    "_instructions": (
        "Add one entry per found photo. Remove this _instructions key when done. "
        "The 'id' must match scan_manifest.json. "
        "Apply with: python scripts/apply_scan_results.py photos scan_results/YOUR_FILE.json"
    ),
    "scan_type":  "photos",
    "scan_date":  "YYYY-MM-DD",
    "agent_note": "Describe search strategy used",
    "results": [
        {
            "id":          "RVK.D.3",
            "muni_slug":   "reykjavik",
            "party_code":  "D",
            "ballot":      3,
            "name":        "Example Name",
            "photo_url":   "https://example.com/photo.jpg",
            "photo_local": "images/candidates/HASH.png",
            "source":      "URL where photo was found"
        }
    ]
}

POLICY_RESULT_TEMPLATE = {
    "_instructions": (
        "Add one entry per party whose policy was found. Remove this _instructions key when done. "
        "Apply with: python scripts/apply_scan_results.py policy scan_results/YOUR_FILE.json"
    ),
    "scan_type":  "policy",
    "scan_date":  "YYYY-MM-DD",
    "agent_note": "Describe search strategy used",
    "results": [
        {
            "id":           "SNB.M",
            "muni_slug":    "sudurnesjabaer",
            "party_code":   "M",
            "platform_url": "https://example.com/stefna/",
            "tagline":      "Updated tagline for the party",
            "agenda": [
                {"icon": "🏗️", "title": "Topic", "text": "Description of policy point."},
                {"icon": "🏠", "title": "Topic", "text": "Description of policy point."},
                {"icon": "📚", "title": "Topic", "text": "Description of policy point."}
            ]
        }
    ]
}

NEWS_RESULT_TEMPLATE = {
    "_instructions": (
        "Add one entry per candidate with new articles found. Only include NEW articles "
        "(not already in news_urls from the manifest). Remove this _instructions key. "
        "Apply with: python scripts/apply_scan_results.py news scan_results/YOUR_FILE.json"
    ),
    "scan_type":  "news",
    "scan_date":  "YYYY-MM-DD",
    "agent_note": "Describe search strategy used",
    "results": [
        {
            "id":          "RVK.D.1",
            "muni_slug":   "reykjavik",
            "party_code":  "D",
            "ballot":      1,
            "name":        "Example Name",
            "new_articles": [
                {"title": "Article headline", "url": "https://...", "source": "mbl.is"},
                {"title": "Article headline", "url": "https://...", "source": "ruv.is"}
            ]
        }
    ]
}


BIO_RESULT_TEMPLATE = {
    "_instructions": (
        "Add one entry per candidate whose bio was written. Only include candidates "
        "whose has_extended flag is true in the manifest (others can't be applied automatically). "
        "Bio must be written in Icelandic. Remove this _instructions key when done. "
        "Apply with: python scripts/apply_scan_results.py bios scan_results/YOUR_FILE.json"
    ),
    "scan_type":  "bios",
    "scan_date":  "YYYY-MM-DD",
    "agent_note": "Describe search strategy used",
    "results": [
        {
            "id":          "RVK.D.1",
            "muni_slug":   "reykjavik",
            "party_code":  "D",
            "ballot":      1,
            "name":        "Example Name",
            "age":         45,
            "bio":         "Bio text written in Icelandic...",
            "interests":   ["Interest 1", "Interest 2", "Interest 3"],
            "social":      {"linkedin": "https://...", "facebook": "https://..."}
        }
    ]
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Ensure stdout handles Unicode on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print(f"Reading {CANDIDATES_JS} ...")
    if not CANDIDATES_JS.exists():
        print(f"ERROR: {CANDIDATES_JS} not found", file=sys.stderr)
        sys.exit(1)

    parties, candidates = parse_candidates_js(CANDIDATES_JS)
    manifest = build_manifest(parties, candidates)

    MANIFEST_OUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[OK] Wrote {MANIFEST_OUT}")

    s = manifest["summary"]
    print(f"\n  Candidates:      {s['total_candidates']}")
    print(f"  Parties:         {s['total_parties']}")
    print(f"  Missing photos:  {s['missing_photos']}")
    print(f"  Missing policy:  {s['missing_policy']}")
    print(f"  Missing bios:    {s['missing_bios']} (ballot 1–6)")
    print(f"  Zero news:       {s['zero_news']}")
    print(f"  Low news (1-3):  {s['low_news_1_3']}")
    print(f"  Good news (4+):  {s['good_news_4_plus']}")

    # Write result templates if they don't exist yet
    templates = [
        ("scan_results/TEMPLATE_photos.json",  PHOTO_RESULT_TEMPLATE),
        ("scan_results/TEMPLATE_policy.json",  POLICY_RESULT_TEMPLATE),
        ("scan_results/TEMPLATE_news.json",    NEWS_RESULT_TEMPLATE),
        ("scan_results/TEMPLATE_bios.json",    BIO_RESULT_TEMPLATE),
    ]
    for fname, tmpl in templates:
        p = ROOT / fname
        if not p.exists():
            p.write_text(json.dumps(tmpl, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[OK] Created template {p.name}")

    print("\nNext: run scan agents with scan_manifest.json as their input.")


if __name__ == "__main__":
    main()
