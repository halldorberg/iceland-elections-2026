#!/usr/bin/env python3
"""Scrape live municipal results from RÚV's GraphQL API into the backend draft.

RÚV's election widget (ruv.is front page / kosningar.ruv.is) is powered by
a public Apollo GraphQL endpoint. We replay its persisted queries:

  GET_CONSTITUENCIES   electionID=394            → [{identifier, text}]
  GET_BOX_LETTER_ROW   electionId=394,           → per-muni results:
                       constituencyId, timeIndex   counted, datetime,
                                                   list[{letter,text,votes,
                                                         ratio,seats}]

`ratio` is already a 0–100 percentage; `letter` is the official ballot
letter (matches our muni_config.partyIds for most munis; composite-code
munis — GB/SCS/THV…/MY… — are reconciled by party name via parties.js).

Only munis with `counted > 0` are written. Output =
data/live-results.draft.json — the exact shape the backend reads and
publish_live_results.py consumes. This script NEVER publishes; you review
in the backend (Reload from disk) and approve.

Usage:
  python scripts/scrape_ruv_results.py            # all munis with results
  python scripts/scrape_ruv_results.py --dry-run  # print, don't write
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "muni_config.json"
PARTIES_JS = ROOT / "js" / "data" / "parties.js"
DRAFT = ROOT / "data" / "live-results.draft.json"

GQL = "https://gql.kosningar.ruv.is/graphql"
ELECTION_ID = 394
HASH_CONSTS = "5ff7802df277a980271793405b8c1e7b363789a2300a7f52b5d18a7ce712dcac"
HASH_BOXROW = "e2bc7b9bf65bc04e6921d70df3603512466f829b867b9216814b7101a7b7dd40"
HEADERS = {
    "User-Agent": "Mozilla/5.0 Chrome/130",
    "Origin": "https://www.ruv.is",
    "Referer": "https://www.ruv.is/",
    "apollo-require-preflight": "true",
}

_TR = str.maketrans({
    "ð": "d", "þ": "th", "æ": "ae", "ö": "o", "á": "a", "é": "e",
    "í": "i", "ó": "o", "ú": "u", "ý": "y",
})


def norm_muni(s: str) -> str:
    s = (s or "").lower().translate(_TR)
    s = s.replace("sveitarfelagid", "").replace("byggdin", "")
    s = re.sub(r"[^a-z0-9]+", "", s)
    for suf in ("kaupstadur", "kaupstad", "baer", "hreppur", "sysla"):
        if s.endswith(suf) and len(s) > len(suf) + 2:
            s = s[: -len(suf)]
    return s


def norm_party(s: str) -> str:
    s = (s or "").lower().translate(_TR)
    s = re.sub(r"[^a-z0-9]+", "", s)
    for suf in ("inn", "in", "id", "nir", "na", "ns"):
        if s.endswith(suf) and len(s) > len(suf) + 3:
            return s[: -len(suf)]
    return s


def gql_get(op: str, sha: str, variables: dict):
    qs = urllib.parse.urlencode({
        "operationName": op,
        "variables": json.dumps(variables, separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": sha}},
            separators=(",", ":")),
        # CloudFront caches these GETs and will happily serve a stale
        # "counted: 0" long after a muni starts counting. A per-call
        # cache-buster forces a fresh object every time.
        "_cb": time.time_ns(),
    })
    req = urllib.request.Request(
        f"{GQL}?{qs}",
        headers={**HEADERS, "x-apollo-operation-name": op,
                 "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def parties_js_names() -> dict:
    src = PARTIES_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\s{2}([A-Za-z0-9ÁÉÍÓÚÝÐÞÆÖ]+):\s*\{", src, re.M):
        blk = src[m.end(): src.find("\n  }", m.end())]
        nm = re.search(r"name:\s*'([^']*)'", blk)
        if nm:
            out[m.group(1)] = nm.group(1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--delta", action="store_true",
                    help="watch mode: print ONE line only when RÚV has moved "
                         "since the last check (silent otherwise); never "
                         "writes the draft")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))["munis"]
    by_norm = {norm_muni(c["name"]): mid for mid, c in cfg.items()}
    # Some muni_config names don't norm-match RÚV's short official name
    # (e.g. "Sameinað sveitarfélag Borgarbyggðar…" vs "Borgarbyggð",
    # "Grindavíkurbær" vs "Grindavík"). Fall back to a unique
    # prefix/containment match on the normalised forms.
    cfg_norms = [(norm_muni(c["name"]), mid) for mid, c in cfg.items()]

    def resolve_muni(name: str):
        rn = norm_muni(name)
        if rn in by_norm:
            return by_norm[rn]
        hits = [mid for cn, mid in cfg_norms
                if cn and rn and (cn.startswith(rn) or rn.startswith(cn)
                                  or rn in cn or cn in rn)]
        return hits[0] if len(set(hits)) == 1 else None
    pnames = parties_js_names()

    consts = gql_get("GET_CONSTITUENCIES", HASH_CONSTS,
                     {"electionID": ELECTION_ID})
    clist = consts["data"]["muninn_election"]["constituencies"]

    munis: dict[str, dict] = {}
    warnings: list[str] = []
    summary: list[str] = []
    no_results = 0

    for c in clist:
        cid, cname = c["identifier"], c["text"]
        try:
            box = gql_get("GET_BOX_LETTER_ROW", HASH_BOXROW,
                          {"electionId": ELECTION_ID, "constituencyId": cid,
                           "timeIndex": "-1"})
            le = box["data"]["latestElection"]
        except Exception as e:                       # noqa: BLE001
            warnings.append(f"{cname} ({cid}): fetch failed — {e}")
            continue

        res = le.get("results") or {}
        counted = res.get("counted") or 0
        if counted <= 0:
            no_results += 1
            continue

        mid = resolve_muni(cname)
        if not mid:
            warnings.append(f"{cname} ({cid}): no muni_config match — skipped")
            continue
        valid = cfg[mid]["partyIds"]
        site_by_norm = {}
        for L in valid:
            nm = pnames.get(L)
            if nm:
                site_by_norm.setdefault(norm_party(nm), L)

        rows = res.get("list") or []
        pct: dict[str, float] = {}
        used = set()
        pending = []
        # 1) RÚV ballot letter == our partyId.
        for p in rows:
            L = p.get("letter")
            if L in valid and L not in used:
                pct[L] = round(float(p.get("ratio") or 0), 2)
                used.add(L)
            else:
                pending.append(p)
        # 2) match by party name (composite-code munis: GB/SCS/…).
        for p in list(pending):
            L = site_by_norm.get(norm_party(p.get("text", "")))
            if L and L not in used:
                pct[L] = round(float(p.get("ratio") or 0), 2)
                used.add(L)
                pending.remove(p)
        # 2b) one normalised name is a prefix of / contained in the other
        #     (≥6 chars), uniquely among free letters. Catches local lists
        #     like RÚV "Íbúalistinn" ↔ our IBU "Íbúalisti".
        for p in list(pending):
            rn = norm_party(p.get("text", ""))
            cand = []
            for L in valid:
                if L in used:
                    continue
                sn = norm_party(pnames.get(L, ""))
                if (sn and rn and len(min(rn, sn, key=len)) >= 6
                        and (rn.startswith(sn) or sn.startswith(rn)
                             or rn in sn or sn in rn)):
                    cand.append(L)
            if len(cand) == 1:
                pct[cand[0]] = round(float(p.get("ratio") or 0), 2)
                used.add(cand[0])
                pending.remove(p)
        # 3) site composite code embeds the RÚV letter as its suffix
        #    (MYA↔A, MYZ↔Z, GFB↔B, THVN↔N …), uniquely among free letters.
        for p in list(pending):
            rl = (p.get("letter") or "").lower().translate(_TR).upper()
            if not rl:
                continue
            cand = [L for L in valid if L not in used
                    and L.lower().translate(_TR).upper().endswith(rl)]
            if len(cand) == 1:
                pct[cand[0]] = round(float(p.get("ratio") or 0), 2)
                used.add(cand[0])
                pending.remove(p)
        # 4) lone leftover ↔ lone free ballot letter.
        free = [L for L in valid if L not in used]
        if len(pending) == 1 and len(free) == 1:
            pct[free[0]] = round(float(pending[0].get("ratio") or 0), 2)
            used.add(free[0])
            pending = []
        for p in pending:
            warnings.append(
                f"{cname}: party '{p.get('letter')} {p.get('text')}' "
                f"unmatched (free: {[L for L in valid if L not in used]})")

        if not pct:
            warnings.append(f"{cname}: no parties mapped — skipped")
            continue

        dt = res.get("datetime")
        at = (datetime.now(timezone.utc).isoformat(timespec="seconds")
              .replace("+00:00", "Z"))
        if dt:                       # "2026-05-16 22:17:43" Iceland = UTC
            at = dt.replace(" ", "T") + "Z"

        munis[mid] = {"votesCounted": int(counted), "at": at, "parties": pct}
        flag = "FINAL" if res.get("isfinal") else (
            "proj" if res.get("isprojection") else "")
        top = sorted(pct.items(), key=lambda kv: -kv[1])[:4]
        summary.append(
            f"  {mid:16s} {int(counted):>7,} atkv {flag:5s} "
            + " · ".join(f"{k} {v}" for k, v in top))

    if args.delta:
        # Watch mode. Keep the backend draft fresh EVERY cycle so
        # "Endurhlaða af diski" always reflects the latest RÚV scrape,
        # then emit ONE chat line only when RÚV has moved since the last
        # check; otherwise stay silent so the 5-min Monitor doesn't spam.
        DRAFT.parent.mkdir(parents=True, exist_ok=True)
        DRAFT.write_text(
            json.dumps({"munis": munis}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        seen_path = ROOT / ".scratch" / "ruv_last_seen.json"
        try:
            sig = {m: v["votesCounted"] for m, v in munis.items()}
            try:
                last = json.loads(seen_path.read_text(encoding="utf-8"))
            except Exception:
                last = None
            seen_path.parent.mkdir(parents=True, exist_ok=True)
            seen_path.write_text(json.dumps(sig), encoding="utf-8")
            if last is not None and sig == last:
                return 0                                # no movement → silent
            # Something moved (or first run) → report what's pending vs LIVE.
            live = json.loads(urllib.request.urlopen(
                "https://halldorberg.github.io/iceland-results-live/"
                f"results.json?t={time.time_ns()}", timeout=20).read()
            )["munis"]
            prev = {m: (v["snapshots"][-1]["votesCounted"]
                        if v.get("snapshots") else None)
                    for m, v in live.items()}
            new, up = [], []
            for m, v in sorted(sig.items()):
                p = prev.get(m)
                if p is None:
                    new.append(f"{m} {v:,}")
                elif v != p:
                    up.append(f"{m} {p:,}->{v:,}")
            ts = datetime.now(timezone.utc).strftime("%H:%M")
            if new or up:
                print(f"[{ts}Z] 🔔 RÚV update — pending vs live: "
                      f"NEW {len(new)} ({'; '.join(new) or '-'}) · "
                      f"UPDATED {len(up)} ({'; '.join(up) or '-'}) · "
                      f"{len(munis)} scraped", flush=True)
            else:
                print(f"[{ts}Z] RÚV moved but nothing pending vs live "
                      f"({len(munis)} scraped)", flush=True)
        except Exception as e:                           # noqa: BLE001
            ts = datetime.now(timezone.utc).strftime("%H:%M")
            print(f"[{ts}Z] ⚠ watch error: {e}", flush=True)
        return 0

    print(f"RÚV results: {len(munis)} muni(s) with results, "
          f"{no_results} not counted yet.")
    print("\n".join(sorted(summary)) if summary else "  (none in yet)")
    if warnings:
        print("\nWarnings:")
        for w in warnings[:40]:
            print(f"  ⚠ {w}")

    if args.dry_run:
        print("\n(dry run — draft NOT written)")
        return 0

    DRAFT.parent.mkdir(parents=True, exist_ok=True)
    DRAFT.write_text(
        json.dumps({"munis": munis}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"\nWrote {DRAFT} ({len(munis)} munis). "
          "Review in the backend (↻ Reload), then approve to publish.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
