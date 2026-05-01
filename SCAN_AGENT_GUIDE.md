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

> **Why this section is so prescriptive:** earlier policy scans drifted into
> hallucination territory because agents were given soft rules ("find a
> credible source"). They would land on a news article, paraphrase plausible
> bullets that didn't actually appear in the source, then attribute them to a
> party-owned URL the agent never fetched. The protocol below — three hard
> rules at the agent level + a mechanical post-scan audit using a different
> HTTP client than the agent's WebFetch — is what prevents that.

#### Three hard rules every agent must follow

1. **Pattern-probe FIRST.** Before any web search, WebFetch each predicted
   party-domain URL directly. Search is the fallback, not the entry point.
   - Sjálfstæðisflokkur (D): `xd.is/sveitastjornir/<muni>/`, `x<letter><muni-prefix>.is`
   - Framsókn (B): `framsokn.is/sveitarfelog/<muni>`, `framsokn.is/<muni>`, `/stefna`
   - Samfylking (S): `xs.is/<muni>`, `xs.is/<muni>-alla-aevi`
   - Vinstri Græn (V) / Vinstrið (A): `vg.is/<muni>`, `vinstrigraen<muni>.is`
   - Miðflokkur (M): `midflokkurinn.is/<muni>` ← key pattern
   - Viðreisn (C): `vidreisn.is/<muni>/stefnan/`, `vidreisn.is/<muni>/`
   - Píratar (P): `piratar.is/<muni>`
   - Local lists: try `<listname>.is`, then search for `"<list name> stefna 2026"`

   Note: many `xd.is/sveitastjornir/<muni>/` and `framsokn.is/sveitarfelog/<muni>`
   pages are candidate rosters with no policy text. Reject them — don't paraphrase
   from a navigation menu.

2. **Recency.** The fetched page must show evidence of the 2026 election
   cycle — a publication or "last updated" date ≥ 2025-01-01, OR explicit
   text "2026" / "kosningar 2026" / "sveitarstjórnarkosningar 2026". An
   undated 2022-era platform from the same party does not count, however
   credible it looks.

3. **Platform page beats op-ed on the same domain.** When `midflokkurinn.is/<muni>`
   exists with policy content AND a candidate op-ed exists on the same domain,
   the platform page wins. Do not stop at the first hit if a cleaner one is
   reachable from the patterns above.

#### Per-bullet provenance

For every kept entry, every agenda bullet must carry:

- `source_quote`: 30–250 chars of **verbatim Icelandic** copied from the
  WebFetch output. Not paraphrase. Not "summarised from". Verbatim.
- `text`: 1–2 sentence Icelandic restatement (this is what gets surfaced in
  the candidate modal)
- `title`, `icon`

And the entry as a whole carries:

- `verified_source_kind`: `"own-site"` or `"news-with-rationale"`
- `recency_evidence`: short string showing the recency proof (e.g.
  `"page footer dated 2026-04"`)
- `audit_note`: which patterns were probed, why this URL won, how recency
  was verified

If you cannot produce ≥3 quotable bullets from a single fetched page, **skip
the party**. Skipping is correct. Quality > coverage.

#### Agent prompt template

```
You are running a STRICT policy scan for the Icelandic 2026 municipal elections.

Read the file: scan_manifest.json
Work through the entries in: manifest["missing_policy"]

(Or, for parallelism, read scan_worklist_policy_YYYY-MM-DD_<X>.json — a slice
file the orchestrator created.)

THREE NON-NEGOTIABLE RULES — see SCAN_AGENT_GUIDE.md "Policy" section for
the full pattern table:

1. Pattern-probe before search. WebFetch the party's predicted own-domain
   URLs directly before doing any web search.
2. Recency. Source must show date ≥ 2025-01-01 OR explicit 2026 reference.
3. Party platform page beats op-ed on the same party domain.

WORKFLOW PER PARTY:
1. Build 4–6 candidate URLs from the party-pattern table.
2. For each URL: WebFetch with prompt
     "List the policy points / stefnumál on this page verbatim, as quoted
     Icelandic phrases. When was this page published or updated? Does it
     reference 2026 or any other election year?"
3. Score the result:
   - STRONG  = ≥4 distinct policy quotes AND recency confirmed → KEEP
   - REJECT  = old date, candidate roster only, or <3 quotes
4. After patterns exhausted, fall back to web search — same recency rule.
5. If no STRONG-tier source found → SKIP the party.

For each KEPT entry, every agenda bullet has source_quote (verbatim Icelandic,
30–250 chars), text, title, icon. Per entry: platform_url, verified_source_kind,
recency_evidence, audit_note, tagline, agenda[].

Rate-limit strategy:
- Process parties in batches of ~7
- Write partial results to the output file after every batch
- Resume by reading the output file to find which parties are already done

Result format — write to: scan_results/policy_YYYY-MM-DD.json (or
scan_results/policy_YYYY-MM-DD_<X>.json for parallel slices)
Use TEMPLATE: scan_results/TEMPLATE_policy.json

DO NOT git commit. DO NOT alter content you can't quote. DO NOT read candidates.js.
```

#### MANDATORY post-scan audit (do not skip)

After all agents finish, run the mechanical quote audit:

```bash
python scripts/verify_quotes.py
```

This script does, for every entry across all `policy_YYYY-MM-DD_*.json` files:

1. Fetches `platform_url` with a real Chrome User-Agent + Accept-Language
   header (this bypasses bot-blocks that defeat WebFetch on `bb.is`,
   `mbl.is`, etc.) using `urllib`.
2. Strips `<script>`/`<style>` blocks and tags, collapses whitespace.
3. For each `source_quote`, applies three matching tests:
   - exact substring
   - normalized substring (lowercase, non-letters → spaces)
   - word-overlap fallback: ≥75% of words ≥ 4 chars must appear in body
4. Per entry: KEEP if ≥75% of bullets match; otherwise DROP.
5. Annotates each surviving bullet with `quote_verified: true|false`.
6. Writes `policy_YYYY-MM-DD_*_AUDITED.json` and **deletes the originals**
   so the renderer only sees verified data.

The renderer (`generate_review.py`) shows per-bullet provenance directly on
the review page: green ✓ "verbatim from page" or red ⚠ "not found on linked
page". This is the user's spot-check surface.

**Why the audit is non-negotiable:** the agent and the auditor have to
agree, and the auditor is a deterministic Python script — it cannot
hallucinate. If a hallucinated quote sneaks past the agent (which it will,
especially on bot-blocked domains where the agent falls back to search
snippets), the audit catches it.

#### Live review flow (parallel agents)

Same pattern as the news scan:

- Slice `missing_policy` into 4 files (e.g. `scan_worklist_policy_YYYY-MM-DD_A.json`
  through `_D.json`). Put the no-agenda priority parties at the top of slice A.
- Each agent writes to its own `policy_YYYY-MM-DD_<X>.json`. The renderer
  globs `policy_YYYY-MM-DD*.json` and merges by `(muni_slug, party_code)`
  (avoids the `FJA.D` id collision between Fjarðabyggð and Fjallabyggð).
- After each batch write, the orchestrator (main thread) re-renders and
  pushes `scan-review.html`. Agents do **not** commit/push themselves.
- After all agents finish, run `verify_quotes.py`, re-render, push.
- Wait for explicit user approval before `apply_scan_results.py`.

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
2. **The goal is to surface non-election headlines that give a fuller picture
   of the candidate's public life** — career milestones, community/union work,
   sport, culture, business, interviews, controversies, public statements,
   board/charity roles, anything that shows who this person is *outside* the
   2026 campaign.
   **AVOID** pure 2026-election coverage — campaign launches, debate recaps,
   list announcements, polling, party endorsements. Skip them even if they
   mention the candidate by name.
   Acceptable as exceptions: pieces where the candidate is interviewed about
   a substantive personal/policy topic (housing, transit, etc.) where the
   election is only the framing, not the subject.
   Search queries:
   - "<name>" alone
   - "<name> <muni_label>"
   - "<name> site:mbl.is OR site:visir.is OR site:ruv.is OR site:vf.is"
   Try variations like "<name> ferill", "<name> viðtal" to find non-election angles.
3. **Verify identity before adding any article.** Each article MUST mention the
   candidate by full name in the title or body. If a search returns no articles
   that name this specific candidate, write **zero** new articles for them —
   do not substitute articles about a similarly-positioned public figure
   (e.g. another local politician, another woman of the same age, another
   person with the same first name). Common failure mode: a low-profile
   candidate has no coverage, so the agent latches on to a prominent
   adjacent figure and records their articles instead. Don't.
4. **Never modify the `name` field.** Copy it verbatim from the manifest
   entry. The `muni_slug`, `party_code`, `ballot`, and `name` fields together
   identify which candidate the articles belong to — they must always agree.
5. Add articles published AFTER 2021-01-01 (~5 years back). The point is a
   fuller picture of the candidate's public life, so older substantive coverage
   is welcome — career milestones, past interviews, board appointments, etc.
6. Add maximum 3 new articles per candidate per scan
7. Include title, url, and source (domain name)

Result format — write to: scan_results/news_YYYY-MM-DD.json
Use TEMPLATE: scan_results/TEMPLATE_news.json

Rate-limit strategy:
- Process candidates in batches of 10 at a time
- Write partial results to the output file after every batch — do not wait until the end
- Each agent should receive a slice of the list (e.g. items 0-49, 50-99...)
  to allow parallel scanning without overlap

Live review page (run after every batch write):
After saving a batch to scan_results/news_YYYY-MM-DD.json, immediately re-render
and push the review page so the user can monitor progress in near real time:

```bash
python scripts/generate_review.py --date YYYY-MM-DD
git add scan-review.html
git commit -m "Scan review live update — news batch YYYY-MM-DD"
git push origin master
```

This applies to every batch, not just the final one. The scan-review.html the
user sees at https://lydraedisveislan.is/scan-review.html should grow alongside
the agent's progress. Same pattern applies if multiple agents are running in
parallel — each one re-renders after its own batch; the renderer reads whatever
is currently on disk in news_YYYY-MM-DD*.json and produces a combined view.

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

### 4. Bios — write candidate biographies

**When:** Anytime. Only candidates in ballot positions 1–6 appear in `missing_bios`.
Candidates where `has_extended` is `false` cannot be applied automatically — skip them.

**Agent prompt template:**

```
You are a biography research agent. Your task is to write short Icelandic-language
biographies for Icelandic municipal election candidates who currently have no bio.

Read the file: scan_manifest.json
Work through the entries in: manifest["missing_bios"]

Skip any entry where has_extended is false — those cannot be applied automatically.

For each candidate:
1. Search broadly for the candidate's full name to find biographical details:
   - Age or birth year
   - Education and career background
   - Community roles, union work, board memberships
   - Political history (previous terms, other parties, other offices)
   - Personal interests, hobbies, family if publicly known
   - Any interviews or quotes
   Try: "<name> site:mbl.is OR site:visir.is OR site:ruv.is OR site:vf.is"
   Also try LinkedIn, party websites, municipal council pages.
2. Write a bio of 3–5 sentences in Icelandic, in third person.
   - Stick strictly to what sources confirm — do not invent details.
   - If age/birth year is found, include it.
   - If very little is found, write a minimal 1–2 sentence bio from what is known
     (name, occupation, municipality) rather than leaving it blank.
3. Record age (as integer years, NOT birth year), interests (array), and social
   links (linkedin, facebook) if found.
4. Record every URL you used as a source in the `sources` array (even if it
   only confirmed a single detail). If a search returned nothing useful, still
   note the search terms in agent_note.

Rate-limit strategy:
- Process candidates in batches of 10 at a time
- Write partial results to the output file after every batch — do not wait until the end

Resuming after a rate limit:
- If the user asks you to continue scanning after a rate limit, read the partial
  results file to find which candidates you already processed, then continue from
  the first candidate not yet in that file, writing to the same file.

Result format — write to: scan_results/bios_YYYY-MM-DD.json
Use TEMPLATE: scan_results/TEMPLATE_bios.json

IMPORTANT: Bios must be written in Icelandic.
DO NOT read candidates.js. The manifest has everything you need.
```

---

## Reviewing results (before applying)

> ⚠️ **Do not apply scan results to `candidates.js` until the user has reviewed
> and approved the page.** "Apply" means running `apply_scan_results.py`, not
> the live review-page commits described below — those are *expected* during
> a scan and don't touch candidate data.

The review page updates **live during the scan**. Each agent re-renders and
pushes `scan-review.html` after every batch write (see the news section above
for the exact commands), so the user can monitor progress at
**https://lydraedisveislan.is/scan-review.html** (password-protected, pw:
`happyhappy`) while the scan is still running. The page shows:
- All bios written, with source info
- All news articles found, by candidate
- All party platforms found, with sources
- All photos found, with where they came from

