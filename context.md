# Session Context — Iceland Elections Project

## Architecture

**Project root**: `F:\Claude Projects\iceland-elections\`
**GitHub remote**: `iceland-elections-2026` (https://github.com/halldorberg/iceland-elections-2026)
Static web app for Icelandic municipal elections (2026).

### Key Files
- `js/data/candidates.js` — master candidate data
  - Structure: `const RVK = { B: { tagline, platformUrl, agenda[], list[] } }`
  - List entries: `[seat, 'Name', 'occupation', 'imageUrl'|null, { age, bio, heimild, interests, social, news }]`
  - Short-form entries (no image slot): `[seat, 'Name', 'occupation']` — inserting a photo URL requires adding it before the closing `]`
- `js/data/candidates.en.js` / `candidates.pl.js` — overlay JS (committed). Built from `translations/strings_*.json` via `i18n_translate_pending.py`
- `js/data/eye_positions.js` — per-image eyeY map (committed). Built by `scripts/detect_eye_positions.py`
- `css/municipality.css` — candidate modal styling
- `translations/pending.json` — i18n strings awaiting translation (gitignored)
- `js/data/municipalities.js` — municipality metadata

### Modal hero photo positioning
`js/municipality.js applySmartCrop()` positions the hero photo so the subject's eyes land at ~1/3 from the top of the visible area:
1. Looks up `EYE_POSITIONS[<images/candidates/...path>]` first (precomputed by OpenCV).
2. Falls back to browser `FaceDetector` API (mostly Android Chromium only).
3. Falls back to CSS default `object-position: center 25%`.
- **Regenerate map**: `python scripts/detect_eye_positions.py` (covers all `images/candidates/*` — currently ~97% detection rate).
- Remote (Framer) images aren't covered by the map; they rely on the browser fallback or CSS default.

### Infrastructure
- Preview server: `localhost:3457` (`python serve.py 3457`)
- Worktrees: Claude Code agents may run in `.claude/worktrees/<name>/`. The preview server (per `.claude/launch.json`) starts in the worktree's cwd, so its file changes are mirrored from `main` for verification before commits land on master.
- Edge browser on CDP port `9222` — used for JS-rendered sites (framsokn.is)
- i18n hook fires on commit — changed translatable string keys auto-added to `translations/pending.json`

### Party Codes
Each municipality object has party sub-objects keyed by letter:
- `B` = Framsóknarflokkurinn
- `J` = Sósíalistaflokkurinn (Reykjavík only)
- `P` = Píratar (Reykjavík)
- `D` = Sjálfstæðisflokkurinn
- etc.

---

## Recent commits (master)
- `5c45e22` — Position modal hero photo with face-detected eye Y (per-image OpenCV detection)
- `e221361` — Translate RVK J bios #1–5 to EN and PL
- `8315325` — Rewrite RVK J candidate bios as proper third-person summaries
- `b544f4d` — Add all Framsóknarflokkurinn candidate photos from framsokn.is

---

## Known follow-ups (deferred)

### `_occupations` block vs top-level `_occ:` keys
`translations/strings_*.json` has 4 occupation entries that drifted from the `_occupations` nested block to top-level `_occ:` prefixed keys. `municipality.js:28` reads `TR._occupations?.[occ]`, so those occupations would fall back to Icelandic if shipped. Affected occupations:
- `Stjórnmálasagnfræðingur`
- `Stuðningsfulltrúi í grunnskóla`
- `Stuðningsfulltrúi í grunnskóla og leikjahönnuður`
- `Stuðningsfulltrúi í grunnskóla og listfræðinemi`

The kopavogur.J.list.1/.2 bio + occupation strings have also drifted between source and overlay. To resolve: decide on the structure (probably move `_occ:` entries back into `_occupations` block) and rebuild overlays.

### Untracked top-level files
~50 untracked Python scripts and JSON files clutter the project root and `scripts/`. Most appear to be one-shot research/scraping artifacts. Worth a sweep to either commit or `.gitignore` them.

---

## Constraints / Gotchas

- **framsokn.is is JS-rendered** — WebFetch returns no images; must use Edge CDP (port 9222)
- **Chrome MCP blocks framsokn.is** domain — use Edge CDP directly via PowerShell WebSocket
- **Short-form candidate entries** `[seat, name, occupation]` have no image slot — insert URL before closing `]`
- **PowerShell 5.x**: no `??` null-coalescing, no `&&` pipeline chaining — use explicit null checks and `;`
- **framsokn.is images**: hosted on `framerusercontent.com` CDN; URL format `https://framerusercontent.com/images/[ID].jpg`
- **i18n hook**: fires automatically on every commit — any changed translatable string keys get added to `translations/pending.json`
- **Translation pipeline**: `pending.json` (gitignored) → `strings_*.json` (gitignored) → `candidates.{en,pl}.js` (committed). Running `scripts/i18n_translate_pending.py` translates pending entries via OpenAI and rebuilds the overlay JS files. To ship hand-written translations, edit `strings_*.json` directly and call `rebuild_overlay`.
- **MediaPipe quirk on Windows**: the wheel installs without `mediapipe.solutions`. Use OpenCV Haar cascades or the new `mediapipe.tasks` API.
