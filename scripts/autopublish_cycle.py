#!/usr/bin/env python3
"""autopublish_cycle.py — one election-night watch+publish cycle.

Run every 5 min by the Monitor loop. Does exactly what the operator was
doing by hand on each "publish":

  1. scrape RÚV  (scripts/scrape_ruv_results.py → writes the draft)
  2. diff the draft against the LIVE channel by votesCounted
  3. if nothing moved → print nothing, exit 0 (Monitor stays silent)
  4. if something moved → write a trimmed draft of ONLY the changed
     munis, run publish_live_results.py, commit + push the micro-repo,
     verify it is serving, then print ONE timestamped summary line

Never raises. Any failure prints a single "WARN" line and exits 0 so the
loop keeps going and the next cycle retries cleanly.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "data" / "live-results.draft.json"
TRIM = ROOT / ".scratch" / "pub_auto.json"
MICRO = ROOT.parent / "iceland-results-live"
LIVE_URL = "https://halldorberg.github.io/iceland-results-live/results.json"
PY = sys.executable

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M")


def _run(cmd, cwd=None, timeout=180):
    return subprocess.run(
        cmd, cwd=cwd, timeout=timeout,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace")


def _live_counts() -> dict:
    raw = urllib.request.urlopen(
        f"{LIVE_URL}?t={time.time_ns()}", timeout=20).read()
    munis = json.loads(raw)["munis"]
    out = {}
    for mid, v in munis.items():
        snaps = v.get("snapshots") or []
        out[mid] = snaps[-1]["votesCounted"] if snaps else None
    return out


def main() -> int:
    ts = _ts()
    try:
        # 1. scrape (writes the draft on disk; output discarded)
        r = _run([PY, str(ROOT / "scripts" / "scrape_ruv_results.py")])
        if r.returncode != 0:
            print(f"[{ts}Z] WARN scrape rc={r.returncode}: "
                  f"{r.stdout.strip()[-300:]}", flush=True)
            return 0

        draft = json.loads(DRAFT.read_text(encoding="utf-8"))["munis"]
        live = _live_counts()

        changed, new, upd = {}, [], []
        for mid, v in sorted(draft.items()):
            dv = v["votesCounted"]
            pv = live.get(mid)
            if pv is None:
                changed[mid] = v
                new.append(f"{mid} {dv:,}")
            elif dv != pv:
                changed[mid] = v
                upd.append(f"{mid} {pv:,}->{dv:,}")

        if not changed:
            return 0  # nothing moved → silent

        # 2. trimmed draft of only the changed munis
        TRIM.parent.mkdir(parents=True, exist_ok=True)
        TRIM.write_text(
            json.dumps({"munis": changed}, ensure_ascii=False, indent=2)
            + "\n", encoding="utf-8")

        # 3. publish (D'Hondt + append snapshots → micro-repo results.json)
        r = _run([PY, str(ROOT / "scripts" / "publish_live_results.py"),
                  "--draft", str(TRIM)])
        if r.returncode != 0:
            print(f"[{ts}Z] WARN publish rc={r.returncode}: "
                  f"{r.stdout.strip()[-300:]}", flush=True)
            return 0

        # 4. commit + push the micro-repo
        n = len(changed)
        msg = (f"Auto results batch {ts}Z — "
               f"NEW {len(new)} ({'; '.join(new) or '-'}) · "
               f"UPD {len(upd)} ({'; '.join(upd) or '-'}) ({n} munis)")
        _run(["git", "-C", str(MICRO), "add", "results.json"])
        c = _run(["git", "-C", str(MICRO),
                  "-c", "user.email=noreply@anthropic.com",
                  "-c", "user.name=Claude",
                  "commit", "-q", "-m", msg])
        if c.returncode != 0:
            print(f"[{ts}Z] WARN git commit: "
                  f"{c.stdout.strip()[-300:]}", flush=True)
            return 0
        p = _run(["git", "-C", str(MICRO), "push", "-q", "origin", "main"])
        if p.returncode != 0:
            print(f"[{ts}Z] WARN git push: "
                  f"{p.stdout.strip()[-300:]}", flush=True)
            return 0

        # 5. verify it is serving (best-effort, ~40s budget)
        served = False
        want = {m: draft[m]["votesCounted"] for m in changed}
        for _ in range(5):
            time.sleep(8)
            try:
                lv = _live_counts()
                if all(lv.get(m) == w for m, w in want.items()):
                    served = True
                    break
            except Exception:
                pass

        flag = "LIVE" if served else "pushed (CDN propagating)"
        print(f"[{ts}Z] 🔔 AUTO-PUBLISHED {n} muni(s) — {flag} · "
              f"NEW {len(new)} ({'; '.join(new) or '-'}) · "
              f"UPD {len(upd)} ({'; '.join(upd) or '-'})", flush=True)
        return 0

    except Exception as e:  # noqa: BLE001
        print(f"[{_ts()}Z] WARN cycle error: {e}", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