When all scans are done:

1. **For policy scans**, run `python scripts/verify_quotes.py` first — this
   fetches each `platform_url` independently and drops any entry whose
   `source_quote` text doesn't appear in the actual page body. Originals are
   replaced with `*_AUDITED.json` files. See "Policy" section above for why
   this audit is non-negotiable.
2. Do one final `generate_review.py` + push to make sure the page reflects
   the final state.
3. Wait for the user to give **explicit approval** before proceeding to
   apply results.

After approval, **clear the review page** so it is blank for the next scan:
```bash
# Overwrite with an empty placeholder
python scripts/generate_review.py --clear
git add scan-review.html && git commit -m "Clear review page after approval" && git push
```

---

## Applying results

```bash
# Dry run first (no changes written)
python scripts/apply_scan_results.py news   scan_results/news_2026-05-01.json --dry-run
python scripts/apply_scan_results.py photos scan_results/photos_2026-05-01.json --dry-run
python scripts/apply_scan_results.py policy scan_results/policy_2026-05-01.json --dry-run
python scripts/apply_scan_results.py bios   scan_results/bios_2026-05-01.json --dry-run

# Apply for real
python scripts/apply_scan_results.py news   scan_results/news_2026-05-01.json
python scripts/apply_scan_results.py photos scan_results/photos_2026-05-01.json
python scripts/apply_scan_results.py policy scan_results/policy_2026-05-01.json
python scripts/apply_scan_results.py bios   scan_results/bios_2026-05-01.json
```

After applying, bump the cache-bust version in `js/municipality.js` (line 3):
```js
import { ... } from './data/candidates.js?v=21';  // increment by 1
```

Then run translations before committing:
```bash
python scripts/i18n_translate_pending.py
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
scan_manifest.json                       ← generated before each session
scan_results/
  TEMPLATE_news.json                     ← copy & fill in
  TEMPLATE_photos.json                   ← copy & fill in
  TEMPLATE_policy.json                   ← copy & fill in
  news_2026-05-01.json                   ← result files (date-stamped)
  news_2026-05-01_A.json                 ← parallel-agent slices
  photos_2026-04-28.json
  policy_2026-04-28_A.json               ← parallel-agent slices
  policy_2026-04-28_A_AUDITED.json       ← post-verify_quotes.py
  applied/                               ← move applied scans here
  quarantine/                            ← move untrustworthy scans here
scripts/
  generate_manifest.py                   ← run first
  generate_review.py                     ← live-render the review page
  verify_quotes.py                       ← MANDATORY for policy scans, before review
  apply_scan_results.py                  ← run after results are approved
```
