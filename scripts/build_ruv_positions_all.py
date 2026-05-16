#!/usr/bin/env python3
"""Build js/data/ruv_positions.js for ALL munis from data/party_answers_all.json.

data/party_answers_all.json is reliable PER PARTY GROUP (each group carries the
correct `ruvName`, `constituencyId`, `slug` and party `name`/`answers`) but its
top-level muni KEYS are mis-assigned for ~13 munis (build_all_party_answers.py's
hand-coded MUNI_BY_CONSTITUENCY map is wrong/duplicated). So this script IGNORES
the JSON's muni keys and re-resolves every group:

  1. site muni  ← `ruvName` (authoritative RÚV constituency name) matched to
     muni_config names by a suffix-stripping normaliser; slug-prefix fallback;
     a tiny explicit alias map for the few RÚV/​site slug-convention diffs.
  2. ballot letter ← RÚV party `name` matched to the site party name
     (parties.js) for that muni's ballot letters; the lone remaining local
     list is paired by elimination.

Only PROPOSITION questions with a literal A/B/C/D answer are kept.
`importance[qid][letter]=1` iff the party flagged the proposition important.

The script PRINTS A FULL REPORT and refuses to hide problems: any muni or
party it cannot confidently resolve is listed loudly so it can be eyeballed
before election night. Output shape is unchanged (scoreCoalition consumes it):

  RUV_POSITIONS = { "<muni_id>": {
      "order":[qid...], "questions":{qid:{title,slug,importance:{L:1}}},
      "parties":{ <ballotLetter>: { qid:{value,mean,n:1,std:0} } } } }

Usage:  python scripts/build_ruv_positions_all.py
"""
from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "party_answers_all.json"
CONFIG = ROOT / "data" / "muni_config.json"
PARTIES_JS = ROOT / "js" / "data" / "parties.js"
OUT = ROOT / "js" / "data" / "ruv_positions.js"

LETTER_TO_NUM = {"A": 1, "B": 2, "C": 3, "D": 4}

# RÚV muni slug prefix → site muni_id. The party `slug` is the ONLY field
# that's reliably correct in party_answers_all.json (the JSON's muni key AND
# its ruvName are both corrupted in lockstep for the mis-mapped entries), so
# muni resolution is slug-prefix only. These cover RÚV slug spellings that
# don't fall out of slugify(our muni name): þ dropped, suffixes trimmed, etc.
SLUG_ALIAS = {
    "ingeyjarsveit": "thingeyjarsveit",
    "vopnafjardarhreppur": "vopnafjordur",
    "sudavikurhreppur": "sudavik",
    "svalbardsstrandarhreppur": "svalbardsstrond",
    "rangarthing-ytra": "rangarthingytra",
    "rangarthing-eystra": "rangarthingeystra",
    "grimsnes-og-grafningshreppur": "grimsnesgrafningur",
    "skeida-og-gnupverjahreppur": "skeidagnup",
    "hunathing-vestra": "hunathing",
    "reykholahreppur": "reykholar",
}

_TR = str.maketrans({
    "ð": "d", "þ": "th", "æ": "ae", "ö": "o", "á": "a", "é": "e",
    "í": "i", "ó": "o", "ú": "u", "ý": "y",
})


def slugify(s: str) -> str:
    s = (s or "").lower().translate(_TR)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def norm_muni(s: str) -> str:
    """Loose muni-name key: drop 'Sveitarfélagið', common suffixes, separators."""
    s = (s or "").lower().translate(_TR)
    s = s.replace("sveitarfelagid", "").replace("byggdin", "")
    s = re.sub(r"[^a-z0-9]+", "", s)
    for suf in ("kaupstadur", "kaupstad", "baer", "hreppur", "sysla"):
        if s.endswith(suf) and len(s) > len(suf) + 2:
            s = s[: -len(suf)]
    return s


def norm_party(s: str) -> str:
    """Party-name key: strip diacritics/separators + the definite-article tail
    so 'Sjálfstæðisflokkur' == 'Sjálfstæðisflokkurinn', 'listi'=='listinn'."""
    s = (s or "").lower().translate(_TR)
    s = re.sub(r"[^a-z0-9]+", "", s)
    for suf in ("inn", "in", "id", "nir", "na", "ns"):
        if s.endswith(suf) and len(s) > len(suf) + 3:
            s = s[: -len(suf)]
            break
    return s


