#!/usr/bin/env python3
"""publish_live_results.py — election-night fast-path publisher.

Takes the backend's draft batch, validates it, computes D'Hondt seat
allocations, appends a timestamped snapshot per municipality to the live
history, and writes the result into the *micro-repo* (iceland-results-live)
that the website fetches at runtime. The main 6,800-file repo is never
touched on election night, so a push deploys in seconds.

──────────────────────────────────────────────────────────────────────────
DRAFT  (data/live-results.draft.json — written by the results backend)
──────────────────────────────────────────────────────────────────────────
{
  "munis": {
    "reykjavik": {
      "votesCounted": 12345,
      "at": "2026-05-16T22:14:30Z",        # optional; stamped now if absent
      "parties": { "D": 28.7, "S": 20.4 }  # pct only; seats are computed
    }
  }
}
Only munis present in the draft get a new snapshot; everything else is
carried over unchanged.

──────────────────────────────────────────────────────────────────────────
PUBLISHED  (iceland-results-live/results.json — fetched by the page)
──────────────────────────────────────────────────────────────────────────
{
  "updatedAt": "2026-05-16T22:14:30Z",
  "munis": {
    "reykjavik": {
      "totalSeats": 23,
      "snapshots": [
        { "at": "2026-05-16T22:14:30Z", "votesCounted": 12345,
          "parties": { "D": {"pct":28.7,"seats":7}, "S": {"pct":20.4,"seats":5} } }
      ]
    }
  }
}
Snapshots are append-only and oldest→newest, so the page's carousel can
scroll back through earlier (lower vote-count) results.

──────────────────────────────────────────────────────────────────────────
USAGE
──────────────────────────────────────────────────────────────────────────
  # one-time: create an empty results.json for all 54 contested munis
  python scripts/publish_live_results.py --seed

  # election night: preview what a draft would publish (no write)
  python scripts/publish_live_results.py --dry-run

  # election night: apply the draft (writes results.json in the micro-repo)
  python scripts/publish_live_results.py

Paths default to a sibling micro-repo at ../iceland-results-live and can be
overridden with --out / --draft / --config or the env var
ICELAND_RESULTS_REPO.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to cp1252 and choke on ⚠ / · — force UTF-8 output.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "data" / "muni_config.json"
DEFAULT_DRAFT = ROOT / "data" / "live-results.draft.json"
DEFAULT_REPO = Path(
    os.environ.get("ICELAND_RESULTS_REPO", ROOT.parent / "iceland-results-live")
)


def now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def dhondt(pct: dict[str, float], total_seats: int) -> dict[str, int]:
    """Allocate `total_seats` by the D'Hondt method. pct is proportional to
    votes, so using it directly yields the same allocation as raw votes."""
    seats = {c: 0 for c in pct}
    for _ in range(total_seats):
        best_c, best_q = None, -1.0
        for c, v in pct.items():
            q = v / (seats[c] + 1)
            if q > best_q:
                best_q, best_c = q, c
        if best_c is None:
            break
        seats[best_c] += 1
    return seats


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ── seed ────────────────────────────────────────────────────────────────
def seed(config: dict, out: Path) -> None:
    munis = {
        mid: {"totalSeats": c["totalSeats"], "snapshots": []}
        for mid, c in sorted(config["munis"].items())
    }
    write_json(out, {"updatedAt": None, "munis": munis})
    print(f"Seeded {out} with {len(munis)} contested munis (empty snapshots).")
    unver = [m for m, c in config["munis"].items() if c.get("seatsUnverified")]
    if unver:
        print(f"  ⚠ verify council size before the night: {', '.join(unver)}")


# ── publish ─────────────────────────────────────────────────────────────
def publish(config: dict, draft: dict, out: Path, dry_run: bool) -> int:
    published = load_json(out)
    if published is None:
        print(f"ERROR: {out} not found. Run --seed first.", file=sys.stderr)
        return 2

    cfg_munis = config["munis"]
    pub_munis = published["munis"]
    draft_munis = (draft or {}).get("munis", {})
    if not draft_munis:
        print("Draft has no munis — nothing to publish.")
        return 1

    warnings: list[str] = []
    summary: list[str] = []

    for mid, batch in draft_munis.items():
        if mid not in cfg_munis:
            warnings.append(f"{mid}: not a contested muni in muni_config — skipped")
            continue
        cfg = cfg_munis[mid]
        total_seats = cfg["totalSeats"]
        valid_letters = set(cfg["partyIds"])

        raw = batch.get("parties", {})
        unknown = sorted(set(raw) - valid_letters)
        if unknown:
            warnings.append(
                f"{mid}: unknown party letters {unknown} "
                f"(valid: {sorted(valid_letters)}) — they are dropped"
            )
        pct = {
            k: float(v)
            for k, v in raw.items()
            if k in valid_letters and v is not None
        }
        if not pct:
            warnings.append(f"{mid}: no valid party percentages — skipped")
            continue

        s = sum(pct.values())
        if not (90.0 <= s <= 110.0):
            warnings.append(f"{mid}: party % sum to {s:.1f} (expected ≈100)")

        votes = batch.get("votesCounted")
        try:
            votes = int(votes)
        except (TypeError, ValueError):
            warnings.append(f"{mid}: votesCounted missing/invalid → recorded as 0")
            votes = 0

        snaps = pub_munis.setdefault(
            mid, {"totalSeats": total_seats, "snapshots": []}
        )["snapshots"]
        if snaps:
            prev = snaps[-1].get("votesCounted", 0)
            if votes < prev:
                warnings.append(
                    f"{mid}: votesCounted {votes} < previous {prev} "
                    "(count went DOWN — check the source)"
                )

        seats = dhondt(pct, total_seats)
        snap = {
            "at": batch.get("at") or now_iso(),
            "votesCounted": votes,
            "parties": {
                k: {"pct": round(pct[k], 2), "seats": seats[k]}
                for k in sorted(pct, key=lambda c: -pct[c])
            },
        }
        snaps.append(snap)

        seat_str = " · ".join(
            f"{k} {v}" for k, v in sorted(seats.items(), key=lambda x: -x[1]) if v
        )
        summary.append(
            f"  {mid:18s} {votes:>7,} atkv · {seat_str}  (#{len(snaps)})"
        )

    published["updatedAt"] = now_iso()

    print(f"\n{'DRY RUN — ' if dry_run else ''}batch covers "
          f"{len(summary)} muni(s):")
    print("\n".join(summary) if summary else "  (nothing)")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if dry_run:
        print(f"\n(dry run — {out} NOT written)")
        return 0

    write_json(out, published)
    print(f"\nWrote {out} · updatedAt {published['updatedAt']}")
    print("Next: cd into the micro-repo, commit results.json, push.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish live election results.")
    ap.add_argument("--seed", action="store_true",
                    help="(re)create an empty results.json for all contested munis")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate + preview the draft without writing")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--draft", type=Path, default=DEFAULT_DRAFT)
    ap.add_argument("--out", type=Path,
                    default=DEFAULT_REPO / "results.json",
                    help="path to the micro-repo's results.json")
    args = ap.parse_args()

    config = load_json(args.config)
    if config is None:
        print(f"ERROR: {args.config} missing. Run build_muni_config.py first.",
              file=sys.stderr)
        return 2

    if args.seed:
        seed(config, args.out)
        return 0

    draft = load_json(args.draft)
    if draft is None:
        print(f"ERROR: draft {args.draft} not found.", file=sys.stderr)
        return 2
    return publish(config, draft, args.out, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
