# Daily Scan Agent Guide

How to run AI scan agents efficiently with minimal rate-limit pressure.

---

## Before every scan session

```
python scripts/generate_manifest.py
```

This reads `candidates.js` and produces `scan_manifest.json` — a small
(~50 KB) work-list. Agents read the manifest, not the 800 KB source file.

---

## The three scan types

### 1. Photos — find missing candidate photos

**When:** Anytime. Photos, once found, disappear from `missing_photos` on the
next manifest run. There's no need to re-scan candidates that already have one.

**Agent prompt template:**

```
You are a photo research agent. Your task is to find portrait photos for
Icelandic municipal election candidates who currently have no photo.

Read the file: scan_manifest.json
Work through the entries in: manifest["missing_photos"]

For each candidate:
- Search the web for their full name + municipality (e.g. "Jón Jónsson Reykjavík")
- Check party websites, social media profiles, local news
- If you find a clear portrait photo (face clearly visible, professional quality):
  - Download it to: images/candidates/<sha256_first16_chars>.jpg
  - Record the result (see format below)

Result format — write to: scan_results/photos_YYYY-MM-DD.json
Use TEMPLATE: scan_results/TEMPLATE_photos.json

Rate-limit strategy:
- Process candidates in batches of 10-15
- If you hit a rate limit, stop, write partial results, and resume later
- Never re-scan a candidate you've already processed in this session

DO NOT read candidates.js. The manifest has everything you need.
```

---

### 2. Policy — find party platforms

**When:** Anytime. Parties with `platformUrl` set are excluded from the list.

**Agent prompt template:**

```
You are a policy research agent. Your task is to find official policy
platforms for Icelandic municipal election parties that don't have one yet.

Read the file: scan_manifest.json
Work through the entries in: manifest["missing_policy"]

For each party:
- Search for: "<party_label> <muni_label> stefna 2026" or similar
- Look for the party's official page, their municipal branch website,
  or a published election platform document
- If you find a credible, sourced policy page:
  - Extract 3-5 key policy points (in Icelandic)
  - Record the platform URL
  - Write a short updated tagline

Result format — write to: scan_results/policy_YYYY-MM-DD.json
Use TEMPLATE: scan_results/TEMPLATE_policy.json

Rate-limit strategy:
- Process parties in batches of 8-12
- Stop and write partial results if you hit rate limits
- Skip parties whose tagline already sounds specific and detailed —
  those likely already have real data and just didn't publish a URL.

DO NOT read candidates.js. The manifest has everything you need.
```

---

### 3. News — find new articles for candidates

**When:** Daily/weekly. Always runs for all candidates, prioritised by
those with fewest existing articles (they appear first in `news_candidates`).

**For 15 largest municipalities only (recommended for daily scan):**

```
You are a news research agent. Your task is to find recent news articles
for Icelandic municipal election candidates.

Read the file: scan_manifest.json
Work through manifest["news_candidates"] — candidates are sorted with
fewest articles first (highest priority).

SCOPE: Only process candidates where muni_slug is one of:
  reykjavik, kopavogur, hafnarfjordur, gardabaer, mosfellsbaer,
  akureyri, seltjarnarnes, reykjanesbaer, sudurnesjabaer, arborg,
  vestmannaeyjar, fjardabyggd, akranes, borgarbyggd, isafjordur

For each candidate:
1. Check their existing news_urls (skip articles already in this list)
2. Search broadly for the candidate's name — not just election coverage. Try:
   - "<name>" alone
   - "<name> <muni_label>"
   - "<name> site:mbl.is OR site:visir.is OR site:ruv.is OR site:vf.is"
   Include any article about them: career, community work, sport, culture, business, interviews, etc.
3. Add only articles published AFTER 2025-01-01
4. Add maximum 3 new articles per candidate per scan
5. Include title, url, and source (domain name)

Result format — write to: scan_results/news_YYYY-MM-DD.json
Use TEMPLATE: scan_results/TEMPLATE_news.json

Rate-limit strategy:
- Process candidates in batches of 10 at a time
- Write partial results to the output file after every batch — do not wait until the end
- Each agent should receive a slice of the list (e.g. items 0-49, 50-99...)
  to allow parallel scanning without overlap

Resuming after a rate limit:
- If the user asks you to continue scanning after a rate limit, read the partial
  results file you were already writing to find out which candidates you already
  processed, then pick up from the first candidate not yet in that file and
  continue writing to the same file.

IMPORTANT: Do not include duplicates. Check existing news_urls carefully.
DO NOT read candidates.js. The manifest has everything you need.
```

**For all municipalities (full scan — use parallel agents):**

Split `news_candidates` into slices and run agents in parallel:
- Agent A: items 0–99
- Agent B: items 100–199
- Agent C: items 200–299
- etc.

Each agent writes to its own file: `news_YYYY-MM-DD_A.json`, `_B.json`, etc.

---

## Applying results

> ⚠️ **Do not apply, commit, or push anything until the user has reviewed and
> approved the scan results.** After the scan is complete, summarise what was
> found and wait for explicit approval before touching any source files.

```bash
# Dry run first (no changes written)
python scripts/apply_scan_results.py news   scan_results/news_2026-05-01.json --dry-run
python scripts/apply_scan_results.py photos scan_results/photos_2026-05-01.json --dry-run
python scripts/apply_scan_results.py policy scan_results/policy_2026-05-01.json --dry-run

# Apply for real
python scripts/apply_scan_results.py news   scan_results/news_2026-05-01.json
python scripts/apply_scan_results.py photos scan_results/photos_2026-05-01.json
python scripts/apply_scan_results.py policy scan_results/policy_2026-05-01.json
```

After applying, bump the cache-bust version in `js/municipality.js` (line 3):
```js
import { ... } from './data/candidates.js?v=21';  // increment by 1
```

Then commit and push.

---

## Rate-limit survival tips

| Tip | Reason |
|-----|--------|
| Use the manifest, not candidates.js | ~16× smaller context = more searches per session |
| Process in batches of 10–20 | Leaves room to finish the batch if limit hits mid-run |
| Write partial results immediately | Never lose work; resume from where you stopped |
| Run photo + policy + news as separate sessions | Each type is independent; don't mix them |
| For news, use parallel agents with non-overlapping slices | 3–4× throughput, no conflicts |

---

## File layout

```
scan_manifest.json            ← generated before each session
scan_results/
  TEMPLATE_news.json          ← copy & fill in
  TEMPLATE_photos.json        ← copy & fill in
  TEMPLATE_policy.json        ← copy & fill in
  news_2026-05-01.json        ← result files (date-stamped)
  photos_2026-04-28.json
  policy_2026-04-28.json
scripts/
  generate_manifest.py        ← run first
  apply_scan_results.py       ← run after results are ready
```