def parties_js_names() -> dict:
    src = PARTIES_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\s{2}([A-Za-z0-9ÁÉÍÓÚÝÐÞÆÖ]+):\s*\{", src, re.M):
        code = m.group(1)
        blk = src[m.end(): src.find("\n  }", m.end())]
        nm = re.search(r"name:\s*'([^']*)'", blk)
        if nm:
            out[code] = nm.group(1)
    return out


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    questions = data.get("questions", {})
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["munis"]
    pnames = parties_js_names()

    # Muni resolution is slug-prefix ONLY (the one trustworthy field).
    # Candidate prefixes per muni: slugify(name), slugify(name minus the
    # 'Sveitarfélagið'/suffix noise), and the muni_id itself. Longest match
    # wins so e.g. 'sveitarfelagid-arborg' beats a stray 'arborg'.
    def name_variants(mid: str, name: str):
        sn = slugify(name)
        v = {sn, mid}
        bare = re.sub(r"^sveitarfelagid-", "", sn)
        v.add(bare)
        # RÚV prefixes many slugs with "sveitarfelagid-" even when our muni
        # name doesn't (e.g. our "Árborg" vs RÚV "sveitarfelagid-arborg").
        v.add("sveitarfelagid-" + sn)
        v.add("sveitarfelagid-" + mid)
        for suf in ("baer", "kaupstadur", "hreppur"):
            if bare.endswith(suf) and len(bare) > len(suf) + 2:
                v.add(bare[: -len(suf)])
        return {s for s in v if s}

    cand = []
    for mid, c in cfg.items():
        for s in name_variants(mid, c["name"]):
            cand.append((s, mid))
    for pref, mid in SLUG_ALIAS.items():
        cand.append((pref, mid))
    cand.sort(key=lambda x: -len(x[0]))

    def resolve_muni(_ruv_name_ignored: str, slug: str):
        for ms, mid in cand:
            if ms and (slug == ms or slug.startswith(ms + "-")):
                return mid
        return None

    # Collect every party group across the (mis-keyed) JSON, re-bucket by the
    # resolved site muni.
    buckets: dict[str, list] = {}
    unresolved_muni = []
    for entry in data["munis"].values():
        for p in entry.get("parties", []):
            mid = resolve_muni(entry.get("ruvName", ""), p.get("slug", ""))
            if not mid:
                unresolved_muni.append(
                    (entry.get("ruvName"), p.get("slug"), p.get("name")))
                continue
            buckets.setdefault(mid, []).append(p)

    out: dict[str, dict] = {}
    report: list[str] = []
    problems: list[str] = []

    for mid, plist in sorted(buckets.items()):
        if mid not in cfg:
            problems.append(f"{mid}: resolved but not in muni_config")
            continue
        letters = cfg[mid]["partyIds"]
        # site name(normalised) → ballot letter for this muni
        site_by_norm = {}
        for L in letters:
            nm = pnames.get(L)
            if nm:
                site_by_norm.setdefault(norm_party(nm), L)

        order: list[str] = []
        q_out: dict[str, dict] = {}
        p_out: dict[str, dict] = {}
        seen = set()
        used_letters = set()
        matched = []
        pending = list(plist)

        def take(p, L, how):
            used_letters.add(L)
            matched.append((f"{p.get('name')} {how}", L))
            _ingest(p, L, questions, order, q_out, p_out, seen)

        def free():
            return [L for L in letters if L not in used_letters]

        # 1) RÚV code == ballot letter (national parties, most locals).
        for p in pending[:]:
            c = p.get("code")
            if c in letters and c not in used_letters:
                take(p, c, "[code]"); pending.remove(p)

        # 2) exact normalised party-name match.
        for p in pending[:]:
            L = site_by_norm.get(norm_party(p.get("name", "")))
            if L and L not in used_letters:
                take(p, L, "[name]"); pending.remove(p)

        # 3) one normalised name is a prefix of the other (≥6 chars) and
        #    that ballot letter is uniquely free.
        for p in pending[:]:
            rn = norm_party(p.get("name", ""))
            hits = [L for L in free()
                    if (sn := norm_party(pnames.get(L, "")))
                    and len(min(rn, sn, key=len)) >= 6
                    and (rn.startswith(sn) or sn.startswith(rn)
                         or rn in sn or sn in rn)]
            if len(hits) == 1:
                take(p, hits[0], "[name~]"); pending.remove(p)

        # 4) site letter embeds the RÚV code as its suffix (MYA↔A, GFB↔B,
        #    THVN↔N, ARNA↔Á …), uniquely among free letters.
        for p in pending[:]:
            tc = slugify(p.get("code", "")).upper()
            if not tc:
                continue
            hits = [L for L in free() if slugify(L).upper().endswith(tc)]
            if len(hits) == 1:
                take(p, hits[0], "[code~]"); pending.remove(p)

        # 5) lone remaining RÚV list ↔ lone remaining ballot letter.
        if len(pending) == 1 and len(free()) == 1:
            take(pending[0], free()[0], "[elim]"); pending = []

        unmatched_ruv = [p.get("name") for p in pending]

        if order and p_out:
            out[mid] = {"order": order, "questions": q_out, "parties": p_out}

        tag = "" if not unmatched_ruv else "  ⚠"
        report.append(
            f"  {mid:20s} {len(matched)}/{len(plist)} parties"
            f"{'  unmatched RÚV: ' + ', '.join(unmatched_ruv) if unmatched_ruv else ''}{tag}"
        )
        if unmatched_ruv:
            problems.append(
                f"{mid}: unmatched RÚV parties {unmatched_ruv}; "
                f"free ballot letters {[L for L in letters if L not in used_letters]}"
            )

    out = dict(sorted(out.items()))
    HEADER = (
        "// Auto-generated by scripts/build_ruv_positions_all.py — DO NOT EDIT.\n"
        "// Re-run the script and commit the regenerated file.\n"
        "//\n"
        "// Per-muni RÚV kosningapróf 2026 stances for every contested muni,\n"
        "// keyed by the OFFICIAL ballot letter (RÚV's own party codes are\n"
        "// reconciled to our ballot letters by party name). Likert: A=1…D=4.\n"
        "//   questions[qid] = { title, slug, importance: { letter: 1 } }\n"
        "//   parties[letter][qid] = { value, mean, n: 1, std: 0 }\n"
        "export const RUV_POSITIONS = "
    )
    OUT.write_text(
        HEADER + json.dumps(out, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )

    print(f"Wrote {OUT.relative_to(ROOT)} — {len(out)} munis "
          f"(of {len(cfg)} contested), "
          f"{sum(len(v['questions']) for v in out.values())} muni-questions.")
    print("\nPer-muni party match:")
    print("\n".join(report))
    if unresolved_muni:
        print(f"\n⚠ {len(unresolved_muni)} party groups with UNRESOLVED muni:")
        for rn, sl, pn in unresolved_muni[:40]:
            print(f"    ruvName={rn!r} slug={sl!r} party={pn!r}")
    missing = sorted(set(cfg) - set(out))
    if missing:
        print(f"\n{len(missing)} contested munis with NO RÚV data "
              f"(coalition = seats only): {', '.join(missing)}")
    if problems:
        print(f"\n⚠ {len(problems)} muni(s) need review:")
        for pr in problems:
            print(f"    {pr}")
    return 0


def _ingest(p, letter, questions, order, q_out, p_out, seen):
    for ans in p.get("answers", []):
        qid = str(ans.get("qid"))
        val = ans.get("value")
        qm = questions.get(qid)
        if not qm or qm.get("type") != "PROPOSITION" or val not in LETTER_TO_NUM:
            continue
        if qid not in seen:
            seen.add(qid)
            order.append(qid)
            q_out[qid] = {
                "title": qm.get("title", ""),
                "slug": qm.get("slug", ""),
                "importance": {},
            }
        if ans.get("important"):
            q_out[qid]["importance"][letter] = 1
        p_out.setdefault(letter, {})[qid] = {
            "value": val,
            "mean": float(LETTER_TO_NUM[val]),
            "n": 1,
            "std": 0.0,
        }


if __name__ == "__main__":
    raise SystemExit(main())
