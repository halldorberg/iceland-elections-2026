# Election-night fast-path

A way to push live election results in ~30 seconds instead of the 2–5 min the
current push pipeline takes. Captured 2026-05-14, picking up tomorrow.

---

## Why the current pipeline is slow

When you say "push live" today, this happens:

| # | Step | Time |
|---|---|---:|
| 1 | Edit source files (data, maybe a cache-version bump) | seconds |
| 2 | Bump `?v=N` in `municipality.html` and inside `municipality.js`'s imports | seconds |
| 3 | Mirror edits to `.claude/worktrees/happy-wright-16c982/…` so the preview server sees them | ~1 s |
| 4 | **Run `scripts/build_static_pages.py`** — regenerate 3,882 pre-rendered HTML stubs (one per route × 3 langs). Each stub hard-codes the literal `?v=N` URLs, so any cache bump rewrites *every* stub. | **30–60 s** |
| 5 | `git add -u` (thousands of stub diffs) | 10–30 s |
| 6 | `git commit` (typically 7–8k-line diff) | 5–10 s |
| 7 | `git push` (uploads ~5–10 MB) | 20–60 s |
| 8 | Cloudflare edge cache rotates | 30 s – 2 min |

End-to-end **2–5 minutes**, dominated by step 4 (stub regen) and step 7 (push).

The cost exists because **caching is opt-in via the URL** (`?v=N` query string).
That's the right design for the rest of the site — but on election night we'd
rather pay zero cache cost for the few numbers that change every minute.

---

## Proposal: "Live results channel"

Break live results out into one JSON file that the browser fetches fresh on
every page load, with no version pinning. Everything else keeps the
current caching guarantees.

### 1. Data file

`/data/live-results.json` at the repo root:

```json
{
  "updatedAt": "2026-05-16T22:14:30Z",
  "reykjavik": {
    "totalSeats": 23,
    "parties": {
      "D": { "votes": 12345, "pct": 28.7, "seats": 7 },
      "S": { "votes":  8765, "pct": 20.4, "seats": 5 }
    }
  },
  "kopavogur": { ... },
  ...
}
```

A small Python helper (`scripts/publish_live_results.py`) takes the backend
output, validates it, and writes this file.

### 2. Runtime fetch in the page

```js
const live = await fetch(`/data/live-results.json?t=${Date.now()}`)
                      .then(r => r.json())
                      .catch(() => null);
```

`?t=${Date.now()}` is the cache buster — browser asks Cloudflare every time;
Cloudflare asks origin every time the edge TTL has expired (see step 3).

### 3. Cloudflare rule

Page Rule / Cache Rule on `/data/live-results.json`:

- **Edge TTL: 30 s** (or shorter if you want)
- **Browser TTL: 0** (do not cache locally)
- Optional: have a Worker stamp `Cache-Control: public, max-age=10` instead

### 4. Push command on election night

```bash
git add data/live-results.json
git commit -m "results $(date +%H:%M)"
git push
```

About **15–25 s total**, no stub regen, no cache version bumps.

### 5. Total edit-to-live

≈ **30–45 seconds**, with Cloudflare's TTL as the only floor. Compared to
today's 2–5 minutes.

---

## Page-side changes (one-time)

Wire `renderLiveResults(muni)` into `municipality.js` so it overlays
fetched numbers on top of whatever's in `polls.js`:

- If `live-results.json` has data for the current muni, it overrides the
  most-recent poll display.
- Otherwise the page renders identically to today.
- Show a timestamp pill: **"Niðurstöður · uppfært 22:14"** so visitors
  know they're seeing real-time results, not a poll.
- Optional `setInterval(refetch, 60_000)` so the page keeps up on its own.

---

## Fail-safe

- Missing/malformed file → page falls back to polls. Same UX as today.
- Stale cache → at worst 30 s behind the latest push.
- No `?v=N` to drift out of sync, no stale module pointing at a deleted file.

---

## Tradeoffs / decisions to make tomorrow

1. **TTL value.** 30 s feels right; 10 s if you want it snappier (more
   origin hits but Cloudflare free tier handles this easily). Decide before
   election night.
2. **Auto-refresh on the page?** 60 s `setInterval` is cheap; without it
   visitors only see updates when they refresh.
3. **Schema lock-in.** Once we wire it, the backend has to emit the exact
   shape. Pin the schema in the doc.
4. **Backend mechanics.** Backend writes the file → git push → CI?
   Or backend pushes directly via a script? Plan the handoff.
5. **Result display.** Where on the muni page does the live-results banner
   live? Replacing the top poll block makes the most sense; the polls
   collapse to "Skoðanakönnun" history. Sketch the UI.

---

## Even faster variants (optional)

- **Cloudflare Worker + KV store** instead of git. Backend writes to KV;
  page fetches via Worker. No git push at all — publishes in <1 s.
  Worth it only if updates land more often than every 30 s.
- **Cloudflare R2 + signed updates.** Same idea, file storage instead of KV.

These bypass the git repo for live results, so the history isn't polluted
with 200 commits on election night. Worth considering once the basic
JSON-file flow is in.

---

## Estimated implementation cost

30–60 minutes total:
- Schema design + sample `data/live-results.json` (10 min)
- `renderLiveResults(muni)` + timestamp pill + optional auto-refresh in
  `municipality.js` (~15 min)
- `scripts/publish_live_results.py` helper your backend can call (10 min)
- Cloudflare rule (5 min in the dashboard)
- Test on one muni, then verify push-to-live timing (~10 min)

Pick this up tomorrow.
